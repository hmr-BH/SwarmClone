"""
ASR 配置模块
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class ASRSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ASR_",
        env_file=".env",
        extra="ignore",
    )

    core_ws_url: str = "ws://127.0.0.1:8765"
    model: str = "base"
    language: str = "zh"
    sample_rate: int = 16000
    vad_threshold: float = 0.5
    silence_duration: float = 1.0
