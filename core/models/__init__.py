"""
消息模型模块
"""

from core.models.messages import (
    BaseMessage,
    MessageType,
    ActionMessage,
    ConfigMessage,
    StatusMessage,
)

__all__ = [
    "BaseMessage",
    "MessageType",
    "ActionMessage",
    "ConfigMessage",
    "StatusMessage",
]
