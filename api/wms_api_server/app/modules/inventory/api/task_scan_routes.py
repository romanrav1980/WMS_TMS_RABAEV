from ...master_data.contracts import MarkingProfileCode
"""Warehouse marking draft endpoints with injected typed ports."""
from typing import Any, Protocol
from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field

class ScanUser(Protocol):
    username: str

class ScanDraftPort(Protocol):
    def context(self, task_id: int) -> dict[str, Any]: ...
    def latest(self, task_id: int, actor: str) -> dict[str, Any] | None: ...
    def save(self, task_id: int, request: dict[str, Any], actor: str) -> dict[str, Any]: ...

def scan_view() -> ScanUser:
    raise RuntimeError("Warehouse scan view not wired")

def scan_execute() -> ScanUser:
    raise RuntimeError("Warehouse scan execute not wired")

def scan_draft_service() -> ScanDraftPort:
    raise RuntimeError("Warehouse scan drafts not wired")

class UnitScan(BaseModel):
    model_config=ConfigDict(extra="forbid")
    system_code: str=Field(min_length=1,max_length=40)
    profile_code: MarkingProfileCode
    code: str=Field(min_length=1,max_length=4000)

class ScanDraftInput(BaseModel):
    model_config=ConfigDict(extra="forbid")
    draft_id: str=Field(min_length=1,max_length=100)
    profile_signature: str=Field(pattern=r"^[A-F0-9]{64}$")
    expected_stock_version: int=Field(strict=True,ge=0)
    scans: list[UnitScan]=Field(min_length=1,max_length=10000)

router=APIRouter(prefix="/api/warehouse-tasks",tags=["warehouse-task-marking"])

@router.get("/{task_id}/scan-context")
def get_scan_context(task_id: int,user: ScanUser=Depends(scan_view),
                     service: ScanDraftPort=Depends(scan_draft_service)) -> dict[str, Any]:
    return service.context(task_id)

@router.get("/{task_id}/scan-draft")
def get_scan_draft(task_id: int,user: ScanUser=Depends(scan_execute),
                   service: ScanDraftPort=Depends(scan_draft_service)) -> dict[str, Any] | None:
    return service.latest(task_id,user.username)

@router.post("/{task_id}/scan-draft")
def save_scan_draft(task_id: int,request: ScanDraftInput,user: ScanUser=Depends(scan_execute),
                    service: ScanDraftPort=Depends(scan_draft_service)) -> dict[str, Any]:
    return service.save(task_id,request.model_dump(),user.username)
