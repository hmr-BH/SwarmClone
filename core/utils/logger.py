"""
日志配置模块
"""

import sys
from loguru import logger


def setup_logger(level: str = "INFO") -> None:
    logger.remove()

    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
    )

    logger.add(
        "logs/swarmclone_{time:YYYY-MM-DD}.log",
        level=level,
        rotation="00:00",
        retention="7 days",
        encoding="utf-8",
    )
