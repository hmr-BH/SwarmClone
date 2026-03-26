"""
WebSocket 服务端
"""

import asyncio
import json
from typing import Any

import websockets
from loguru import logger
from websockets.server import serve, WebSocketServerProtocol

from core.config.settings import Settings
from core.models.messages import BaseMessage
from core.router.message_router import MessageRouter


class WebSocketServer:
    def __init__(
        self,
        settings: Settings,
        router: MessageRouter,
    ) -> None:
        self.settings = settings
        self.router = router
        self._clients: set[WebSocketServerProtocol] = set()
        self._server: Any = None

    async def handler(
        self, websocket: WebSocketServerProtocol, path: str
    ) -> None:
        client_addr = websocket.remote_address
        logger.info(f"客户端连接: {client_addr}")
        self._clients.add(websocket)

        try:
            async for raw_message in websocket:
                try:
                    data = json.loads(raw_message)
                    message = BaseMessage.model_validate(data)
                    await self.router.route(message)
                except json.JSONDecodeError:
                    logger.error(f"无效的 JSON 消息: {raw_message}")
                except Exception as e:
                    logger.error(f"处理消息时出错: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"客户端断开: {client_addr}")
        finally:
            self._clients.discard(websocket)

    async def broadcast(self, message: BaseMessage) -> None:
        if not self._clients:
            return

        raw_message = message.model_dump_json()
        tasks = [client.send(raw_message) for client in self._clients]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def start(self) -> None:
        self._server = await serve(
            self.handler,
            self.settings.host,
            self.settings.port,
        )
        logger.info(
            f"WebSocket 服务端启动: {self.settings.websocket_url}"
        )

    async def stop(self) -> None:
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            logger.info("WebSocket 服务端已停止")

    @property
    def client_count(self) -> int:
        return len(self._clients)
