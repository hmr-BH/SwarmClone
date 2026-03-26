"""
ASR服务主程序
"""

import asyncio
import json
import signal
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import redis.asyncio as redis
from loguru import logger

from src.config import ASRConfig, RedisConfig
from src.engine import ASREngine, ASRResult, MockASREngine, WhisperEngine
from src.audio import AudioCapture, VAD


class ASRService:
    """ASR服务"""

    def __init__(
        self,
        asr_config: ASRConfig,
        redis_config: RedisConfig,
    ):
        self.asr_config = asr_config
        self.redis_config = redis_config

        self.engine: Optional[ASREngine] = None
        self.audio: Optional[AudioCapture] = None
        self.vad: Optional[VAD] = None
        self.redis: Optional[redis.Redis] = None

        self._running = False
        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        """启动服务"""
        logger.info("启动ASR服务...")

        await self._init_redis()
        await self._init_engine()
        self._init_audio()

        self._running = True
        logger.info("ASR服务已启动")

    async def stop(self) -> None:
        """停止服务"""
        logger.info("停止ASR服务...")

        self._running = False

        if self.audio:
            self.audio.stop()

        if self.engine:
            await self.engine.shutdown()

        if self.redis:
            await self.redis.close()

        logger.info("ASR服务已停止")

    async def _init_redis(self) -> None:
        """初始化Redis连接"""
        self.redis = redis.Redis(
            host=self.redis_config.host,
            port=self.redis_config.port,
            db=self.redis_config.db,
            decode_responses=True,
        )
        await self.redis.ping()
        logger.info(f"已连接到Redis: {self.redis_config.host}:{self.redis_config.port}")

    async def _init_engine(self) -> None:
        """初始化ASR引擎"""
        if self.asr_config.engine == "whisper":
            try:
                self.engine = WhisperEngine(
                    model=self.asr_config.model,
                    language=self.asr_config.language,
                    device=self.asr_config.device,
                )
                await self.engine.initialize()
            except Exception as e:
                logger.warning(f"Whisper初始化失败: {e}，使用Mock引擎")
                self.engine = MockASREngine()
                await self.engine.initialize()
        else:
            self.engine = MockASREngine()
            await self.engine.initialize()

    def _init_audio(self) -> None:
        """初始化音频捕获"""
        self.vad = VAD(
            threshold=self.asr_config.vad_threshold,
            silence_duration=self.asr_config.silence_duration,
            sample_rate=self.asr_config.sample_rate,
        )

        self.audio = AudioCapture(
            sample_rate=self.asr_config.sample_rate,
            chunk_size=self.asr_config.chunk_size,
        )

        self.audio.start(self._on_audio)

    def _on_audio(self, audio: np.ndarray) -> None:
        """音频回调"""
        if not self._running:
            return

        if self.asr_config.vad_enabled and self.vad:
            speaking, complete_audio = self.vad.process(audio)
            if complete_audio is not None:
                asyncio.create_task(self._process_audio(complete_audio))
        else:
            asyncio.create_task(self._process_audio(audio))

    async def _process_audio(self, audio: np.ndarray) -> None:
        """处理音频并识别"""
        try:
            result = await self.engine.transcribe(audio)

            if result.text:
                logger.info(f"识别结果: {result.text}")
                await self._publish_result(result)

        except Exception as e:
            logger.error(f"音频处理错误: {e}")

    async def _publish_result(self, result: ASRResult) -> None:
        """发布识别结果"""
        if not self.redis:
            return

        message = {
            "type": "asr_result",
            "timestamp": asyncio.get_event_loop().time(),
            "data": {
                "text": result.text,
                "confidence": result.confidence,
                "is_final": result.is_final,
                "language": result.language,
            },
        }

        await self.redis.publish(self.redis_config.channel, json.dumps(message, ensure_ascii=False))

    async def wait_for_shutdown(self) -> None:
        """等待关闭信号"""
        await self._shutdown_event.wait()

    def request_shutdown(self) -> None:
        """请求关闭"""
        self._shutdown_event.set()


def load_config(config_path: str = "config/config.yaml") -> tuple[ASRConfig, RedisConfig]:
    """加载配置"""
    import yaml

    path = Path(config_path)
    if path.exists():
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        services = data.get("services", {}).get("asr", {})
        messaging = data.get("messaging", {}).get("redis", {})

        asr_config = ASRConfig(**services)
        redis_config = RedisConfig(**messaging)
    else:
        asr_config = ASRConfig()
        redis_config = RedisConfig()

    return asr_config, redis_config


async def main() -> None:
    """主函数"""
    logger.remove()
    logger.add(sys.stdout, level="INFO")

    asr_config, redis_config = load_config()

    if not asr_config.enabled:
        logger.info("ASR服务已禁用")
        return

    service = ASRService(asr_config, redis_config)

    def signal_handler(signum, frame):
        logger.info(f"收到信号 {signum}，正在关闭...")
        service.request_shutdown()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await service.start()
        await service.wait_for_shutdown()
    except Exception as e:
        logger.error(f"ASR服务错误: {e}")
        sys.exit(1)
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
