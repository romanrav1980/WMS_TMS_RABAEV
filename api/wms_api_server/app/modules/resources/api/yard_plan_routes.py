"""TRADECASE yard: planned dock intervals of visits (C-0158); facts stay in the yard visit routes."""
from collections.abc import Callable
from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from ...platform.public import AdminUser, get_current_user
from ..contracts_yard_plan import YardError, YardPlanCancel, YardPlanCreate, YardPlanMove, YardPlanPort, yard_plan_service

router = APIRouter(prefix="/api/tradecase/warehouses/{warehouse}/yard/dock-plans", tags=["tradecase-yard"])


def _call(run: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        return run()
    except YardError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "outcome_confirmed": exc.status != 503,
                                         "retry_same_operation_id": exc.status == 503}) from exc


@router.get("")
def plans(warehouse: int = Path(gt=0), start: datetime = Query(alias="from"), finish: datetime = Query(alias="to"),
          user: AdminUser = Depends(get_current_user), service: YardPlanPort = Depends(yard_plan_service)) -> dict[str, Any]:
    if start.tzinfo is None or finish.tzinfo is None:
        raise HTTPException(422, {"code": "YARD_PLAN_WINDOW_TIMEZONE_REQUIRED"})
    return _call(lambda: service.plans(warehouse, user.username, start, finish))


@router.post("")
def plan(body: YardPlanCreate, warehouse: int = Path(gt=0), user: AdminUser = Depends(get_current_user),
         service: YardPlanPort = Depends(yard_plan_service)) -> dict[str, Any]:
    return _call(lambda: service.plan(warehouse, body, user.username))


@router.post("/{plan_id}/move")
def move(body: YardPlanMove, warehouse: int = Path(gt=0), plan_id: int = Path(gt=0), user: AdminUser = Depends(get_current_user),
         service: YardPlanPort = Depends(yard_plan_service)) -> dict[str, Any]:
    return _call(lambda: service.move(warehouse, plan_id, body, user.username))


@router.post("/{plan_id}/cancel")
def cancel(body: YardPlanCancel, warehouse: int = Path(gt=0), plan_id: int = Path(gt=0), user: AdminUser = Depends(get_current_user),
           service: YardPlanPort = Depends(yard_plan_service)) -> dict[str, Any]:
    return _call(lambda: service.cancel(warehouse, plan_id, body, user.username))
