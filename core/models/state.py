"""
状态相关数据模型
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SystemMode(str, Enum):
    """系统运行模式"""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class ServiceStatus(str, Enum):
    """服务状态枚举"""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class ModelState(BaseModel):
    """模型状态"""

    is_loaded: bool = False
    model_type: Optional[str] = None
    model_path: Optional[str] = None
    current_action: Optional[str] = None
    parameters: dict[str, float] = Field(default_factory=dict)
    expressions: dict[str, float] = Field(default_factory=dict)


class VRChatState(BaseModel):
    """VRChat连接状态"""

    connected: bool = False
    osc_address: str = "127.0.0.1"
    osc_port: int = 9000
    avatar_id: Optional[str] = None


class ServiceInfo(BaseModel):
    """服务信息"""

    name: str
    status: ServiceStatus = ServiceStatus.STOPPED
    pid: Optional[int] = None
    uptime: float = 0.0
    error_message: Optional[str] = None


class SystemState(BaseModel):
    """系统全局状态"""

    mode: SystemMode = SystemMode.DEVELOPMENT
    version: str = "0.1.0"
    uptime: float = 0.0
    services: dict[str, ServiceInfo] = Field(default_factory=dict)
    model_state: ModelState = Field(default_factory=ModelState)
    vrchat_state: VRChatState = Field(default_factory=VRChatState)
    current_action: Optional[str] = None
