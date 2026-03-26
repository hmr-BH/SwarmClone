"""
ASR 客户端入口
"""

import asyncio

from loguru import logger

from services.asr_client.client import ASRClient
from services.asr_client.config import ASRSettings


async def main() -> None:
    logger.info("启动 ASR 客户端服务...")

    settings = ASRSettings()
    client = ASRClient(settings)

    try:
        await client.connect()
        logger.info("ASR 客户端已启动，按 Ctrl+C 停止")
        await client.listen_loop()
    except KeyboardInterrupt:
        logger.info("正在停止 ASR 客户端...")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
