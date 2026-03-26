"""
配置设置模块
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SWARMCLONE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "127.0.0.1"
    port: int = 8765
    log_level: str = "INFO"

    debug: bool = False

    @property
    def websocket_url(self) -> str:
        return f"ws://{self.host}:{self.port}"
