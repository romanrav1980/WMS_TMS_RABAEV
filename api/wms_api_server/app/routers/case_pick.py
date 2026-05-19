from fastapi import APIRouter, Depends, HTTPException

from ..auth import (
    AdminUser,
    CASE_PICK_EXECUTE_PERMISSION,
    CASE_PICK_MANAGE_PERMISSION,
    CASE_PICK_SHORT_APPROVE_PERMISSION,
    CASE_PICK_VIEW_PERMISSION,
    require_permission,
)
from ..schemas import (
    CasePickLineConfirmRequest,
    CasePickLineShortRequest,
    CasePickShortDecisionRequest,
    CasePickTaskActionRequest,
    CasePickTransferRequest,
    PalletTypeUpsertRequest,
)
from ..services.case_pick_service import CasePickService

router = APIRouter(prefix="/api/case-pick", tags=["case-pick"])


@router.post("/waves/{pick_wave_id}/ensure")
def ensure_wave_case_pick_tasks(
    pick_wave_id: int,
    user: AdminUser = Depends(require_permission(CASE_PICK_MANAGE_PERMISSION)),
) -> dict[str, int]:
    created_count = CasePickService().ensure_wave_case_pick_tasks(pick_wave_id, user.username)
    return {"pick_wave_id": pick_wave_id, "created_count": created_count}


@router.get("/tasks")
def list_case_pick_tasks(
    resource_id: int | None = None,
    scope: str = "mine",
    status: str | None = None,
    limit: int = 100,
    _user: AdminUser = Depends(require_permission(CASE_PICK_VIEW_PERMISSION)),
) -> list[dict]:
    return CasePickService().list_tasks(resource_id=resource_id, scope=scope, status=status, limit=limit)


@router.get("/tasks/{case_pick_task_id}")
def get_case_pick_task(
    case_pick_task_id: int,
    _user: AdminUser = Depends(require_permission(CASE_PICK_VIEW_PERMISSION)),
) -> dict:
    task = CasePickService().get_task(case_pick_task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Case-pick task not found.")
    return task


@router.post("/tasks/{case_pick_task_id}/claim")
def claim_case_pick_task(
    case_pick_task_id: int,
    request: CasePickTaskActionRequest,
    user: AdminUser = Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION)),
) -> dict[str, int | str]:
    request.actor = request.actor or user.username
    CasePickService().claim_task(case_pick_task_id, request)
    return {"case_pick_task_id": case_pick_task_id, "status": "ASSIGNED"}


@router.post("/tasks/{case_pick_task_id}/start")
def start_case_pick_task(
    case_pick_task_id: int,
    request: CasePickTaskActionRequest,
    user: AdminUser = Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION)),
) -> dict[str, int | str]:
    request.actor = request.actor or user.username
    CasePickService().start_task(case_pick_task_id, request)
    return {"case_pick_task_id": case_pick_task_id, "status": "IN_PROGRESS"}


@router.post("/tasks/{case_pick_task_id}/transfer")
def transfer_case_pick_task(
    case_pick_task_id: int,
    request: CasePickTransferRequest,
    user: AdminUser = Depends(require_permission(CASE_PICK_MANAGE_PERMISSION)),
) -> dict[str, int | str]:
    request.actor = request.actor or user.username
    CasePickService().transfer_task(case_pick_task_id, request)
    return {"case_pick_task_id": case_pick_task_id, "status": "TRANSFERRED"}


@router.post("/tasks/{case_pick_task_id}/lines/{line_id}/confirm")
def confirm_case_pick_line(
    case_pick_task_id: int,
    line_id: int,
    request: CasePickLineConfirmRequest,
    user: AdminUser = Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION)),
) -> dict:
    request.actor = request.actor or user.username
    result = CasePickService().confirm_line(case_pick_task_id, line_id, request)
    return {"case_pick_task_id": case_pick_task_id, "case_pick_line_id": line_id, **result}


@router.post("/tasks/{case_pick_task_id}/lines/{line_id}/short")
def create_case_pick_short(
    case_pick_task_id: int,
    line_id: int,
    request: CasePickLineShortRequest,
    user: AdminUser = Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION)),
) -> dict:
    request.actor = request.actor or user.username
    result = CasePickService().short_line(case_pick_task_id, line_id, request)
    return {"case_pick_task_id": case_pick_task_id, "case_pick_line_id": line_id, **result}


@router.post("/tasks/{case_pick_task_id}/close-pallet")
def close_case_pick_task(
    case_pick_task_id: int,
    request: CasePickTaskActionRequest,
    user: AdminUser = Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION)),
) -> dict:
    request.actor = request.actor or user.username
    result = CasePickService().close_task(case_pick_task_id, request)
    return {"case_pick_task_id": case_pick_task_id, **result}


@router.get("/shorts")
def list_case_pick_shorts(
    status: str | None = None,
    limit: int = 200,
    _user: AdminUser = Depends(require_permission(CASE_PICK_VIEW_PERMISSION)),
) -> list[dict]:
    return CasePickService().list_shorts(status=status, limit=limit)


@router.post("/shorts/{short_id}/approve")
def approve_case_pick_short(
    short_id: int,
    request: CasePickShortDecisionRequest,
    user: AdminUser = Depends(require_permission(CASE_PICK_SHORT_APPROVE_PERMISSION)),
) -> dict:
    request.actor = request.actor or user.username
    return {"case_pick_short_id": short_id, **CasePickService().approve_short(short_id, request)}


@router.post("/shorts/{short_id}/reject")
def reject_case_pick_short(
    short_id: int,
    request: CasePickShortDecisionRequest,
    user: AdminUser = Depends(require_permission(CASE_PICK_SHORT_APPROVE_PERMISSION)),
) -> dict:
    request.actor = request.actor or user.username
    return {"case_pick_short_id": short_id, **CasePickService().reject_short(short_id, request)}


@router.get("/pallet-types")
def list_pallet_types(
    active_only: int | None = None,
    _user: AdminUser = Depends(require_permission(CASE_PICK_VIEW_PERMISSION)),
) -> list[dict]:
    return CasePickService().list_pallet_types(active_only=active_only)


@router.post("/pallet-types")
def upsert_pallet_type(
    request: PalletTypeUpsertRequest,
    user: AdminUser = Depends(require_permission(CASE_PICK_MANAGE_PERMISSION)),
) -> dict[str, int]:
    request.updated_by = request.updated_by or user.username
    pallet_type_id = CasePickService().upsert_pallet_type(request)
    return {"pallet_type_id": pallet_type_id}
