"""
VRChat服务配置
"""

from typing import Optional

from pydantic import BaseModel


class VRChatConfig(BaseModel):
    """VRChat服务配置"""

    enabled: bool = True
    osc_address: str = "127.0.0.1"
    osc_port: int = 9000
    auto_reconnect: bool = True
    reconnect_interval: float = 5.0


class RedisConfig(BaseModel):
    """Redis配置"""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    channel: str = "action:trigger"


class ParameterMapping(BaseModel):
    """参数映射"""

    address: str
    value: float | int | str | bool
    type: str = "float"
    transition_time: float = 0.0
