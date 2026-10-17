"""Versioned warehouse assignment commands; native current authority owns admission."""
from fastapi import FastAPI
from .modules.resources.public import task_resource_router, task_resource_service, build_task_resource_service


def register_warehouse_task_resource_commands(app: FastAPI) -> None:
    app.dependency_overrides[task_resource_service] = build_task_resource_service
    app.include_router(task_resource_router)
