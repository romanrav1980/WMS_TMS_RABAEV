from typing import Any
from fastapi import APIRouter,Depends
from ...platform.public import AdminUser,require_permission

router=APIRouter(prefix="/api/integrations/regulatory",tags=["regulatory"])
def regulatory_runtime_service() -> dict[str,Any]:
    raise RuntimeError("Regulatory runtime status not wired")

@router.get("/runtime")
def runtime(user: AdminUser=Depends(require_permission("external_outbox_view")),status: dict[str,Any]=Depends(regulatory_runtime_service)) -> dict[str,Any]:
    return status
