"""Read-only POST to bundle bounded wave IDs, not a business command."""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, PositiveInt, model_validator
from ...platform.public import AdminUser, get_current_user
from ..contracts_shift_overview import ShiftOverviewError, ShiftOverviewPort, shift_overview_service


class OverviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    warehouse_id: int = Field(strict=True, gt=0)
    wave_ids: list[PositiveInt] = Field(min_length=1, max_length=50)

    @model_validator(mode="after")
    def distinct_waves(self) -> "OverviewInput":
        if len(self.wave_ids) != len(set(self.wave_ids)):
            raise ValueError("Duplicate wave IDs are not a batch")
        return self


router = APIRouter(prefix="/api/picking", tags=["shift-overview"])


@router.post("/shift-overview")
def overview(body: OverviewInput, user: AdminUser = Depends(get_current_user),
             service: ShiftOverviewPort = Depends(shift_overview_service)) -> dict[str, Any]:
    try:
        return service.read(user.username, body.warehouse_id, body.wave_ids)
    except ShiftOverviewError as error:
        raise HTTPException(error.status, {"code": error.code}) from error
