"""
ASR服务配置
"""

from typing import Optional

from pydantic import BaseModel


class ASRConfig(BaseModel):
    """ASR服务配置"""

    enabled: bool = True
    engine: str = "whisper"
    model: str = "base"
    language: str = "zh"
    device: Optional[str] = None
    sample_rate: int = 16000
    chunk_size: int = 1024
    vad_enabled: bool = True
    vad_threshold: float = 0.5
    silence_duration: float = 1.0


class RedisConfig(BaseModel):
    """Redis配置"""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    channel: str = "asr:result"
