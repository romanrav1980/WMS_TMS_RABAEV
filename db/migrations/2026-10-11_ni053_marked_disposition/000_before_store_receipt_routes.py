"""Authenticated destination confirmation, distinct from driver_id and trip closing."""
from typing import Any, Literal, Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from ...platform.public import AdminUser, require_permission
from ..contracts import StoreReceiptError, StoreReceiptPort, store_receipt_service

router=APIRouter(prefix="/api/delivery/store-receipts",tags=["store-receipt"])


class StoreDisposition(BaseModel):
    model_config=ConfigDict(extra="forbid")
    lot_uid: str=Field(strict=True,min_length=1,max_length=200)
    accepted: str=Field(strict=True,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")
    missing: str=Field(default="0",strict=True,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")
    refused: str=Field(default="0",strict=True,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")
    damaged: str=Field(default="0",strict=True,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")
    extra: str=Field(default="0",strict=True,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")


class StoreUnitScan(BaseModel):
    model_config=ConfigDict(extra="forbid")
    system_code: str=Field(strict=True,min_length=1,max_length=40)
    profile_code: str=Field(strict=True,min_length=1,max_length=60)
    code: str=Field(strict=True,min_length=1,max_length=4000)

class StoreReceiptRequest(BaseModel):
    scans: list[StoreUnitScan]=Field(default_factory=list,max_length=20000)
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    load_operation_id: str=Field(min_length=1,max_length=100)
    store_address: str=Field(min_length=1,max_length=255)
    scan_place: str=Field(min_length=1,max_length=200)
    expected_composition_signature: str=Field(pattern=r"^[A-F0-9]{64}$")
    before_cameras: bool=Field(strict=True)
    observations: list[StoreDisposition]=Field(default_factory=list,max_length=200)
    case_note: str=Field(default="",max_length=2000)
    scale_capture_key: str=Field(default="",pattern=r"^([A-F0-9]{64})?$")
    photo_ids: list[Annotated[str,Field(strict=True,pattern=r"^[A-F0-9]{64}$")]]=Field(default_factory=list,max_length=12)
    weight_act_confirmed: bool=Field(default=False,strict=True)


class PolicyRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    store_address: str=Field(min_length=1,max_length=255)
    mode: Literal["BARCODE","WEIGHT_PHOTO"]
    expected_version: int=Field(strict=True,ge=0)


class ReceiverRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    store_address: str=Field(min_length=1,max_length=255)
    username: str=Field(min_length=1,max_length=50)


def failure(error: StoreReceiptError) -> HTTPException:
    return HTTPException(error.status,detail={"code":error.code,"message":str(error),
        "operation_id":error.operation_id,"retry_same_operation_id":bool(error.operation_id),
        "outcome_confirmed":error.status<500})


@router.get("/preview")
def preview(load_operation_id: str,store_address: str,
            user: AdminUser=Depends(require_permission("store_receipt_confirm")),
            service: StoreReceiptPort=Depends(store_receipt_service)) -> dict[str,Any]:
    if not 1<=len(load_operation_id)<=100 or not 1<=len(store_address)<=255:
        raise HTTPException(422,"Укажите погрузку и адрес магазина")
    try:
        return service.preview(load_operation_id,store_address,user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc


@router.get("/trips/{trip_id}/places")
def places(trip_id: int,store_address: str,
           user: AdminUser=Depends(require_permission("store_receipt_confirm")),
           service: StoreReceiptPort=Depends(store_receipt_service)) -> list[dict[str,Any]]:
    if trip_id<1 or not 1<=len(store_address)<=255:
        raise HTTPException(422,"Укажите рейс и адрес магазина")
    try:
        return service.places(trip_id,store_address,user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc


@router.post("/confirm")
def confirm(body: StoreReceiptRequest,
            user: AdminUser=Depends(require_permission("store_receipt_confirm")),
            service: StoreReceiptPort=Depends(store_receipt_service)) -> dict[str,Any]:
    metadata=body.model_dump(exclude={"scans","operation_id","load_operation_id","store_address","observations","case_note","scale_capture_key","photo_ids","weight_act_confirmed"})
    if body.scans:
        metadata["scans"]=[scan.model_dump() for scan in body.scans]
    if body.observations:
        metadata["observations"]=[row.model_dump() for row in body.observations]
    if body.case_note:
        if len(body.case_note.encode("utf-8"))>2000:
            raise HTTPException(422,"Сократите описание расхождения до 2000 байт")
        metadata["case_note"]=body.case_note
    if body.scale_capture_key:
        metadata["scale_capture_key"]=body.scale_capture_key
    if body.photo_ids:
        metadata["photo_ids"]=body.photo_ids
    if body.weight_act_confirmed:
        metadata["weight_act_confirmed"]=True
    try:
        return service.confirm(body.operation_id,body.load_operation_id,body.store_address,metadata,user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc


@router.put("/policy")
def configure(body: PolicyRequest,
              user: AdminUser=Depends(require_permission("warehouse_settings_edit")),
              service: StoreReceiptPort=Depends(store_receipt_service)) -> dict[str,Any]:
    try:
        return service.configure(body.store_address,body.mode,body.expected_version,user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc


@router.post("/receivers")
def assign_receiver(body: ReceiverRequest,
                    user: AdminUser=Depends(require_permission("warehouse_settings_edit")),
                    service: StoreReceiptPort=Depends(store_receipt_service)) -> dict[str,Any]:
    try:
        return service.assign_receiver(body.store_address,body.username,user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc


@router.get("/cases")
def cases(store_address: str, after: str = "", limit: int = 50,
          user: AdminUser=Depends(require_permission("transport_dispatch_view")),
          service: StoreReceiptPort=Depends(store_receipt_service)) -> dict[str,Any]:
    if not 1<=len(store_address)<=255 or len(after)>100 or not 1<=limit<=100:
        raise HTTPException(422,"Укажите адрес, курсор и размер страницы от 1 до 100")
    try:
        return service.cases(store_address,after,limit)
    except StoreReceiptError as exc:
        raise failure(exc) from exc


@router.get("/cases/{case_id}")
def case_detail(case_id: str,
                user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                service: StoreReceiptPort=Depends(store_receipt_service)) -> dict[str,Any]:
    if not 1<=len(case_id)<=100:
        raise HTTPException(422,"Укажите разбирательство")
    try:
        return service.case_detail(case_id)
    except StoreReceiptError as exc:
        raise failure(exc) from exc
