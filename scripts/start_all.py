#!/usr/bin/env python3
"""
SwarmClone 启动脚本

用于启动所有服务的便捷脚本。
"""

import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent.absolute()


SERVICES = {
    "core": {
        "cmd": [sys.executable, "-m", "core.main"],
        "cwd": PROJECT_ROOT,
        "enabled": True,
    },
    "asr": {
        "cmd": [sys.executable, "-m", "src.main"],
        "cwd": PROJECT_ROOT / "services" / "asr",
        "enabled": True,
    },
    "vrchat": {
        "cmd": [sys.executable, "-m", "src.main"],
        "cwd": PROJECT_ROOT / "services" / "vrchat",
        "enabled": True,
    },
    "keyboard": {
        "cmd": [sys.executable, "-m", "src.main"],
        "cwd": PROJECT_ROOT / "services" / "keyboard",
        "enabled": True,
    },
    "vision": {
        "cmd": [sys.executable, "-m", "src.main"],
        "cwd": PROJECT_ROOT / "services" / "vision",
        "enabled": False,
    },
}


def get_env():
    """获取环境变量"""
    env = os.environ.copy()
    pythonpath = str(PROJECT_ROOT)
    if "PYTHONPATH" in env:
        pythonpath = f"{pythonpath}{os.pathsep}{env['PYTHONPATH']}"
    env["PYTHONPATH"] = pythonpath
    return env


def start_redis():
    """启动Redis服务"""
    print("启动Redis服务...")
    try:
        subprocess.run(
            ["docker-compose", "up", "-d", "redis"],
            cwd=PROJECT_ROOT,
            check=True,
        )
        print("Redis服务已启动")
    except FileNotFoundError:
        print("Docker未安装，请手动启动Redis")
        print("  可以运行: redis-server")
    except subprocess.CalledProcessError as e:
        print(f"启动Redis失败: {e}")


def start_service(name: str, config: dict) -> subprocess.Popen:
    """启动单个服务"""
    cwd = config.get("cwd", PROJECT_ROOT)
    print(f"启动服务: {name}")

    process = subprocess.Popen(
        config["cmd"],
        cwd=cwd,
        env=get_env(),
    )
    return process


def main():
    """主函数"""
    print("=" * 50)
    print("SwarmClone 启动器")
    print("=" * 50)
    print(f"项目根目录: {PROJECT_ROOT}")
    print()

    start_redis()
    print()

    processes = []

    for name, config in SERVICES.items():
        if config.get("enabled", True):
            try:
                proc = start_service(name, config)
                processes.append((name, proc))
            except Exception as e:
                print(f"启动服务 {name} 失败: {e}")

    print()
    print("=" * 50)
    print("所有服务已启动")
    print("按 Ctrl+C 停止所有服务")
    print("=" * 50)
    print()

    try:
        for name, proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        print("\n正在停止所有服务...")
        for name, proc in processes:
            proc.terminate()
            print(f"服务 {name} 已停止")


if __name__ == "__main__":
    main()
