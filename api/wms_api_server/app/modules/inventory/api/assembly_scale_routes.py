"""Operator scans/consent and dedicated sender evidence have separate identities."""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from ...platform.public import AdminUser, get_current_user
from ..contracts_assembly_recovery import AssemblyReconciliationCapture
from ..contracts_assembly_scale import (
    AssemblyScalePort, assembly_scale_service, AssemblyScaleError, AssemblyStationPolicy, AssemblySkuPolicy,
    AssemblySessionOpen, AssemblyStepOpen, AssemblyCapture, AssemblyFinish,
)

router = APIRouter(prefix="/api/inventory/assembly-scale", tags=["incremental-assembly"])


def failure(exc: AssemblyScaleError) -> HTTPException:
    details = dict(code=exc.code, message=str(exc), outcome_confirmed=exc.status < 500,
        read_before_retry=exc.status >= 500)
    details.update(exc.details)
    return HTTPException(exc.status, details)


@router.get("/context")
def context(task_id: int = Query(ge=1), user: AdminUser = Depends(get_current_user),
            service: AssemblyScalePort = Depends(assembly_scale_service)) -> dict[str, Any]:
    try:
        return service.context(task_id, user.username)
    except AssemblyScaleError as exc:
        raise failure(exc) from exc


@router.get("/sessions/{session}")
def session_read(session: str, user: AdminUser = Depends(get_current_user),
                 service: AssemblyScalePort = Depends(assembly_scale_service)) -> dict[str, Any]:
    try:
        return service.read_session(session, user.username)
    except AssemblyScaleError as exc:
        raise failure(exc) from exc


@router.get("/steps/{step}")
def step_read(step: str, user: AdminUser = Depends(get_current_user),
              service: AssemblyScalePort = Depends(assembly_scale_service)) -> dict[str, Any]:
    try:
        return service.read_step(step, user.username)
    except AssemblyScaleError as exc:
        raise failure(exc) from exc


@router.get("/gateway/requests")
def requests(device_id: str = Query(min_length=1, max_length=100), user: AdminUser = Depends(get_current_user),
             service: AssemblyScalePort = Depends(assembly_scale_service)) -> dict[str, Any]:
    try:
        return service.gateway_requests(device_id, user.username)
    except AssemblyScaleError as exc:
        raise failure(exc) from exc


@router.put("/station-policies/{device}")
def station_policy(device: str, body: AssemblyStationPolicy, user: AdminUser = Depends(get_current_user),
                   service: AssemblyScalePort = Depends(assembly_scale_service)) -> dict[str, Any]:
    try:
        return service.station_policy(device, body, user.username)
    except AssemblyScaleError as exc:
        raise failure(exc) from exc


@router.put("/sku-policies")
def sku_policy(body: AssemblySkuPolicy, user: AdminUser = Depends(get_current_user),
               service: AssemblyScalePort = Depends(assembly_scale_service)) -> dict[str, Any]:
    try:
        return service.sku_policy(body, user.username)
    except AssemblyScaleError as exc:
        raise failure(exc) from exc


@router.post("/sessions")
def session_open(body: AssemblySessionOpen, user: AdminUser = Depends(get_current_user),
                 service: AssemblyScalePort = Depends(assembly_scale_service)) -> dict[str, Any]:
    try:
        return service.open_session(body, user.username)
    except AssemblyScaleError as exc:
        raise failure(exc) from exc


@router.post("/sessions/{session}/steps")
def step_open(session: str, body: AssemblyStepOpen, user: AdminUser = Depends(get_current_user),
              service: AssemblyScalePort = Depends(assembly_scale_service)) -> dict[str, Any]:
    try:
        return service.open_step(session, body, user.username)
    except AssemblyScaleError as exc:
        raise failure(exc) from exc


@router.post("/captures")
def capture(body: AssemblyCapture | AssemblyReconciliationCapture, user: AdminUser = Depends(get_current_user),
            service: AssemblyScalePort = Depends(assembly_scale_service)) -> dict[str, Any]:
    try:
        return service.capture(body, user.username)
    except AssemblyScaleError as exc:
        raise failure(exc) from exc


@router.post("/steps/{step}/placed")
def placed(step: str, user: AdminUser = Depends(get_current_user),
           service: AssemblyScalePort = Depends(assembly_scale_service)) -> dict[str, Any]:
    try:
        return service.placed(step, user.username)
    except AssemblyScaleError as exc:
        raise failure(exc) from exc


@router.post("/sessions/{session}/finish")
def finish(session: str, body: AssemblyFinish, user: AdminUser = Depends(get_current_user),
           service: AssemblyScalePort = Depends(assembly_scale_service)) -> dict[str, Any]:
    try:
        return service.finish(session, body, user.username)
    except AssemblyScaleError as exc:
        raise failure(exc) from exc
