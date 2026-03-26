"""
键盘服务配置
"""

from typing import Optional

from pydantic import BaseModel


class KeyboardConfig(BaseModel):
    """键盘服务配置"""

    enabled: bool = True
    hotkeys: dict[str, str] = {}


class RedisConfig(BaseModel):
    """Redis配置"""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    channel: str = "keyboard:event"


class HotkeyMapping(BaseModel):
    """快捷键映射"""

    key: str
    action: str
    enabled: bool = True
