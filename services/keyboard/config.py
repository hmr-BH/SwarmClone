"""
键盘操作配置模块
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class KeyboardSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KEYBOARD_",
        env_file=".env",
        extra="ignore",
    )

    core_ws_url: str = "ws://127.0.0.1:8765"
    hotkeys: dict[str, str] = {
        "f1": "wave",
        "f2": "nod",
        "f3": "shake_head",
        "f4": "point",
    }
