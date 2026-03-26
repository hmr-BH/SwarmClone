"""
SwarmClone 核心引擎主程序
"""

import asyncio
import signal
import sys
from pathlib import Path
from typing import Optional

from core.engine.action_mapper import ActionMapper
from core.engine.event_handler import EventDispatcher
from core.engine.message_router import MessageRouter
from core.engine.state_manager import StateManager
from core.models.state import ServiceStatus
from core.utils.config_loader import ConfigLoader
from core.utils.logger import setup_logger
from loguru import logger


class CoreEngine:
    """核心引擎"""

    def __init__(self, config_path: str | Path = "config"):
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.load()

        setup_logger(
            log_level=self.config.system.log_level,
            log_dir="logs",
        )

        self.action_mapper = ActionMapper()
        self.state_manager = StateManager()
        self.dispatcher = EventDispatcher(self.action_mapper)
        self.message_router = MessageRouter(
            redis_host=self.config.redis.host,
            redis_port=self.config.redis.port,
            redis_db=self.config.redis.db,
        )

        self._running = False
        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        """启动核心引擎"""
        logger.info("正在启动核心引擎...")

        self.state_manager.start()

        self._load_action_mappings()

        await self.message_router.connect()
        self.message_router.set_dispatcher(self.dispatcher)

        channels = []
        if self.config.asr.enabled:
            channels.append(MessageRouter.CHANNEL_ASR_RESULT)
        if self.config.vision.enabled:
            channels.append(MessageRouter.CHANNEL_VISION_UPDATE)
        if self.config.keyboard.enabled:
            channels.append(MessageRouter.CHANNEL_KEYBOARD_EVENT)

        if channels:
            await self.message_router.subscribe(channels)

        self.state_manager.update_service_status("core", ServiceStatus.RUNNING)

        self._running = True
        logger.info("核心引擎启动完成")

        try:
            await self.message_router.start_listening()
        except asyncio.CancelledError:
            logger.info("消息监听被取消")

    async def stop(self) -> None:
        """停止核心引擎"""
        logger.info("正在停止核心引擎...")

        self._running = False

        await self.message_router.stop_listening()
        await self.message_router.disconnect()

        self.state_manager.update_service_status("core", ServiceStatus.STOPPED)
        self.state_manager.stop()

        logger.info("核心引擎已停止")

    def _load_action_mappings(self) -> None:
        """加载动作映射配置"""
        mapping_file = Path("config/action_mapping.yaml")
        if mapping_file.exists():
            import yaml

            with open(mapping_file, encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
                mappings = config.get("mappings", [])
                self.action_mapper.load_mappings(mappings)
                logger.info(f"已加载 {len(mappings)} 个动作映射")
        else:
            logger.warning(f"动作映射配置文件不存在: {mapping_file}")

    async def wait_for_shutdown(self) -> None:
        """等待关闭信号"""
        await self._shutdown_event.wait()

    def request_shutdown(self) -> None:
        """请求关闭"""
        self._shutdown_event.set()


async def main() -> None:
    """主函数"""
    engine = CoreEngine()

    def signal_handler(signum, frame):
        logger.info(f"收到信号 {signum}，正在关闭...")
        engine.request_shutdown()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        start_task = asyncio.create_task(engine.start())
        wait_task = asyncio.create_task(engine.wait_for_shutdown())

        done, pending = await asyncio.wait(
            [start_task, wait_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    except Exception as e:
        logger.error(f"核心引擎运行错误: {e}")
        sys.exit(1)

    finally:
        await engine.stop()


if __name__ == "__main__":
    asyncio.run(main())
