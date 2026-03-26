"""
TTS服务主程序
"""

import asyncio
import json
import signal
import sys
from pathlib import Path
from typing import Optional

import redis.asyncio as redis
from loguru import logger

from src.config import TTSConfig, RedisConfig
from src.aliyun_tts import AliyunTTSEngine


class TTSService:
    """TTS服务"""

    def __init__(
        self,
        tts_config: TTSConfig,
        redis_config: RedisConfig,
    ):
        self.tts_config = tts_config
        self.redis_config = redis_config

        self.engine: Optional[AliyunTTSEngine] = None
        self.redis: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None

        self._running = False
        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        """启动服务"""
        logger.info("启动TTS服务...")

        if not self.tts_config.api_key:
            logger.error("未配置API Key")
            return

        await self._init_redis()
        await self._init_engine()

        self._running = True
        logger.info("TTS服务已启动")

    async def stop(self) -> None:
        """停止服务"""
        logger.info("停止TTS服务...")

        self._running = False

        if self.pubsub:
            await self.pubsub.close()

        if self.redis:
            await self.redis.close()

        if self.engine:
            await self.engine.shutdown()

        logger.info("TTS服务已停止")

    async def _init_redis(self) -> None:
        """初始化Redis连接"""
        self.redis = redis.Redis(
            host=self.redis_config.host,
            port=self.redis_config.port,
            db=self.redis_config.db,
            decode_responses=True,
        )
        await self.redis.ping()

        self.pubsub = self.redis.pubsub()
        await self.pubsub.subscribe(self.redis_config.input_channel)

        logger.info(f"已连接到Redis: {self.redis_config.host}:{self.redis_config.port}")

    async def _init_engine(self) -> None:
        """初始化TTS引擎"""
        if self.tts_config.engine == "aliyun":
            self.engine = AliyunTTSEngine(
                api_key=self.tts_config.api_key,
                model=self.tts_config.model,
                voice=self.tts_config.voice,
                sample_rate=self.tts_config.sample_rate,
            )
            await self.engine.initialize()
        else:
            logger.error(f"未知TTS引擎: {self.tts_config.engine}")

    async def run(self) -> None:
        """运行服务"""
        logger.info(f"开始监听TTS请求: {self.redis_config.input_channel}")

        try:
            async for message in self.pubsub.listen():
                if not self._running:
                    break

                if message["type"] == "message":
                    await self._handle_message(message)

        except asyncio.CancelledError:
            logger.info("消息监听被取消")
        except Exception as e:
            logger.error(f"消息监听错误: {e}")

    async def _handle_message(self, message: dict) -> None:
        """处理消息"""
        data = message.get("data", "")

        try:
            if isinstance(data, str):
                msg = json.loads(data)
            else:
                msg = data

            text = msg.get("data", {}).get("text")
            if not text:
                text = msg.get("text")

            if text:
                logger.info(f"收到TTS请求: {text[:50]}...")
                audio_data = await self.engine.synthesize(text)

                await self._publish_audio(audio_data, text)

        except json.JSONDecodeError:
            logger.warning(f"无效的消息格式: {data}")
        except Exception as e:
            logger.error(f"处理消息错误: {e}")

    async def _publish_audio(self, audio_data: bytes, text: str) -> None:
        """发布音频数据"""
        audio_b64 = base64.b64encode(audio_data).decode("ascii")

        message = {
            "type": "tts_audio",
            "text": text,
            "audio": audio_b64,
            "sample_rate": self.tts_config.sample_rate,
            "format": self.tts_config.format,
        }

        await self.redis.publish(self.redis_config.output_channel, json.dumps(message))

        logger.info(f"音频已发布: {len(audio_data)}字节")

    async def wait_for_shutdown(self) -> None:
        """等待关闭信号"""
        await self._shutdown_event.wait()

    def request_shutdown(self) -> None:
        """请求关闭"""
        self._shutdown_event.set()


import base64


def load_config(config_path: str = "config/config.yaml") -> tuple[TTSConfig, RedisConfig]:
    """加载配置"""
    import yaml

    path = Path(config_path)
    if path.exists():
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        services = data.get("services", {}).get("tts", {})
        messaging = data.get("messaging", {}).get("redis", {})

        tts_config = TTSConfig(**services)
        redis_config = RedisConfig(**messaging)
    else:
        tts_config = TTSConfig()
        redis_config = RedisConfig()

    return tts_config, redis_config


async def main() -> None:
    """主函数"""
    logger.remove()
    logger.add(sys.stdout, level="INFO")

    tts_config, redis_config = load_config()

    if not tts_config.enabled:
        logger.info("TTS服务已禁用")
        return

    service = TTSService(tts_config, redis_config)

    def signal_handler(signum, frame):
        logger.info(f"收到信号 {signum}，正在关闭...")
        service.request_shutdown()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await service.start()

        run_task = asyncio.create_task(service.run())
        wait_task = asyncio.create_task(service.wait_for_shutdown())

        done, pending = await asyncio.wait(
            [run_task, wait_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    except Exception as e:
        logger.error(f"TTS服务错误: {e}")
        sys.exit(1)
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
