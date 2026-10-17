"""Compose operator workflow, existing single stock writer and its terminal."""
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .oracle_gateway import OracleGateway
from .static_content import register_web_media_types
from .modules.inventory.public import (assembly_scale_router, assembly_scale_service,
                                       build_assembly_scale, assembly_intent_router, assembly_intent_service, AssemblyIntents, warehouse_weigh_requests_router, warehouse_weigh_requests_service, build_warehouse_weigh_requests, assembly_close_router, assembly_close_service, AssemblyClose, assembly_recovery_router)
from .modules.resources.public import assert_case_task_access


def register_assembly_scale(app: FastAPI) -> None:
    register_web_media_types()
    app.dependency_overrides[assembly_scale_service] = lambda: build_assembly_scale(OracleGateway())
    app.include_router(assembly_scale_router)
    app.dependency_overrides[assembly_close_service] = lambda: AssemblyClose(OracleGateway(), assert_case_task_access)
    app.include_router(assembly_close_router)
    app.include_router(assembly_recovery_router)
    app.dependency_overrides[assembly_intent_service] = lambda: AssemblyIntents(OracleGateway())
    app.include_router(assembly_intent_router)
    app.dependency_overrides[warehouse_weigh_requests_service] = lambda: build_warehouse_weigh_requests(OracleGateway())
    app.include_router(warehouse_weigh_requests_router)
    build = Path(__file__).resolve().parents[3] / "terminal/wms_terminal_web/dist"
    if (build / "assembly/index.html").is_file():
        app.mount("/assembly", StaticFiles(directory=build / "assembly", html=True), name="assembly-application")
