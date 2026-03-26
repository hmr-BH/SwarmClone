"""
视觉捕获配置模块
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class VisionSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="VISION_",
        env_file=".env",
        extra="ignore",
    )

    core_ws_url: str = "ws://127.0.0.1:8765"
    camera_index: int = 0
    frame_width: int = 640
    frame_height: int = 480
    fps: int = 30
    enable_face_detection: bool = True
    enable_face_mesh: bool = True
    enable_pose: bool = False
