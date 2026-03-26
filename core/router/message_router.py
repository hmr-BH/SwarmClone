"""
消息路由器
"""

import asyncio
from collections.abc import Callable, Awaitable
from typing import Any

from loguru import logger

from core.models.messages import BaseMessage, MessageType


Handler = Callable[[BaseMessage], Awaitable[None]]


class MessageRouter:
    def __init__(self) -> None:
        self._handlers: dict[MessageType, list[Handler]] = {
            msg_type: [] for msg_type in MessageType
        }
        self._default_handlers: list[Handler] = []

    def register(
        self, msg_type: MessageType | None, handler: Handler
    ) -> None:
        if msg_type is None:
            self._default_handlers.append(handler)
        else:
            self._handlers[msg_type].append(handler)

    async def route(self, message: BaseMessage) -> None:
        handlers = self._handlers.get(message.type, [])

        if not handlers:
            logger.warning(f"未找到消息类型 {message.type} 的处理器")
            handlers = self._default_handlers

        tasks = [handler(message) for handler in handlers]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def on(
        self, msg_type: MessageType | None = None
    ) -> Callable[[Handler], Handler]:
        def decorator(func: Handler) -> Handler:
            self.register(msg_type, func)
            return func

        return decorator
