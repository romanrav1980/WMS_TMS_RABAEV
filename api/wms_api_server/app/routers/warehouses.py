from fastapi import APIRouter, Depends, HTTPException

from ..auth import (
    AdminUser,
    WAREHOUSE_SETTINGS_EDIT_PERMISSION,
    WAREHOUSE_SETTINGS_VIEW_PERMISSION,
    require_permission,
)
from ..schemas import WarehouseSettingsUpdateRequest
from ..services.warehouse_service import WarehouseService

router = APIRouter(prefix="/api/admin/warehouses", tags=["warehouses"])


@router.get("")
def list_warehouses(
    role: str | None = None,
    mes_enabled: int | None = None,
    limit: int = 200,
    _user: AdminUser = Depends(require_permission(WAREHOUSE_SETTINGS_VIEW_PERMISSION)),
) -> list[dict]:
    return WarehouseService().list_warehouses(
        role=role,
        mes_enabled=mes_enabled,
        limit=limit,
    )


@router.patch("/{ware_id}")
def update_warehouse(
    ware_id: int,
    request: WarehouseSettingsUpdateRequest,
    _user: AdminUser = Depends(require_permission(WAREHOUSE_SETTINGS_EDIT_PERMISSION)),
) -> dict[str, str]:
    updated = WarehouseService().update_warehouse(ware_id, request)
    if updated == 0:
        raise HTTPException(status_code=404, detail="Warehouse not found.")
    return {"status": "ok"}
