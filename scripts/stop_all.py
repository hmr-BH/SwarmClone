#!/usr/bin/env python3
"""
停止所有服务
"""

import subprocess
import sys


def stop_redis():
    """停止Redis服务"""
    print("停止Redis服务...")
    try:
        subprocess.run(
            ["docker-compose", "down"],
            check=True,
        )
        print("Redis服务已停止")
    except Exception as e:
        print(f"停止Redis失败: {e}")


def main():
    print("停止所有服务...")
    stop_redis()
    print("完成")


if __name__ == "__main__":
    main()
