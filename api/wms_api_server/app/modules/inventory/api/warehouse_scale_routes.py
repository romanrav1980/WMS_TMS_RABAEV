"""Warehouse device packets are evidence, never browser-supplied stock quantities."""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from ...platform.public import AdminUser, require_permission, get_current_user
from ..contracts_warehouse_scale import (
    WarehouseScaleConfiguration, WarehouseScalePacket, WarehouseFinalScalePacket, WarehouseScalePort,
    WarehouseScaleError, warehouse_scale_service, ManualEmptyTareRequest,
)

router = APIRouter(prefix="/api/inventory/warehouse-scales", tags=["warehouse-scale-evidence"])


@router.post("/tasks/{task}/manual-empty-tare")
def manual_empty_tare(task: int, body: ManualEmptyTareRequest,
                      user: AdminUser = Depends(get_current_user),
                      service: WarehouseScalePort = Depends(warehouse_scale_service)) -> dict[str, Any]:
    if task<1:raise HTTPException(422,"Укажите задание сборки")
    try:return service.manual_tare(task,body,user.username)
    except WarehouseScaleError as exc:
        uncertain=exc.status>=500 or exc.status==403 or "CONFLICT"in str(exc)
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),
            "operation_id":body.operation_id,"retry_same_operation_id":uncertain,
            "outcome_confirmed":not uncertain})from exc


def failure(exc: WarehouseScaleError) -> HTTPException:
    return HTTPException(exc.status, {"code": exc.code, "message": str(exc),
        "outcome_confirmed": exc.status < 500, "retry_same_capture": exc.status >= 500})


@router.put("/devices/{device}")
def configure(device: str, body: WarehouseScaleConfiguration,
              user: AdminUser = Depends(require_permission("warehouse_settings_edit")),
              service: WarehouseScalePort = Depends(warehouse_scale_service)) -> dict[str, Any]:
    if not 1 <= len(device) <= 100:
        raise HTTPException(422, "Scale device ID required")
    try:
        return service.configure(device, body, user.username)
    except WarehouseScaleError as exc:
        raise failure(exc) from exc


@router.post("/captures")
def capture(body: WarehouseScalePacket, user: AdminUser = Depends(require_permission("warehouse_scale_ingest")),
            service: WarehouseScalePort = Depends(warehouse_scale_service)) -> dict[str, Any]:
    try:
        return service.capture(body, user.username)
    except WarehouseScaleError as exc:
        error = failure(exc)
        error.detail.update(device_id=body.device_id, capture_id=body.capture_id)
        raise error from exc


@router.get("/captures")
def readings(task: int = Query(ge=1), line: int = Query(ge=1),
             user: AdminUser = Depends(get_current_user),
             service: WarehouseScalePort = Depends(warehouse_scale_service)) -> dict[str, Any]:
    try:
        return service.readings(task, line, user.username)
    except WarehouseScaleError as exc:
        raise failure(exc) from exc


@router.get("/captures/{key}")
def reading(key: str, user: AdminUser = Depends(get_current_user),
            service: WarehouseScalePort = Depends(warehouse_scale_service)) -> dict[str, Any]:
    if len(key) != 64 or any(c not in "0123456789ABCDEF" for c in key):
        raise HTTPException(422, "Scale capture key required")
    try:
        return service.reading(key, user.username)
    except WarehouseScaleError as exc:
        raise failure(exc) from exc


@router.post("/final-captures")
def final_capture(body:WarehouseFinalScalePacket,user:AdminUser=Depends(require_permission("warehouse_scale_ingest")),
                  service:WarehouseScalePort=Depends(warehouse_scale_service))->dict[str,Any]:
    try:return service.capture(body,user.username)
    except WarehouseScaleError as exc:
        error=failure(exc);error.detail.update(device_id=body.device_id,capture_id=body.capture_id);raise error from exc

@router.get("/final-captures")
def final_readings(task:int=Query(ge=1),user:AdminUser=Depends(get_current_user),
                   service:WarehouseScalePort=Depends(warehouse_scale_service))->dict[str,Any]:
    try:return service.final_readings(task,user.username)
    except WarehouseScaleError as exc:raise failure(exc)from exc
