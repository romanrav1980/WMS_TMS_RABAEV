"""Composition root supplies the existing warehouse assignment implementation."""
from typing import Any
from .schemas import WarehouseTaskStatusRequest
from .services.warehouse_task_service import WarehouseTaskService
from .modules.resources.public import build_qualification_service,QualificationService

def assign_warehouse(gateway: Any,task_id: int,request: WarehouseTaskStatusRequest) -> None:
    WarehouseTaskService(gateway).assign_task(task_id,request)

def build_resource_qualification() -> QualificationService:
    return build_qualification_service(assign_warehouse)
