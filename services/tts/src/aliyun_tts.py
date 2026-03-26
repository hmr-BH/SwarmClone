"""
阿里云TTS引擎实现

支持千问TTS实时语音合成
"""

import asyncio
import base64
import tempfile
import threading
import wave
from pathlib import Path
from typing import Optional

import numpy as np
from loguru import logger

try:
    import dashscope
    from dashscope.audio.qwen_tts_realtime import (
        QwenTtsRealtime,
        QwenTtsRealtimeCallback,
        AudioFormat,
    )

    DASHSCOPE_TTS_AVAILABLE = True
except ImportError:
    DASHSCOPE_TTS_AVAILABLE = False


class TTSCallback(QwenTtsRealtimeCallback):
    """TTS回调处理器"""

    def __init__(self):
        self.complete_event = threading.Event()
        self.audio_data: list[bytes] = []
        self.session_id: Optional[str] = None
        self.first_audio_delay: float = 0.0

    def on_open(self) -> None:
        logger.debug("TTS连接已打开")

    def on_close(self, close_status_code, close_msg) -> None:
        logger.debug(f"TTS连接已关闭: {close_status_code}, {close_msg}")
        self.complete_event.set()

    def on_event(self, response: dict) -> None:
        try:
            event_type = response.get("type", "")

            if event_type == "session.created":
                self.session_id = response["session"]["id"]
                logger.debug(f"TTS会话已创建: {self.session_id}")

            elif event_type == "response.audio.delta":
                audio_b64 = response.get("delta", "")
                if audio_b64:
                    audio_bytes = base64.b64decode(audio_b64)
                    self.audio_data.append(audio_bytes)

            elif event_type == "session.finished":
                logger.debug("TTS会话已结束")
                self.complete_event.set()

        except Exception as e:
            logger.error(f"TTS事件处理错误: {e}")

    def wait_for_finished(self, timeout: float = 30.0) -> bool:
        return self.complete_event.wait(timeout=timeout)

    def get_audio(self) -> bytes:
        return b"".join(self.audio_data)

    def reset(self) -> None:
        self.complete_event.clear()
        self.audio_data = []
        self.session_id = None


class AliyunTTSEngine:
    """阿里云TTS引擎"""

    VOICES = {
        "Cherry": "芊悦 - 阳光积极小姐姐",
        "Serena": "苏瑶 - 温柔小姐姐",
        "Ethan": "晨煦 - 阳光温暖男声",
        "Chelsie": "千雪 - 二次元虚拟女友",
        "Momo": "茉兔 - 撒娇搞怪",
        "Vivian": "十三 - 拽拽可爱",
        "Moon": "月白 - 率性帅气",
        "Maia": "四月 - 知性温柔",
        "Kai": "凯 - 耳朵SPA",
    }

    def __init__(
        self,
        api_key: str,
        model: str = "qwen3-tts-flash-realtime",
        voice: str = "Cherry",
        sample_rate: int = 24000,
        format: str = "pcm",
    ):
        if not DASHSCOPE_TTS_AVAILABLE:
            raise ImportError("dashscope TTS模块未安装")

        self.api_key = api_key
        self.model = model
        self.voice = voice
        self.sample_rate = sample_rate
        self.format = format

        dashscope.api_key = api_key

        self._tts: Optional[QwenTtsRealtime] = None
        self._callback: Optional[TTSCallback] = None

    async def initialize(self) -> None:
        logger.info(f"阿里云TTS引擎已初始化: {self.model}, 音色: {self.voice}")

    async def synthesize(self, text: str) -> bytes:
        """
        合成语音

        Args:
            text: 要合成的文本

        Returns:
            音频数据（PCM格式）
        """
        self._callback = TTSCallback()

        self._tts = QwenTtsRealtime(
            model=self.model,
            callback=self._callback,
            url="wss://dashscope.aliyuncs.com/api-ws/v1/realtime",
        )

        self._tts.connect()

        audio_format = AudioFormat.PCM_24000HZ_MONO_16BIT
        if self.sample_rate == 16000:
            audio_format = AudioFormat.PCM_16000HZ_MONO_16BIT
        elif self.sample_rate == 48000:
            audio_format = AudioFormat.PCM_48000HZ_MONO_16BIT

        self._tts.update_session(
            voice=self.voice, response_format=audio_format, mode="server_commit"
        )

        self._tts.append_text(text)
        self._tts.finish()

        self._callback.wait_for_finished(timeout=60.0)

        audio_data = self._callback.get_audio()

        logger.info(f"TTS合成完成: {len(text)}字符 -> {len(audio_data)}字节音频")

        return audio_data

    async def synthesize_to_file(self, text: str, output_path: str) -> Path:
        """
        合成语音并保存为文件

        Args:
            text: 要合成的文本
            output_path: 输出文件路径

        Returns:
            输出文件路径
        """
        audio_data = await self.synthesize(text)

        output = Path(output_path)

        if output.suffix.lower() == ".wav":
            with wave.open(str(output), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data)
        else:
            with open(output, "wb") as f:
                f.write(audio_data)

        logger.info(f"音频已保存: {output}")
        return output

    async def shutdown(self) -> None:
        logger.info("阿里云TTS引擎已关闭")

    @classmethod
    def list_voices(cls) -> dict[str, str]:
        """列出可用音色"""
        return cls.VOICES.copy()

    def set_voice(self, voice: str) -> None:
        """设置音色"""
        if voice not in self.VOICES:
            logger.warning(f"未知音色: {voice}，使用默认音色")
        self.voice = voice
        logger.info(f"音色已切换: {voice}")
