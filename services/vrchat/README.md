# SwarmClone VRChat服务

VRChat OSC通信服务模块。

## 功能

- OSC协议通信
- 动作参数映射
- Redis消息订阅
- 自动重连

## 安装

```bash
pip install -e .
```

## 运行

```bash
python -m src.main
```

## 配置

在 `config/config.yaml` 中配置：

```yaml
services:
  vrchat:
    enabled: true
    osc_address: 127.0.0.1
    osc_port: 9000
```

在 `config/vrchat_params.yaml` 中配置参数映射：

```yaml
parameters:
  wave:
    - address: "/avatar/parameters/GestureLeft"
      value: 1
      type: int
```
