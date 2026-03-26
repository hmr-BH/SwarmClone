"""
键盘服务主程序
"""

import asyncio
import json
import signal
import sys
from pathlib import Path
from typing import Optional

import redis.asyncio as redis
from loguru import logger

from src.config import KeyboardConfig, RedisConfig
from src.listener import HotkeyListener, PYNPUT_AVAILABLE


class KeyboardService:
    """键盘服务"""

    def __init__(
        self,
        keyboard_config: KeyboardConfig,
        redis_config: RedisConfig,
    ):
        self.keyboard_config = keyboard_config
        self.redis_config = redis_config

        self.listener: Optional[HotkeyListener] = None
        self.redis: Optional[redis.Redis] = None

        self._running = False
        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        """启动服务"""
        logger.info("启动键盘服务...")

        await self._init_redis()
        self._init_listener()

        self._running = True
        logger.info("键盘服务已启动")

    async def stop(self) -> None:
        """停止服务"""
        logger.info("停止键盘服务...")

        self._running = False

        if self.listener:
            self.listener.stop()

        if self.redis:
            await self.redis.close()

        logger.info("键盘服务已停止")

    async def _init_redis(self) -> None:
        """初始化Redis连接"""
        self.redis = redis.Redis(
            host=self.redis_config.host,
            port=self.redis_config.port,
            db=self.redis_config.db,
            decode_responses=True,
        )
        await self.redis.ping()
        logger.info(f"已连接到Redis: {self.redis_config.host}:{self.redis_config.port}")

    def _init_listener(self) -> None:
        """初始化快捷键监听器"""
        self.listener = HotkeyListener()

        for hotkey, action in self.keyboard_config.hotkeys.items():
            self.listener.register(hotkey, self._create_callback(action))

        self.listener.start()

    def _create_callback(self, action: str):
        """创建快捷键回调"""

        async def callback(hotkey: str) -> None:
            logger.info(f"快捷键触发: {hotkey} -> {action}")
            await self._publish_event(hotkey, action)

        return callback

    async def _publish_event(self, hotkey: str, action: str) -> None:
        """发布键盘事件"""
        if not self.redis:
            return

        message = {
            "type": "keyboard_event",
            "timestamp": asyncio.get_event_loop().time(),
            "data": {
                "key": hotkey,
                "action": action,
            },
        }

        await self.redis.publish(self.redis_config.channel, json.dumps(message, ensure_ascii=False))

    async def wait_for_shutdown(self) -> None:
        """等待关闭信号"""
        await self._shutdown_event.wait()

    def request_shutdown(self) -> None:
        """请求关闭"""
        self._shutdown_event.set()


def load_config(config_path: str = "config/config.yaml") -> tuple[KeyboardConfig, RedisConfig]:
    """加载配置"""
    import yaml

    path = Path(config_path)
    if path.exists():
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        services = data.get("services", {}).get("keyboard", {})
        messaging = data.get("messaging", {}).get("redis", {})

        keyboard_config = KeyboardConfig(**services)
        redis_config = RedisConfig(**messaging)
    else:
        keyboard_config = KeyboardConfig()
        redis_config = RedisConfig()

    hotkey_file = Path("config/hotkeys.yaml")
    if hotkey_file.exists():
        with open(hotkey_file, encoding="utf-8") as f:
            hotkey_data = yaml.safe_load(f) or {}
            keyboard_config.hotkeys = hotkey_data.get("hotkeys", {})

    return keyboard_config, redis_config


async def main() -> None:
    """主函数"""
    logger.remove()
    logger.add(sys.stdout, level="INFO")

    keyboard_config, redis_config = load_config()

    if not keyboard_config.enabled:
        logger.info("键盘服务已禁用")
        return

    if not PYNPUT_AVAILABLE:
        logger.warning("pynput未安装，快捷键监听将无法工作")

    service = KeyboardService(keyboard_config, redis_config)

    def signal_handler(signum, frame):
        logger.info(f"收到信号 {signum}，正在关闭...")
        service.request_shutdown()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await service.start()
        await service.wait_for_shutdown()
    except Exception as e:
        logger.error(f"键盘服务错误: {e}")
        sys.exit(1)
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
