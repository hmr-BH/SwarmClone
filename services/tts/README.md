# SwarmClone TTS服务

阿里云千问TTS语音合成服务模块。

## 功能

- 阿里云千问TTS实时语音合成
- 多种音色选择
- 流式输入输出
- Redis消息集成

## 安装

```bash
pip install -e .
```

## 运行

```bash
python -m src.main
```

## 可用音色

| 音色ID | 描述 |
|--------|------|
| Cherry | 芊悦 - 阳光积极小姐姐 |
| Serena | 苏瑶 - 温柔小姐姐 |
| Ethan | 晨煦 - 阳光温暖男声 |
| Chelsie | 千雪 - 二次元虚拟女友 |

## 配置

在 `config/config.yaml` 中配置：

```yaml
services:
  tts:
    enabled: true
    engine: aliyun
    model: qwen3-tts-flash-realtime
    voice: Cherry
    api_key: your-api-key
```
