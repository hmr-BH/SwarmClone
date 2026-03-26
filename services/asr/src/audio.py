"""
音频捕获模块
"""

import asyncio
from typing import Callable, Optional

import numpy as np
from loguru import logger

try:
    import pyaudio

    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False


class AudioCapture:
    """音频捕获器"""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        device_index: Optional[int] = None,
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.device_index = device_index

        self.audio: Optional[pyaudio.PyAudio] = None
        self.stream: Optional[pyaudio.Stream] = None
        self._running = False
        self._callback: Optional[Callable] = None

    def list_devices(self) -> list[dict]:
        """列出可用音频设备"""
        if not PYAUDIO_AVAILABLE:
            logger.warning("pyaudio未安装，无法列出设备")
            return []

        audio = pyaudio.PyAudio()
        devices = []

        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if info["maxInputChannels"] > 0:
                devices.append(
                    {
                        "index": i,
                        "name": info["name"],
                        "channels": info["maxInputChannels"],
                        "sample_rate": int(info["defaultSampleRate"]),
                    }
                )

        audio.terminate()
        return devices

    def start(self, callback: Callable[[np.ndarray], None]) -> None:
        """开始捕获音频"""
        if not PYAUDIO_AVAILABLE:
            logger.warning("pyaudio未安装，使用模拟音频")
            self._running = True
            return

        self._callback = callback
        self.audio = pyaudio.PyAudio()

        self.stream = self.audio.open(
            format=pyaudio.paFloat32,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=self.chunk_size,
            stream_callback=self._on_audio,
        )

        self.stream.start_stream()
        self._running = True
        logger.info(f"音频捕获已启动: {self.sample_rate}Hz")

    def stop(self) -> None:
        """停止捕获音频"""
        self._running = False

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        if self.audio:
            self.audio.terminate()
            self.audio = None

        logger.info("音频捕获已停止")

    def _on_audio(self, in_data, frame_count, time_info, status):
        """音频回调"""
        if self._callback and self._running:
            audio_data = np.frombuffer(in_data, dtype=np.float32)
            self._callback(audio_data)
        return (None, pyaudio.paContinue)

    @property
    def is_running(self) -> bool:
        return self._running


class VAD:
    """语音活动检测"""

    def __init__(
        self,
        threshold: float = 0.5,
        silence_duration: float = 1.0,
        sample_rate: int = 16000,
    ):
        self.threshold = threshold
        self.silence_duration = silence_duration
        self.sample_rate = sample_rate

        self._silence_frames = 0
        self._is_speaking = False
        self._audio_buffer: list[np.ndarray] = []

    def process(self, audio: np.ndarray) -> tuple[bool, Optional[np.ndarray]]:
        """
        处理音频帧

        Args:
            audio: 音频帧

        Returns:
            (是否在说话, 完整的语音段)
        """
        rms = np.sqrt(np.mean(audio**2))
        is_voice = rms > self.threshold

        if is_voice:
            self._is_speaking = True
            self._silence_frames = 0
            self._audio_buffer.append(audio)
            return True, None
        else:
            if self._is_speaking:
                self._silence_frames += len(audio)
                self._audio_buffer.append(audio)

                silence_samples = self.silence_duration * self.sample_rate
                if self._silence_frames >= silence_samples:
                    complete_audio = np.concatenate(self._audio_buffer)
                    self._audio_buffer = []
                    self._silence_frames = 0
                    self._is_speaking = False
                    return False, complete_audio

                return True, None

        return False, None

    def reset(self) -> None:
        """重置状态"""
        self._silence_frames = 0
        self._is_speaking = False
        self._audio_buffer = []
