"""SUPPLY composition in parts (C-0163): parts, END, the transfer list and an explicit hand-over retry; native grants on every call."""
from collections.abc import Callable
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from ...platform.public import AdminUser, get_current_user
from ..contracts_supply_parts import SupplyPartsPort, TradeSupplyPart, TradeSupplyPartsEnd, supply_parts_service
from ..contracts_tradecase import TradecaseError

router = APIRouter(prefix="/api/tradecase", tags=["tradecase"])


def _call(run: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        return run()
    except TradecaseError as exc:
        raise HTTPException(exc.status, {"code": exc.code}) from exc


@router.post("/supply-parts")
def put_part(body: TradeSupplyPart, user: AdminUser = Depends(get_current_user),
             service: SupplyPartsPort = Depends(supply_parts_service)) -> dict[str, Any]:
    return _call(lambda: service.put_part(body, user.username))


@router.post("/supply-parts/end")
def put_end(body: TradeSupplyPartsEnd, user: AdminUser = Depends(get_current_user),
            service: SupplyPartsPort = Depends(supply_parts_service)) -> dict[str, Any]:
    return _call(lambda: service.put_end(body, user.username))


@router.get("/warehouses/{warehouse_id}/supply-transfers")
def transfers(warehouse_id: int = Path(gt=0), limit: int = Query(default=50, ge=1, le=100), user: AdminUser = Depends(get_current_user),
              service: SupplyPartsPort = Depends(supply_parts_service)) -> dict[str, Any]:
    return _call(lambda: service.transfers(warehouse_id, limit, user.username))


@router.post("/warehouses/{warehouse_id}/supply-transfers/{source_id}/{transfer_id}/deliver")
def deliver(warehouse_id: int = Path(gt=0), source_id: str = Path(min_length=1, max_length=100), transfer_id: str = Path(min_length=1, max_length=100),
            user: AdminUser = Depends(get_current_user), service: SupplyPartsPort = Depends(supply_parts_service)) -> dict[str, Any]:
    return _call(lambda: service.deliver(warehouse_id, source_id, transfer_id, user.username))
