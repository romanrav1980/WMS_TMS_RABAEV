from datetime import timedelta, timezone
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field
from ...platform.public import AdminUser, get_current_user
from ..contracts import StoreReceiptError
from ..contracts_delivery_time import DeliveryTimePort, delivery_time_service

router = APIRouter(prefix="/api/delivery/timing", tags=["delivery-kpi"])


class TimeCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    load_operation_id: str = Field(min_length=1, max_length=100)
    store_address: str = Field(min_length=1, max_length=255)
    reason: str = Field(min_length=8, max_length=500)


class WindowCommand(TimeCommand):
    expected_version: int = Field(strict=True, ge=0)
    window_start: AwareDatetime
    window_finish: AwareDatetime


class ArrivalCommand(TimeCommand):
    arrived_at: AwareDatetime | None = None


def canonical(body: TimeCommand) -> dict[str, Any]:
    result = body.model_dump(mode="json", exclude_none=True)
    for key in ("window_start", "window_finish", "arrived_at"):
        value = getattr(body, key, None)
        if value is not None:
            result[key] = value.astimezone(timezone.utc).isoformat(timespec="microseconds")
    return result


def failure(error: StoreReceiptError) -> HTTPException:
    return HTTPException(error.status, {"code": error.code, "message": str(error),
        "operation_id": error.operation_id, "outcome_confirmed": error.status < 500})


@router.post("/window")
def plan_window(body: WindowCommand, user: AdminUser = Depends(get_current_user),
                service: DeliveryTimePort = Depends(delivery_time_service)) -> dict[str, Any]:
    if body.window_finish < body.window_start or body.window_finish - body.window_start > timedelta(days=7):
        raise HTTPException(422, "DELIVERY_WINDOW_BOUND_7_DAYS")
    try:
        return service.command("plan_window", canonical(body), user.username)
    except StoreReceiptError as error:
        raise failure(error) from error


@router.post("/arrival")
def arrival(body: ArrivalCommand, user: AdminUser = Depends(get_current_user),
            service: DeliveryTimePort = Depends(delivery_time_service)) -> dict[str, Any]:
    try:
        return service.command("record_arrival", canonical(body), user.username)
    except StoreReceiptError as error:
        raise failure(error) from error


@router.get("/place")
def read(load_operation_id: Annotated[str, Query(min_length=1, max_length=100)],
         store_address: Annotated[str, Query(min_length=1, max_length=255)],
         user: AdminUser = Depends(get_current_user), service: DeliveryTimePort = Depends(delivery_time_service)) -> dict[str, Any]:
    try:
        return service.read(load_operation_id, store_address, user.username)
    except StoreReceiptError as error:
        raise failure(error) from error


@router.get("/kpis")
def report(warehouse_id: Annotated[int, Query(gt=0)], start_at: AwareDatetime, finish_at: AwareDatetime,
           user: AdminUser = Depends(get_current_user), service: DeliveryTimePort = Depends(delivery_time_service)) -> dict[str, Any]:
    if finish_at <= start_at or finish_at - start_at > timedelta(days=31):
        raise HTTPException(422, "DELIVERY_KPI_WINDOW_BOUND_31_DAYS")
    try:
        return service.report(warehouse_id, start_at.astimezone(timezone.utc).isoformat(timespec="microseconds"),
            finish_at.astimezone(timezone.utc).isoformat(timespec="microseconds"), user.username)
    except StoreReceiptError as error:
        raise failure(error) from error
