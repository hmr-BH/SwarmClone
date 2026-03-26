# SwarmClone ASR服务

语音识别服务模块，支持多种ASR引擎。

## 功能

- 支持Whisper本地识别
- 支持模拟引擎（测试用）
- 语音活动检测(VAD)
- Redis消息发布

## 安装

```bash
pip install -e .

# 安装Whisper支持
pip install -e ".[whisper]"
```

## 运行

```bash
python -m src.main
```

## 配置

在 `config/config.yaml` 中配置：

```yaml
services:
  asr:
    enabled: true
    engine: whisper
    model: base
    language: zh
```
