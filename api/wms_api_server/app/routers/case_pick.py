from ..modules.resources.public import CaseReadPort, CaseReadError, case_read_service, assert_case_task_access
from ..modules.inventory.public import CaseCarrierReturnRequest, CaseCarrierCloseRequest
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
    resource_id: int | None = None, scope: str = "mine", status: str | None = None, limit: int = 100,
    user: AdminUser = Depends(require_permission(CASE_PICK_VIEW_PERMISSION)),
    service: CaseReadPort = Depends(case_read_service),
) -> list[dict]:
    try:
        return service.tasks(user.username, resource_id, scope, status, limit)
    except CaseReadError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc


@router.get("/tasks/{case_pick_task_id}")
def get_case_pick_task(
    case_pick_task_id: int,
    user: AdminUser = Depends(require_permission(CASE_PICK_VIEW_PERMISSION)),
    service: CaseReadPort = Depends(case_read_service),
) -> dict:
    try:
        return service.task(case_pick_task_id, user.username)
    except CaseReadError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc


@router.post("/tasks/{case_pick_task_id}/claim")
def claim_case_pick_task(
    case_pick_task_id: int,
    request: CasePickTaskActionRequest,
    user: AdminUser = Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION)),
) -> dict[str, int | str]:
    request.actor = user.username
    CasePickService().claim_task(case_pick_task_id, request)
    return {"case_pick_task_id": case_pick_task_id, "status": "ASSIGNED"}


@router.post("/tasks/{case_pick_task_id}/start")
def start_case_pick_task(
    case_pick_task_id: int,
    request: CasePickTaskActionRequest,
    user: AdminUser = Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION)),
) -> dict[str, int | str]:
    request.actor = user.username
    CasePickService().start_task(case_pick_task_id, request)
    return {"case_pick_task_id": case_pick_task_id, "status": "IN_PROGRESS"}


@router.post("/tasks/{case_pick_task_id}/transfer")
def transfer_case_pick_task(
    case_pick_task_id: int,
    request: CasePickTransferRequest,
    user: AdminUser = Depends(require_permission(CASE_PICK_MANAGE_PERMISSION)),
) -> dict[str, int | str]:
    request.actor = user.username
    CasePickService().transfer_task(case_pick_task_id, request)
    return {"case_pick_task_id": case_pick_task_id, "status": "TRANSFERRED"}


from pydantic import BaseModel, Field


class CaseCarrierMoveRequest(BaseModel):
    operation_id: str = Field(min_length=1, max_length=100)
    scan_container: str = Field(min_length=1, max_length=150)
    scanned_to_cell: str = Field(min_length=1, max_length=60)
    expected_content_version: int = Field(ge=0, strict=True)


@router.post("/tasks/{case_pick_task_id}/move-carrier")
def move_case_carrier(case_pick_task_id: int, request: CaseCarrierMoveRequest,
    user: AdminUser = Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION))) -> dict:
    from ..modules.inventory.public import build_case_carrier_move_service
    from ..modules.inventory.public import StockPostingError
    try:
        return build_case_carrier_move_service().execute(request.operation_id, user.username,
            case_pick_task_id, request.scan_container, request.scanned_to_cell, request.expected_content_version)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except StockPostingError as exc:
        uncertain = exc.code in {"RESULT_UNCERTAIN", "REQUEST_DEADLINE", "CONNECTION_UNUSABLE", "LOCK_RETRY_EXHAUSTED", "STOCK_RELEASE_NOT_ACTIVE"}
        raise HTTPException(503 if uncertain else 409, detail={"code": exc.code,
            "operation_id": exc.operation_id, "oracle_code": exc.oracle_code,
            "outcome_confirmed": not uncertain, "retry_same_operation_id": uncertain}) from exc


@router.get("/tasks/{case_pick_task_id}/lines/{line_id}/marking-policy")
def case_line_marking_policy(case_pick_task_id: int, line_id: int,
    user: AdminUser = Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION))) -> dict:
    from ..modules.inventory.public import build_case_task_services
    try:
        return build_case_task_services().marking_policy(case_pick_task_id, line_id, user.username, assert_case_task_access)
    except CaseReadError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc


@router.post("/tasks/{case_pick_task_id}/lines/{line_id}/confirm")
def confirm_case_pick_line(
    case_pick_task_id: int,
    line_id: int,
    request: CasePickLineConfirmRequest,
    user: AdminUser = Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION)),
) -> dict:
    request.actor = user.username
    result = CasePickService().confirm_line(case_pick_task_id, line_id, request)
    return {"case_pick_task_id": case_pick_task_id, "case_pick_line_id": line_id, **result}


@router.post("/tasks/{case_pick_task_id}/lines/{line_id}/short")
def create_case_pick_short(
    case_pick_task_id: int,
    line_id: int,
    request: CasePickLineShortRequest,
    user: AdminUser = Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION)),
) -> dict:
    request.actor = user.username
    try:
        result = CasePickService().short_line(case_pick_task_id, line_id, request)
    except CaseReadError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc
    except HTTPException as exc:
        detail = exc.detail if isinstance(exc.detail, dict) else {"message": str(exc.detail)}
        if exc.status_code == 422 or detail.get("code") == "CASE_SHORT_PICKED_FACT_MUST_BE_POSTED":
            raise HTTPException(exc.status_code, {**detail, "outcome_confirmed": True,
                "retry_same_operation_id": False, "offline_event_id": request.offline_event_id}) from exc
        raise
    return {"case_pick_task_id": case_pick_task_id, "case_pick_line_id": line_id, "offline_event_id": request.offline_event_id, **result}


@router.post("/tasks/{case_pick_task_id}/close-pallet")
def close_case_pick_task(
    case_pick_task_id: int,
    request: CaseCarrierCloseRequest,
    user: AdminUser = Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION)),
) -> dict:
    request.actor = user.username
    try:
        result = CasePickService().close_task(case_pick_task_id, request)
    except CaseReadError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc
    return {"case_pick_task_id": case_pick_task_id, **result, "operation_id": request.operation_id}


@router.get("/shorts")
def list_case_pick_shorts(
    status: str | None = None, limit: int = 200,
    user: AdminUser = Depends(require_permission(CASE_PICK_VIEW_PERMISSION)),
    service: CaseReadPort = Depends(case_read_service),
) -> list[dict]:
    try:
        return service.shorts(user.username, status, limit)
    except CaseReadError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc


@router.post("/shorts/{short_id}/approve")
def approve_case_pick_short(
    short_id: int,
    request: CasePickShortDecisionRequest,
    user: AdminUser = Depends(require_permission(CASE_PICK_SHORT_APPROVE_PERMISSION)),
) -> dict:
    request.actor = user.username
    return {"case_pick_short_id": short_id, **CasePickService().approve_short(short_id, request)}


@router.post("/shorts/{short_id}/reject")
def reject_case_pick_short(
    short_id: int,
    request: CasePickShortDecisionRequest,
    user: AdminUser = Depends(require_permission(CASE_PICK_SHORT_APPROVE_PERMISSION)),
) -> dict:
    request.actor = user.username
    try:
        return {"case_pick_short_id": short_id, **CasePickService().reject_short(short_id, request)}
    except CaseReadError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc


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
    request.updated_by = user.username
    pallet_type_id = CasePickService().upsert_pallet_type(request)
    return {"pallet_type_id": pallet_type_id}


class CaseShipmentBindRequest(BaseModel):
    pallet_identifier: str = Field(min_length=1, max_length=150)
    scan_container: str = Field(min_length=1, max_length=150)
    expected_content_version: int = Field(ge=0, strict=True)


@router.post("/tasks/{case_pick_task_id}/bind-shipment")
def bind_case_shipment(case_pick_task_id: int, request: CaseShipmentBindRequest,
    user: AdminUser = Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION))) -> dict:
    from ..modules.inventory.public import build_case_task_services
    try:
        return build_case_task_services().bind_shipment(case_pick_task_id,
            request.pallet_identifier, request.scan_container, request.expected_content_version, user.username)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc




@router.post("/tasks/{case_pick_task_id}/return-carrier")
def return_case_carrier(case_pick_task_id:int,request:CaseCarrierReturnRequest,
    user:AdminUser=Depends(require_permission(CASE_PICK_MANAGE_PERMISSION))) -> dict:
    from ..modules.inventory.public import return_existing_case_carrier
    return return_existing_case_carrier(case_pick_task_id,request,user.username)
