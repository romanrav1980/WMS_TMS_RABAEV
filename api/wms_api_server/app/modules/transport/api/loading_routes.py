"""Scan the real upper place, vehicle and dock; departure is a separate command."""
from decimal import Decimal
from typing import Any, Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, model_validator
from ...platform.public import AdminUser, get_current_user, require_permission
from ..contracts import TransportLoadingError, TransportLoadingPort, transport_loading_service

router = APIRouter(prefix="/api/transport/loading", tags=["transport-loading"])


class LoadMeasures(BaseModel):
    model_config = ConfigDict(extra="forbid")
    origin: Literal["MANUAL_CONFIRMED"]
    content_version: int = Field(ge=0)
    gross_weight_kg: Decimal = Field(gt=0,max_digits=18,decimal_places=9)
    width_m: Decimal = Field(gt=0,max_digits=18,decimal_places=9)
    depth_m: Decimal = Field(gt=0,max_digits=18,decimal_places=9)
    height_m: Decimal = Field(gt=0,max_digits=18,decimal_places=9)


class PhysicalBoxWeight(BaseModel):
    model_config=ConfigDict(extra="forbid")
    box_uid: str=Field(strict=True,min_length=1,max_length=200)
    scan_box: str=Field(strict=True,min_length=1,max_length=200)
    content_version: int=Field(strict=True,ge=0)
    origin: Literal["MANUAL_CONFIRMED"]
    gross_weight_kg: str=Field(strict=True,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")
    measurement_ref: str=Field(strict=True,min_length=1,max_length=100)


class LoadingTemperatureConfirmation(BaseModel):
    model_config=ConfigDict(extra="forbid")
    origin: Literal["MANUAL_AT_LOADING"]
    observed_c: str=Field(strict=True,pattern=r"^-?[0-9]{1,6}(\.[0-9]{1,3})?$")
    vehicle_profile_version: int=Field(strict=True,ge=1)
    observation_reference: str=Field(strict=True,min_length=1,max_length=100)

class LoadingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    identifier: str = Field(min_length=1,max_length=200)
    expected_version: int = Field(ge=0)
    scan_container: str = Field(min_length=1,max_length=200)
    scan_cell: str = Field(min_length=1,max_length=60)
    transport_task_id: int = Field(ge=1)
    scan_vehicle: str = Field(min_length=1,max_length=50)
    scan_dock: str = Field(min_length=1,max_length=50)
    temperature_confirmation: LoadingTemperatureConfirmation | None=None
    measurements: LoadMeasures
    physical_boxes: list[PhysicalBoxWeight]=Field(default_factory=list,max_length=200)


class DepartureTemperatureConfirmation(LoadingTemperatureConfirmation):
    origin: Literal["MANUAL_AT_DEPARTURE"]


class DepartureRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    temperature_confirmation: DepartureTemperatureConfirmation | None=None
    operation_id: str = Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")


def failure(exc: TransportLoadingError) -> HTTPException:
    unconfirmed=exc.status>=500 or exc.status in {401,403} or "OPERATION_CONFLICT" in str(exc)
    return HTTPException(exc.status, detail={"code":exc.code,"message":str(exc),
        "operation_id":exc.operation_id,"retry_same_operation_id":bool(exc.operation_id),"outcome_confirmed":not unconfirmed})


@router.get("/{task_id}/status")
def status(task_id: int, user: AdminUser = Depends(get_current_user),
           service: TransportLoadingPort = Depends(transport_loading_service)) -> dict[str, Any]:
    try:
        return service.status(task_id, user.username)
    except TransportLoadingError as exc:
        raise failure(exc) from exc


def loading_metadata(body: LoadingRequest) -> dict[str, Any]:
    metadata = body.model_dump(mode="json",exclude={"operation_id","identifier","transport_task_id","scan_vehicle","scan_dock","measurements","physical_boxes","temperature_confirmation","source_kind"})
    metadata["loading_context"]={"transport_task_id":body.transport_task_id,
        "scan_vehicle":body.scan_vehicle,"scan_dock":body.scan_dock,
        "measurements":body.measurements.model_dump(mode="json")}
    if body.temperature_confirmation:
        metadata["loading_context"]["temperature_confirmation"]=body.temperature_confirmation.model_dump(mode="json")
    if body.physical_boxes:
        metadata["loading_context"]["physical_boxes"]=[item.model_dump() for item in body.physical_boxes]
    return metadata


@router.post("/confirm")
def confirm(body: LoadingRequest, user: AdminUser = Depends(get_current_user),
            service: TransportLoadingPort = Depends(transport_loading_service)) -> dict[str, Any]:
    try:
        return service.load(body.operation_id,body.identifier,loading_metadata(body),user.username)
    except TransportLoadingError as exc:
        raise failure(exc) from exc


class BulkLoadingRequest(LoadingRequest):
    source_kind: Literal["HU","SINGLE"] = "HU"
    expected_composition_signature: str | None = Field(default=None,pattern=r"^[A-F0-9]{64}$")

    @model_validator(mode="after")
    def require_signature(self) -> "BulkLoadingRequest":
        if self.source_kind=="SINGLE" and self.expected_composition_signature is None:
            raise ValueError("Read the current carton composition before loading")
        return self


@router.get("/bulk-box-preview")
def bulk_box_preview(identifier: str = Query(min_length=1,max_length=200),
                     user: AdminUser = Depends(get_current_user),
                     service: TransportLoadingPort = Depends(transport_loading_service)) -> dict[str, Any]:
    try:return service.preview_bulk(identifier,user.username)
    except TransportLoadingError as exc:raise failure(exc)from exc


@router.post("/confirm-bulk-box")
def confirm_bulk_box(body: BulkLoadingRequest, user: AdminUser = Depends(get_current_user),
                     service: TransportLoadingPort = Depends(transport_loading_service)) -> dict[str, Any]:
    metadata=loading_metadata(body)
    metadata["bulk_box_scan"]=True
    try:
        if body.source_kind=="SINGLE":
            return service.load_single(body.operation_id,body.identifier,metadata,user.username)
        metadata.pop("expected_composition_signature",None)
        return service.load(body.operation_id,body.identifier,metadata,user.username)
    except TransportLoadingError as exc:
        raise failure(exc) from exc


@router.post("/{task_id}/depart")
def depart(task_id: int, body: DepartureRequest,
           user: AdminUser = Depends(get_current_user),
           service: TransportLoadingPort = Depends(transport_loading_service)) -> dict[str, Any]:
    if task_id<1:
        raise HTTPException(422,"Положительный идентификатор рейса обязателен")
    try:
        if body.temperature_confirmation:
            return service.depart(body.operation_id,task_id,user.username,body.temperature_confirmation.model_dump(mode="json"))
        return service.depart(body.operation_id,task_id,user.username)
    except TransportLoadingError as exc:
        raise failure(exc) from exc


class SingleLoadingRequest(LoadingRequest):
    expected_composition_signature: str = Field(pattern=r"^[A-F0-9]{64}$")


@router.get("/single-preview")
def single_preview(shipment_identifier: str,
                   user: AdminUser = Depends(get_current_user),
                   service: TransportLoadingPort = Depends(transport_loading_service)) -> dict[str, Any]:
    if not shipment_identifier or len(shipment_identifier)>200:
        raise HTTPException(422,"Укажите идентификатор СТ")
    try:
        return service.preview_single(shipment_identifier,user.username)
    except TransportLoadingError as exc:
        raise failure(exc) from exc


@router.post("/confirm-single")
def confirm_single(body: SingleLoadingRequest,
                   user: AdminUser = Depends(get_current_user),
                   service: TransportLoadingPort = Depends(transport_loading_service)) -> dict[str, Any]:
    metadata=body.model_dump(mode="json",exclude={"operation_id","identifier","transport_task_id","scan_vehicle","scan_dock","measurements","physical_boxes","temperature_confirmation"})
    metadata["loading_context"]={"transport_task_id":body.transport_task_id,
        "scan_vehicle":body.scan_vehicle,"scan_dock":body.scan_dock,
        "measurements":body.measurements.model_dump(mode="json")}
    if body.temperature_confirmation:
        metadata["loading_context"]["temperature_confirmation"]=body.temperature_confirmation.model_dump(mode="json")
    if body.physical_boxes:
        metadata["loading_context"]["physical_boxes"]=[item.model_dump() for item in body.physical_boxes]
    try:
        return service.load_single(body.operation_id,body.identifier,metadata,user.username)
    except TransportLoadingError as exc:
        raise failure(exc) from exc

class ReconciliationLoadingRequest(SingleLoadingRequest):
    identifier: str = Field(min_length=1,max_length=100)


@router.get("/reconciliation-preview")
def reconciliation_preview(shipping_operation_id: str,
                           user: AdminUser = Depends(require_permission("stock_posting_shipping")),
                           service: TransportLoadingPort = Depends(transport_loading_service)) -> dict[str, Any]:
    if not shipping_operation_id or len(shipping_operation_id)>100:
        raise HTTPException(422,"Укажите исходную операцию отгрузки")
    try:
        return service.preview_reconciliation(shipping_operation_id)
    except TransportLoadingError as exc:
        raise failure(exc) from exc


@router.post("/confirm-reconciliation")
def confirm_reconciliation(body: ReconciliationLoadingRequest,
                           user: AdminUser = Depends(require_permission("stock_posting_shipping")),
                           service: TransportLoadingPort = Depends(transport_loading_service)) -> dict[str, Any]:
    metadata=body.model_dump(mode="json",exclude={"operation_id","identifier","transport_task_id","scan_vehicle","scan_dock","measurements","physical_boxes","temperature_confirmation"})
    metadata["loading_context"]={"transport_task_id":body.transport_task_id,
        "scan_vehicle":body.scan_vehicle,"scan_dock":body.scan_dock,
        "measurements":body.measurements.model_dump(mode="json")}
    if body.temperature_confirmation:
        metadata["loading_context"]["temperature_confirmation"]=body.temperature_confirmation.model_dump(mode="json")
    if body.physical_boxes:
        metadata["loading_context"]["physical_boxes"]=[item.model_dump() for item in body.physical_boxes]
    try:
        return service.reconcile(body.operation_id,body.identifier,metadata,user.username)
    except TransportLoadingError as exc:
        raise failure(exc) from exc
