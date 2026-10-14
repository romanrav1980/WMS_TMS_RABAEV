from typing import Any
from .oracle_gateway import OracleGateway
from .modules.transport.public import driver_workspace_router, driver_workspace_service, build_driver_workspace

def build_driver_service() -> Any:
    return build_driver_workspace(OracleGateway())

def register(app: Any) -> None:
    app.include_router(driver_workspace_router)
    app.dependency_overrides[driver_workspace_service]=build_driver_service
