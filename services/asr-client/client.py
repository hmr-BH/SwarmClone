"""
ASR 客户端主模块
"""

import asyncio
import json
from typing import Any

import websockets
from loguru import logger

from services.asr_client.config import ASRSettings


class ASRClient:
    def __init__(self, settings: ASRSettings | None = None) -> None:
        self.settings = settings or ASRSettings()
        self._ws: websockets.WebSocketClientProtocol | None = None
        self._running = False

    async def connect(self) -> None:
        try:
            self._ws = await websockets.connect(self.settings.core_ws_url)
            logger.info(f"已连接到核心服务: {self.settings.core_ws_url}")
        except Exception as e:
            logger.error(f"连接核心服务失败: {e}")
            raise

    async def disconnect(self) -> None:
        if self._ws:
            await self._ws.close()
            self._ws = None
            logger.info("已断开与核心服务的连接")

    async def send_text(self, text: str, confidence: float = 1.0) -> None:
        if not self._ws:
            logger.warning("未连接到核心服务")
            return

        message = {
            "type": "speech",
            "source": "asr-client",
            "data": {
                "text": text,
                "confidence": confidence,
                "language": self.settings.language,
            },
        }

        await self._ws.send(json.dumps(message))
        logger.debug(f"发送语音文本: {text}")

    async def process_audio(self, audio_data: bytes) -> str:
        logger.debug(f"处理音频数据: {len(audio_data)} 字节")
        return "[模拟识别结果] 这是一段测试语音"

    async def listen_loop(self) -> None:
        self._running = True
        logger.info("ASR 客户端开始监听...")

        while self._running:
            try:
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break

    def stop(self) -> None:
        self._running = False
        logger.info("ASR 客户端停止监听")


async def main() -> None:
    settings = ASRSettings()
    client = ASRClient(settings)

    try:
        await client.connect()
        await client.listen_loop()
    except KeyboardInterrupt:
        logger.info("收到停止信号")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
