from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from ...platform.public import AdminUser, get_current_user
from ..contracts_trade_stock import TradeMarkConfirmation, TradeCellPolicy, TradeOwnerGrant, TradeStockBind, TradeStockError, TradeStockPort

router = APIRouter(prefix="/api/tradecase/warehouses/{warehouse_id}/stock", tags=["tradecase-stock"])


def trade_stock_service() -> TradeStockPort:
    raise RuntimeError("TRADECASE stock is not wired")


@router.post("/bind")
def bind(body: TradeStockBind, warehouse_id: int = Path(gt=0), user: AdminUser = Depends(get_current_user),
         service: TradeStockPort = Depends(trade_stock_service)) -> dict[str, Any]:
    try:
        return service.bind(warehouse_id, body, user.username)
    except TradeStockError as exc:
        raise HTTPException(exc.status, {"code": exc.code}) from exc


@router.put("/cells/{cell}")
def cell_policy(body: TradeCellPolicy, cell: str = Path(min_length=1, max_length=60),
                warehouse_id: int = Path(gt=0), user: AdminUser = Depends(get_current_user),
                service: TradeStockPort = Depends(trade_stock_service)) -> dict[str, Any]:
    try:
        return service.cell(warehouse_id, cell, body, user.username)
    except TradeStockError as exc:
        raise HTTPException(exc.status, {"code": exc.code}) from exc


@router.put("/owner-grants")
def owner_grant(body: TradeOwnerGrant, warehouse_id: int = Path(gt=0),
                user: AdminUser = Depends(get_current_user),
                service: TradeStockPort = Depends(trade_stock_service)) -> dict[str, Any]:
    try:
        return service.grant(warehouse_id, body, user.username)
    except TradeStockError as exc:
        raise HTTPException(exc.status, {"code": exc.code}) from exc


@router.get("")
def stock(warehouse_id: int = Path(gt=0), after: str = Query(default="", max_length=64),
          limit: int = Query(default=50, ge=1, le=100), user: AdminUser = Depends(get_current_user),
          service: TradeStockPort = Depends(trade_stock_service)) -> dict[str, Any]:
    try:
        return service.view(warehouse_id, after, limit, user.username)
    except TradeStockError as exc:
        raise HTTPException(exc.status, {"code": exc.code}) from exc


@router.post("/mark-confirmations")
def confirm_marks(body: TradeMarkConfirmation, warehouse_id: int = Path(gt=0), user: AdminUser = Depends(get_current_user),
                  service: TradeStockPort = Depends(trade_stock_service)) -> dict[str, Any]:
    try:
        return service.confirm_marks(warehouse_id, body, user.username)
    except TradeStockError as exc:
        raise HTTPException(exc.status, {"code": exc.code}) from exc


@router.get("/pallets")
def summary(warehouse_id: int = Path(gt=0), after: str = Query(default="", max_length=64),
            limit: int = Query(default=50, ge=1, le=100), user: AdminUser = Depends(get_current_user),
            service: TradeStockPort = Depends(trade_stock_service)) -> dict[str, Any]:
    try:
        return service.summary(warehouse_id, after, limit, user.username)
    except TradeStockError as exc:
        raise HTTPException(exc.status, {"code": exc.code}) from exc
