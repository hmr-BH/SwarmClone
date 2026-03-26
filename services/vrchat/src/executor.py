"""
动作执行器
"""

import asyncio
import time
from pathlib import Path
from typing import Optional

import yaml
from loguru import logger

from src.config import ParameterMapping
from src.osc_client import OSCClient, AvatarParameterSender


class ActionExecutor:
    """动作执行器"""

    def __init__(self, osc_client: OSCClient):
        self.osc_client = osc_client
        self.sender = AvatarParameterSender(osc_client)
        self.mappings: dict[str, list[ParameterMapping]] = {}
        self._current_action: Optional[str] = None

    def load_mappings(self, config_path: str = "config/vrchat_params.yaml") -> None:
        """加载参数映射配置"""
        path = Path(config_path)
        if not path.exists():
            logger.warning(f"参数映射文件不存在: {config_path}")
            return

        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        self.mappings = {}
        for action_name, params in data.get("parameters", {}).items():
            self.mappings[action_name] = [ParameterMapping(**p) for p in params]

        logger.info(f"已加载 {len(self.mappings)} 个动作参数映射")

    async def execute(self, action_name: str) -> bool:
        """
        执行动作

        Args:
            action_name: 动作名称

        Returns:
            是否执行成功
        """
        if action_name not in self.mappings:
            logger.warning(f"未找到动作映射: {action_name}")
            return False

        if not self.osc_client.is_connected:
            logger.warning("OSC未连接，无法执行动作")
            return False

        self._current_action = action_name
        params = self.mappings[action_name]

        logger.info(f"执行动作: {action_name}")

        tasks = []
        for param in params:
            tasks.append(self._send_parameter(param))

        await asyncio.gather(*tasks)

        return True

    async def _send_parameter(self, param: ParameterMapping) -> None:
        """发送参数"""
        if param.transition_time > 0:
            await asyncio.sleep(param.transition_time)

        self.osc_client.send(param.address, param.value)

    async def execute_gesture(
        self,
        gesture_name: str,
        hand: str = "right",
        weight: float = 1.0,
    ) -> bool:
        """
        执行预设手势

        Args:
            gesture_name: 手势名称
            hand: 手
            weight: 权重
        """
        gestures = {
            "neutral": 0,
            "fist": 1,
            "handopen": 2,
            "fingerpoint": 3,
            "victory": 4,
            "rock": 5,
            "handgun": 6,
            "thumbsup": 7,
        }

        gesture_id = gestures.get(gesture_name.lower())
        if gesture_id is None:
            logger.warning(f"未知手势: {gesture_name}")
            return False

        return self.sender.set_gesture(hand, gesture_id, weight)

    def stop(self) -> None:
        """停止当前动作"""
        self.sender.reset_parameters()
        self._current_action = None
        logger.info("动作已停止")

    @property
    def current_action(self) -> Optional[str]:
        return self._current_action
