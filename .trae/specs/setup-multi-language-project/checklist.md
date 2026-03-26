# Checklist

## Phase 1: 基础架构搭建

- [ ] 项目配置文件已创建并配置正确
- [ ] CLI 模块 (Rust) 可以编译并执行基础命令
- [ ] Core 模块 (Python) 可以启动并监听 WebSocket
- [ ] Frontend 模块 (Godot) 可以启动并显示基础场景
- [ ] Panel 模块 (Vue.js) 可以启动并显示基础界面

## Phase 2: Services 服务模块

- [ ] ASR 客户端可以捕获语音并转换为文本
- [ ] 视觉捕获服务可以捕获摄像头画面并识别面部
- [ ] VRChat 对接服务可以与 VRChat 进行 OSC 通信
- [ ] 键盘操作服务可以监听全局热键

## Phase 3: 集成与测试

- [ ] 所有模块可以通过 WebSocket 与核心通信
- [ ] CLI 可以启动、停止、查看所有服务状态
- [ ] Panel 可以显示所有服务状态和日志
- [ ] Frontend 可以响应来自核心的动作指令
- [ ] 开发环境脚本可以一键搭建环境
