"""
配置数据模型
"""

from typing import Optional

from pydantic import BaseModel, Field


class RedisConfig(BaseModel):
    """Redis配置"""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None


class ASRConfig(BaseModel):
    """ASR服务配置"""

    enabled: bool = True
    engine: str = "whisper"
    model: str = "base"
    language: str = "zh"
    device: Optional[str] = None


class VisionConfig(BaseModel):
    """视觉服务配置"""

    enabled: bool = False
    device: int = 0
    fps: int = 30


class VRChatConfig(BaseModel):
    """VRChat服务配置"""

    enabled: bool = True
    osc_address: str = "127.0.0.1"
    osc_port: int = 9000
    auto_reconnect: bool = True
    reconnect_interval: float = 5.0


class KeyboardConfig(BaseModel):
    """键盘服务配置"""

    enabled: bool = True


class WebConfig(BaseModel):
    """Web面板配置"""

    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 8080


class SystemConfig(BaseModel):
    """系统配置"""

    mode: str = "development"
    log_level: str = "INFO"


class Config(BaseModel):
    """主配置"""

    system: SystemConfig = Field(default_factory=SystemConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    asr: ASRConfig = Field(default_factory=ASRConfig)
    vision: VisionConfig = Field(default_factory=VisionConfig)
    vrchat: VRChatConfig = Field(default_factory=VRChatConfig)
    keyboard: KeyboardConfig = Field(default_factory=KeyboardConfig)
    web: WebConfig = Field(default_factory=WebConfig)
