# SwarmClone

多语言混合开发的虚拟形象控制系统，为VRChat等虚拟社交平台提供智能化的虚拟形象驱动能力。

## 项目结构

```
project/
├── cli/              # Rust CLI工具
├── core/             # Python核心业务逻辑
├── frontend/         # Godot 3D前端
├── panel/            # Vue.js Web控制面板
├── scripts/          # 快捷脚本
├── services/         # 独立服务模块
│   ├── asr/          # ASR客户端
│   ├── vision/       # 视觉捕获
│   ├── vrchat/       # VRChat对接
│   └── keyboard/     # 键盘操作
├── config/           # 配置文件
├── logs/             # 日志文件
├── data/             # 数据存储
└── models/           # 模型资源
```

## 技术栈

| 组件 | 技术栈 |
|------|--------|
| CLI工具 | Rust |
| 核心引擎 | Python 3.9+ |
| 3D前端 | Godot 4.0 |
| VRChat对接 | C# |
| Web控制面板 | Vue.js 3 |
| 消息总线 | Redis |

## 快速开始

```bash
# 安装依赖
pip install -e ./core

# 启动服务
python -m core.main
```

## 开发

详见 [.spec/](./.spec/) 目录下的设计文档。

## 许可证

MIT License
