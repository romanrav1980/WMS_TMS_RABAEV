from fastapi import APIRouter, Depends, HTTPException

from ..auth import (
    AdminUser,
    PICK_PLAN_CANCEL_PERMISSION,
    PICK_PLAN_CREATE_PERMISSION,
    PICK_PLAN_VIEW_PERMISSION,
    PICK_RESERVATION_VIEW_PERMISSION,
    PICK_SHORTAGE_VIEW_PERMISSION,
    require_permission,
)
from ..schemas import PickingPlanCancelRequest, PickingPlanCreateRequest
from ..services.picking_service import PickingService

router = APIRouter(prefix="/api/picking", tags=["picking"])


@router.post("/plans")
def create_picking_plan(
    request: PickingPlanCreateRequest,
    user: AdminUser = Depends(require_permission(PICK_PLAN_CREATE_PERMISSION)),
) -> dict[str, int]:
    request.created_by = request.created_by or user.username
    pick_plan_id = PickingService().create_plan(request)
    return {"pick_plan_id": pick_plan_id}


@router.get("/plans")
def list_picking_plans(
    status: str | None = None,
    customer_order_id: int | None = None,
    customer_id: int | None = None,
    limit: int = 100,
    _user: AdminUser = Depends(require_permission(PICK_PLAN_VIEW_PERMISSION)),
) -> list[dict]:
    return PickingService().list_plans(
        status=status,
        customer_order_id=customer_order_id,
        customer_id=customer_id,
        limit=limit,
    )


@router.get("/plans/{pick_plan_id}")
def get_picking_plan(
    pick_plan_id: int,
    _user: AdminUser = Depends(require_permission(PICK_PLAN_VIEW_PERMISSION)),
) -> dict:
    plan = PickingService().get_plan(pick_plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Picking plan not found.")
    return plan


@router.post("/plans/{pick_plan_id}/cancel")
def cancel_picking_plan(
    pick_plan_id: int,
    request: PickingPlanCancelRequest,
    user: AdminUser = Depends(require_permission(PICK_PLAN_CANCEL_PERMISSION)),
) -> dict[str, str | int]:
    PickingService().cancel_plan(pick_plan_id, updated_by=request.updated_by or user.username)
    return {"pick_plan_id": pick_plan_id, "status": "CANCELLED"}


@router.get("/reservations")
def list_picking_reservations(
    pick_plan_id: int | None = None,
    status: str | None = None,
    customer_order_id: int | None = None,
    pallet_uid: str | None = None,
    articul: str | None = None,
    limit: int = 200,
    _user: AdminUser = Depends(require_permission(PICK_RESERVATION_VIEW_PERMISSION)),
) -> list[dict]:
    return PickingService().list_reservations(
        pick_plan_id=pick_plan_id,
        status=status,
        customer_order_id=customer_order_id,
        pallet_uid=pallet_uid,
        articul=articul,
        limit=limit,
    )


@router.get("/shortages")
def list_picking_shortages(
    pick_plan_id: int | None = None,
    limit: int = 200,
    _user: AdminUser = Depends(require_permission(PICK_SHORTAGE_VIEW_PERMISSION)),
) -> list[dict]:
    return PickingService().list_shortages(pick_plan_id=pick_plan_id, limit=limit)


@router.get("/plans/{pick_plan_id}/shortages")
def list_picking_plan_shortages(
    pick_plan_id: int,
    limit: int = 200,
    _user: AdminUser = Depends(require_permission(PICK_SHORTAGE_VIEW_PERMISSION)),
) -> list[dict]:
    return PickingService().list_shortages(pick_plan_id=pick_plan_id, limit=limit)
