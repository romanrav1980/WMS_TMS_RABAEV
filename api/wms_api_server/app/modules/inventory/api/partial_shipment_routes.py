from typing import Annotated, Protocol
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from ...platform.public import AdminUser, require_permission


class PartialLayoutPort(Protocol):
    def preview(self, task_id: int, identifier: str) -> dict: ...
    def prepare(self, task_id: int, body: dict, actor: str) -> dict: ...


router = APIRouter(prefix="/api/case-pick/tasks", tags=["partial-shipment-layout"])


def partial_layout_service() -> PartialLayoutPort:
    raise RuntimeError("Partial layout service not wired")


class PartialLayoutRequest(BaseModel):
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    pallet_identifier: str = Field(min_length=1, max_length=150)
    scan_container: str = Field(min_length=1, max_length=150)
    expected_content_version: int = Field(ge=0, strict=True)
    expected_physical_signature: str = Field(pattern=r"^[a-f0-9]{64}$")
    expected_layout_signature: str = Field(pattern=r"^[a-f0-9]{64}$")
    reason: str = Field(min_length=3, max_length=1000)
    actual_pack_counts: dict[str, Annotated[int, Field(ge=1, le=1000000000, strict=True)]] = Field(default_factory=dict, max_length=200)


@router.get("/{task_id}/partial-shipment-layout")
def preview(task_id: int, pallet_identifier: str = Query(min_length=1, max_length=150),
            _user: AdminUser = Depends(require_permission("case_pick_short_approve")),
            service: PartialLayoutPort = Depends(partial_layout_service)) -> dict:
    try:
        return service.preview(task_id, pallet_identifier)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc


@router.post("/{task_id}/partial-shipment-layout")
def prepare(task_id: int, body: PartialLayoutRequest,
            user: AdminUser = Depends(require_permission("case_pick_short_approve")),
            service: PartialLayoutPort = Depends(partial_layout_service)) -> dict:
    try:
        return service.prepare(task_id, body.model_dump(mode="json"), user.username)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
