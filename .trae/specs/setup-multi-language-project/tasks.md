# Tasks

## Phase 1: 基础架构搭建

- [ ] Task 1: 创建项目配置文件
  - [ ] SubTask 1.1: 创建根目录的 pyproject.toml 更新，添加核心依赖
  - [ ] SubTask 1.2: 创建 .editorconfig 统一编辑器配置
  - [ ] SubTask 1.3: 创建 docker-compose.yml 用于服务编排

- [ ] Task 2: CLI 模块初始化 (Rust)
  - [ ] SubTask 2.1: 初始化 Rust 项目 (cargo init)
  - [ ] SubTask 2.2: 添加核心依赖 (clap, tokio, serde, anyhow)
  - [ ] SubTask 2.3: 实现基础命令框架 (init, start, stop, status)
  - [ ] SubTask 2.4: 实现进程管理功能

- [ ] Task 3: Core 核心模块初始化 (Python)
  - [ ] SubTask 3.1: 创建核心模块目录结构
  - [ ] SubTask 3.2: 实现配置管理模块
  - [ ] SubTask 3.3: 实现消息路由器
  - [ ] SubTask 3.4: 实现 WebSocket 服务端

- [ ] Task 4: Frontend 前端模块初始化 (Godot)
  - [ ] SubTask 4.1: 创建 Godot 4 项目结构
  - [ ] SubTask 4.2: 配置 Live2D 插件支持
  - [ ] SubTask 4.3: 配置 VRM 模型加载支持
  - [ ] SubTask 4.4: 实现 WebSocket 客户端

- [ ] Task 5: Panel 控制面板初始化 (Vue.js)
  - [ ] SubTask 5.1: 初始化 Vue 3 + TypeScript 项目
  - [ ] SubTask 5.2: 配置 UI 组件库 (如 Element Plus 或 Naive UI)
  - [ ] SubTask 5.3: 实现基础布局和路由
  - [ ] SubTask 5.4: 实现 WebSocket 连接管理

## Phase 2: Services 服务模块

- [ ] Task 6: ASR 客户端服务
  - [ ] SubTask 6.1: 创建 Python 模块结构
  - [ ] SubTask 6.2: 集成语音识别库 (如 whisper 或云端 API)
  - [ ] SubTask 6.3: 实现 WebSocket 客户端连接核心

- [ ] Task 7: 视觉捕获服务
  - [ ] SubTask 7.1: 创建 Python 模块结构
  - [ ] SubTask 7.2: 集成摄像头捕获 (OpenCV)
  - [ ] SubTask 7.3: 集成面部识别 (MediaPipe)
  - [ ] SubTask 7.4: 实现数据发送到核心

- [ ] Task 8: VRChat 对接服务 (C#)
  - [ ] SubTask 8.1: 创建 .NET 项目
  - [ ] SubTask 8.2: 实现 OSC 通信
  - [ ] SubTask 8.3: 实现参数同步
  - [ ] SubTask 8.4: 实现 WebSocket 客户端连接核心

- [ ] Task 9: 键盘操作服务
  - [ ] SubTask 9.1: 创建 Python 模块结构
  - [ ] SubTask 9.2: 集成全局热键库 (pynput 或 keyboard)
  - [ ] SubTask 9.3: 实现热键配置和回调

## Phase 3: 集成与测试

- [ ] Task 10: 模块间通信集成
  - [ ] SubTask 10.1: 定义统一消息协议
  - [ ] SubTask 10.2: 实现各模块的消息编解码
  - [ ] SubTask 10.3: 测试模块间通信

- [ ] Task 11: CLI 一键部署完善
  - [ ] SubTask 11.1: 实现依赖检测和安装
  - [ ] SubTask 11.2: 实现服务编排启动
  - [ ] SubTask 11.3: 实现日志聚合查看

- [ ] Task 12: 文档和脚本
  - [ ] SubTask 12.1: 编写开发环境搭建脚本
  - [ ] SubTask 12.2: 编写快速启动脚本

---

# Task Dependencies

- Task 2 依赖 Task 1
- Task 3 依赖 Task 1
- Task 4 依赖 Task 1
- Task 5 依赖 Task 1
- Task 6 依赖 Task 3
- Task 7 依赖 Task 3
- Task 8 依赖 Task 3
- Task 9 依赖 Task 3
- Task 10 依赖 Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9
- Task 11 依赖 Task 10
- Task 12 依赖 Task 11

---

# 并行执行建议

以下任务可以并行执行：
- Phase 1 中的 Task 2, 3, 4, 5 可以并行
- Phase 2 中的 Task 6, 7, 8, 9 可以并行（前提是 Task 3 完成）
