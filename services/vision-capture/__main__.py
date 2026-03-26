"""
视觉捕获服务入口
"""

import asyncio

from loguru import logger

from services.vision_capture.capture import VisionCapture
from services.vision_capture.config import VisionSettings


async def main() -> None:
    logger.info("启动视觉捕获服务...")

    settings = VisionSettings()
    capture = VisionCapture(settings)

    try:
        await capture.connect()
        logger.info("视觉捕获服务已启动，按 Ctrl+C 停止")
        await capture.capture_loop()
    except KeyboardInterrupt:
        logger.info("正在停止视觉捕获服务...")
    finally:
        await capture.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
