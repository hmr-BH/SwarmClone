"""
动作映射引擎
"""

import re
import time
from typing import Optional

from core.models.action import Action, ActionMapping, ActionType
from loguru import logger


class ActionMapper:
    """动作映射器"""

    def __init__(self):
        self.mappings: list[ActionMapping] = []
        self.cooldowns: dict[str, float] = {}

    def load_mappings(self, mappings: list[dict]) -> None:
        """
        加载动作映射配置

        Args:
            mappings: 映射配置列表
        """
        self.mappings = []
        for mapping_data in mappings:
            mapping = ActionMapping(**mapping_data)
            self.mappings.append(mapping)
        logger.info(f"已加载 {len(self.mappings)} 个动作映射")

    def map_trigger(self, trigger: str) -> Optional[Action]:
        """
        将触发条件映射为动作

        Args:
            trigger: 触发条件（语音关键词或快捷键）

        Returns:
            Action对象，如果没有匹配则返回None
        """
        if self._in_cooldown(trigger):
            logger.debug(f"触发条件 '{trigger}' 处于冷却中")
            return None

        for mapping in sorted(self.mappings, key=lambda m: m.priority, reverse=True):
            if not mapping.enabled:
                continue

            if self._match_trigger(trigger, mapping.trigger):
                self._set_cooldown(trigger, mapping.cooldown)

                action = Action(
                    type=mapping.action_type,
                    name=mapping.action_name,
                    parameters=mapping.parameters,
                    priority=mapping.priority,
                )

                logger.info(f"触发条件 '{trigger}' 映射到动作 '{mapping.action_name}'")
                return action

        logger.debug(f"触发条件 '{trigger}' 未找到匹配的动作映射")
        return None

    def _match_trigger(self, trigger: str, pattern: str) -> bool:
        """
        匹配触发条件

        Args:
            trigger: 实际触发内容
            pattern: 匹配模式

        Returns:
            是否匹配
        """
        if trigger.lower() == pattern.lower():
            return True

        if pattern.startswith("re:"):
            regex_pattern = pattern[3:]
            try:
                return bool(re.search(regex_pattern, trigger, re.IGNORECASE))
            except re.error:
                logger.warning(f"无效的正则表达式模式: {regex_pattern}")
                return False

        if pattern.startswith("key:"):
            return trigger.lower() == pattern[4:].lower()

        return False

    def _in_cooldown(self, trigger: str) -> bool:
        """检查触发条件是否在冷却中"""
        if trigger not in self.cooldowns:
            return False
        return time.time() < self.cooldowns[trigger]

    def _set_cooldown(self, trigger: str, cooldown: float) -> None:
        """设置冷却时间"""
        if cooldown > 0:
            self.cooldowns[trigger] = time.time() + cooldown

    def add_mapping(self, mapping: ActionMapping) -> None:
        """添加动作映射"""
        self.mappings.append(mapping)
        logger.debug(f"添加动作映射: {mapping.trigger} -> {mapping.action_name}")

    def remove_mapping(self, trigger: str) -> bool:
        """移除动作映射"""
        for i, mapping in enumerate(self.mappings):
            if mapping.trigger == trigger:
                self.mappings.pop(i)
                logger.debug(f"移除动作映射: {trigger}")
                return True
        return False

    def clear_mappings(self) -> None:
        """清除所有映射"""
        self.mappings = []
        self.cooldowns = {}
        logger.debug("已清除所有动作映射")
