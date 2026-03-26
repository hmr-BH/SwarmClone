"""
快捷键监听器
"""

import asyncio
import threading
from collections import defaultdict
from typing import Callable, Optional

from loguru import logger

try:
    from pynput import keyboard

    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


class HotkeyListener:
    """快捷键监听器"""

    def __init__(self):
        self._listener: Optional[keyboard.Listener] = None
        self._hotkeys: dict[str, Callable] = {}
        self._pressed_keys: set = set()
        self._running = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def register(self, hotkey: str, callback: Callable) -> None:
        """
        注册快捷键

        Args:
            hotkey: 快捷键组合，如 "ctrl+shift+h"
            callback: 回调函数
        """
        self._hotkeys[hotkey.lower()] = callback
        logger.debug(f"注册快捷键: {hotkey}")

    def unregister(self, hotkey: str) -> None:
        """取消注册快捷键"""
        key = hotkey.lower()
        if key in self._hotkeys:
            del self._hotkeys[key]
            logger.debug(f"取消注册快捷键: {hotkey}")

    def start(self) -> None:
        """开始监听"""
        if not PYNPUT_AVAILABLE:
            logger.warning("pynput未安装，使用模拟监听")
            self._running = True
            return

        self._running = True
        self._loop = asyncio.get_event_loop()

        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.start()
        logger.info("快捷键监听已启动")

    def stop(self) -> None:
        """停止监听"""
        self._running = False

        if self._listener:
            self._listener.stop()
            self._listener = None

        self._pressed_keys.clear()
        logger.info("快捷键监听已停止")

    def _on_press(self, key) -> None:
        """按键按下事件"""
        if not self._running:
            return

        key_name = self._get_key_name(key)
        if key_name:
            self._pressed_keys.add(key_name)
            self._check_hotkeys()

    def _on_release(self, key) -> None:
        """按键释放事件"""
        key_name = self._get_key_name(key)
        if key_name and key_name in self._pressed_keys:
            self._pressed_keys.remove(key_name)

    def _get_key_name(self, key) -> Optional[str]:
        """获取按键名称"""
        if key is None:
            return None

        if hasattr(key, "name"):
            name = key.name.lower()
            if name == "ctrl_l" or name == "ctrl_r":
                return "ctrl"
            if name == "shift_l" or name == "shift_r":
                return "shift"
            if name == "alt_l" or name == "alt_r":
                return "alt"
            if name == "cmd" or name == "cmd_l" or name == "cmd_r":
                return "cmd"
            return name

        if hasattr(key, "char") and key.char:
            return key.char.lower()

        return None

    def _check_hotkeys(self) -> None:
        """检查是否匹配快捷键"""
        current = "+".join(sorted(self._pressed_keys))

        for hotkey, callback in self._hotkeys.items():
            hotkey_parts = sorted(hotkey.split("+"))
            hotkey_str = "+".join(hotkey_parts)

            if current == hotkey_str:
                logger.info(f"触发快捷键: {hotkey}")
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(hotkey))
                else:
                    callback(hotkey)

    @property
    def is_running(self) -> bool:
        return self._running


class MockHotkeyListener(HotkeyListener):
    """模拟快捷键监听器（用于测试）"""

    def __init__(self):
        super().__init__()
        self._hotkeys: dict[str, Callable] = {}

    def start(self) -> None:
        self._running = True
        logger.info("模拟快捷键监听已启动")

    def stop(self) -> None:
        self._running = False
        logger.info("模拟快捷键监听已停止")

    def simulate_press(self, hotkey: str) -> None:
        """模拟按键"""
        if hotkey in self._hotkeys:
            callback = self._hotkeys[hotkey]
            if asyncio.iscoroutinefunction(callback):
                asyncio.create_task(callback(hotkey))
            else:
                callback(hotkey)
