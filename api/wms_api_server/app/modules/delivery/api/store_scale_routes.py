"""Gateway packets only; no browser-supplied weight can confirm a receipt."""
from typing import Any, Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field
from ...platform.public import AdminUser,require_permission
from ..contracts import StoreReceiptError
from ..contracts_scales import StoreScalesPort,store_scales_service
from .store_receipt_routes import failure

router=APIRouter(prefix="/api/delivery/store-scales",tags=["store-scale-evidence"])
UTC_PATTERN=r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}\+00:00$"
DECIMAL_PATTERN=r"^[0-9]{1,18}(\.[0-9]{1,9})?$"


class ScaleConfiguration(BaseModel):
    model_config=ConfigDict(extra="forbid")
    store_address: str=Field(strict=True,min_length=1,max_length=255)
    sender_id: str=Field(strict=True,min_length=1,max_length=50)
    expected_version: int=Field(strict=True,ge=0)
    active: bool=Field(strict=True)
    capacity_kg: str=Field(strict=True,pattern=DECIMAL_PATTERN)
    resolution_kg: str=Field(strict=True,pattern=DECIMAL_PATTERN)
    calibration_ref: str=Field(strict=True,min_length=1,max_length=100)
    calibrated_until: str=Field(strict=True,pattern=UTC_PATTERN)


class ScaleSample(BaseModel):
    model_config=ConfigDict(extra="forbid")
    offset_ms: int=Field(strict=True,ge=0,le=10000)
    gross_weight_kg: str=Field(strict=True,pattern=DECIMAL_PATTERN)


class ScalePacket(BaseModel):
    model_config=ConfigDict(extra="forbid")
    device_id: str=Field(strict=True,min_length=1,max_length=100)
    capture_id: str=Field(strict=True,min_length=1,max_length=100)
    load_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    store_address: str=Field(strict=True,min_length=1,max_length=255)
    device_policy_version: int=Field(strict=True,ge=1)
    calibration_ref: str=Field(strict=True,min_length=1,max_length=100)
    unit: Literal["KG"]
    basis: Literal["GROSS"]
    preset_tare_kg: Literal["0"]
    zero_confirmed: bool=Field(strict=True)
    zero_check_kg: str=Field(strict=True,pattern=r"^-?[0-9]{1,18}(\.[0-9]{1,9})?$")
    zero_check_at: str=Field(strict=True,pattern=UTC_PATTERN)
    measured_at: str=Field(strict=True,pattern=UTC_PATTERN)
    samples: list[ScaleSample]=Field(min_length=5,max_length=25)


@router.put("/devices/{device_id}")
def configure(device_id: str,body: ScaleConfiguration,
              user: AdminUser=Depends(require_permission("warehouse_settings_edit")),
              service: StoreScalesPort=Depends(store_scales_service)) -> dict[str,Any]:
    if not 1<=len(device_id)<=100:
        raise HTTPException(422,"Укажите идентификатор весов")
    try:
        return service.configure(device_id,body.model_dump(),user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc


@router.post("/captures")
def capture(body: ScalePacket,
            user: AdminUser=Depends(require_permission("store_scale_ingest")),
            service: StoreScalesPort=Depends(store_scales_service)) -> dict[str,Any]:
    try:
        return service.capture(body.model_dump(),user.username)
    except StoreReceiptError as exc:
        error=failure(exc)
        error.detail.update(device_id=body.device_id,capture_id=body.capture_id,retry_same_capture=exc.status>=500)
        raise error from exc


@router.get("/captures/{capture_key}")
def reading(capture_key: str,
            user: AdminUser=Depends(require_permission("store_receipt_confirm")),
            service: StoreScalesPort=Depends(store_scales_service)) -> dict[str,Any]:
    if len(capture_key)!=64 or any(char not in "0123456789ABCDEF" for char in capture_key):
        raise HTTPException(422,"Укажите ключ измерения")
    try:
        return service.reading(capture_key,user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc


@router.get("/captures")
def readings(load_operation_id: str,store_address: str,
             user: AdminUser=Depends(require_permission("store_receipt_confirm")),
             service: StoreScalesPort=Depends(store_scales_service)) -> dict[str,Any]:
    if not 1<=len(load_operation_id)<=100 or not 1<=len(store_address)<=255:
        raise HTTPException(422,"Укажите погрузку и адрес магазина")
    try:
        return service.readings(load_operation_id,store_address,user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc
