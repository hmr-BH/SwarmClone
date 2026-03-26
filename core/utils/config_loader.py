"""
配置加载器模块
"""

from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import ValidationError

from core.models.config import Config
from loguru import logger

try:
    import tomli
except ImportError:
    import tomllib as tomli


class ConfigLoader:
    """配置加载器"""

    def __init__(self, config_path: str | Path = "config"):
        self.config_path = Path(config_path)
        self._config: Optional[Config] = None
        self._raw_config: dict[str, Any] = {}

    def load(self) -> Config:
        """
        加载配置文件

        Returns:
            Config对象
        """
        self._raw_config = {}

        self._load_yaml(self.config_path / "config.yaml")

        env_config = self._load_env_vars()
        self._raw_config = self._deep_merge(self._raw_config, env_config)

        try:
            self._config = Config(**self._raw_config)
            logger.info("配置加载成功")
            return self._config
        except ValidationError as e:
            logger.error(f"配置验证失败: {e}")
            raise

    def _load_yaml(self, path: Path) -> None:
        """加载YAML配置文件"""
        if path.exists():
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                self._raw_config = self._deep_merge(self._raw_config, data)
                logger.debug(f"已加载配置文件: {path}")

    def _load_env_vars(self) -> dict[str, Any]:
        """从环境变量加载配置"""
        import os

        env_config: dict[str, Any] = {}

        env_mappings = {
            "SWARMCLONE_MODE": ("system", "mode"),
            "SWARMCLONE_LOG_LEVEL": ("system", "log_level"),
            "REDIS_HOST": ("redis", "host"),
            "REDIS_PORT": ("redis", "port"),
            "REDIS_PASSWORD": ("redis", "password"),
            "ASR_ENGINE": ("asr", "engine"),
            "ASR_MODEL": ("asr", "model"),
            "VRCHAT_OSC_ADDRESS": ("vrchat", "osc_address"),
            "VRCHAT_OSC_PORT": ("vrchat", "osc_port"),
            "WEB_HOST": ("web", "host"),
            "WEB_PORT": ("web", "port"),
        }

        for env_key, config_path in env_mappings.items():
            value = os.environ.get(env_key)
            if value:
                self._set_nested(env_config, config_path, value)

        return env_config

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """深度合并字典"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _set_nested(self, data: dict, path: tuple, value: Any) -> None:
        """设置嵌套字典值"""
        for key in path[:-1]:
            if key not in data:
                data[key] = {}
            data = data[key]
        data[path[-1]] = value

    @property
    def config(self) -> Config:
        """获取当前配置"""
        if self._config is None:
            self.load()
        return self._config

    def reload(self) -> Config:
        """重新加载配置"""
        return self.load()
