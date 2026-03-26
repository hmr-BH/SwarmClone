"""
状态管理器
"""

import threading
import time
from typing import Any, Callable, Optional

from core.models.state import SystemState, ServiceStatus, ModelState, VRChatState
from loguru import logger


class StateManager:
    """状态管理器"""

    def __init__(self):
        self._state = SystemState()
        self._lock = threading.RLock()
        self._subscribers: dict[str, list[Callable]] = {}
        self._start_time: Optional[float] = None

    def start(self) -> None:
        """启动状态管理器"""
        with self._lock:
            self._start_time = time.time()
            logger.info("状态管理器已启动")

    def stop(self) -> None:
        """停止状态管理器"""
        with self._lock:
            self._start_time = None
            logger.info("状态管理器已停止")

    def get_state(self) -> SystemState:
        """获取系统状态"""
        with self._lock:
            state = self._state.model_copy()
            if self._start_time:
                state.uptime = time.time() - self._start_time
            return state

    def get(self, key: str) -> Any:
        """
        获取状态值

        Args:
            key: 状态键，支持点分隔的嵌套路径

        Returns:
            状态值
        """
        with self._lock:
            parts = key.split(".")
            value = self._state

            for part in parts:
                if hasattr(value, part):
                    value = getattr(value, part)
                elif isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None

            return value

    def set(self, key: str, value: Any) -> None:
        """
        设置状态值

        Args:
            key: 状态键
            value: 状态值
        """
        with self._lock:
            parts = key.split(".")
            target = self._state

            for part in parts[:-1]:
                if hasattr(target, part):
                    target = getattr(target, part)
                else:
                    return

            final_key = parts[-1]
            if hasattr(target, final_key):
                setattr(target, final_key, value)
                self._notify_subscribers(key, value)
                logger.debug(f"状态更新: {key} = {value}")

    def update_service_status(
        self,
        service_name: str,
        status: ServiceStatus,
        pid: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """更新服务状态"""
        from core.models.state import ServiceInfo

        with self._lock:
            service_info = self._state.services.get(service_name, ServiceInfo(name=service_name))
            service_info.status = status
            service_info.pid = pid
            service_info.error_message = error_message
            self._state.services[service_name] = service_info
            self._notify_subscribers(f"services.{service_name}", service_info)
            logger.debug(f"服务状态更新: {service_name} -> {status}")

    def update_model_state(self, model_state: ModelState) -> None:
        """更新模型状态"""
        with self._lock:
            self._state.model_state = model_state
            self._notify_subscribers("model_state", model_state)

    def update_vrchat_state(self, vrchat_state: VRChatState) -> None:
        """更新VRChat状态"""
        with self._lock:
            self._state.vrchat_state = vrchat_state
            self._notify_subscribers("vrchat_state", vrchat_state)

    def subscribe(self, key: str, callback: Callable[[Any], None]) -> None:
        """
        订阅状态变更

        Args:
            key: 状态键
            callback: 回调函数
        """
        if key not in self._subscribers:
            self._subscribers[key] = []
        self._subscribers[key].append(callback)

    def unsubscribe(self, key: str, callback: Callable) -> None:
        """取消订阅"""
        if key in self._subscribers:
            self._subscribers[key] = [cb for cb in self._subscribers[key] if cb != callback]

    def _notify_subscribers(self, key: str, value: Any) -> None:
        """通知订阅者"""
        if key in self._subscribers:
            for callback in self._subscribers[key]:
                try:
                    callback(value)
                except Exception as e:
                    logger.error(f"订阅回调执行失败: {e}")
