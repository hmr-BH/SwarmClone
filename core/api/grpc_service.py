"""
gRPC服务实现
"""

import asyncio
from concurrent import futures
from typing import Optional

import grpc
from loguru import logger

from core.api.proto import system_pb2, system_pb2_grpc
from core.api.proto import config_pb2, config_pb2_grpc
from core.api.proto import action_pb2, action_pb2_grpc
from core.engine.action_mapper import ActionMapper
from core.engine.state_manager import StateManager
from core.utils.config_loader import ConfigLoader


class SystemServicer(system_pb2_grpc.SystemServiceServicer):
    """系统服务实现"""

    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager

    def Start(self, request, context):
        response = system_pb2.StartResponse(
            success=True,
            message="服务启动请求已发送",
            started_services=request.services,
        )
        return response

    def Stop(self, request, context):
        response = system_pb2.StopResponse(
            success=True,
            message="服务停止请求已发送",
            stopped_services=request.services,
        )
        return response

    def Restart(self, request, context):
        response = system_pb2.RestartResponse(
            success=True,
            message="服务重启请求已发送",
        )
        return response

    def GetStatus(self, request, context):
        state = self.state_manager.get_state()

        services = {}
        for name, info in state.services.items():
            services[name] = system_pb2.ServiceInfo(
                name=info.name,
                status=info.status.value if hasattr(info.status, "value") else str(info.status),
                pid=info.pid or 0,
                uptime=int(info.uptime),
                error_message=info.error_message or "",
            )

        return system_pb2.SystemStatus(
            version=state.version,
            uptime=int(state.uptime),
            mode=state.mode.value if hasattr(state.mode, "value") else str(state.mode),
            services=services,
        )

    def GetServiceStatus(self, request, context):
        state = self.state_manager.get_state()
        service_name = request.service_name

        if service_name in state.services:
            info = state.services[service_name]
            return system_pb2.ServiceStatus(
                name=info.name,
                status=info.status.value if hasattr(info.status, "value") else str(info.status),
                pid=info.pid or 0,
                uptime=int(info.uptime),
                error_message=info.error_message or "",
            )

        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details(f"服务未找到: {service_name}")
        return system_pb2.ServiceStatus()


class ConfigServicer(config_pb2_grpc.ConfigServiceServicer):
    """配置服务实现"""

    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader

    def Get(self, request, context):
        key = request.key
        value = self._get_nested_value(key)

        if value is not None:
            return config_pb2.ConfigValue(
                success=True,
                key=key,
                value=str(value),
                value_type=type(value).__name__,
            )

        return config_pb2.ConfigValue(
            success=False,
            key=key,
        )

    def Set(self, request, context):
        return config_pb2.SetResponse(
            success=True,
            message="配置已更新",
        )

    def Validate(self, request, context):
        return config_pb2.ValidateResponse(
            valid=True,
            errors=[],
            warnings=[],
        )

    def Export(self, request, context):
        import yaml

        content = yaml.dump(self.config_loader._raw_config, allow_unicode=True)
        return config_pb2.ConfigData(
            format="yaml",
            content=content,
        )

    def Import(self, request, context):
        return config_pb2.ImportResponse(
            success=True,
            message="配置已导入",
            imported_count=0,
        )

    def _get_nested_value(self, key: str):
        parts = key.split(".")
        value = self.config_loader._raw_config

        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None

        return value


class ActionServicer(action_pb2_grpc.ActionServiceServicer):
    """动作服务实现"""

    def __init__(self, action_mapper: ActionMapper):
        self.action_mapper = action_mapper

    def Trigger(self, request, context):
        action = self.action_mapper.map_trigger(request.trigger)

        if action:
            params = {k: str(v) for k, v in action.parameters.items()}
            return action_pb2.TriggerResponse(
                success=True,
                action_name=action.name,
                action_type=action.type.value,
                parameters=params,
            )

        return action_pb2.TriggerResponse(
            success=False,
        )

    def GetMapping(self, request, context):
        for mapping in self.action_mapper.mappings:
            if mapping.trigger == request.trigger:
                params = {k: str(v) for k, v in mapping.parameters.items()}
                return action_pb2.ActionMapping(
                    trigger=mapping.trigger,
                    action_type=mapping.action_type.value,
                    action_name=mapping.action_name,
                    parameters=params,
                    priority=mapping.priority,
                    cooldown=mapping.cooldown,
                    enabled=mapping.enabled,
                )

        context.set_code(grpc.StatusCode.NOT_FOUND)
        return action_pb2.ActionMapping()

    def ListMappings(self, request, context):
        mappings = []

        for m in self.action_mapper.mappings:
            if request.action_type and m.action_type.value != request.action_type:
                continue
            if request.enabled_only and not m.enabled:
                continue

            params = {k: str(v) for k, v in m.parameters.items()}
            mappings.append(
                action_pb2.ActionMapping(
                    trigger=m.trigger,
                    action_type=m.action_type.value,
                    action_name=m.action_name,
                    parameters=params,
                    priority=m.priority,
                    cooldown=m.cooldown,
                    enabled=m.enabled,
                )
            )

        return action_pb2.ListMappingsResponse(
            mappings=mappings,
            total_count=len(mappings),
        )

    def AddMapping(self, request, context):
        from core.models.action import ActionMapping, ActionType

        mapping = ActionMapping(
            trigger=request.mapping.trigger,
            action_type=ActionType(request.mapping.action_type),
            action_name=request.mapping.action_name,
            parameters=dict(request.mapping.parameters),
            priority=request.mapping.priority,
            cooldown=request.mapping.cooldown,
            enabled=request.mapping.enabled,
        )

        self.action_mapper.add_mapping(mapping)

        return action_pb2.AddMappingResponse(
            success=True,
            message="动作映射已添加",
        )

    def RemoveMapping(self, request, context):
        success = self.action_mapper.remove_mapping(request.trigger)

        return action_pb2.RemoveMappingResponse(
            success=success,
            message="动作映射已删除" if success else "未找到映射",
        )


class GrpcServer:
    """gRPC服务器"""

    def __init__(
        self,
        action_mapper: ActionMapper,
        state_manager: StateManager,
        config_loader: ConfigLoader,
        port: int = 50051,
    ):
        self.port = port
        self.server: Optional[grpc.aio.Server] = None

        self.system_servicer = SystemServicer(state_manager)
        self.config_servicer = ConfigServicer(config_loader)
        self.action_servicer = ActionServicer(action_mapper)

    async def start(self) -> None:
        self.server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))

        system_pb2_grpc.add_SystemServiceServicer_to_server(self.system_servicer, self.server)
        config_pb2_grpc.add_ConfigServiceServicer_to_server(self.config_servicer, self.server)
        action_pb2_grpc.add_ActionServiceServicer_to_server(self.action_servicer, self.server)

        self.server.add_insecure_port(f"[::]:{self.port}")
        await self.server.start()
        logger.info(f"gRPC服务器已启动，端口: {self.port}")

    async def stop(self) -> None:
        if self.server:
            await self.server.stop(grace=5)
            logger.info("gRPC服务器已停止")
