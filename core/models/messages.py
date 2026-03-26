"""
消息模型定义
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    ACTION = "action"
    CONFIG = "config"
    STATUS = "status"
    LOG = "log"
    SPEECH = "speech"
    VISION = "vision"
    CONTROL = "control"


class BaseMessage(BaseModel):
    type: MessageType
    source: str = Field(default="unknown")
    target: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)


class ActionMessage(BaseMessage):
    type: MessageType = MessageType.ACTION
    action_name: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class ConfigMessage(BaseMessage):
    type: MessageType = MessageType.CONFIG
    key: str
    value: Any


class StatusMessage(BaseMessage):
    type: MessageType = MessageType.STATUS
    service_name: str
    status: str
    details: dict[str, Any] = Field(default_factory=dict)
