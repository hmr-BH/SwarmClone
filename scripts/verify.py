#!/usr/bin/env python3
"""
SwarmClone 验证脚本

检查所有模块是否可以正常导入和运行。
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def check_module(name: str, import_path: str) -> bool:
    """检查模块是否可以导入"""
    try:
        __import__(import_path)
        print(f"  [OK] {name}")
        return True
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        return False


def check_core():
    """检查核心模块"""
    print("\n核心模块:")
    results = []
    results.append(check_module("models.action", "core.models.action"))
    results.append(check_module("models.state", "core.models.state"))
    results.append(check_module("models.config", "core.models.config"))
    results.append(check_module("engine.action_mapper", "core.engine.action_mapper"))
    results.append(check_module("engine.state_manager", "core.engine.state_manager"))
    results.append(check_module("engine.event_handler", "core.engine.event_handler"))
    results.append(check_module("engine.message_router", "core.engine.message_router"))
    results.append(check_module("api.grpc_service", "core.api.grpc_service"))
    return all(results)


def check_services():
    """检查服务模块"""
    print("\nService modules:")
    results = []

    orig_path = sys.path.copy()

    sys.path = orig_path + [str(PROJECT_ROOT / "services" / "asr" / "src")]
    results.append(check_module("asr.engine", "engine"))
    results.append(check_module("asr.audio", "audio"))

    sys.path = orig_path + [str(PROJECT_ROOT / "services" / "keyboard" / "src")]
    results.append(check_module("keyboard.listener", "listener"))

    sys.path = orig_path + [str(PROJECT_ROOT / "services" / "vrchat" / "src")]
    results.append(check_module("vrchat.osc_client", "osc_client"))

    sys.path = orig_path + [str(PROJECT_ROOT / "services" / "vision" / "src")]
    results.append(check_module("vision.tracker", "tracker"))

    sys.path = orig_path

    return all(results)


def check_functionality():
    """检查功能"""
    print("\n功能测试:")
    results = []

    try:
        from core.engine.action_mapper import ActionMapper

        mapper = ActionMapper()
        mapper.load_mappings(
            [{"trigger": "test", "action_type": "gesture", "action_name": "wave", "parameters": {}}]
        )
        action = mapper.map_trigger("test")
        if action and action.name == "wave":
            print("  [OK] Action mapper")
            results.append(True)
        else:
            print("  [FAIL] Action mapper: incorrect result")
            results.append(False)
    except Exception as e:
        print(f"  [FAIL] Action mapper: {e}")
        results.append(False)

    try:
        from core.engine.state_manager import StateManager
        from core.models.state import ServiceStatus

        manager = StateManager()
        manager.start()
        manager.update_service_status("test_service", ServiceStatus.RUNNING, pid=1234)
        state = manager.get_state()
        if (
            "test_service" in state.services
            and state.services["test_service"].status == ServiceStatus.RUNNING
        ):
            print("  [OK] State manager")
            results.append(True)
        else:
            print("  [FAIL] State manager: incorrect status")
            results.append(False)
    except Exception as e:
        print(f"  [FAIL] State manager: {e}")
        results.append(False)

    return all(results)


def main():
    print("=" * 50)
    print("SwarmClone 模块验证")
    print("=" * 50)

    core_ok = check_core()
    services_ok = check_services()
    func_ok = check_functionality()

    print("\n" + "=" * 50)
    if core_ok and services_ok and func_ok:
        print("[OK] All modules verified successfully")
        return 0
    else:
        print("[FAIL] Some modules failed verification")
        return 1


if __name__ == "__main__":
    sys.exit(main())
