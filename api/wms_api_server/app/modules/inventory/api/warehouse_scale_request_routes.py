"""Identity-only operator boundary and separately authenticated device sender."""
from typing import Any, Literal
from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query
from ...platform.public import AdminUser, get_current_user, require_permission
from ..contracts_warehouse_scale import WarehouseScaleError
from ..contracts_warehouse_scale_requests import (
    WarehouseWeighRequest, WarehouseWeighClaim, WarehouseWeighZero, WarehouseWeighRequestsPort, warehouse_weigh_requests_service,
)

router = APIRouter(prefix="/api/inventory/warehouse-scales", tags=["warehouse-scale-requests"])


def failure(exc: WarehouseScaleError, request_id: str | None = None) -> HTTPException:
    conflict = "PAYLOAD_CONFLICT" in str(exc)
    return HTTPException(exc.status, {"code": exc.code, "message": str(exc), "request_id": request_id,
        "outcome_confirmed": exc.status < 500 and exc.status not in (401, 403) and not conflict,
        "retry_same_request": exc.status >= 500, "read_before_retry": conflict or exc.status >= 500})


@router.post("/requests")
def request_capture(body: WarehouseWeighRequest, user: AdminUser = Depends(get_current_user),
                    protocol_version: Literal["1.0"] = Header(default="1.0", alias="X-Scale-Protocol-Version"),
                    service: WarehouseWeighRequestsPort = Depends(warehouse_weigh_requests_service)) -> dict[str, Any]:
    try:
        return service.request(body.model_dump(exclude_none=True), user.username)
    except WarehouseScaleError as exc:
        raise failure(exc, body.request_id) from exc


@router.get("/requests/{request_id}")
def request_status(request_id: str = Path(min_length=1, max_length=100),
                   protocol_version: Literal["1.0"] = Header(default="1.0", alias="X-Scale-Protocol-Version"),
                   user: AdminUser = Depends(get_current_user),
                   service: WarehouseWeighRequestsPort = Depends(warehouse_weigh_requests_service)) -> dict[str, Any]:
    try:
        return service.status(request_id, user.username)
    except WarehouseScaleError as exc:
        raise failure(exc, request_id) from exc


@router.get("/gateway/requests")
def pending(device_id: str = Query(min_length=1, max_length=100),
            protocol_version: Literal["1.0"] = Header(default="1.0", alias="X-Scale-Protocol-Version"),
            user: AdminUser = Depends(require_permission("warehouse_scale_ingest")),
            service: WarehouseWeighRequestsPort = Depends(warehouse_weigh_requests_service)) -> dict[str, Any]:
    try:
        return service.pending(device_id, user.username)
    except WarehouseScaleError as exc:
        raise failure(exc) from exc


@router.get("/devices")
def devices(case_task_id: int = Query(ge=1), purpose: Literal["PICK", "EMPTY_TARE", "FINAL_GROSS"] = Query(),
            protocol_version: Literal["1.0"] = Header(default="1.0", alias="X-Scale-Protocol-Version"),
            user: AdminUser = Depends(get_current_user),
            service: WarehouseWeighRequestsPort = Depends(warehouse_weigh_requests_service)) -> dict[str, Any]:
    try:
        return service.devices(case_task_id, purpose, user.username)
    except WarehouseScaleError as exc:
        raise failure(exc) from exc


@router.post("/gateway/requests/{request_id}/claim")
def claim(request_id: str, body: WarehouseWeighClaim,
          protocol_version: Literal["1.0"] = Header(default="1.0", alias="X-Scale-Protocol-Version"),
          user: AdminUser = Depends(require_permission("warehouse_scale_ingest")),
          service: WarehouseWeighRequestsPort = Depends(warehouse_weigh_requests_service)) -> dict[str, Any]:
    try:
        return service.claim(request_id, body.model_dump(), user.username)
    except WarehouseScaleError as exc:
        error = failure(exc, request_id)
        error.detail.update(claim_id=body.claim_id, device_id=body.device_id)
        raise error from exc


@router.post("/gateway/requests/{request_id}/zero-confirmed")
def confirm_zero(request_id: str, body: WarehouseWeighZero,
                 protocol_version: Literal["1.0"] = Header(default="1.0", alias="X-Scale-Protocol-Version"),
                 user: AdminUser = Depends(require_permission("warehouse_scale_ingest")),
                 service: WarehouseWeighRequestsPort = Depends(warehouse_weigh_requests_service)) -> dict[str, Any]:
    try:
        return service.zero(request_id, body.model_dump(), user.username)
    except WarehouseScaleError as exc:
        error = failure(exc, request_id)
        error.detail.update(claim_id=body.claim_id, device_id=body.device_id)
        raise error from exc
