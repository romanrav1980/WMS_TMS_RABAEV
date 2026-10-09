"""Authorized read-only visibility; physical writes stay behind business commands."""
from typing import Any
from fastapi import APIRouter, Depends, Path
from ....auth import AdminUser, require_permission, STOCK_RESERVATION_VIEW_PERMISSION
from ..application.stock_ports import StockQueriesPort

router = APIRouter(prefix="/api/inventory/stock-posting", tags=["stock-posting"])


def stock_queries_service() -> StockQueriesPort:
    raise RuntimeError("Stock queries service not wired")


@router.get("/status")
def status(
    user: AdminUser = Depends(require_permission(STOCK_RESERVATION_VIEW_PERMISSION)),
    service: StockQueriesPort = Depends(stock_queries_service),
) -> dict[str, Any]:
    return service.status()


@router.get("/operations/{operation_id}")
def operation(
    operation_id: str = Path(min_length=1, max_length=100),
    user: AdminUser = Depends(require_permission(STOCK_RESERVATION_VIEW_PERMISSION)),
    service: StockQueriesPort = Depends(stock_queries_service),
) -> dict[str, Any]:
    return service.operation(operation_id, user.username)
