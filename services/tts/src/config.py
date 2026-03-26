"""
TTS服务配置
"""

from typing import Optional

from pydantic import BaseModel


class TTSConfig(BaseModel):
    """TTS服务配置"""

    enabled: bool = True
    engine: str = "aliyun"
    model: str = "qwen3-tts-flash-realtime"
    voice: str = "Cherry"
    sample_rate: int = 24000
    format: str = "pcm"
    api_key: Optional[str] = None


class RedisConfig(BaseModel):
    """Redis配置"""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    input_channel: str = "tts:request"
    output_channel: str = "tts:audio"
