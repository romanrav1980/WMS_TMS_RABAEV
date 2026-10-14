"""Existing inventory/recovery tasks through typed injected ports and existing rights."""
from typing import Any, Protocol
from fastapi import APIRouter, Depends, Query


class RecoveryPort(Protocol):
    def list_inventory(self, limit: int, task_id: int | None = None) -> list[dict[str, Any]]: ...
    def list_recovery(self, limit: int) -> list[dict[str, Any]]: ...
    def claim_inventory(self, task_id: int, actor: str) -> dict[str, Any]: ...


class TaskUser(Protocol):
    username: str


def inventory_task_view() -> TaskUser:
    raise RuntimeError("Inventory view permission not wired")


def inventory_task_execute() -> TaskUser:
    raise RuntimeError("Inventory execute permission not wired")


def recovery_view() -> TaskUser:
    raise RuntimeError("Recovery view permission not wired")


def recovery_tasks_service() -> RecoveryPort:
    raise RuntimeError("Recovery task service not wired")


router = APIRouter(prefix="/api/inventory", tags=["inventory-tasks"])


@router.get("/tasks")
def list_inventory_tasks(
    limit: int = Query(default=50, ge=1, le=100),
    task_id: int | None = Query(default=None, gt=0),
    user: TaskUser = Depends(inventory_task_view),
    service: RecoveryPort = Depends(recovery_tasks_service),
) -> list[dict[str, Any]]:
    return service.list_inventory(limit, task_id)


@router.post("/tasks/{task_id}/claim")
def claim_inventory_task(
    task_id: int,
    user: TaskUser = Depends(inventory_task_execute),
    service: RecoveryPort = Depends(recovery_tasks_service),
) -> dict[str, Any]:
    return service.claim_inventory(task_id, user.username)


@router.get("/recovery-shorts")
def list_recovery_shorts(
    limit: int = Query(default=50, ge=1, le=100),
    user: TaskUser = Depends(recovery_view),
    service: RecoveryPort = Depends(recovery_tasks_service),
) -> list[dict[str, Any]]:
    return service.list_recovery(limit)
