from fastapi import APIRouter, Depends, HTTPException

from ..auth import (
    AdminUser,
    QUALITY_BATCH_EDIT_PERMISSION,
    QUALITY_BATCH_VIEW_PERMISSION,
    require_permission,
)
from ..schemas import ProductShipmentSettingsUpdateRequest
from ..services.product_service import ProductService

router = APIRouter(prefix="/api/admin/product-shipment-settings", tags=["product-shipment-settings"])


@router.get("")
def list_product_shipment_settings(
    articul_like: str | None = None,
    only_with_aging: int | None = None,
    limit: int = 200,
    _user: AdminUser = Depends(require_permission(QUALITY_BATCH_VIEW_PERMISSION)),
) -> list[dict]:
    return ProductService().list_shipment_settings(
        articul_like=articul_like,
        only_with_aging=only_with_aging,
        limit=limit,
    )


@router.patch("/{articul}")
def update_product_shipment_settings(
    articul: str,
    request: ProductShipmentSettingsUpdateRequest,
    _user: AdminUser = Depends(require_permission(QUALITY_BATCH_EDIT_PERMISSION)),
) -> dict[str, str]:
    updated = ProductService().update_shipment_settings(articul, request)
    if updated == 0:
        raise HTTPException(status_code=404, detail="Product articul not found.")
    return {"status": "ok"}
