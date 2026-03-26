"""
OSC客户端模块
"""

import asyncio
from typing import Optional, Union

from loguru import logger
from pythonosc import udp_client
from pythonosc.osc_message_builder import OscMessageBuilder


class OSCClient:
    """OSC客户端"""

    def __init__(
        self,
        address: str = "127.0.0.1",
        port: int = 9000,
    ):
        self.address = address
        self.port = port
        self._client: Optional[udp_client.SimpleUDPClient] = None
        self._connected = False

    def connect(self) -> bool:
        """连接到OSC服务器"""
        try:
            self._client = udp_client.SimpleUDPClient(self.address, self.port)
            self._connected = True
            logger.info(f"OSC已连接: {self.address}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"OSC连接失败: {e}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """断开连接"""
        self._client = None
        self._connected = False
        logger.info("OSC已断开")

    def send(self, address: str, value: Union[float, int, str, bool, list]) -> bool:
        """
        发送OSC消息

        Args:
            address: OSC地址，如 "/avatar/parameters/GestureLeft"
            value: 参数值

        Returns:
            是否发送成功
        """
        if not self._client or not self._connected:
            logger.warning("OSC未连接")
            return False

        try:
            self._client.send_message(address, value)
            logger.debug(f"OSC发送: {address} = {value}")
            return True
        except Exception as e:
            logger.error(f"OSC发送失败: {e}")
            return False

    def send_multiple(self, messages: list[tuple[str, Union[float, int, str, bool]]]) -> bool:
        """
        发送多个OSC消息

        Args:
            messages: 消息列表 [(address, value), ...]

        Returns:
            是否全部发送成功
        """
        success = True
        for address, value in messages:
            if not self.send(address, value):
                success = False
        return success

    @property
    def is_connected(self) -> bool:
        return self._connected


class AvatarParameterSender:
    """Avatar参数发送器"""

    def __init__(self, osc_client: OSCClient):
        self.osc_client = osc_client
        self._parameters: dict[str, Union[float, int, str, bool]] = {}

    def set_parameter(
        self,
        name: str,
        value: Union[float, int, str, bool],
        address_prefix: str = "/avatar/parameters/",
    ) -> bool:
        """设置Avatar参数"""
        address = f"{address_prefix}{name}"
        self._parameters[name] = value
        return self.osc_client.send(address, value)

    def set_gesture(
        self,
        hand: str,
        gesture: int,
        weight: float = 1.0,
    ) -> bool:
        """
        设置手势

        Args:
            hand: "left" 或 "right"
            gesture: 手势ID (0-7)
            weight: 权重 (0.0-1.0)
        """
        if hand.lower() == "left":
            gesture_addr = "/avatar/parameters/GestureLeft"
            weight_addr = "/avatar/parameters/GestureLeftWeight"
        else:
            gesture_addr = "/avatar/parameters/GestureRight"
            weight_addr = "/avatar/parameters/GestureRightWeight"

        return self.osc_client.send_multiple(
            [
                (gesture_addr, gesture),
                (weight_addr, weight),
            ]
        )

    def set_expression(self, expression: str) -> bool:
        """设置表情"""
        return self.osc_client.send("/avatar/parameters/VRCFaceExpression", expression)

    def reset_parameters(self) -> None:
        """重置所有参数"""
        self.osc_client.send("/avatar/parameters/GestureLeft", 0)
        self.osc_client.send("/avatar/parameters/GestureLeftWeight", 0.0)
        self.osc_client.send("/avatar/parameters/GestureRight", 0)
        self.osc_client.send("/avatar/parameters/GestureRightWeight", 0.0)
        self._parameters.clear()

    def get_current_parameters(self) -> dict:
        """获取当前参数"""
        return self._parameters.copy()
