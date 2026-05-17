from fastapi import APIRouter, Depends

from ..auth import (
    AdminUser,
    FINISHED_GOODS_BATCH_VIEW_PERMISSION,
    FINISHED_GOODS_EDIT_PERMISSION,
    FINISHED_GOODS_STOCK_VIEW_PERMISSION,
    FINISHED_GOODS_VIEW_PERMISSION,
    require_permission,
)
from ..schemas import FinishedGoodsSkuSettingsUpdateRequest
from ..services.finished_goods_service import FinishedGoodsService

router = APIRouter(prefix="/api/finished-goods", tags=["finished-goods"])


@router.get("/skus")
def list_finished_goods_skus(
    search: str | None = None,
    only_active: int | None = 1,
    only_with_stock: int | None = None,
    limit: int = 200,
    _user: AdminUser = Depends(require_permission(FINISHED_GOODS_VIEW_PERMISSION)),
) -> list[dict]:
    return FinishedGoodsService().list_skus(
        search=search,
        only_active=only_active,
        only_with_stock=only_with_stock,
        limit=limit,
    )


@router.patch("/skus/{articul}")
def update_finished_goods_sku(
    articul: str,
    request: FinishedGoodsSkuSettingsUpdateRequest,
    _user: AdminUser = Depends(require_permission(FINISHED_GOODS_EDIT_PERMISSION)),
) -> dict[str, str]:
    FinishedGoodsService().update_sku_settings(articul, request)
    return {"status": "ok"}


@router.get("/warehouses")
def list_finished_goods_warehouses(
    limit: int = 200,
    _user: AdminUser = Depends(require_permission(FINISHED_GOODS_VIEW_PERMISSION)),
) -> list[dict]:
    return FinishedGoodsService().list_warehouses(limit=limit)


@router.get("/batches")
def list_finished_goods_batches(
    prod_batch_id: int | None = None,
    articul: str | None = None,
    batch_no: str | None = None,
    quality_status: str | None = None,
    limit: int = 200,
    _user: AdminUser = Depends(require_permission(FINISHED_GOODS_BATCH_VIEW_PERMISSION)),
) -> list[dict]:
    return FinishedGoodsService().list_batches(
        prod_batch_id=prod_batch_id,
        articul=articul,
        batch_no=batch_no,
        quality_status=quality_status,
        limit=limit,
    )


@router.get("/remains")
def list_finished_goods_remains(
    prod_batch_id: int | None = None,
    articul: str | None = None,
    ware_id: int | None = None,
    ware_ids: str | None = None,
    prod_batch_no: str | None = None,
    cell: str | None = None,
    quality_status: str | None = None,
    only_available: int | None = 1,
    limit: int = 500,
    _user: AdminUser = Depends(require_permission(FINISHED_GOODS_STOCK_VIEW_PERMISSION)),
) -> list[dict]:
    return FinishedGoodsService().list_remains(
        prod_batch_id=prod_batch_id,
        articul=articul,
        ware_id=ware_id,
        ware_ids=ware_ids,
        prod_batch_no=prod_batch_no,
        cell=cell,
        quality_status=quality_status,
        only_available=only_available,
        limit=limit,
    )
