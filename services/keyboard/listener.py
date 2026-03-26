"""
键盘监听模块
"""

import asyncio
import json
from typing import Callable

import websockets
from loguru import logger

from services.keyboard.config import KeyboardSettings


class KeyboardListener:
    def __init__(self, settings: KeyboardSettings | None = None) -> None:
        self.settings = settings or KeyboardSettings()
        self._ws: websockets.WebSocketClientProtocol | None = None
        self._running = False
        self._key_callbacks: dict[str, Callable[[], None]] = {}

    async def connect(self) -> None:
        try:
            self._ws = await websockets.connect(self.settings.core_ws_url)
            logger.info(f"已连接到核心服务: {self.settings.core_ws_url}")
        except Exception as e:
            logger.error(f"连接核心服务失败: {e}")
            raise

    async def disconnect(self) -> None:
        if self._ws:
            await self._ws.close()
            self._ws = None
            logger.info("已断开与核心服务的连接")

    async def send_action(self, action_name: str, parameters: dict | None = None) -> None:
        if not self._ws:
            logger.warning("未连接到核心服务")
            return

        message = {
            "type": "action",
            "source": "keyboard-service",
            "action_name": action_name,
            "parameters": parameters or {},
        }

        await self._ws.send(json.dumps(message))
        logger.info(f"发送动作: {action_name}")

    def register_hotkey(self, key: str, action: str) -> None:
        async def callback() -> None:
            await self.send_action(action)

        self._key_callbacks[key.lower()] = lambda: asyncio.create_task(callback())
        logger.info(f"注册热键: {key} -> {action}")

    def setup_hotkeys(self) -> None:
        for key, action in self.settings.hotkeys.items():
            self.register_hotkey(key, action)

    async def listen_loop(self) -> None:
        self._running = True
        self.setup_hotkeys()
        logger.info("键盘监听服务开始运行...")
        logger.info(f"已注册热键: {list(self.settings.hotkeys.keys())}")

        try:
            from pynput import keyboard

            def on_press(key: keyboard.Key | keyboard.KeyCode | None) -> None:
                if not self._running:
                    return

                key_name = None
                if isinstance(key, keyboard.Key):
                    key_name = key.name
                elif isinstance(key, keyboard.KeyCode):
                    key_name = key.char or str(key)

                if key_name and key_name.lower() in self._key_callbacks:
                    logger.debug(f"检测到热键: {key_name}")
                    self._key_callbacks[key_name.lower()]()

            listener = keyboard.Listener(on_press=on_press)
            listener.start()

            while self._running:
                await asyncio.sleep(0.1)

            listener.stop()

        except ImportError:
            logger.warning("pynput 未安装，使用模拟模式")
            while self._running:
                await asyncio.sleep(0.1)

    def stop(self) -> None:
        self._running = False
        logger.info("键盘监听服务停止")


async def main() -> None:
    settings = KeyboardSettings()
    listener = KeyboardListener(settings)

    try:
        await listener.connect()
        await listener.listen_loop()
    except KeyboardInterrupt:
        logger.info("收到停止信号")
    finally:
        await listener.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
