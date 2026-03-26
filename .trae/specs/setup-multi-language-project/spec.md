# SwarmClone 多语言项目开发方案

## Why
SwarmClone 是一个多语言协作的虚拟角色控制系统，需要整合 VRChat 对接、Live2D/VRM 模型显示、语音识别、视觉捕获、控制面板等多种功能，通过合理的多语言架构设计实现各模块的高效协作。

## What Changes
- 创建多语言项目的基础架构和构建配置
- 定义各模块间的通信协议和接口规范
- 建立统一的开发、测试、部署流程

## Impact
- Affected specs: 项目整体架构
- Affected code: 所有模块目录

---

## 项目架构概览

```
SwarmClone/
├── cli/                    # Rust CLI - 一键部署工具
├── core/                   # Python 核心 - 主要业务逻辑
├── frontend/               # Godot - Live2D/VRM 3D模型显示
├── panel/                  # Vue.js - 控制面板 WebUI
├── scripts/                # 快捷脚本
├── services/               # 独立服务
│   ├── asr-client/        # ASR 语音识别客户端
│   ├── vision-capture/    # 视觉捕获服务
│   ├── vrchat/            # VRChat 对接服务 (C#)
│   └── keyboard/          # 键盘操作服务
└── main.py                 # Python 入口
```

---

## ADDED Requirements

### Requirement: CLI 模块 (Rust)
CLI 模块 SHALL 提供一键部署和管理功能。

#### Scenario: 环境初始化
- **WHEN** 用户执行 `swarmclone init`
- **THEN** 系统自动检测并安装所需依赖（Python、Godot、Node.js 等）

#### Scenario: 服务启动
- **WHEN** 用户执行 `swarmclone start`
- **THEN** 系统按依赖顺序启动所有服务

#### Scenario: 服务停止
- **WHEN** 用户执行 `swarmclone stop`
- **THEN** 系统优雅停止所有运行中的服务

#### Scenario: 状态查看
- **WHEN** 用户执行 `swarmclone status`
- **THEN** 系统显示所有服务的运行状态

### Requirement: Core 核心模块 (Python)
Core 模块 SHALL 提供核心业务逻辑和协调功能。

#### Scenario: 消息路由
- **WHEN** 收到来自任何服务的消息
- **THEN** 系统根据消息类型路由到对应的处理器

#### Scenario: 配置管理
- **WHEN** 系统启动时
- **THEN** 加载并验证所有配置文件

#### Scenario: 服务协调
- **WHEN** 某个服务需要与其他服务通信
- **THEN** 通过核心模块进行消息转发和协调

### Requirement: Frontend 前端模块 (Godot)
Frontend 模块 SHALL 提供 Live2D/VRM 3D 模型的渲染和交互。

#### Scenario: 模型加载
- **WHEN** 系统启动或用户选择模型
- **THEN** 加载并渲染 Live2D 或 VRM 模型

#### Scenario: 动作响应
- **WHEN** 接收到动作指令
- **THEN** 模型执行对应的动画或表情

#### Scenario: 与核心通信
- **WHEN** 需要与核心模块交换数据
- **THEN** 通过 WebSocket 或 TCP 进行通信

### Requirement: Panel 控制面板 (Vue.js)
Panel 模块 SHALL 提供 Web 界面的控制面板。

#### Scenario: 服务监控
- **WHEN** 用户访问控制面板
- **THEN** 显示所有服务的实时状态

#### Scenario: 配置编辑
- **WHEN** 用户修改配置项
- **THEN** 实时更新并保存配置

#### Scenario: 日志查看
- **WHEN** 用户请求查看日志
- **THEN** 显示对应服务的日志输出

### Requirement: Services 独立服务模块
Services 模块 SHALL 提供各种独立的功能服务。

#### Scenario: ASR 语音识别
- **WHEN** 用户说话
- **THEN** ASR 客户端将语音转换为文本并发送给核心

#### Scenario: 视觉捕获
- **WHEN** 摄像头捕获画面
- **THEN** 系统识别面部表情和动作并同步到模型

#### Scenario: VRChat 对接
- **WHEN** VRChat 运行时
- **THEN** 系统与 VRChat 进行数据同步（使用 C#）

#### Scenario: 键盘操作
- **WHEN** 用户按下快捷键
- **THEN** 系统执行对应的预设动作

### Requirement: 模块间通信协议
系统 SHALL 使用统一的通信协议进行模块间通信。

#### Scenario: 消息格式
- **WHEN** 模块间发送消息
- **THEN** 使用 JSON 格式的统一消息结构

#### Scenario: 通信方式
- **WHEN** 模块需要通信
- **THEN** 优先使用 WebSocket 进行实时通信，必要时使用 HTTP REST API

### Requirement: 构建和部署
系统 SHALL 提供统一的构建和部署流程。

#### Scenario: 开发环境
- **WHEN** 开发者运行开发环境
- **THEN** 各模块独立运行，支持热重载

#### Scenario: 生产构建
- **WHEN** 执行构建命令
- **THEN** 各模块分别构建并打包为可分发的格式

---

## 技术选型详情

| 模块 | 语言/框架 | 主要用途 |
|------|----------|---------|
| cli | Rust | CLI 工具、进程管理、依赖检测 |
| core | Python 3.12+ | 核心逻辑、消息路由、AI 集成 |
| frontend | Godot 4.x | Live2D/VRM 渲染、动画控制 |
| panel | Vue.js 3 + TypeScript | WebUI、实时监控、配置管理 |
| services/vrchat | C# (.NET) | VRChat OSC/API 对接 |
| services/asr-client | Python | 语音识别客户端 |
| services/vision-capture | Python | 视觉捕获和处理 |
| services/keyboard | Python | 全局热键监听 |

---

## 通信架构

```
                    ┌─────────────┐
                    │   Panel     │
                    │  (Vue.js)   │
                    └──────┬──────┘
                           │ WebSocket
                           ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   CLI       │◄───►│    Core     │◄───►│  Frontend   │
│  (Rust)     │     │  (Python)   │     │  (Godot)    │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ ASR Client  │     │  Vision     │     │  VRChat     │
│  (Python)   │     │  (Python)   │     │   (C#)      │
└─────────────┘     └─────────────┘     └─────────────┘
```
