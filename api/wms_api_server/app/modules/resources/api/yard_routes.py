"""TRADECASE yard: expected/arrived/at dock/working/done/departed visits of one warehouse."""
from collections.abc import Callable
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from ...platform.public import AdminUser, get_current_user
from ..contracts_yard import YardError, YardExpect, YardPort, YardTransition, yard_service

router = APIRouter(prefix="/api/tradecase/warehouses/{warehouse}/yard", tags=["tradecase-yard"])


def _call(run: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        return run()
    except YardError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "outcome_confirmed": exc.status != 503,
                                         "retry_same_operation_id": exc.status == 503}) from exc


@router.get("/visits")
def visits(warehouse: int = Path(gt=0), active: bool = Query(default=True), user: AdminUser = Depends(get_current_user),
           service: YardPort = Depends(yard_service)) -> dict[str, Any]:
    return _call(lambda: service.visits(warehouse, user.username, active))


@router.post("/visits")
def expect(body: YardExpect, warehouse: int = Path(gt=0), user: AdminUser = Depends(get_current_user),
           service: YardPort = Depends(yard_service)) -> dict[str, Any]:
    return _call(lambda: service.expect(warehouse, body, user.username))


@router.post("/visits/{visit}/transitions")
def transition(body: YardTransition, warehouse: int = Path(gt=0), visit: int = Path(gt=0), user: AdminUser = Depends(get_current_user),
               service: YardPort = Depends(yard_service)) -> dict[str, Any]:
    return _call(lambda: service.transition(warehouse, visit, body, user.username))
