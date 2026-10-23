"""Assembled order composition (C-0164): report it, receive the SAP/SKM business result, list the waiting orders; native grants on every call."""
from collections.abc import Callable
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from ...platform.public import AdminUser, get_current_user
from ..contracts_composition_ack import CompositionAck, CompositionAckPort, CompositionReport, composition_ack_service
from ..contracts_tradecase import TradecaseError

router = APIRouter(prefix="/api/tradecase", tags=["tradecase"])


def _call(run: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        return run()
    except TradecaseError as exc:
        raise HTTPException(exc.status, {"code": exc.code}) from exc


@router.post("/order-compositions/report")
def report(body: CompositionReport, user: AdminUser = Depends(get_current_user),
           service: CompositionAckPort = Depends(composition_ack_service)) -> dict[str, Any]:
    return _call(lambda: service.report(body, user.username))


@router.post("/order-compositions/acknowledgments")
def acknowledge(body: CompositionAck, user: AdminUser = Depends(get_current_user),
                service: CompositionAckPort = Depends(composition_ack_service)) -> dict[str, Any]:
    return _call(lambda: service.acknowledge(body, user.username))


@router.get("/warehouses/{warehouse_id}/order-compositions")
def orders(warehouse_id: int = Path(gt=0), limit: int = Query(default=50, ge=1, le=100), user: AdminUser = Depends(get_current_user),
           service: CompositionAckPort = Depends(composition_ack_service)) -> dict[str, Any]:
    return _call(lambda: service.orders(warehouse_id, limit, user.username))
