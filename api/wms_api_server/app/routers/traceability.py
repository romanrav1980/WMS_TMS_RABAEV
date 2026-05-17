from fastapi import APIRouter, Depends, HTTPException

from ..auth import (
    EXTERNAL_OUTBOX_RETRY_PERMISSION,
    EXTERNAL_OUTBOX_VIEW_PERMISSION,
    TRACEABILITY_VIEW_PERMISSION,
    AdminUser,
    require_permission,
)
from ..schemas import ExternalOutboxRetryRequest
from ..services.traceability_service import TraceabilityService

router = APIRouter(tags=["traceability"])


@router.get("/api/trace/entities/{entity_type}/{entity_id}/forward")
def trace_forward(
    entity_type: str,
    entity_id: str,
    limit: int = 100,
    _user: AdminUser = Depends(require_permission(TRACEABILITY_VIEW_PERMISSION)),
) -> list[dict]:
    return TraceabilityService().list_edges(
        entity_type=entity_type,
        entity_id=entity_id,
        direction="forward",
        limit=limit,
    )


@router.get("/api/trace/entities/{entity_type}/{entity_id}/backward")
def trace_backward(
    entity_type: str,
    entity_id: str,
    limit: int = 100,
    _user: AdminUser = Depends(require_permission(TRACEABILITY_VIEW_PERMISSION)),
) -> list[dict]:
    return TraceabilityService().list_edges(
        entity_type=entity_type,
        entity_id=entity_id,
        direction="backward",
        limit=limit,
    )


@router.get("/api/admin/event-outbox")
def list_event_outbox(
    status: str | None = None,
    target_system: str | None = None,
    event_type: str | None = None,
    aggregate_type: str | None = None,
    aggregate_id: str | None = None,
    limit: int = 100,
    _user: AdminUser = Depends(require_permission(EXTERNAL_OUTBOX_VIEW_PERMISSION)),
) -> list[dict]:
    return TraceabilityService().list_outbox(
        status=status,
        target_system=target_system,
        event_type=event_type,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        limit=limit,
    )


@router.get("/api/admin/event-outbox/{event_outbox_id}")
def get_event_outbox(
    event_outbox_id: int,
    _user: AdminUser = Depends(require_permission(EXTERNAL_OUTBOX_VIEW_PERMISSION)),
) -> dict:
    event = TraceabilityService().get_outbox_event(event_outbox_id)
    if not event:
        raise HTTPException(status_code=404, detail="Outbox event not found.")
    return event


@router.post("/api/admin/event-outbox/{event_outbox_id}/retry")
def retry_event_outbox(
    event_outbox_id: int,
    request: ExternalOutboxRetryRequest,
    user: AdminUser = Depends(require_permission(EXTERNAL_OUTBOX_VIEW_PERMISSION)),
) -> dict:
    if (
        not request.dry_run
        and "*" not in user.permissions
        and EXTERNAL_OUTBOX_RETRY_PERMISSION not in user.permissions
    ):
        raise HTTPException(
            status_code=403,
            detail=f"Permission required: {EXTERNAL_OUTBOX_RETRY_PERMISSION}",
        )
    return TraceabilityService().retry_outbox_event(
        event_outbox_id=event_outbox_id,
        dry_run=request.dry_run,
        reason=request.reason,
    )


@router.get("/api/admin/adapter-requests")
def list_adapter_requests(
    event_outbox_id: int | None = None,
    system_code: str | None = None,
    status: str | None = None,
    business_key: str | None = None,
    limit: int = 100,
    _user: AdminUser = Depends(require_permission(EXTERNAL_OUTBOX_VIEW_PERMISSION)),
) -> list[dict]:
    return TraceabilityService().list_adapter_requests(
        event_outbox_id=event_outbox_id,
        system_code=system_code,
        status=status,
        business_key=business_key,
        limit=limit,
    )


@router.get("/api/admin/adapter-requests/{adapter_request_id}")
def get_adapter_request(
    adapter_request_id: int,
    _user: AdminUser = Depends(require_permission(EXTERNAL_OUTBOX_VIEW_PERMISSION)),
) -> dict:
    request = TraceabilityService().get_adapter_request(adapter_request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Adapter request not found.")
    return request
