from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path

from ..auth import (
    AdminUser,
    PICK_PLAN_CANCEL_PERMISSION,
    PICK_PLAN_CREATE_PERMISSION,
    PICK_PLAN_VIEW_PERMISSION,
    PICK_RESERVATION_VIEW_PERMISSION,
    PICK_SHORTAGE_VIEW_PERMISSION,
    PICK_TOPOLOGY_EDIT_PERMISSION,
    PICK_TOPOLOGY_VIEW_PERMISSION,
    PICK_WAVE_AUDIT_VIEW_PERMISSION,
    PICK_WAVE_CALCULATE_PERMISSION,
    PICK_WAVE_CANCEL_PERMISSION,
    PICK_WAVE_CREATE_PERMISSION,
    PICK_WAVE_LAUNCH_PERMISSION,
    PICK_WAVE_RELEASE_RESERVES_PERMISSION,
    PICK_WAVE_VIEW_PERMISSION,
    require_permission,
)
from ..schemas import (
    ArticulReplenishmentRuleUpsertRequest,
    PickFaceArticulUpsertRequest,
    PickFaceUpsertRequest,
    PickRouteConsumptionMaterializeRequest,
    PickRouteCellUpsertRequest,
    PickRouteUpsertRequest,
    PickTaskCompleteRequest,
    PickWaveActionRequest,
    PickWaveAddPlanRequest,
    PickWaveCreateRequest,
    PickWaveStagingReleaseRequest,
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


@router.get("/waves")
def list_pick_waves(
    status: str | None = None,
    ware_id: int | None = None,
    customer_id: int | None = None,
    limit: int = 100,
    _user: AdminUser = Depends(require_permission(PICK_WAVE_VIEW_PERMISSION)),
) -> list[dict]:
    return PickingService().list_waves(
        status=status,
        ware_id=ware_id,
        customer_id=customer_id,
        limit=limit,
    )


@router.post("/waves")
def create_pick_wave(
    request: PickWaveCreateRequest,
    user: AdminUser = Depends(require_permission(PICK_WAVE_CREATE_PERMISSION)),
) -> dict[str, int]:
    request.created_by = request.created_by or user.username
    pick_wave_id = PickingService().create_wave(request)
    return {"pick_wave_id": pick_wave_id}


@router.get("/waves/candidates")
def list_pick_wave_candidates(
    ware_id: int | None = None,
    route_id: int | None = None,
    dock_id: int | None = None,
    shipment_from: str | None = None,
    shipment_to: str | None = None,
    limit: int = 100,
    _user: AdminUser = Depends(require_permission(PICK_WAVE_VIEW_PERMISSION)),
) -> list[dict]:
    return PickingService().list_wave_candidates(
        ware_id=ware_id,
        route_id=route_id,
        dock_id=dock_id,
        shipment_from=shipment_from,
        shipment_to=shipment_to,
        limit=limit,
    )


@router.get("/waves/{pick_wave_id}")
def get_pick_wave(
    pick_wave_id: int,
    _user: AdminUser = Depends(require_permission(PICK_WAVE_VIEW_PERMISSION)),
) -> dict:
    wave = PickingService().get_wave(pick_wave_id)
    if wave is None:
        raise HTTPException(status_code=404, detail="Pick wave not found.")
    return wave


@router.get("/waves/{pick_wave_id}/readiness")
def get_pick_wave_readiness(
    pick_wave_id: int,
    _user: AdminUser = Depends(require_permission(PICK_WAVE_VIEW_PERMISSION)),
) -> dict:
    readiness = PickingService().get_wave_readiness(pick_wave_id)
    if readiness is None:
        raise HTTPException(status_code=404, detail="Pick wave not found.")
    return readiness


@router.post("/waves/{pick_wave_id}/plans")
def add_pick_wave_plan(
    pick_wave_id: int,
    request: PickWaveAddPlanRequest,
    user: AdminUser = Depends(require_permission(PICK_WAVE_CREATE_PERMISSION)),
) -> dict[str, str | int]:
    request.created_by = request.created_by or user.username
    PickingService().add_wave_plan(pick_wave_id, request)
    return {"pick_wave_id": pick_wave_id, "pick_plan_id": request.pick_plan_id, "status": "ADDED"}


@router.post("/waves/{pick_wave_id}/calculate")
def calculate_pick_wave(
    pick_wave_id: int,
    request: PickWaveActionRequest,
    user: AdminUser = Depends(require_permission(PICK_WAVE_CALCULATE_PERMISSION)),
) -> dict[str, str | int]:
    request.updated_by = request.updated_by or user.username
    PickingService().preview_wave(pick_wave_id, request)
    return {"pick_wave_id": pick_wave_id, "status": "PREVIEW"}


@router.post("/waves/{pick_wave_id}/launch")
def launch_pick_wave(
    pick_wave_id: int,
    request: PickWaveActionRequest,
    user: AdminUser = Depends(require_permission(PICK_WAVE_LAUNCH_PERMISSION)),
) -> dict[str, str | int]:
    request.updated_by = request.updated_by or user.username
    PickingService().launch_wave(pick_wave_id, request)
    return {"pick_wave_id": pick_wave_id, "status": "LAUNCHED"}


@router.post("/waves/{pick_wave_id}/cancel")
def cancel_pick_wave(
    pick_wave_id: int,
    request: PickWaveActionRequest,
    user: AdminUser = Depends(require_permission(PICK_WAVE_CANCEL_PERMISSION)),
) -> dict[str, str | int]:
    request.updated_by = request.updated_by or user.username
    PickingService().cancel_wave(pick_wave_id, request)
    return {"pick_wave_id": pick_wave_id, "status": "CANCELLED"}


@router.post("/waves/{pick_wave_id}/release-reservations")
def release_pick_wave_reservations(
    pick_wave_id: int,
    request: PickWaveActionRequest,
    user: AdminUser = Depends(require_permission(PICK_WAVE_RELEASE_RESERVES_PERMISSION)),
) -> dict[str, str | int]:
    request.updated_by = request.updated_by or user.username
    PickingService().release_wave_reservations(pick_wave_id, request)
    return {"pick_wave_id": pick_wave_id, "status": "PREVIEW"}


@router.post("/waves/{pick_wave_id}/replenishment/minimax-check")
def release_pick_wave_minimax_replenishment(
    pick_wave_id: int,
    request: PickWaveActionRequest,
    user: AdminUser = Depends(require_permission(PICK_WAVE_LAUNCH_PERMISSION)),
) -> dict[str, str | int]:
    request.updated_by = request.updated_by or user.username
    released_count = PickingService().release_minimax_replenishment(pick_wave_id, request)
    return {"pick_wave_id": pick_wave_id, "status": "CHECKED", "released_count": released_count}


@router.post("/waves/{pick_wave_id}/staging/release")
def release_pick_wave_staging(
    pick_wave_id: int,
    request: PickWaveStagingReleaseRequest,
    user: AdminUser = Depends(require_permission(PICK_WAVE_LAUNCH_PERMISSION)),
) -> dict[str, str | int]:
    request.updated_by = request.updated_by or user.username
    released_count = PickingService().release_wave_staging(pick_wave_id, request)
    return {"pick_wave_id": pick_wave_id, "status": "RELEASED", "released_count": released_count}


@router.get("/waves/{pick_wave_id}/reservations")
def list_pick_wave_reservations(
    pick_wave_id: int,
    limit: int = 200,
    _user: AdminUser = Depends(require_permission(PICK_WAVE_VIEW_PERMISSION)),
) -> list[dict]:
    return PickingService().list_wave_reservations(pick_wave_id, limit=limit)


@router.get("/waves/{pick_wave_id}/replenishment-tasks")
def list_pick_wave_replenishment_tasks(
    pick_wave_id: int,
    limit: int = 200,
    _user: AdminUser = Depends(require_permission(PICK_WAVE_VIEW_PERMISSION)),
) -> list[dict]:
    return PickingService().list_wave_replenishment_tasks(pick_wave_id, limit=limit)


@router.get("/waves/{pick_wave_id}/tasks")
def list_pick_wave_tasks(
    pick_wave_id: int,
    limit: int = 200,
    _user: AdminUser = Depends(require_permission(PICK_WAVE_VIEW_PERMISSION)),
) -> list[dict]:
    return PickingService().list_wave_tasks(pick_wave_id, limit=limit)


@router.post("/waves/{pick_wave_id}/tasks/{pick_task_id}/complete")
def complete_pick_wave_task(
    pick_wave_id: int,
    pick_task_id: int,
    request: PickTaskCompleteRequest,
    user: AdminUser = Depends(require_permission(PICK_WAVE_LAUNCH_PERMISSION)),
) -> dict[str, str | int | float]:
    request.completed_by = request.completed_by or user.username
    return PickingService().complete_wave_pick_task(pick_wave_id, pick_task_id, request)


@router.get("/waves/{pick_wave_id}/audit")
def list_pick_wave_audit(
    pick_wave_id: int,
    limit: int = 200,
    _user: AdminUser = Depends(require_permission(PICK_WAVE_AUDIT_VIEW_PERMISSION)),
) -> list[dict]:
    return PickingService().list_wave_audit(pick_wave_id, limit=limit)


@router.get("/warehouses/{ware_id}/route-consumption-readiness")
def get_route_consumption_readiness(
    ware_id: Annotated[int, Path(gt=0)],
    _user: AdminUser = Depends(require_permission(PICK_TOPOLOGY_VIEW_PERMISSION)),
) -> dict:
    return PickingService().get_route_consumption_readiness(ware_id)


@router.post("/warehouses/{ware_id}/route-consumption/materialize")
def materialize_route_consumption(
    ware_id: Annotated[int, Path(gt=0)],
    request: PickRouteConsumptionMaterializeRequest,
    user: AdminUser = Depends(require_permission(PICK_TOPOLOGY_EDIT_PERMISSION)),
) -> dict:
    request.updated_by = request.updated_by or user.username
    return PickingService().materialize_route_consumption(ware_id, request)


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


@router.get("/articul-replenishment-rules")
def list_articul_replenishment_rules(
    articul: str | None = None,
    active_only: int | None = None,
    _user: AdminUser = Depends(require_permission(PICK_TOPOLOGY_VIEW_PERMISSION)),
) -> list[dict]:
    return PickingService().list_articul_replenishment_rules(
        articul=articul,
        active_only=active_only,
    )


@router.post("/articul-replenishment-rules")
def upsert_articul_replenishment_rule(
    request: ArticulReplenishmentRuleUpsertRequest,
    user: AdminUser = Depends(require_permission(PICK_TOPOLOGY_EDIT_PERMISSION)),
) -> dict[str, int]:
    request.updated_by = request.updated_by or user.username
    articul_replenish_rule_id = PickingService().upsert_articul_replenishment_rule(request)
    return {"articul_replenish_rule_id": articul_replenish_rule_id}
