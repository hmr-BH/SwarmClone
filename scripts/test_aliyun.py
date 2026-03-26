#!/usr/bin/env python3
"""
阿里云ASR/TTS测试脚本

测试阿里云语音识别和语音合成功能
"""

import asyncio
import os
import sys
import tempfile
import wave
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "services" / "asr" / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "services" / "tts" / "src"))

API_KEY = "sk-85dc18b3af764f298c287eaa726a5fd2"


def test_tts():
    """测试TTS语音合成"""
    print("\n" + "=" * 50)
    print("测试阿里云TTS语音合成")
    print("=" * 50)

    try:
        from aliyun_tts import AliyunTTSEngine

        print("\n可用音色:")
        voices = AliyunTTSEngine.list_voices()
        for voice_id, desc in voices.items():
            print(f"  - {voice_id}: {desc}")

        print("\n初始化TTS引擎...")
        engine = AliyunTTSEngine(
            api_key=API_KEY,
            model="qwen3-tts-flash-realtime",
            voice="Cherry",
            sample_rate=24000,
        )

        print("合成测试文本...")
        text = "你好，我是SwarmClone虚拟形象助手。"

        audio_data = asyncio.run(engine.synthesize(text))

        output_file = Path("test_output_tts.wav")
        with wave.open(str(output_file), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(audio_data)

        print(f"\n[成功] 音频已保存: {output_file}")
        print(f"  文本: {text}")
        print(f"  音频大小: {len(audio_data)} 字节")

        return True

    except Exception as e:
        print(f"\n[失败] TTS测试错误: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_asr():
    """测试ASR语音识别"""
    print("\n" + "=" * 50)
    print("测试阿里云ASR语音识别")
    print("=" * 50)

    try:
        from aliyun_engine import AliyunASRFileEngine

        print("\n初始化ASR引擎...")
        engine = AliyunASRFileEngine(
            api_key=API_KEY,
            model="fun-asr",
            language_hints=["zh"],
        )
        asyncio.run(engine.initialize())

        test_url = "https://dashscope.oss-cn-beijing.aliyuncs.com/samples/audio/paraformer/hello_world_female2.wav"
        print(f"\n识别测试音频: {test_url}")

        result = asyncio.run(engine.transcribe_file(test_url))

        print(f"\n[成功] 识别结果:")
        print(f"  文本: {result.text}")
        print(f"  置信度: {result.confidence:.2f}")

        return True

    except Exception as e:
        print(f"\n[失败] ASR测试错误: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_tts_different_voices():
    """测试不同音色"""
    print("\n" + "=" * 50)
    print("测试不同TTS音色")
    print("=" * 50)

    try:
        from aliyun_tts import AliyunTTSEngine

        voices_to_test = ["Cherry", "Ethan", "Serena"]
        text = "欢迎使用SwarmClone虚拟形象系统。"

        for voice in voices_to_test:
            print(f"\n测试音色: {voice}")

            engine = AliyunTTSEngine(
                api_key=API_KEY,
                model="qwen3-tts-flash-realtime",
                voice=voice,
                sample_rate=24000,
            )

            audio_data = asyncio.run(engine.synthesize(text))

            output_file = Path(f"test_output_{voice}.wav")
            with wave.open(str(output_file), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(audio_data)

            print(f"  已保存: {output_file} ({len(audio_data)} 字节)")

        print("\n[成功] 所有音色测试完成")
        return True

    except Exception as e:
        print(f"\n[失败] 音色测试错误: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    print("=" * 50)
    print("阿里云ASR/TTS功能测试")
    print("=" * 50)
    print(f"API Key: {API_KEY[:10]}...")

    results = []

    results.append(("TTS语音合成", test_tts()))
    results.append(("ASR语音识别", test_asr()))
    results.append(("TTS多音色", test_tts_different_voices()))

    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)

    for name, success in results:
        status = "[OK]" if success else "[FAIL]"
        print(f"  {status} {name}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("=" * 50))
    if all_passed:
        print("[OK] 所有测试通过!")
    else:
        print("[FAIL] 部分测试失败")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
