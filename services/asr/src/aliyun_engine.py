"""
阿里云ASR引擎实现

支持Fun-ASR、Paraformer、SenseVoice模型
"""

import asyncio
import json
import tempfile
import wave
from pathlib import Path
from typing import Optional

import numpy as np
from loguru import logger

try:
    import dashscope
    from dashscope.audio.asr import Transcription
    from http import HTTPStatus
    from urllib import request

    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False

from src.engine import ASREngine, ASRResult


class AliyunASREngine(ASREngine):
    """阿里云ASR引擎"""

    def __init__(
        self,
        api_key: str,
        model: str = "fun-asr",
        language_hints: list[str] = None,
        sample_rate: int = 16000,
    ):
        if not DASHSCOPE_AVAILABLE:
            raise ImportError("dashscope未安装，请运行: pip install dashscope")

        self.api_key = api_key
        self.model = model
        self.language_hints = language_hints or ["zh"]
        self.sample_rate = sample_rate

        dashscope.api_key = api_key
        dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"

    async def initialize(self) -> None:
        logger.info(f"阿里云ASR引擎已初始化: {self.model}")

    async def transcribe(self, audio: np.ndarray) -> ASRResult:
        audio_file = await self._save_temp_audio(audio)

        try:
            result = await self._transcribe_file(audio_file)
            return result
        finally:
            if audio_file.exists():
                audio_file.unlink()

    async def _save_temp_audio(self, audio: np.ndarray) -> Path:
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_path = Path(temp_file.name)

        with wave.open(str(temp_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            audio_int16 = (audio * 32767).astype(np.int16)
            wf.writeframes(audio_int16.tobytes())

        return temp_path

    async def _transcribe_file(self, audio_path: Path) -> ASRResult:
        import oss2

        auth = oss2.Auth(
            oss2.StsAuth(self.api_key, "", "") if False else oss2.Auth(self.api_key, "")
        )

        task_response = await asyncio.to_thread(
            Transcription.async_call,
            model=self.model,
            file_urls=[f"file://{audio_path.absolute()}"],
            language_hints=self.language_hints,
        )

        if task_response.status_code != HTTPStatus.OK:
            logger.error(f"ASR任务提交失败: {task_response.output.message}")
            return ASRResult(text="", confidence=0.0)

        task_id = task_response.output.task_id
        logger.debug(f"ASR任务已提交: {task_id}")

        transcription_response = await asyncio.to_thread(
            Transcription.wait,
            task=task_id,
        )

        if transcription_response.status_code != HTTPStatus.OK:
            logger.error(f"ASR任务失败: {transcription_response.output.message}")
            return ASRResult(text="", confidence=0.0)

        return self._parse_result(transcription_response)

    def _parse_result(self, response) -> ASRResult:
        for transcription in response.output.get("results", []):
            if transcription.get("subtask_status") == "SUCCEEDED":
                url = transcription.get("transcription_url")
                if url:
                    result_json = request.urlopen(url).read().decode("utf8")
                    result = json.loads(result_json)

                    transcripts = result.get("transcripts", [])
                    if transcripts:
                        text = transcripts[0].get("text", "")

                        sentences = transcripts[0].get("sentences", [])
                        confidence = 1.0
                        if sentences:
                            confidences = [s.get("confidence", 1.0) for s in sentences]
                            confidence = sum(confidences) / len(confidences) if confidences else 1.0

                        return ASRResult(
                            text=text,
                            confidence=confidence,
                            is_final=True,
                            language=self.language_hints[0] if self.language_hints else None,
                        )

        return ASRResult(text="", confidence=0.0)

    async def shutdown(self) -> None:
        logger.info("阿里云ASR引擎已关闭")


class AliyunASRStreamEngine(ASREngine):
    """阿里云流式ASR引擎（实时语音识别）"""

    def __init__(
        self,
        api_key: str,
        model: str = "paraformer-realtime-v2",
        language: str = "zh",
        sample_rate: int = 16000,
    ):
        if not DASHSCOPE_AVAILABLE:
            raise ImportError("dashscope未安装")

        self.api_key = api_key
        self.model = model
        self.language = language
        self.sample_rate = sample_rate

        dashscope.api_key = api_key

    async def initialize(self) -> None:
        logger.info(f"阿里云流式ASR引擎已初始化: {self.model}")

    async def transcribe(self, audio: np.ndarray) -> ASRResult:
        return ASRResult(
            text="[流式识别需要持续音频流]",
            confidence=0.9,
            is_final=True,
        )

    async def shutdown(self) -> None:
        logger.info("阿里云流式ASR引擎已关闭")


class AliyunASRFileEngine(ASREngine):
    """阿里云文件识别引擎（用于测试）"""

    def __init__(
        self,
        api_key: str,
        model: str = "fun-asr",
        language_hints: list[str] = None,
    ):
        if not DASHSCOPE_AVAILABLE:
            raise ImportError("dashscope未安装")

        self.api_key = api_key
        self.model = model
        self.language_hints = language_hints or ["zh"]

        dashscope.api_key = api_key
        dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"

    async def initialize(self) -> None:
        logger.info(f"阿里云文件ASR引擎已初始化: {self.model}")

    async def transcribe(self, audio: np.ndarray) -> ASRResult:
        return ASRResult(
            text="[请使用transcribe_file方法识别文件]",
            confidence=1.0,
            is_final=True,
        )

    async def transcribe_file(self, file_url: str) -> ASRResult:
        """
        识别音频文件

        Args:
            file_url: 音频文件URL

        Returns:
            ASRResult
        """
        task_response = await asyncio.to_thread(
            Transcription.async_call,
            model=self.model,
            file_urls=[file_url],
            language_hints=self.language_hints,
        )

        if task_response.status_code != HTTPStatus.OK:
            logger.error(f"任务提交失败: {task_response.output.message}")
            return ASRResult(text="", confidence=0.0)

        task_id = task_response.output.task_id
        logger.info(f"任务已提交: {task_id}")

        transcription_response = await asyncio.to_thread(
            Transcription.wait,
            task=task_id,
        )

        if transcription_response.status_code != HTTPStatus.OK:
            logger.error(f"任务失败: {transcription_response.output.message}")
            return ASRResult(text="", confidence=0.0)

        for transcription in transcription_response.output.get("results", []):
            if transcription.get("subtask_status") == "SUCCEEDED":
                url = transcription.get("transcription_url")
                if url:
                    result_json = request.urlopen(url).read().decode("utf8")
                    result = json.loads(result_json)

                    transcripts = result.get("transcripts", [])
                    if transcripts:
                        text = transcripts[0].get("text", "")
                        logger.info(f"识别结果: {text}")

                        return ASRResult(
                            text=text,
                            confidence=1.0,
                            is_final=True,
                        )

        return ASRResult(text="", confidence=0.0)

    async def shutdown(self) -> None:
        logger.info("阿里云文件ASR引擎已关闭")
