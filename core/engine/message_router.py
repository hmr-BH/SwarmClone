"""
消息路由器模块
"""

import asyncio
import json
from typing import Any, Optional

import redis.asyncio as redis
from core.engine.event_handler import EventData, EventDispatcher
from core.models.action import Action
from loguru import logger


class MessageRouter:
    """消息路由器"""

    CHANNEL_ASR_RESULT = "asr:result"
    CHANNEL_VISION_UPDATE = "vision:update"
    CHANNEL_KEYBOARD_EVENT = "keyboard:event"
    CHANNEL_ACTION_TRIGGER = "action:trigger"
    CHANNEL_ACTION_COMPLETE = "action:complete"
    CHANNEL_STATE_CHANGE = "state:change"
    CHANNEL_LOG_STREAM = "log:stream"

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
    ):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.dispatcher: Optional[EventDispatcher] = None
        self._running = False
        self._subscribed_channels: set[str] = set()

    async def connect(self) -> None:
        """连接Redis"""
        try:
            self.redis = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                decode_responses=True,
            )
            await self.redis.ping()
            self.pubsub = self.redis.pubsub()
            logger.info(f"已连接到Redis: {self.redis_host}:{self.redis_port}")
        except Exception as e:
            logger.error(f"连接Redis失败: {e}")
            raise

    async def disconnect(self) -> None:
        """断开Redis连接"""
        self._running = False
        if self.pubsub:
            await self.pubsub.close()
        if self.redis:
            await self.redis.close()
        logger.info("已断开Redis连接")

    def set_dispatcher(self, dispatcher: EventDispatcher) -> None:
        """设置事件分发器"""
        self.dispatcher = dispatcher

    async def subscribe(self, channels: list[str]) -> None:
        """
        订阅消息频道

        Args:
            channels: 频道列表
        """
        if not self.pubsub:
            raise RuntimeError("未连接到Redis")

        await self.pubsub.subscribe(*channels)
        for channel in channels:
            self._subscribed_channels.add(channel)
        logger.info(f"已订阅频道: {channels}")

    async def unsubscribe(self, channels: list[str]) -> None:
        """取消订阅频道"""
        if self.pubsub:
            await self.pubsub.unsubscribe(*channels)
            for channel in channels:
                self._subscribed_channels.discard(channel)
            logger.info(f"已取消订阅频道: {channels}")

    async def publish(self, channel: str, message: dict[str, Any]) -> None:
        """
        发布消息

        Args:
            channel: 频道名称
            message: 消息内容
        """
        if not self.redis:
            raise RuntimeError("未连接到Redis")

        message_data = {
            "type": channel.split(":")[-1] if ":" in channel else "message",
            "timestamp": asyncio.get_event_loop().time(),
            "data": message,
        }

        await self.redis.publish(channel, json.dumps(message_data, ensure_ascii=False))
        logger.debug(f"已发布消息到 {channel}: {message}")

    async def start_listening(self) -> None:
        """开始监听消息"""
        if not self.pubsub:
            raise RuntimeError("未连接到Redis")

        self._running = True
        logger.info("开始监听消息...")

        try:
            async for message in self.pubsub.listen():
                if not self._running:
                    break

                if message["type"] == "message":
                    await self._handle_message(message)
        except asyncio.CancelledError:
            logger.info("消息监听已取消")
        except Exception as e:
            logger.error(f"消息监听错误: {e}")

    async def stop_listening(self) -> None:
        """停止监听消息"""
        self._running = False
        logger.info("停止监听消息")

    async def _handle_message(self, message: dict) -> None:
        """处理收到的消息"""
        channel = message.get("channel", "")
        data = message.get("data", "")

        try:
            if isinstance(data, str):
                message_data = json.loads(data)
            else:
                message_data = data

            event = self._create_event(channel, message_data)

            if event and self.dispatcher:
                action = await self.dispatcher.dispatch(event)
                if action:
                    await self._handle_action(action)

        except json.JSONDecodeError:
            logger.warning(f"无效的JSON消息: {data}")
        except Exception as e:
            logger.error(f"处理消息错误: {e}")

    def _create_event(self, channel: str, message_data: dict) -> Optional[EventData]:
        """根据频道创建对应的事件对象"""
        from core.engine.event_handler import (
            ASRResultEvent,
            VisionUpdateEvent,
            KeyboardEvent,
        )

        data = message_data.get("data", {})

        if channel == self.CHANNEL_ASR_RESULT:
            return ASRResultEvent(
                text=data.get("text", ""),
                confidence=data.get("confidence", 0.0),
                is_final=data.get("is_final", True),
            )

        elif channel == self.CHANNEL_VISION_UPDATE:
            return VisionUpdateEvent(face_data=data)

        elif channel == self.CHANNEL_KEYBOARD_EVENT:
            return KeyboardEvent(
                key=data.get("key", ""),
                action_type=data.get("action", "press"),
            )

        return None

    async def _handle_action(self, action: Action) -> None:
        """处理触发的动作"""
        action_message = {
            "name": action.name,
            "type": action.type.value,
            "parameters": action.parameters,
            "priority": action.priority,
        }

        await self.publish(self.CHANNEL_ACTION_TRIGGER, action_message)
        logger.info(f"已触发动作: {action.name}")
