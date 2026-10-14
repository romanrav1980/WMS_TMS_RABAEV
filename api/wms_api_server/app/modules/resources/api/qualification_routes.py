"""Typed resource qualification, observed position and nearest dispatch ports."""
from typing import Any, Protocol
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

class ResourceUser(Protocol):
    username: str

class QualificationPort(Protocol):
    def qualifications(self, resource_id: int) -> list[dict[str, Any]]: ...
    def set_qualification(self, resource_id: int, task_type: str, active: bool, actor: str) -> dict[str, Any]: ...
    def position(self, session_id: int, cell: str, actor: str) -> dict[str, Any]: ...
    def warehouse(self, task_id: int, limit: int) -> list[dict[str, Any]]: ...
    def dispatch(self, task_id: int, actor: str) -> dict[str, Any]: ...

def resource_view() -> ResourceUser:
    raise RuntimeError("Resource view not wired")

def qualification_edit() -> ResourceUser:
    raise RuntimeError("Qualification edit not wired")

def resource_position_user() -> ResourceUser:
    raise RuntimeError("Resource position auth not wired")

def resource_dispatch_user() -> ResourceUser:
    raise RuntimeError("Resource dispatch auth not wired")

def qualification_service() -> QualificationPort:
    raise RuntimeError("Resource qualification service not wired")

class QualificationInput(BaseModel):
    task_type: str = Field(min_length=1, max_length=40, pattern=r"^[A-Z_]+$")
    active: bool = True

class PositionInput(BaseModel):
    cell: str = Field(min_length=1, max_length=15)

router = APIRouter(prefix="/api/resources", tags=["resource-qualification"])

@router.get("/{resource_id}/qualifications")
def list_qualifications(resource_id: int, user: ResourceUser = Depends(resource_view),
                        service: QualificationPort = Depends(qualification_service)) -> list[dict[str, Any]]:
    return service.qualifications(resource_id)

@router.put("/{resource_id}/qualifications")
def save_qualification(resource_id: int, request: QualificationInput,
                       user: ResourceUser = Depends(qualification_edit),
                       service: QualificationPort = Depends(qualification_service)) -> dict[str, Any]:
    return service.set_qualification(resource_id, request.task_type, request.active, user.username)

@router.post("/sessions/{session_id}/position")
def confirm_position(session_id: int, request: PositionInput,
                     user: ResourceUser = Depends(resource_position_user),
                     service: QualificationPort = Depends(qualification_service)) -> dict[str, Any]:
    return service.position(session_id, request.cell, user.username)

@router.get("/warehouse-tasks/{task_id}/candidates")
def nearest_candidates(task_id: int, limit: int = Query(default=10,ge=1,le=20),
                       user: ResourceUser = Depends(resource_view),
                       service: QualificationPort = Depends(qualification_service)) -> list[dict[str, Any]]:
    return service.warehouse(task_id, limit)

@router.post("/warehouse-tasks/{task_id}/dispatch-nearest")
def dispatch_nearest(task_id: int, user: ResourceUser = Depends(resource_dispatch_user),
                     service: QualificationPort = Depends(qualification_service)) -> dict[str, Any]:
    return service.dispatch(task_id, user.username)
