"""Versioned incident review and configured CCTV links; quantities remain behind the root."""
from typing import Any, Literal, Protocol
from fastapi import APIRouter, Depends, Path, Query
from pydantic import BaseModel, ConfigDict, Field

class InvestigationUser(Protocol):
    username: str

class CameraInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    warehouse: int = Field(strict=True, gt=0)
    cell: str = Field(min_length=1, max_length=60)
    viewpoint: str = Field(min_length=1, max_length=80)
    expected_version: int = Field(strict=True, ge=0)
    archive_uri_template: str = Field(min_length=1, max_length=2000)
    stored_time_offset: str = Field(default="+03:00", pattern=r"^[+-][0-1][0-9]:[0-5][0-9]$")
    before_seconds: int = Field(strict=True, default=120, ge=0, le=3600)
    after_seconds: int = Field(strict=True, default=120, ge=0, le=3600)
    active: bool = True

class InvestigationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(strict=True, ge=0)
    offline_event_id: str = Field(min_length=1, max_length=100)
    status: Literal["REVIEWING", "CLOSED"]
    note: str = Field(min_length=1, max_length=1000)
    video_uri: str | None = Field(default=None, max_length=1500)

class InvestigationPort(Protocol):
    def camera_settings(self,warehouse: int,cell: str) -> list[dict[str,Any]]: ...
    def read(self, short_id: int) -> dict[str, Any]: ...
    def review(self, short_id: int, request: InvestigationInput, actor: str) -> dict[str, Any]: ...
    def configure(self, request: CameraInput, actor: str) -> dict[str, Any]: ...

def investigation_view() -> InvestigationUser:
    raise RuntimeError("Investigation view not wired")

def investigation_edit() -> InvestigationUser:
    raise RuntimeError("Investigation review not wired")

def camera_edit() -> InvestigationUser:
    raise RuntimeError("Camera configuration not wired")

def investigation_service() -> InvestigationPort:
    raise RuntimeError("Investigation service not wired")

router = APIRouter(prefix="/api/inventory", tags=["short-investigation"])

@router.get("/shorts/{short_id}/investigation")
def read(short_id: int = Path(gt=0), user: InvestigationUser = Depends(investigation_view),
         service: InvestigationPort = Depends(investigation_service)) -> dict[str, Any]:
    return service.read(short_id)

@router.post("/shorts/{short_id}/investigation")
def review(request: InvestigationInput, short_id: int = Path(gt=0),
           user: InvestigationUser = Depends(investigation_edit),
           service: InvestigationPort = Depends(investigation_service)) -> dict[str, Any]:
    return service.review(short_id, request, user.username)

@router.put("/cctv-viewpoints")
def configure(request: CameraInput, user: InvestigationUser = Depends(camera_edit),
              service: InvestigationPort = Depends(investigation_service)) -> dict[str, Any]:
    return service.configure(request, user.username)

@router.get("/cctv-viewpoints")
def camera_settings(warehouse: int=Query(gt=0),cell: str=Query(min_length=1,max_length=60),
                    user: InvestigationUser=Depends(camera_edit),
                    service: InvestigationPort=Depends(investigation_service))->list[dict[str,Any]]:
    return service.camera_settings(warehouse,cell)
