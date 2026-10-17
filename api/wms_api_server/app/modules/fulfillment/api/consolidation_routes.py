"""Authenticated identity only; Oracle verifies current target and source authority."""
from typing import Annotated, Literal
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, ConfigDict, Field, field_validator
from ...platform.public import AdminUser, get_current_user
from ..contracts_consolidation import ConsolidationError, ConsolidationPort, consolidation_service

router = APIRouter(prefix="/api/consolidation-plans", tags=["consolidation-plans"])
PlanId = Annotated[str, Path(pattern=r"^[A-Za-z0-9_.:-]{1,100}$")]


class Command(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    operation_id: str = Field(pattern=r"^[A-Za-z0-9_.:-]{1,100}$")
    expected_version: int = Field(ge=0)
    reason: str = Field(min_length=1, max_length=1000)


class Save(Command):
    root_identifier: str = Field(min_length=1, max_length=200)
    warehouse_id: int = Field(gt=0)
    cell: str = Field(min_length=1, max_length=60)
    fulfillment_ids: list[Annotated[int, Field(gt=0)]] = Field(min_length=1, max_length=200)

    @field_validator("root_identifier", "cell")
    @classmethod
    def identifiers(cls, value: str, info: object) -> str:
        limit = 60 if getattr(info, "field_name", None) == "cell" else 200
        if value.strip() != value or len(value.encode("utf-8")) > limit:
            raise ValueError("Identifier whitespace or UTF-8 byte bound exceeded")
        return value

    @field_validator("fulfillment_ids")
    @classmethod
    def distinct_members(cls, value: list[int]) -> list[int]:
        if len(value) != len(set(value)):
            raise ValueError("Duplicate fulfillment ID")
        return sorted(value)


def invoke(service: ConsolidationPort, plan: str, actor: str, body: dict | None = None) -> dict:
    try:
        return service.read(plan, actor) if body is None else service.command(plan, body, actor)
    except ConsolidationError as error:
        raise HTTPException(error.status, dict(code=error.code, operation_id=error.operation_id,
            outcome_confirmed=not error.uncertain, retry_same_operation_id=bool(error.operation_id and error.uncertain))) from error


@router.get("/{plan_id}")
def read(plan_id: PlanId, user: AdminUser = Depends(get_current_user),
         service: ConsolidationPort = Depends(consolidation_service)) -> dict:
    return invoke(service, plan_id, user.username)


@router.get("")
def page(warehouse_id: Annotated[int, Query(gt=0)],
         after: Annotated[str | None, Query(pattern=r"^[A-Za-z0-9_.:-]{1,100}$")] = None,
         limit: Annotated[int, Query(ge=1, le=50)] = 30,
         status: Literal["ACTIVE", "CANCELLED", "ALL"] = "ACTIVE",
         user: AdminUser = Depends(get_current_user),
         service: ConsolidationPort = Depends(consolidation_service)) -> dict:
    try:
        return service.page(warehouse_id, user.username, after, limit, status)
    except ConsolidationError as error:
        raise HTTPException(error.status, dict(code=error.code, outcome_confirmed=True)) from error


@router.put("/{plan_id}")
def save(plan_id: PlanId, body: Save, user: AdminUser = Depends(get_current_user),
         service: ConsolidationPort = Depends(consolidation_service)) -> dict:
    return invoke(service, plan_id, user.username, dict(body.model_dump(), command_type="SAVE"))


@router.post("/{plan_id}/cancel")
def cancel(plan_id: PlanId, body: Command, user: AdminUser = Depends(get_current_user),
           service: ConsolidationPort = Depends(consolidation_service)) -> dict:
    return invoke(service, plan_id, user.username, dict(body.model_dump(), command_type="CANCEL"))
