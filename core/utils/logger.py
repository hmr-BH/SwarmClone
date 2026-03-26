"""
日志配置模块
"""

import sys
from pathlib import Path

from loguru import logger


def setup_logger(
    log_level: str = "INFO",
    log_dir: str | Path = "logs",
    rotation: str = "10 MB",
    retention: str = "7 days",
) -> None:
    """
    配置日志系统

    Args:
        log_level: 日志级别
        log_dir: 日志目录
        rotation: 日志轮转大小
        retention: 日志保留时间
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    logger.remove()

    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
    )

    logger.add(
        log_path / "swarmclone_{time:YYYY-MM-DD}.log",
        level=log_level,
        rotation=rotation,
        retention=retention,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        encoding="utf-8",
    )

    logger.info(f"日志系统已初始化，级别: {log_level}")
