# SwarmClone CLI

SwarmClone 命令行工具，用于部署和管理虚拟形象控制系统。

## 功能

- `deploy` - 一键部署系统，检查依赖并生成配置
- `start` - 启动服务
- `stop` - 停止服务
- `status` - 查看系统状态
- `config` - 配置管理

## 构建

```bash
cargo build --release
```

## 使用

```bash
# 部署系统
swarmclone deploy

# 启动所有服务
swarmclone start --all

# 查看状态
swarmclone status

# 查看配置
swarmclone config show
```
