"""Slotted packing reuses the original native HU attach and placement owners."""
from fastapi import APIRouter, Depends
from pydantic import Field
from ...platform.public import AdminUser, get_current_user
from .warehouse_hu_routes import (
    Link, CaseLink, Measurements, WarehouseHuPort, warehouse_hu_service, execute,
)

router = APIRouter(prefix="/api/warehouse-hus", tags=["warehouse-hu"])


class Repack(Link):
    scan_cell: str = Field(min_length=1, max_length=60)
    scan_parent_slot: str = Field(min_length=1, max_length=100)
    scan_child_slot: str = Field(min_length=1, max_length=100)
    measurements: Measurements
    reason: str = Field(min_length=1, max_length=1000)


class CaseRepack(CaseLink):
    scan_cell: str = Field(min_length=1, max_length=60)
    scan_parent_slot: str = Field(min_length=1, max_length=100)
    scan_child_slot: str = Field(min_length=1, max_length=100)
    measurements: Measurements
    reason: str = Field(min_length=1, max_length=1000)


@router.post("/repack-slot")
def repack(body: Repack, user: AdminUser = Depends(get_current_user),
           service: WarehouseHuPort = Depends(warehouse_hu_service)) -> dict:
    return execute(service, "HU_REPACK_SLOT", body, user.username)


@router.post("/repack-case-slot")
def repack_case(body: CaseRepack, user: AdminUser = Depends(get_current_user),
                service: WarehouseHuPort = Depends(warehouse_hu_service)) -> dict:
    return execute(service, "HU_REPACK_SLOT", body, user.username)
