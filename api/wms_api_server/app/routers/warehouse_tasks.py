from fastapi import APIRouter, Depends

from ..auth import (
    AdminUser,
    WAREHOUSE_TASK_EXECUTE_PERMISSION,
    WAREHOUSE_TASK_VIEW_PERMISSION,
    require_permission,
)
from ..schemas import WarehouseTaskStatusRequest
from ..services.warehouse_task_domain_sync_service import WarehouseTaskDomainSyncService
from ..services.warehouse_task_service import WarehouseTaskService

router = APIRouter(prefix="/api/warehouse-tasks", tags=["warehouse-tasks"])


@router.get("")
def list_warehouse_tasks(
    status: str | None = None,
    task_type: str | None = None,
    task_source: str | None = None,
    assigned_to: str | None = None,
    production_order_id: int | None = None,
    source_doc_type: str | None = None,
    source_doc_id: int | None = None,
    limit: int = 100,
    _user: AdminUser = Depends(require_permission(WAREHOUSE_TASK_VIEW_PERMISSION)),
) -> list[dict]:
    return WarehouseTaskService().list_tasks(
        status=status,
        task_type=task_type,
        task_source=task_source,
        assigned_to=assigned_to,
        production_order_id=production_order_id,
        source_doc_type=source_doc_type,
        source_doc_id=source_doc_id,
        limit=limit,
    )


@router.get("/domain-sync")
def list_warehouse_task_sync(
    status: str | None = None,
    task_source: str | None = None,
    source_doc_type: str | None = None,
    source_doc_id: int | None = None,
    limit: int = 100,
    _user: AdminUser = Depends(require_permission(WAREHOUSE_TASK_VIEW_PERMISSION)),
) -> list[dict]:
    return WarehouseTaskDomainSyncService().list_sync(
        status=status,
        task_source=task_source,
        source_doc_type=source_doc_type,
        source_doc_id=source_doc_id,
        limit=limit,
    )


@router.get("/{task_id}")
def get_warehouse_task(
    task_id: int,
    _user: AdminUser = Depends(require_permission(WAREHOUSE_TASK_VIEW_PERMISSION)),
) -> dict:
    return WarehouseTaskService().get_task_or_404(task_id)


@router.get("/{task_id}/sync")
def get_warehouse_task_sync(
    task_id: int,
    _user: AdminUser = Depends(require_permission(WAREHOUSE_TASK_VIEW_PERMISSION)),
) -> dict:
    sync = WarehouseTaskDomainSyncService().get_task_sync(task_id)
    return sync or {"task_id": task_id, "sync_status": "NOT_CREATED"}


@router.post("/{task_id}/assign")
def assign_warehouse_task(
    task_id: int,
    request: WarehouseTaskStatusRequest,
    _user: AdminUser = Depends(require_permission(WAREHOUSE_TASK_EXECUTE_PERMISSION)),
) -> dict[str, str]:
    WarehouseTaskService().assign_task(task_id, request)
    return {"status": "ok"}


@router.post("/{task_id}/start")
def start_warehouse_task(
    task_id: int,
    request: WarehouseTaskStatusRequest,
    _user: AdminUser = Depends(require_permission(WAREHOUSE_TASK_EXECUTE_PERMISSION)),
) -> dict[str, str]:
    WarehouseTaskService().start_task(task_id, request)
    return {"status": "ok"}


@router.post("/{task_id}/complete")
def complete_warehouse_task(
    task_id: int,
    request: WarehouseTaskStatusRequest,
    _user: AdminUser = Depends(require_permission(WAREHOUSE_TASK_EXECUTE_PERMISSION)),
) -> dict[str, str]:
    WarehouseTaskService().complete_task(task_id, request)
    return {"status": "ok"}


@router.post("/{task_id}/sync/retry")
def retry_warehouse_task_sync(
    task_id: int,
    request: WarehouseTaskStatusRequest,
    _user: AdminUser = Depends(require_permission(WAREHOUSE_TASK_EXECUTE_PERMISSION)),
) -> dict:
    sync = WarehouseTaskDomainSyncService().retry_task_sync(task_id, request.updated_by or request.assigned_to)
    return {"status": "ok", "sync": sync}


@router.post("/{task_id}/cancel")
def cancel_warehouse_task(
    task_id: int,
    request: WarehouseTaskStatusRequest,
    _user: AdminUser = Depends(require_permission(WAREHOUSE_TASK_EXECUTE_PERMISSION)),
) -> dict[str, str]:
    WarehouseTaskService().cancel_task(task_id, request)
    return {"status": "ok"}
