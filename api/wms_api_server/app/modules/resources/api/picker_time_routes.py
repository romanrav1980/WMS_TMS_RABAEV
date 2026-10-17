"""Identity-only self time commands; native current actual-warehouse rights are authoritative."""
from datetime import datetime
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import AwareDatetime
from ...platform.public import AdminUser, get_current_user
from ..contracts_picker_time import PickerTimeCommand, PickerTimeError, PickerTimePort, picker_time_service

router = APIRouter(prefix="/api/resources/picker-time", tags=["picker-actual-time"])


def failure(error: PickerTimeError) -> HTTPException:
    return HTTPException(error.status, {"code": error.code, "operation_id": error.operation_id,
                                      "outcome_confirmed": False, "read_before_retry": True})


@router.get("/me/current")
def current(user: AdminUser = Depends(get_current_user), service: PickerTimePort = Depends(picker_time_service)) -> dict[str, Any]:
    try:
        return service.current(user.username)
    except PickerTimeError as error:
        raise failure(error) from error


@router.post("/me/commands", response_model=None)
def command(body: PickerTimeCommand, user: AdminUser = Depends(get_current_user),
            service: PickerTimePort = Depends(picker_time_service)) -> Any:
    try:
        result = service.command(body, user.username)
    except PickerTimeError as error:
        raise failure(error) from error
    return JSONResponse(status_code=409, content=result) if result["outcome"] == "REJECTED" else result


@router.get("/commands/{operation_id}")
def receipt(operation_id: str, user: AdminUser = Depends(get_current_user),
            service: PickerTimePort = Depends(picker_time_service)) -> dict[str, Any]:
    try:
        return service.receipt(operation_id, user.username)
    except PickerTimeError as error:
        raise failure(error) from error


@router.get("/me/window")
def window(start_at: Annotated[AwareDatetime, Query()], finish_at: Annotated[AwareDatetime, Query()],
           user: AdminUser = Depends(get_current_user), service: PickerTimePort = Depends(picker_time_service)) -> dict[str, Any]:
    try:
        return service.window(start_at, finish_at, user.username)
    except PickerTimeError as error:
        raise failure(error) from error
