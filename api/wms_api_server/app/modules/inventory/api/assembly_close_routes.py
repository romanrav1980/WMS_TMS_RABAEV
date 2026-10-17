"""Terminal identity only; no admin-login requirement or browser-supplied actor."""
from typing import Any
from fastapi import APIRouter, Depends
from ...platform.public import AdminUser, get_current_user
from ..contracts_assembly_close import AssemblyCloseInput, AssemblyClosePort, assembly_close_service

router=APIRouter(prefix="/api/inventory/assembly-scale",tags=["incremental-assembly"])

@router.post("/sessions/{session}/close")
def close(session: str, body: AssemblyCloseInput, user: AdminUser=Depends(get_current_user),
          service: AssemblyClosePort=Depends(assembly_close_service)) -> dict[str,Any]:
    return service.close(session,body,user.username)
