from datetime import timedelta
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import AwareDatetime
from ...platform.public import AdminUser, get_current_user
from ..contracts_picker_kpi import PickerKpiError, PickerKpiPort, picker_kpi_service

router = APIRouter(prefix="/api/resources/picker-kpis", tags=["picker-kpi"])


@router.get("")
def window(warehouse_id: Annotated[int, Query(gt=0)], start_at: AwareDatetime, finish_at: AwareDatetime,
           operator_id: Annotated[str | None, Query(min_length=1, max_length=50)] = None,
           user: AdminUser = Depends(get_current_user),
           service: PickerKpiPort = Depends(picker_kpi_service)) -> dict[str, Any]:
    if finish_at <= start_at or finish_at - start_at > timedelta(days=31):
        raise HTTPException(422, "KPI_WINDOW_BOUND_31_DAYS")
    try:
        return service.window(warehouse_id, start_at, finish_at, user.username, operator_id)
    except PickerKpiError as error:
        raise HTTPException(error.status, {"code": error.code}) from error
