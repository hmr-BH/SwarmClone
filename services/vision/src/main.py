"""
视觉服务主程序
"""

import asyncio
import json
import signal
import sys
import time
from pathlib import Path
from typing import Optional

import redis.asyncio as redis
from loguru import logger

from src.config import VisionConfig, RedisConfig
from src.tracker import FaceTracker, CameraCapture, CV2_AVAILABLE


class VisionService:
    """视觉服务"""

    def __init__(
        self,
        vision_config: VisionConfig,
        redis_config: RedisConfig,
    ):
        self.vision_config = vision_config
        self.redis_config = redis_config

        self.camera: Optional[CameraCapture] = None
        self.tracker: Optional[FaceTracker] = None
        self.redis: Optional[redis.Redis] = None

        self._running = False
        self._shutdown_event = asyncio.Event()
        self._last_publish = 0.0
        self._publish_interval = 1.0 / 30  # 30fps

    async def start(self) -> None:
        """启动服务"""
        logger.info("启动视觉服务...")

        if not CV2_AVAILABLE:
            logger.warning("opencv未安装，视觉服务将无法捕获图像")

        await self._init_redis()
        self._init_camera()
        self._init_tracker()

        self._running = True
        logger.info("视觉服务已启动")

    async def stop(self) -> None:
        """停止服务"""
        logger.info("停止视觉服务...")

        self._running = False

        if self.camera:
            self.camera.stop()

        if self.tracker:
            self.tracker.close()

        if self.redis:
            await self.redis.close()

        logger.info("视觉服务已停止")

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

    def _init_camera(self) -> None:
        """初始化摄像头"""
        self.camera = CameraCapture(
            device=self.vision_config.device,
            width=self.vision_config.width,
            height=self.vision_config.height,
            fps=self.vision_config.fps,
        )

        if not self.camera.start():
            logger.warning("摄像头启动失败")

    def _init_tracker(self) -> None:
        """初始化面部追踪器"""
        self.tracker = FaceTracker()

        if not self.tracker.is_available:
            logger.warning("面部追踪器不可用")

    async def run(self) -> None:
        """运行服务"""
        if not self.camera or not self.camera.is_running:
            logger.warning("摄像头未启动，等待...")
            while self._running and not (self.camera and self.camera.is_running):
                await asyncio.sleep(1.0)

        logger.info("开始捕获和处理...")

        while self._running:
            frame = self.camera.read()

            if frame is not None and self.tracker:
                face_data = self.tracker.process(frame)

                if face_data:
                    await self._maybe_publish(face_data)

            await asyncio.sleep(1.0 / self.vision_config.fps)

    async def _maybe_publish(self, face_data: dict) -> None:
        """根据时间间隔发布数据"""
        now = time.time()
        if now - self._last_publish < self._publish_interval:
            return

        self._last_publish = now

        message = {
            "type": "vision_update",
            "timestamp": face_data["timestamp"],
            "data": {
                "eye_left": face_data["eye_left"],
                "eye_right": face_data["eye_right"],
                "mouth": face_data["mouth"],
            },
        }

        await self.redis.publish(self.redis_config.channel, json.dumps(message, ensure_ascii=False))

    async def wait_for_shutdown(self) -> None:
        """等待关闭信号"""
        await self._shutdown_event.wait()

    def request_shutdown(self) -> None:
        """请求关闭"""
        self._shutdown_event.set()


def load_config(config_path: str = "config/config.yaml") -> tuple[VisionConfig, RedisConfig]:
    """加载配置"""
    import yaml

    path = Path(config_path)
    if path.exists():
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        services = data.get("services", {}).get("vision", {})
        messaging = data.get("messaging", {}).get("redis", {})

        vision_config = VisionConfig(**services)
        redis_config = RedisConfig(**messaging)
    else:
        vision_config = VisionConfig()
        redis_config = RedisConfig()

    return vision_config, redis_config


async def main() -> None:
    """主函数"""
    logger.remove()
    logger.add(sys.stdout, level="INFO")

    vision_config, redis_config = load_config()

    if not vision_config.enabled:
        logger.info("视觉服务已禁用")
        return

    service = VisionService(vision_config, redis_config)

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
        logger.error(f"视觉服务错误: {e}")
        sys.exit(1)
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
