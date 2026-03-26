"""
视觉服务配置
"""

from typing import Optional

from pydantic import BaseModel


class VisionConfig(BaseModel):
    """视觉服务配置"""

    enabled: bool = False
    device: int = 0
    fps: int = 30
    width: int = 640
    height: int = 480
    enable_face_tracking: bool = True
    enable_eye_tracking: bool = True
    enable_mouth_tracking: bool = True


class RedisConfig(BaseModel):
    """Redis配置"""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    channel: str = "vision:update"
