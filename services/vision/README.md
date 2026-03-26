# SwarmClone 视觉服务

面部追踪和表情检测服务模块。

## 功能

- 摄像头捕获
- MediaPipe面部追踪
- 眼睛开合检测
- 嘴巴开合检测
- Redis消息发布

## 安装

```bash
pip install -e .
pip install -e ".[opencv,mediapipe]"
```

## 运行

```bash
python -m src.main
```

## 配置

在 `config/config.yaml` 中配置：

```yaml
services:
  vision:
    enabled: true
    device: 0
    fps: 30
```
