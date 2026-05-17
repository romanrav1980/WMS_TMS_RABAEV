from fastapi import APIRouter, Depends, HTTPException

from ..auth import (
    AdminUser,
    MES_PRODUCTION_COMPLETE_PERMISSION,
    MES_PRODUCTION_EDIT_PERMISSION,
    MES_PRODUCTION_VIEW_PERMISSION,
    MES_WMS_BRIDGE_APPLY_PERMISSION,
    require_permission,
)
from ..schemas import (
    IdResponse,
    MesApplyWmsRequest,
    MesCompleteOrderRequest,
    MesProductionOrderCreateRequest,
    MesRawIssueRequest,
    MesRetryMovementRequest,
)
from ..services.mes_service import MesService

router = APIRouter(prefix="/api/mes", tags=["mes"])


@router.get("/production-orders")
def list_production_orders(
    status: str | None = None,
    target_articul: str | None = None,
    limit: int = 100,
    _user: AdminUser = Depends(require_permission(MES_PRODUCTION_VIEW_PERMISSION)),
) -> list[dict]:
    return MesService().list_orders(status=status, target_articul=target_articul, limit=limit)


@router.post("/production-orders", response_model=IdResponse)
def create_production_order(
    request: MesProductionOrderCreateRequest,
    _user: AdminUser = Depends(require_permission(MES_PRODUCTION_EDIT_PERMISSION)),
) -> IdResponse:
    return IdResponse(id=MesService().create_order(request))


@router.get("/production-orders/{production_order_id}")
def get_production_order(
    production_order_id: int,
    _user: AdminUser = Depends(require_permission(MES_PRODUCTION_VIEW_PERMISSION)),
) -> dict:
    order = MesService().get_order(production_order_id)
    if not order:
        raise HTTPException(status_code=404, detail="MES production order not found.")
    return order


@router.post("/production-orders/{production_order_id}/issue-raw", response_model=IdResponse)
def issue_raw(
    production_order_id: int,
    request: MesRawIssueRequest,
    _user: AdminUser = Depends(require_permission(MES_PRODUCTION_EDIT_PERMISSION)),
) -> IdResponse:
    return IdResponse(id=MesService().issue_raw(production_order_id, request))


@router.post("/production-orders/{production_order_id}/complete", response_model=IdResponse)
def complete_order(
    production_order_id: int,
    request: MesCompleteOrderRequest,
    _user: AdminUser = Depends(require_permission(MES_PRODUCTION_COMPLETE_PERMISSION)),
) -> IdResponse:
    return IdResponse(id=MesService().complete_order(production_order_id, request))


@router.post("/production-orders/{production_order_id}/apply-wms")
def apply_wms(
    production_order_id: int,
    request: MesApplyWmsRequest,
    _user: AdminUser = Depends(require_permission(MES_WMS_BRIDGE_APPLY_PERMISSION)),
) -> dict[str, str]:
    MesService().apply_wms(production_order_id, request)
    return {"status": "ok"}


@router.get("/production-orders/{production_order_id}/genealogy")
def get_genealogy(
    production_order_id: int,
    _user: AdminUser = Depends(require_permission(MES_PRODUCTION_VIEW_PERMISSION)),
) -> dict:
    return MesService().get_genealogy(production_order_id)


@router.get("/movements")
def list_movements(
    production_order_id: int | None = None,
    status: str | None = None,
    movement_type: str | None = None,
    limit: int = 100,
    _user: AdminUser = Depends(require_permission(MES_PRODUCTION_VIEW_PERMISSION)),
) -> list[dict]:
    return MesService().list_movements(
        production_order_id=production_order_id,
        status=status,
        movement_type=movement_type,
        limit=limit,
    )


@router.post("/movements/{movement_id}/retry")
def retry_movement(
    movement_id: int,
    request: MesRetryMovementRequest,
    _user: AdminUser = Depends(require_permission(MES_WMS_BRIDGE_APPLY_PERMISSION)),
) -> dict[str, str]:
    MesService().retry_movement(movement_id, request)
    return {"status": "ok"}
