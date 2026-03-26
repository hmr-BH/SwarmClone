"""
动作映射测试
"""

import pytest
from core.engine.action_mapper import ActionMapper
from core.models.action import ActionType


def test_action_mapper_init():
    mapper = ActionMapper()
    assert mapper.mappings == []
    assert mapper.cooldowns == {}


def test_action_mapper_load():
    mapper = ActionMapper()
    mappings = [
        {
            "trigger": "你好",
            "action_type": "gesture",
            "action_name": "wave",
            "parameters": {"intensity": 0.8},
            "cooldown": 2.0,
        }
    ]
    mapper.load_mappings(mappings)
    assert len(mapper.mappings) == 1


def test_action_mapper_match():
    mapper = ActionMapper()
    mapper.load_mappings(
        [
            {
                "trigger": "你好",
                "action_type": "gesture",
                "action_name": "wave",
                "parameters": {},
                "cooldown": 0,
            }
        ]
    )

    action = mapper.map_trigger("你好")
    assert action is not None
    assert action.name == "wave"
    assert action.type == ActionType.GESTURE


def test_action_mapper_no_match():
    mapper = ActionMapper()
    action = mapper.map_trigger("未知触发词")
    assert action is None


def test_action_mapper_cooldown():
    mapper = ActionMapper()
    mapper.load_mappings(
        [
            {
                "trigger": "测试",
                "action_type": "expression",
                "action_name": "happy",
                "parameters": {},
                "cooldown": 10.0,
            }
        ]
    )

    action1 = mapper.map_trigger("测试")
    assert action1 is not None

    action2 = mapper.map_trigger("测试")
    assert action2 is None  # 冷却中
