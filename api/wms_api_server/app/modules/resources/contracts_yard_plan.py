"""Planned dock intervals of yard visits (C-0158): PLAN / MOVE / CANCEL of [from, to) on one dock of the site. A plan is not a fact."""
from datetime import datetime
from typing import Any, Protocol
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator
from .contracts_yard import Operation, YardError, wire

__all__ = ["YardPlanCreate", "YardPlanMove", "YardPlanCancel", "YardPlanPort", "yard_plan_service", "YardError", "wire"]


class _Interval(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Operation
    dock: str = Field(min_length=1, max_length=50)
    planned_from: AwareDatetime
    planned_to: AwareDatetime

    @model_validator(mode="after")
    def interval(self) -> "_Interval":
        # Seconds precision is what Oracle stores and compares; the employee sets both ends (no invented norms).
        if self.planned_to.replace(microsecond=0) <= self.planned_from.replace(microsecond=0):
            raise ValueError("The planned end must be after the planned start")
        if not self.dock.strip():
            raise ValueError("Dock is required")
        return self


class YardPlanCreate(_Interval):
    visit_id: int = Field(strict=True, gt=0)


class YardPlanMove(_Interval):
    expected_version: int = Field(strict=True, gt=0)


class YardPlanCancel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Operation
    expected_version: int = Field(strict=True, gt=0)
    reason: str = Field(min_length=3, max_length=500)


class YardPlanPort(Protocol):
    def plans(self, ware: int, actor: str, start: datetime, finish: datetime) -> dict[str, Any]: ...
    def plan(self, ware: int, body: YardPlanCreate, actor: str) -> dict[str, Any]: ...
    def move(self, ware: int, plan: int, body: YardPlanMove, actor: str) -> dict[str, Any]: ...
    def cancel(self, ware: int, plan: int, body: YardPlanCancel, actor: str) -> dict[str, Any]: ...


def yard_plan_service() -> YardPlanPort:
    raise RuntimeError("Yard dock plans are not wired")
