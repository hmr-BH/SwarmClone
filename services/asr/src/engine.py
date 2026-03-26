"""
ASR引擎基类和实现
"""

from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
from pydantic import BaseModel
from loguru import logger


class ASRResult(BaseModel):
    """ASR识别结果"""

    text: str
    confidence: float = 1.0
    is_final: bool = True
    language: Optional[str] = None
    duration: float = 0.0


class ASREngine(ABC):
    """ASR引擎基类"""

    @abstractmethod
    async def initialize(self) -> None:
        """初始化引擎"""
        pass

    @abstractmethod
    async def transcribe(self, audio: np.ndarray) -> ASRResult:
        """
        转录音频

        Args:
            audio: 音频数据 (numpy数组)

        Returns:
            识别结果
        """
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """关闭引擎"""
        pass


class MockASREngine(ASREngine):
    """模拟ASR引擎（用于测试）"""

    def __init__(self, config: dict = None):
        self.config = config or {}

    async def initialize(self) -> None:
        logger.info("Mock ASR引擎已初始化")

    async def transcribe(self, audio: np.ndarray) -> ASRResult:
        return ASRResult(
            text="[模拟识别结果]",
            confidence=0.95,
            is_final=True,
        )

    async def shutdown(self) -> None:
        logger.info("Mock ASR引擎已关闭")


class WhisperEngine(ASREngine):
    """Whisper ASR引擎"""

    def __init__(self, model: str = "base", language: str = "zh", device: Optional[str] = None):
        self.model_name = model
        self.language = language
        self.device = device
        self.model = None

    async def initialize(self) -> None:
        try:
            import whisper

            self.model = whisper.load_model(self.model_name, device=self.device)
            logger.info(f"Whisper模型已加载: {self.model_name}")
        except ImportError:
            logger.warning("未安装whisper，使用Mock引擎")
            raise

    async def transcribe(self, audio: np.ndarray) -> ASRResult:
        if self.model is None:
            raise RuntimeError("引擎未初始化")

        result = self.model.transcribe(
            audio,
            language=self.language,
            fp16=False,
        )

        text = result.get("text", "").strip()
        segments = result.get("segments", [])

        confidence = 1.0
        if segments:
            probs = [s.get("avg_logprob", 0) for s in segments if "avg_logprob" in s]
            if probs:
                confidence = np.exp(np.mean(probs))

        return ASRResult(
            text=text,
            confidence=min(confidence, 1.0),
            is_final=True,
            language=self.language,
        )

    async def shutdown(self) -> None:
        self.model = None
        logger.info("Whisper引擎已关闭")
