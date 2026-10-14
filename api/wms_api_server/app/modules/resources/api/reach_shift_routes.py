"""Typed shift schedule derived from the existing warehouse shift."""
from typing import Any, Protocol
from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel, ConfigDict, Field

class ShiftUser(Protocol):
    username: str

class ReachShiftInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    main_drivers: int = Field(strict=True, ge=1, le=200)
    duty_drivers: int = Field(strict=True, ge=1, le=2)

class ReachShiftPort(Protocol):
    def read(self, base_shift_id: int) -> dict[str, Any]: ...
    def create(self, base_shift_id: int, main_drivers: int, duty_drivers: int, actor: str) -> dict[str, Any]: ...

def reach_shift_view() -> ShiftUser:
    raise RuntimeError("Shift view not wired")

def reach_shift_edit() -> ShiftUser:
    raise RuntimeError("Shift edit not wired")

def reach_shift_service() -> ReachShiftPort:
    raise RuntimeError("Shift planning not wired")

router = APIRouter(prefix="/api/resources/reach-shifts", tags=["reach-shifts"])

@router.get("/{base_shift_id}")
def read(base_shift_id: int = Path(gt=0), user: ShiftUser = Depends(reach_shift_view),
         service: ReachShiftPort = Depends(reach_shift_service)) -> dict[str, Any]:
    return service.read(base_shift_id)

@router.post("/{base_shift_id}")
def create(request: ReachShiftInput, base_shift_id: int = Path(gt=0),
           user: ShiftUser = Depends(reach_shift_edit),
           service: ReachShiftPort = Depends(reach_shift_service)) -> dict[str, Any]:
    return service.create(base_shift_id, request.main_drivers, request.duty_drivers, user.username)
