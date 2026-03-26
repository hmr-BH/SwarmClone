"""
VRChat服务主程序
"""

import asyncio
import json
import signal
import sys
from pathlib import Path
from typing import Optional

import redis.asyncio as redis
from loguru import logger

from src.config import VRChatConfig, RedisConfig
from src.osc_client import OSCClient
from src.executor import ActionExecutor


class VRChatService:
    """VRChat服务"""

    def __init__(
        self,
        vrchat_config: VRChatConfig,
        redis_config: RedisConfig,
    ):
        self.vrchat_config = vrchat_config
        self.redis_config = redis_config

        self.osc_client: Optional[OSCClient] = None
        self.executor: Optional[ActionExecutor] = None
        self.redis: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None

        self._running = False
        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        """启动服务"""
        logger.info("启动VRChat服务...")

        await self._init_redis()
        self._init_osc()
        self._init_executor()

        self._running = True
        logger.info("VRChat服务已启动")

    async def stop(self) -> None:
        """停止服务"""
        logger.info("停止VRChat服务...")

        self._running = False

        if self.pubsub:
            await self.pubsub.close()

        if self.redis:
            await self.redis.close()

        if self.osc_client:
            self.osc_client.disconnect()

        logger.info("VRChat服务已停止")

    async def _init_redis(self) -> None:
        """初始化Redis连接"""
        self.redis = redis.Redis(
            host=self.redis_config.host,
            port=self.redis_config.port,
            db=self.redis_config.db,
            decode_responses=True,
        )
        await self.redis.ping()

        self.pubsub = self.redis.pubsub()
        await self.pubsub.subscribe(self.redis_config.channel)

        logger.info(f"已连接到Redis: {self.redis_config.host}:{self.redis_config.port}")

    def _init_osc(self) -> None:
        """初始化OSC客户端"""
        self.osc_client = OSCClient(
            address=self.vrchat_config.osc_address,
            port=self.vrchat_config.osc_port,
        )

        if self.osc_client.connect():
            logger.info(
                f"OSC已连接: {self.vrchat_config.osc_address}:{self.vrchat_config.osc_port}"
            )
        else:
            logger.warning("OSC连接失败，将在后台重试")

    def _init_executor(self) -> None:
        """初始化动作执行器"""
        self.executor = ActionExecutor(self.osc_client)
        self.executor.load_mappings()

    async def run(self) -> None:
        """运行服务"""
        logger.info("开始监听动作指令...")

        try:
            async for message in self.pubsub.listen():
                if not self._running:
                    break

                if message["type"] == "message":
                    await self._handle_message(message)

        except asyncio.CancelledError:
            logger.info("消息监听被取消")
        except Exception as e:
            logger.error(f"消息监听错误: {e}")

    async def _handle_message(self, message: dict) -> None:
        """处理消息"""
        data = message.get("data", "")

        try:
            if isinstance(data, str):
                msg = json.loads(data)
            else:
                msg = data

            action_name = msg.get("data", {}).get("name")
            if not action_name:
                action_name = msg.get("name")

            if action_name:
                logger.info(f"收到动作指令: {action_name}")
                await self.executor.execute(action_name)

        except json.JSONDecodeError:
            logger.warning(f"无效的消息格式: {data}")
        except Exception as e:
            logger.error(f"处理消息错误: {e}")

    async def wait_for_shutdown(self) -> None:
        """等待关闭信号"""
        await self._shutdown_event.wait()

    def request_shutdown(self) -> None:
        """请求关闭"""
        self._shutdown_event.set()


def load_config(config_path: str = "config/config.yaml") -> tuple[VRChatConfig, RedisConfig]:
    """加载配置"""
    import yaml

    path = Path(config_path)
    if path.exists():
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        services = data.get("services", {}).get("vrchat", {})
        messaging = data.get("messaging", {}).get("redis", {})

        vrchat_config = VRChatConfig(**services)
        redis_config = RedisConfig(**messaging)
    else:
        vrchat_config = VRChatConfig()
        redis_config = RedisConfig()

    return vrchat_config, redis_config


async def main() -> None:
    """主函数"""
    logger.remove()
    logger.add(sys.stdout, level="INFO")

    vrchat_config, redis_config = load_config()

    if not vrchat_config.enabled:
        logger.info("VRChat服务已禁用")
        return

    service = VRChatService(vrchat_config, redis_config)

    def signal_handler(signum, frame):
        logger.info(f"收到信号 {signum}，正在关闭...")
        service.request_shutdown()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await service.start()

        run_task = asyncio.create_task(service.run())
        wait_task = asyncio.create_task(service.wait_for_shutdown())

        done, pending = await asyncio.wait(
            [run_task, wait_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    except Exception as e:
        logger.error(f"VRChat服务错误: {e}")
        sys.exit(1)
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
