from fastapi import APIRouter, Depends, HTTPException

from ..auth import (
    AdminUser,
    PICK_PLAN_CANCEL_PERMISSION,
    PICK_PLAN_CREATE_PERMISSION,
    PICK_PLAN_VIEW_PERMISSION,
    PICK_RESERVATION_VIEW_PERMISSION,
    PICK_SHORTAGE_VIEW_PERMISSION,
    PICK_TOPOLOGY_EDIT_PERMISSION,
    PICK_TOPOLOGY_VIEW_PERMISSION,
    require_permission,
)
from ..schemas import (
    PickFaceArticulUpsertRequest,
    PickFaceUpsertRequest,
    PickRouteCellUpsertRequest,
    PickRouteUpsertRequest,
    PickingPlanCancelRequest,
    PickingPlanCreateRequest,
)
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


@router.get("/routes")
def list_pick_routes(
    ware_id: int | None = None,
    active_only: int | None = None,
    _user: AdminUser = Depends(require_permission(PICK_TOPOLOGY_VIEW_PERMISSION)),
) -> list[dict]:
    return PickingService().list_routes(ware_id=ware_id, active_only=active_only)


@router.post("/routes")
def upsert_pick_route(
    request: PickRouteUpsertRequest,
    user: AdminUser = Depends(require_permission(PICK_TOPOLOGY_EDIT_PERMISSION)),
) -> dict[str, int]:
    request.updated_by = request.updated_by or user.username
    pick_route_id = PickingService().upsert_route(request)
    return {"pick_route_id": pick_route_id}


@router.get("/route-cells")
def list_pick_route_cells(
    pick_route_id: int | None = None,
    ware_id: int | None = None,
    active_only: int | None = None,
    _user: AdminUser = Depends(require_permission(PICK_TOPOLOGY_VIEW_PERMISSION)),
) -> list[dict]:
    return PickingService().list_route_cells(
        pick_route_id=pick_route_id,
        ware_id=ware_id,
        active_only=active_only,
    )


@router.post("/route-cells")
def upsert_pick_route_cell(
    request: PickRouteCellUpsertRequest,
    user: AdminUser = Depends(require_permission(PICK_TOPOLOGY_EDIT_PERMISSION)),
) -> dict[str, int]:
    request.updated_by = request.updated_by or user.username
    pick_route_cell_id = PickingService().upsert_route_cell(request)
    return {"pick_route_cell_id": pick_route_cell_id}


@router.get("/pick-faces")
def list_pick_faces(
    ware_id: int | None = None,
    articul: str | None = None,
    active_only: int | None = None,
    _user: AdminUser = Depends(require_permission(PICK_TOPOLOGY_VIEW_PERMISSION)),
) -> list[dict]:
    return PickingService().list_pick_faces(
        ware_id=ware_id,
        articul=articul,
        active_only=active_only,
    )


@router.post("/pick-faces")
def upsert_pick_face(
    request: PickFaceUpsertRequest,
    user: AdminUser = Depends(require_permission(PICK_TOPOLOGY_EDIT_PERMISSION)),
) -> dict[str, int]:
    request.updated_by = request.updated_by or user.username
    pick_face_id = PickingService().upsert_pick_face(request)
    return {"pick_face_id": pick_face_id}


@router.get("/pick-faces/{pick_face_id}/articuls")
def list_pick_face_articuls(
    pick_face_id: int,
    _user: AdminUser = Depends(require_permission(PICK_TOPOLOGY_VIEW_PERMISSION)),
) -> list[dict]:
    return PickingService().list_pick_face_articuls(pick_face_id)


@router.post("/pick-faces/{pick_face_id}/articuls")
def assign_pick_face_articul(
    pick_face_id: int,
    request: PickFaceArticulUpsertRequest,
    user: AdminUser = Depends(require_permission(PICK_TOPOLOGY_EDIT_PERMISSION)),
) -> dict[str, int]:
    request.pick_face_id = pick_face_id
    request.updated_by = request.updated_by or user.username
    pick_face_articul_id = PickingService().assign_pick_face_articul(request)
    return {"pick_face_articul_id": pick_face_articul_id}
