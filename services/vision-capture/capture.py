"""
视觉捕获客户端主模块
"""

import asyncio
import json
from typing import Any

import websockets
from loguru import logger

from services.vision_capture.config import VisionSettings


class VisionCapture:
    def __init__(self, settings: VisionSettings | None = None) -> None:
        self.settings = settings or VisionSettings()
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

    async def send_vision_data(
        self,
        face_data: dict[str, Any] | None = None,
        pose_data: dict[str, Any] | None = None,
    ) -> None:
        if not self._ws:
            logger.warning("未连接到核心服务")
            return

        message = {
            "type": "vision",
            "source": "vision-capture",
            "data": {
                "face": face_data,
                "pose": pose_data,
            },
        }

        await self._ws.send(json.dumps(message))
        logger.debug("发送视觉数据")

    async def capture_frame(self) -> dict[str, Any]:
        logger.debug("捕获帧...")
        return {
            "face_detected": True,
            "landmarks": [],
            "expression": "neutral",
            "head_pose": {"pitch": 0.0, "yaw": 0.0, "roll": 0.0},
        }

    async def capture_loop(self) -> None:
        self._running = True
        logger.info("视觉捕获服务开始运行...")

        while self._running:
            try:
                frame_data = await self.capture_frame()
                await self.send_vision_data(face_data=frame_data)
                await asyncio.sleep(1.0 / self.settings.fps)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"捕获帧时出错: {e}")
                await asyncio.sleep(0.1)

    def stop(self) -> None:
        self._running = False
        logger.info("视觉捕获服务停止")


async def main() -> None:
    settings = VisionSettings()
    capture = VisionCapture(settings)

    try:
        await capture.connect()
        await capture.capture_loop()
    except KeyboardInterrupt:
        logger.info("收到停止信号")
    finally:
        await capture.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
