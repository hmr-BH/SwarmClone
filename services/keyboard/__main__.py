"""
键盘操作服务入口
"""

import asyncio

from loguru import logger

from services.keyboard.config import KeyboardSettings
from services.keyboard.listener import KeyboardListener


async def main() -> None:
    logger.info("启动键盘操作服务...")

    settings = KeyboardSettings()
    listener = KeyboardListener(settings)

    try:
        await listener.connect()
        logger.info("键盘操作服务已启动，按 Ctrl+C 停止")
        await listener.listen_loop()
    except KeyboardInterrupt:
        logger.info("正在停止键盘操作服务...")
    finally:
        await listener.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
