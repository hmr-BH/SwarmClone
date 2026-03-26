"""
状态管理器测试
"""

import pytest
from core.engine.state_manager import StateManager
from core.models.state import ServiceStatus


def test_state_manager_init():
    manager = StateManager()
    state = manager.get_state()
    assert state.version == "0.1.0"


def test_state_manager_get_set():
    manager = StateManager()
    manager.start()

    manager.set("mode", "production")
    value = manager.get("mode")
    assert value == "production"


def test_state_manager_service_status():
    manager = StateManager()
    manager.start()

    manager.update_service_status("test_service", ServiceStatus.RUNNING, pid=1234)

    state = manager.get_state()
    assert "test_service" in state.services
    assert state.services["test_service"].status == ServiceStatus.RUNNING
    assert state.services["test_service"].pid == 1234


def test_state_manager_subscribe():
    manager = StateManager()
    manager.start()

    called = []

    def callback(value):
        called.append(value)

    manager.subscribe("mode", callback)
    manager.set("mode", "testing")

    assert len(called) == 1
    assert called[0] == "testing"
