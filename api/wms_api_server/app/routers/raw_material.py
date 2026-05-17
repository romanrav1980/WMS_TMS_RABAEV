from fastapi import APIRouter, Depends

from ..auth import (
    AdminUser,
    RAW_MATERIAL_EDIT_PERMISSION,
    RAW_MATERIAL_STOCK_VIEW_PERMISSION,
    RAW_MATERIAL_VIEW_PERMISSION,
    require_permission,
)
from ..schemas import RawMaterialSkuSettingsUpdateRequest
from ..services.raw_material_service import RawMaterialService

router = APIRouter(prefix="/api/raw-material", tags=["raw-material"])


@router.get("/skus")
def list_raw_material_skus(
    search: str | None = None,
    only_active: int | None = 1,
    only_with_stock: int | None = None,
    limit: int = 200,
    _user: AdminUser = Depends(require_permission(RAW_MATERIAL_VIEW_PERMISSION)),
) -> list[dict]:
    return RawMaterialService().list_skus(
        search=search,
        only_active=only_active,
        only_with_stock=only_with_stock,
        limit=limit,
    )


@router.patch("/skus/{articul}")
def update_raw_material_sku(
    articul: str,
    request: RawMaterialSkuSettingsUpdateRequest,
    _user: AdminUser = Depends(require_permission(RAW_MATERIAL_EDIT_PERMISSION)),
) -> dict[str, str]:
    RawMaterialService().update_sku_settings(articul, request)
    return {"status": "ok"}


@router.get("/warehouses")
def list_raw_material_warehouses(
    limit: int = 200,
    _user: AdminUser = Depends(require_permission(RAW_MATERIAL_VIEW_PERMISSION)),
) -> list[dict]:
    return RawMaterialService().list_warehouses(limit=limit)


@router.get("/remains")
def list_raw_material_remains(
    articul: str | None = None,
    ware_id: int | None = None,
    ware_ids: str | None = None,
    cell: str | None = None,
    batch_no: str | None = None,
    quality_status: str | None = None,
    only_available: int | None = 1,
    limit: int = 500,
    _user: AdminUser = Depends(require_permission(RAW_MATERIAL_STOCK_VIEW_PERMISSION)),
) -> list[dict]:
    return RawMaterialService().list_remains(
        articul=articul,
        ware_id=ware_id,
        ware_ids=ware_ids,
        cell=cell,
        batch_no=batch_no,
        quality_status=quality_status,
        only_available=only_available,
        limit=limit,
    )
