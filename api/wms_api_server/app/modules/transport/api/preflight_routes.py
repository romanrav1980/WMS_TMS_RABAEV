from typing import Any, Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from ...platform.public import AdminUser, require_permission, get_current_user
from ..contracts_preflight import TransportPreflightPort, transport_preflight_service, TransportPlanError

router = APIRouter(prefix="/api/transport/preflight", tags=["transport-preflight"])


class ManualPreflight(BaseModel):
    model_config = ConfigDict(extra="forbid")
    additional_st_numbers: list[str] = Field(default_factory=list, max_length=200)


class TimePreflight(BaseModel):
    model_config = ConfigDict(extra="forbid")
    time_zone: Literal["UTC", "Europe/Moscow", "Asia/Tbilisi"]


class TimeApproval(TimePreflight):
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    trip_id: int = Field(strict=True, gt=0)
    expected_version: int = Field(strict=True, ge=0)
    source_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    reason: str = Field(min_length=8, max_length=500)
    approval_phase: Literal["BEFORE_LOADING", "AFTER_LOADING_REVIEW"] | None = None


@router.get("/trips/{trip_id}/time-context")
def time_context(trip_id: int, user: AdminUser = Depends(get_current_user),
                 service: TransportPreflightPort = Depends(transport_preflight_service)) -> dict[str, Any]:
    if trip_id < 1:
        raise HTTPException(422, "Positive trip required")
    try:
        return service.time_context(trip_id, user.username)
    except TransportPlanError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc


@router.get("/trips/{trip_id}/coordination")
def coordination_preflight(trip_id: int, user: AdminUser = Depends(require_permission("transport_dispatch_edit")),
                            service: TransportPreflightPort = Depends(transport_preflight_service)) -> dict[str, Any]:
    if trip_id < 1:
        raise HTTPException(422, "Positive trip required")
    try:
        return service.coordination(trip_id, user.username)
    except TransportPlanError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc


@router.post("/time-approvals")
def approve_time(body: TimeApproval, user: AdminUser = Depends(require_permission("transport_dispatch_edit")),
                 service: TransportPreflightPort = Depends(transport_preflight_service)) -> dict[str, Any]:
    try:
        return service.approve_time(body.operation_id, body.model_dump(exclude={"operation_id"}, exclude_none=True), user.username)
    except TransportPlanError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc


@router.post("/trips/{trip_id}/time")
def trip_time_preflight(trip_id: int, body: TimePreflight,
                        user: AdminUser = Depends(require_permission("transport_dispatch_edit")),
                        service: TransportPreflightPort = Depends(transport_preflight_service)) -> dict[str, Any]:
    if trip_id < 1:
        raise HTTPException(422, "Positive trip required")
    try:
        return service.trip_time(trip_id, body.time_zone, user.username)
    except TransportPlanError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc


@router.get("/plans/{plan_id}")
def plan_preflight(plan_id: int, user: AdminUser = Depends(require_permission("transport_dispatch_edit")),
                   service: TransportPreflightPort = Depends(transport_preflight_service)) -> dict[str, Any]:
    if plan_id < 1:
        raise HTTPException(422, "Positive plan required")
    try:
        return service.plan(plan_id, user.username)
    except TransportPlanError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc


@router.post("/trips/{trip_id}")
def trip_preflight(trip_id: int, body: ManualPreflight,
                   user: AdminUser = Depends(require_permission("transport_dispatch_edit")),
                   service: TransportPreflightPort = Depends(transport_preflight_service)) -> dict[str, Any]:
    if trip_id < 1 or any(not number.strip() or len(number) > 100 for number in body.additional_st_numbers):
        raise HTTPException(422, "Positive trip and ST numbers1–100 characters required")
    try:
        return service.trip(trip_id, body.additional_st_numbers, user.username)
    except TransportPlanError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc


class RouteInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    trip_id: int = Field(strict=True, gt=0)
    expected_version: int = Field(strict=True, ge=0)
    source_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    drive_min: int = Field(strict=True, gt=0, le=1440)
    drive_back_min: int = Field(strict=True, gt=0, le=1440)
    source_reference: str = Field(min_length=8, max_length=500)
    reason: str = Field(min_length=8, max_length=500)


class RoadRefresh(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    trip_id: int = Field(strict=True, gt=0)
    expected_version: int = Field(strict=True, ge=0)
    source_hash: str = Field(pattern=r"^[a-f0-9]{64}$")


@router.post("/road-refreshes")
def refresh_road(body: RoadRefresh, user: AdminUser = Depends(require_permission("transport_dispatch_edit")),
                 service: TransportPreflightPort = Depends(transport_preflight_service)) -> dict[str, Any]:
    try:
        return service.refresh_road(body.operation_id, body.model_dump(exclude={"operation_id"}), user.username)
    except TransportPlanError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc


@router.get("/trips/{trip_id}/route-context")
def route_context(trip_id: int, user: AdminUser = Depends(require_permission("transport_dispatch_edit")),
                  service: TransportPreflightPort = Depends(transport_preflight_service)) -> dict[str, Any]:
    if trip_id < 1:
        raise HTTPException(422, "Positive trip required")
    try:
        return service.route_context(trip_id, user.username)
    except TransportPlanError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc


@router.post("/route-inputs")
def route_input(body: RouteInput, user: AdminUser = Depends(require_permission("transport_dispatch_edit")),
                service: TransportPreflightPort = Depends(transport_preflight_service)) -> dict[str, Any]:
    try:
        return service.apply_route_input(body.operation_id, body.model_dump(exclude={"operation_id"}), user.username)
    except TransportPlanError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc

@router.get("/trips/{trip_id}/road-legs")
def road_legs(trip_id: int,depot_address: str=Query(default="",max_length=200),max_age_hours: int=Query(default=24,ge=1,le=720),
              user: AdminUser=Depends(require_permission("transport_dispatch_edit")),
              service: TransportPreflightPort=Depends(transport_preflight_service)) -> dict:
    if trip_id<1:raise HTTPException(422,"Positive trip required")
    try:return service.road_legs(trip_id,depot_address.strip(),max_age_hours,user.username)
    except TransportPlanError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc


@router.get("/trips/{trip_id}/delivery-windows")
def delivery_windows(trip_id: int,time_zone: Literal["UTC","Europe/Moscow","Asia/Tbilisi"],
                     depot_address: str=Query(default="",max_length=200),max_age_hours: int=Query(default=24,ge=1,le=720),
                     user: AdminUser=Depends(require_permission("transport_dispatch_edit")),
                     service: TransportPreflightPort=Depends(transport_preflight_service)) -> dict:
    if trip_id<1:raise HTTPException(422,"Positive trip required")
    try:return service.delivery_windows(trip_id,depot_address.strip(),max_age_hours,time_zone,user.username)
    except TransportPlanError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc
