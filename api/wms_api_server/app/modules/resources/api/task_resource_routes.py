"""Identity-only admission; Oracle checks both actual warehouses and current assignment."""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from ...platform.public import AdminUser, get_current_user
from ..contracts_task_resource import TaskResourceCommand, TaskResourceError, TaskResourcePort, task_resource_service

router = APIRouter(prefix="/api/warehouse-tasks", tags=["warehouse-resource-commands"])


def failure(error: TaskResourceError) -> HTTPException:
    return HTTPException(error.status, dict(code=error.code, operation_id=error.operation_id,
                                           outcome_confirmed=False, read_before_retry=True))


@router.get("/{task_id}/resource-context")
def context(task_id: int, target: str | None = Query(None, min_length=1, max_length=100),
            user: AdminUser = Depends(get_current_user),
            service: TaskResourcePort = Depends(task_resource_service)) -> dict[str, Any]:
    try:
        return service.context(task_id, user.username, target or user.username)
    except TaskResourceError as error:
        raise failure(error) from error


@router.post("/{task_id}/resource-commands", response_model=None)
def command(task_id: int, body: TaskResourceCommand, user: AdminUser = Depends(get_current_user),
            service: TaskResourcePort = Depends(task_resource_service)) -> Any:
    try:
        result = service.command(task_id, body, user.username)
    except TaskResourceError as error:
        raise failure(error) from error
    return JSONResponse(status_code=409, content=result) if result["outcome"] == "REJECTED" else result


@router.get("/resource-commands/{operation_id}")
def receipt(operation_id: str, user: AdminUser = Depends(get_current_user),
            service: TaskResourcePort = Depends(task_resource_service)) -> dict[str, Any]:
    try:
        return service.receipt(operation_id, user.username)
    except TaskResourceError as error:
        raise failure(error) from error
