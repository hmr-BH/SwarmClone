"""
配置加载器
"""

import tomli
import tomli_w
from pathlib import Path
from typing import Any

from core.config.settings import Settings


class ConfigLoader:
    def __init__(self, config_path: str | Path = "config.toml"):
        self.config_path = Path(config_path)

    def load(self) -> dict[str, Any]:
        if not self.config_path.exists():
            return {}

        with open(self.config_path, "rb") as f:
            return tomli.load(f)

    def save(self, config: dict[str, Any]) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "wb") as f:
            tomli_w.dump(config, f)

    def load_settings(self) -> Settings:
        config = self.load()
        return Settings(**config.get("core", {}))
