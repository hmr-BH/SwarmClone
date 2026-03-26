"""
服务基类模块
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Optional

from core.models.state import ServiceStatus
from loguru import logger


class BaseService(ABC):
    """服务基类"""

    def __init__(self, name: str, config: Optional[dict] = None):
        self.name = name
        self.config = config or {}
        self._status = ServiceStatus.STOPPED
        self._task: Optional[asyncio.Task] = None

    @property
    def status(self) -> ServiceStatus:
        """获取服务状态"""
        return self._status

    @abstractmethod
    async def start(self) -> None:
        """启动服务"""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """停止服务"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass

    def _set_status(self, status: ServiceStatus) -> None:
        """设置服务状态"""
        self._status = status
        logger.debug(f"服务 {self.name} 状态变更: {status}")

    async def _run_with_error_handling(self) -> None:
        """带错误处理的运行"""
        try:
            self._set_status(ServiceStatus.STARTING)
            await self.start()
            self._set_status(ServiceStatus.RUNNING)
        except Exception as e:
            self._set_status(ServiceStatus.ERROR)
            logger.error(f"服务 {self.name} 启动失败: {e}")

    async def start_safe(self) -> bool:
        """安全启动服务"""
        try:
            await self._run_with_error_handling()
            return self._status == ServiceStatus.RUNNING
        except Exception as e:
            logger.error(f"服务 {self.name} 启动异常: {e}")
            return False

    async def stop_safe(self) -> bool:
        """安全停止服务"""
        try:
            self._set_status(ServiceStatus.STOPPING)
            await self.stop()
            self._set_status(ServiceStatus.STOPPED)
            return True
        except Exception as e:
            self._set_status(ServiceStatus.ERROR)
            logger.error(f"服务 {self.name} 停止失败: {e}")
            return False
