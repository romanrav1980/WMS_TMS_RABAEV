"""Compose versioned CASE resource commands without an admin-shell gate."""
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .modules.resources.public import case_resource_router,case_resource_service,build_case_resource_service
from .modules.resources.public import (
    resource_intent_router, resource_intent_service, build_resource_intent_service,
)
from .modules.inventory.public import (
    case_current_close_router, case_current_close_service, build_case_current_close,
    case_empty_router, case_empty_service, build_case_empty,
)
from .modules.resources.public import (
    picker_time_router, picker_time_service, build_picker_time_service,
    picker_kpi_router, picker_kpi_service, build_picker_kpi_service,
)


def register_case_resource_commands(app: FastAPI) -> None:
    app.dependency_overrides[case_resource_service]=build_case_resource_service
    app.include_router(case_resource_router)
    app.dependency_overrides[resource_intent_service] = build_resource_intent_service
    app.include_router(resource_intent_router)
    app.dependency_overrides[case_current_close_service] = build_case_current_close
    app.include_router(case_current_close_router)
    app.dependency_overrides[case_empty_service] = build_case_empty
    app.include_router(case_empty_router)
    app.dependency_overrides[picker_time_service] = build_picker_time_service
    app.include_router(picker_time_router)
    app.dependency_overrides[picker_kpi_service] = build_picker_kpi_service
    app.include_router(picker_kpi_router)

    build = Path(__file__).resolve().parents[3] / "terminal/wms_terminal_web/dist/case-work"
    if (build / "index.html").is_file():
        app.mount("/case-work", StaticFiles(directory=build, html=True), name="case-work-application")
