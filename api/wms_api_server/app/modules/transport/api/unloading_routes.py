"""Confirmed unloading is a reverse physical fact before departure."""
from typing import Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field
from ...platform.public import AdminUser, get_current_user
from ..contracts import TransportLoadingError, TransportLoadingPort, transport_loading_service
from .loading_routes import failure

router = APIRouter(prefix="/api/transport/loading", tags=["transport-loading"])


class UnloadingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(strict=True, min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    load_operation_id: str = Field(strict=True, min_length=1, max_length=100)
    expected_version: int = Field(strict=True, ge=0)
    scan_container: str = Field(strict=True, min_length=1, max_length=200)
    scan_cell: str = Field(strict=True, min_length=1, max_length=60)
    scan_vehicle: str = Field(strict=True, min_length=1, max_length=50)
    scan_dock: str = Field(strict=True, min_length=1, max_length=50)
    target_slot_id: int | None = Field(default=None, strict=True, ge=1)
    scanned_to_slot_code: str | None = Field(default=None, strict=True, min_length=1, max_length=100)
    reason: str = Field(strict=True, min_length=1, max_length=1000)


@router.post("/unload")
def unload(
    body: UnloadingRequest,
    user: AdminUser = Depends(get_current_user),
    service: TransportLoadingPort = Depends(transport_loading_service),
) -> dict[str, Any]:
    try:
        return service.unload(body.operation_id, body.load_operation_id,
                              body.model_dump(exclude={"operation_id", "load_operation_id"}, exclude_none=True), user.username)
    except TransportLoadingError as exc:
        raise failure(exc) from exc
