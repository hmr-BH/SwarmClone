"""
SwarmClone 主入口
"""

import asyncio

from core.config.loader import ConfigLoader
from core.models.messages import BaseMessage, MessageType
from core.router.message_router import MessageRouter
from core.server.websocket_server import WebSocketServer
from core.utils.logger import setup_logger
from loguru import logger


async def main() -> None:
    config_loader = ConfigLoader()
    settings = config_loader.load_settings()

    setup_logger(settings.log_level)

    router = MessageRouter()

    @router.on(MessageType.STATUS)
    async def handle_status(message: BaseMessage) -> None:
        logger.info(f"收到状态消息: {message}")

    @router.on(MessageType.ACTION)
    async def handle_action(message: BaseMessage) -> None:
        logger.info(f"收到动作消息: {message}")

    server = WebSocketServer(settings, router)

    try:
        await server.start()
        logger.info("SwarmClone Core 已启动，按 Ctrl+C 停止")
        await asyncio.Future()
    except KeyboardInterrupt:
        logger.info("正在停止服务...")
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
