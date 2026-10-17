"""Compose read-only resource timeline without expanding legacy resource services."""
from fastapi import FastAPI
from .oracle_gateway import OracleGateway
from .modules.resources.public import resource_timeline_router, resource_timeline_service, build_resource_timeline
from .modules.transport.public import current_timeline_clock


def register_resource_timeline(app: FastAPI) -> None:
    service = build_resource_timeline(OracleGateway(), current_timeline_clock)
    app.include_router(resource_timeline_router)
    app.dependency_overrides[resource_timeline_service] = lambda: service
