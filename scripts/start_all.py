#!/usr/bin/env python3
"""
SwarmClone 启动脚本

用于启动所有服务的便捷脚本。
"""

import asyncio
import subprocess
import sys
from pathlib import Path


SERVICES = {
    "core": {
        "cmd": [sys.executable, "-m", "core.main"],
        "cwd": "core",
        "enabled": True,
    },
    "asr": {
        "cmd": [sys.executable, "-m", "src.main"],
        "cwd": "services/asr",
        "enabled": True,
    },
    "keyboard": {
        "cmd": [sys.executable, "-m", "src.main"],
        "cwd": "services/keyboard",
        "enabled": True,
    },
}


def start_redis():
    """启动Redis服务"""
    print("启动Redis服务...")
    try:
        subprocess.run(
            ["docker-compose", "up", "-d", "redis"],
            check=True,
        )
        print("Redis服务已启动")
    except FileNotFoundError:
        print("Docker未安装，请手动启动Redis")
    except subprocess.CalledProcessError as e:
        print(f"启动Redis失败: {e}")


def start_service(name: str, config: dict) -> subprocess.Popen:
    """启动单个服务"""
    cwd = Path(config["cwd"]) if config.get("cwd") else None
    print(f"启动服务: {name}")

    process = subprocess.Popen(
        config["cmd"],
        cwd=cwd,
    )
    return process


def main():
    """主函数"""
    print("=" * 50)
    print("SwarmClone 启动器")
    print("=" * 50)

    start_redis()

    processes = []

    for name, config in SERVICES.items():
        if config.get("enabled", True):
            try:
                proc = start_service(name, config)
                processes.append((name, proc))
            except Exception as e:
                print(f"启动服务 {name} 失败: {e}")

    print("\n所有服务已启动")
    print("按 Ctrl+C 停止所有服务\n")

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
