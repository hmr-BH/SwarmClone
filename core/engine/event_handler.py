"""
事件处理器模块
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from core.models.action import Action
from core.engine.action_mapper import ActionMapper
from loguru import logger


class EventData:
    """事件数据基类"""

    def __init__(self, event_type: str, data: Any, timestamp: Optional[float] = None):
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or 0.0


class ASRResultEvent(EventData):
    """ASR识别结果事件"""

    def __init__(self, text: str, confidence: float, is_final: bool = True):
        super().__init__(
            "asr_result",
            {
                "text": text,
                "confidence": confidence,
                "is_final": is_final,
            },
        )
        self.text = text
        self.confidence = confidence
        self.is_final = is_final


class VisionUpdateEvent(EventData):
    """视觉追踪更新事件"""

    def __init__(self, face_data: dict[str, Any]):
        super().__init__("vision_update", face_data)
        self.face_data = face_data


class KeyboardEvent(EventData):
    """键盘事件"""

    def __init__(self, key: str, action_type: str = "press"):
        super().__init__(
            "keyboard_event",
            {
                "key": key,
                "action": action_type,
            },
        )
        self.key = key
        self.action_type = action_type


class EventHandler(ABC):
    """事件处理器基类"""

    def __init__(self, action_mapper: ActionMapper):
        self.action_mapper = action_mapper

    @abstractmethod
    def can_handle(self, event: EventData) -> bool:
        """检查是否能处理该事件"""
        pass

    @abstractmethod
    def handle(self, event: EventData) -> Optional[Action]:
        """处理事件"""
        pass


class ASREventHandler(EventHandler):
    """ASR事件处理器"""

    def can_handle(self, event: EventData) -> bool:
        return isinstance(event, ASRResultEvent) and event.is_final

    def handle(self, event: EventData) -> Optional[Action]:
        if not isinstance(event, ASRResultEvent):
            return None

        logger.debug(f"处理ASR结果: {event.text} (置信度: {event.confidence:.2f})")

        if event.confidence < 0.5:
            logger.debug(f"置信度过低，忽略: {event.confidence:.2f}")
            return None

        return self.action_mapper.map_trigger(event.text)


class VisionEventHandler(EventHandler):
    """视觉事件处理器"""

    def can_handle(self, event: EventData) -> bool:
        return isinstance(event, VisionUpdateEvent)

    def handle(self, event: EventData) -> Optional[Action]:
        if not isinstance(event, VisionUpdateEvent):
            return None

        logger.debug(f"处理视觉数据: {event.face_data}")

        return None


class KeyboardEventHandler(EventHandler):
    """键盘事件处理器"""

    def can_handle(self, event: EventData) -> bool:
        return isinstance(event, KeyboardEvent)

    def handle(self, event: EventData) -> Optional[Action]:
        if not isinstance(event, KeyboardEvent):
            return None

        logger.debug(f"处理键盘事件: {event.key} ({event.action_type})")

        trigger = f"key:{event.key}"
        return self.action_mapper.map_trigger(trigger)


class EventDispatcher:
    """事件分发器"""

    def __init__(self, action_mapper: ActionMapper):
        self.handlers: list[EventHandler] = [
            ASREventHandler(action_mapper),
            VisionEventHandler(action_mapper),
            KeyboardEventHandler(action_mapper),
        ]
        self.action_callback: Optional[callable] = None

    def set_action_callback(self, callback: callable) -> None:
        """设置动作回调函数"""
        self.action_callback = callback

    async def dispatch(self, event: EventData) -> Optional[Action]:
        """
        分发事件到对应的处理器

        Args:
            event: 事件数据

        Returns:
            触发的动作，如果没有则返回None
        """
        for handler in self.handlers:
            if handler.can_handle(event):
                action = handler.handle(event)
                if action and self.action_callback:
                    await self.action_callback(action)
                return action

        logger.debug(f"未找到事件处理器: {event.event_type}")
        return None

    def add_handler(self, handler: EventHandler) -> None:
        """添加事件处理器"""
        self.handlers.append(handler)

    def remove_handler(self, handler: EventHandler) -> None:
        """移除事件处理器"""
        if handler in self.handlers:
            self.handlers.remove(handler)
