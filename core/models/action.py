"""
动作相关数据模型
"""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """动作类型枚举"""

    EXPRESSION = "expression"
    GESTURE = "gesture"
    MOVEMENT = "movement"
    PARAMETER = "parameter"
    SEQUENCE = "sequence"


class Action(BaseModel):
    """动作定义"""

    type: ActionType
    name: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    duration: Optional[float] = None
    priority: int = 0


class ActionMapping(BaseModel):
    """动作映射配置"""

    trigger: str
    action_type: ActionType
    action_name: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    priority: int = 0
    cooldown: float = 0.0
    enabled: bool = True
