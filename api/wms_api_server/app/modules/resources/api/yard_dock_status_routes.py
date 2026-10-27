"""Read and change the blocked/reopened status of a dock."""
from collections.abc import Callable
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Path
from ...platform.public import AdminUser, get_current_user
from ..contracts_yard import YardError
from ..contracts_yard_status import YardDockStatusCommand, YardDockStatusPort, yard_dock_status_service

router = APIRouter(prefix="/api/tradecase/warehouses/{warehouse}/yard/docks", tags=["tradecase-yard"])


def _call(run: Callable[[], dict[str, Any]], operation_id: str | None = None) -> dict[str, Any]:
    try:
        return run()
    except YardError as exc:
        uncertain = exc.status in (403, 404, 503) or exc.code == "YARD_OPERATION_CONFLICT"
        detail: dict[str, Any] = {"code": exc.code, "outcome_confirmed": not uncertain,
                                  "retry_same_operation_id": uncertain}
        if operation_id:
            detail["operation_id"] = operation_id
        raise HTTPException(exc.status, detail) from exc


@router.get("")
def docks(warehouse: int = Path(gt=0), user: AdminUser = Depends(get_current_user),
          service: YardDockStatusPort = Depends(yard_dock_status_service)) -> dict[str, Any]:
    return _call(lambda: service.docks(warehouse, user.username))


@router.post("/{dock}/status")
def command(body: YardDockStatusCommand, warehouse: int = Path(gt=0), dock: str = Path(min_length=1, max_length=15),
            user: AdminUser = Depends(get_current_user), service: YardDockStatusPort = Depends(yard_dock_status_service)) -> dict[str, Any]:
    normalized = dock.strip()
    if not normalized:
        raise HTTPException(422, {"code": "YARD_DOCK_STATUS_REQUEST_INVALID"})
    return _call(lambda: service.command(warehouse, normalized, body, user.username), body.operation_id)
