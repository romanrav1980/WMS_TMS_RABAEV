"""TRADECASE yard: planned dock intervals of visits (C-0158); facts stay in the yard visit routes."""
from collections.abc import Callable
from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from ...platform.public import AdminUser, get_current_user
from ..contracts_yard_plan import YardError, YardPlanCancel, YardPlanCreate, YardPlanMove, YardPlanPort, yard_plan_service

router = APIRouter(prefix="/api/tradecase/warehouses/{warehouse}/yard/dock-plans", tags=["tradecase-yard"])


def _call(run: Callable[[], dict[str, Any]], operation_id: str | None = None) -> dict[str, Any]:
    try:
        return run()
    except YardError as exc:
        uncertain = exc.status in (401, 403, 404, 503) or exc.code in {
            "YARD_OPERATION_CONFLICT", "YARD_VISIT_NOT_FOUND", "YARD_PLAN_NOT_FOUND"}
        detail: dict[str, Any] = {"code": exc.code, "outcome_confirmed": not uncertain,
                                  "retry_same_operation_id": uncertain}
        if operation_id is not None:
            detail["operation_id"] = operation_id
        raise HTTPException(exc.status, detail) from exc


@router.get("")
def plans(warehouse: int = Path(gt=0), start: datetime = Query(alias="from"), finish: datetime = Query(alias="to"),
          user: AdminUser = Depends(get_current_user), service: YardPlanPort = Depends(yard_plan_service)) -> dict[str, Any]:
    if start.tzinfo is None or finish.tzinfo is None:
        raise HTTPException(422, {"code": "YARD_PLAN_WINDOW_TIMEZONE_REQUIRED"})
    return _call(lambda: service.plans(warehouse, user.username, start, finish))


@router.post("")
def plan(body: YardPlanCreate, warehouse: int = Path(gt=0), user: AdminUser = Depends(get_current_user),
         service: YardPlanPort = Depends(yard_plan_service)) -> dict[str, Any]:
    return _call(lambda: service.plan(warehouse, body, user.username), body.operation_id)


@router.post("/{plan_id}/move")
def move(body: YardPlanMove, warehouse: int = Path(gt=0), plan_id: int = Path(gt=0), user: AdminUser = Depends(get_current_user),
         service: YardPlanPort = Depends(yard_plan_service)) -> dict[str, Any]:
    return _call(lambda: service.move(warehouse, plan_id, body, user.username), body.operation_id)


@router.post("/{plan_id}/cancel")
def cancel(body: YardPlanCancel, warehouse: int = Path(gt=0), plan_id: int = Path(gt=0), user: AdminUser = Depends(get_current_user),
           service: YardPlanPort = Depends(yard_plan_service)) -> dict[str, Any]:
    return _call(lambda: service.cancel(warehouse, plan_id, body, user.username), body.operation_id)
