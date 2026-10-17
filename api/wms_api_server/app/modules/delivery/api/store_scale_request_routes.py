"""Receiver weighing requests and a separately authenticated gateway inbox."""
from typing import Any, Literal
from fastapi import APIRouter, Depends, Header, Path, Query
from pydantic import BaseModel, ConfigDict, Field
from ...platform.public import AdminUser, get_current_user, require_permission
from ..contracts import StoreReceiptError
from ..contracts_scale_requests import StoreScaleRequestsPort, store_scale_requests_service
from .store_receipt_routes import failure

router = APIRouter(prefix="/api/delivery/store-scales", tags=["store-scale-requests"])


class ScaleRequestBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: str = Field(strict=True, min_length=1, max_length=100)
    device_id: str = Field(strict=True, min_length=1, max_length=100)
    load_operation_id: str = Field(strict=True, min_length=1, max_length=100)
    store_address: str = Field(strict=True, min_length=1, max_length=255)
    expected_composition_signature: str = Field(strict=True, pattern=r"^[A-F0-9]{64}$")


@router.post("/requests")
def request_capture(body: ScaleRequestBody, user: AdminUser = Depends(get_current_user),
                    protocol_version: Literal["1.0"] = Header(default="1.0", alias="X-Scale-Protocol-Version"),
                    service: StoreScaleRequestsPort = Depends(store_scale_requests_service)) -> dict[str, Any]:
    try:
        return service.request(body.model_dump(), user.username)
    except StoreReceiptError as exc:
        error = failure(exc)
        conflict = "PAYLOAD_CONFLICT" in str(exc)
        confirmed = exc.status < 500 and exc.status not in (401, 403) and not conflict
        error.detail.update(request_id=body.request_id, retry_same_request=exc.status >= 500,
                            outcome_confirmed=confirmed, read_before_retry=conflict or exc.status >= 500)
        raise error from exc


@router.get("/requests/{request_id}")
def request_status(request_id: str = Path(min_length=1, max_length=100),
                   protocol_version: Literal["1.0"] = Header(default="1.0", alias="X-Scale-Protocol-Version"),
                   user: AdminUser = Depends(get_current_user),
                   service: StoreScaleRequestsPort = Depends(store_scale_requests_service)) -> dict[str, Any]:
    try:
        return service.status(request_id, user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc


@router.get("/devices")
def devices(load_operation_id: str = Query(min_length=1, max_length=100),
            protocol_version: Literal["1.0"] = Header(default="1.0", alias="X-Scale-Protocol-Version"),
            store_address: str = Query(min_length=1, max_length=255),
            user: AdminUser = Depends(get_current_user),
            service: StoreScaleRequestsPort = Depends(store_scale_requests_service)) -> dict[str, Any]:
    try:
        return service.devices(load_operation_id, store_address, user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc


@router.get("/gateway/requests")
def pending(device_id: str = Query(min_length=1, max_length=100),
            protocol_version: Literal["1.0"] = Header(default="1.0", alias="X-Scale-Protocol-Version"),
            user: AdminUser = Depends(require_permission("store_scale_ingest")),
            service: StoreScaleRequestsPort = Depends(store_scale_requests_service)) -> dict[str, Any]:
    try:
        return service.pending(device_id, user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc
