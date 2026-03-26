# SwarmClone 键盘服务

快捷键监听服务模块。

## 功能

- 全局快捷键监听
- 自定义快捷键映射
- Redis消息发布

## 安装

```bash
pip install -e .
pip install pynput  # 可选，用于全局快捷键监听
```

## 运行

```bash
python -m src.main
```

## 配置

在 `config/hotkeys.yaml` 中配置：

```yaml
hotkeys:
  "ctrl+shift+h": "happy"
  "ctrl+shift+s": "sad"
```
