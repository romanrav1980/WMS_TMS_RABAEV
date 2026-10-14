"""Planner visibility through the existing wave-view permission."""
from decimal import Decimal
from typing import Any, Literal, Protocol
from fastapi import APIRouter, Depends, Query, HTTPException



class SourceAvailabilityPort(Protocol):
    def list_sources(self, warehouse: int, article: str, quantity: Decimal, purpose: str,
                     min_days: int | None, min_percent: Decimal | None,
                     after_uid: str, after_cell: str, limit: int) -> dict[str, Any]: ...


router = APIRouter(prefix="/api/inventory/stock-posting", tags=["stock-posting"])


def source_view_permission() -> object:
    raise RuntimeError("Source view permission not wired")


def source_availability_service() -> SourceAvailabilityPort:
    raise RuntimeError("Source availability service not wired")


@router.get("/source-availability")
def source_availability(
    warehouse: int = Query(gt=0),
    article: str = Query(min_length=1, max_length=160),
    quantity: Decimal = Query(default=Decimal("0"), ge=0, max_digits=27, decimal_places=9),
    purpose: Literal["ALLOCATE", "PICK", "REPLENISH"] = "REPLENISH",
    min_days: int | None = Query(default=None, ge=0),
    min_percent: Decimal | None = Query(default=None, ge=0, le=100),
    after_uid: str = Query(default="", max_length=200),
    after_cell: str = Query(default="", max_length=60),
    limit: int = Query(default=50, ge=1, le=100),
    viewer: object = Depends(source_view_permission),
    service: SourceAvailabilityPort = Depends(source_availability_service),
) -> dict[str, Any]:
    if bool(after_uid) != bool(after_cell):
        raise HTTPException(422, detail="Both source cursor fields are required")
    return service.list_sources(warehouse, article, quantity, purpose, min_days,
                                min_percent, after_uid, after_cell, limit)
