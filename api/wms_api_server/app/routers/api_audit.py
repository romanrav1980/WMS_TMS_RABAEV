from fastapi import APIRouter, Depends, HTTPException

from ..auth import API_AUDIT_REPLAY_PERMISSION, API_AUDIT_VIEW_PERMISSION, AdminUser, require_permission
from ..schemas import ApiReplayRequest
from ..services.api_audit_service import ApiAuditService

router = APIRouter(prefix="/api/admin/api-calls", tags=["api-audit"])


@router.get("")
def list_api_calls(
    from_call_id: int | None = None,
    to_call_id: int | None = None,
    from_at: str | None = None,
    to_at: str | None = None,
    method: str | None = None,
    path_like: str | None = None,
    status: str | None = None,
    replayable: int | None = None,
    limit: int = 100,
    offset: int = 0,
    _user: AdminUser = Depends(require_permission(API_AUDIT_VIEW_PERMISSION)),
) -> list[dict]:
    return ApiAuditService().list_calls(
        from_call_id=from_call_id,
        to_call_id=to_call_id,
        from_at=from_at,
        to_at=to_at,
        method=method,
        path_like=path_like,
        status=status,
        replayable=replayable,
        limit=limit,
        offset=offset,
    )


@router.get("/{api_call_id}")
def get_api_call(
    api_call_id: int,
    _user: AdminUser = Depends(require_permission(API_AUDIT_VIEW_PERMISSION)),
) -> dict:
    call = ApiAuditService().get_call(api_call_id)
    if not call:
        raise HTTPException(status_code=404, detail="API call log entry not found.")
    return call


@router.post("/replay")
def replay_api_calls(
    request: ApiReplayRequest,
    user: AdminUser = Depends(require_permission(API_AUDIT_VIEW_PERMISSION)),
) -> dict:
    if not request.dry_run and "*" not in user.permissions and API_AUDIT_REPLAY_PERMISSION not in user.permissions:
        raise HTTPException(status_code=403, detail=f"Permission required: {API_AUDIT_REPLAY_PERMISSION}")
    payload = request.model_dump() if hasattr(request, "model_dump") else request.dict()
    return ApiAuditService().replay_calls(payload)
