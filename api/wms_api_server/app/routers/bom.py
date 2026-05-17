from datetime import date

from fastapi import APIRouter, Depends, HTTPException

from ..auth import (
    BOM_APPROVE_PERMISSION,
    BOM_BLOCK_PERMISSION,
    BOM_EDIT_PERMISSION,
    BOM_MAKE_PRIMARY_PERMISSION,
    BOM_VIEW_PERMISSION,
    AdminUser,
    require_permission,
)
from ..schemas import (
    BomCalculateRequest,
    BomCloneRequest,
    BomCreateRequest,
    BomLifecycleRequest,
    BomLineRequest,
    BomUpdateRequest,
    IdResponse,
)
from ..services.bom_service import BomService

router = APIRouter(prefix="/api/bom", tags=["bom"])


@router.get("")
def list_boms(
    target_articul: str | None = None,
    status: str | None = None,
    is_primary: int | None = None,
    active_on: date | None = None,
    limit: int = 100,
    _user: AdminUser = Depends(require_permission(BOM_VIEW_PERMISSION)),
) -> list[dict]:
    return BomService().list_boms(
        target_articul=target_articul,
        status=status,
        is_primary=is_primary,
        active_on=active_on,
        limit=limit,
    )


@router.post("", response_model=IdResponse)
def create_bom(
    request: BomCreateRequest,
    _user: AdminUser = Depends(require_permission(BOM_EDIT_PERMISSION)),
) -> IdResponse:
    return IdResponse(id=BomService().create_bom(request))


@router.get("/default")
def find_default_bom(
    target_articul: str,
    planned_date: date | None = None,
    target_mod_id: int | None = None,
    ware_id: int | None = None,
    production_line: str | None = None,
    _user: AdminUser = Depends(require_permission(BOM_VIEW_PERMISSION)),
) -> dict:
    bom = BomService().find_primary(
        target_articul=target_articul,
        planned_date=planned_date,
        target_mod_id=target_mod_id,
        ware_id=ware_id,
        production_line=production_line,
    )
    if not bom:
        raise HTTPException(status_code=404, detail="Primary BOM not found.")
    return bom


@router.get("/{bom_id}")
def get_bom(
    bom_id: int,
    _user: AdminUser = Depends(require_permission(BOM_VIEW_PERMISSION)),
) -> dict:
    bom = BomService().get_bom(bom_id)
    if not bom:
        raise HTTPException(status_code=404, detail="BOM not found.")
    return bom


@router.patch("/{bom_id}")
def update_bom(
    bom_id: int,
    request: BomUpdateRequest,
    _user: AdminUser = Depends(require_permission(BOM_EDIT_PERMISSION)),
) -> dict[str, str]:
    BomService().update_bom(bom_id, request)
    return {"status": "ok"}


@router.post("/{bom_id}/lines", response_model=IdResponse)
def add_bom_line(
    bom_id: int,
    request: BomLineRequest,
    _user: AdminUser = Depends(require_permission(BOM_EDIT_PERMISSION)),
) -> IdResponse:
    return IdResponse(id=BomService().add_line(bom_id, request))


@router.patch("/{bom_id}/lines/{line_id}")
def update_bom_line(
    bom_id: int,
    line_id: int,
    request: BomLineRequest,
    _user: AdminUser = Depends(require_permission(BOM_EDIT_PERMISSION)),
) -> dict[str, str]:
    del bom_id
    BomService().update_line(line_id, request)
    return {"status": "ok"}


@router.delete("/{bom_id}/lines/{line_id}")
def delete_bom_line(
    bom_id: int,
    line_id: int,
    deleted_by: str | None = None,
    _user: AdminUser = Depends(require_permission(BOM_EDIT_PERMISSION)),
) -> dict[str, str]:
    del bom_id
    BomService().delete_line(line_id, deleted_by=deleted_by)
    return {"status": "ok"}


@router.post("/{bom_id}/approve")
def approve_bom(
    bom_id: int,
    request: BomLifecycleRequest,
    _user: AdminUser = Depends(require_permission(BOM_APPROVE_PERMISSION)),
) -> dict[str, str]:
    BomService().approve_bom(bom_id, user_name=request.user_name)
    return {"status": "ok"}


@router.post("/{bom_id}/block")
def block_bom(
    bom_id: int,
    request: BomLifecycleRequest,
    _user: AdminUser = Depends(require_permission(BOM_BLOCK_PERMISSION)),
) -> dict[str, str]:
    BomService().block_bom(bom_id, reason=request.reason, user_name=request.user_name)
    return {"status": "ok"}


@router.post("/{bom_id}/archive")
def archive_bom(
    bom_id: int,
    request: BomLifecycleRequest,
    _user: AdminUser = Depends(require_permission(BOM_BLOCK_PERMISSION)),
) -> dict[str, str]:
    BomService().archive_bom(bom_id, reason=request.reason, user_name=request.user_name)
    return {"status": "ok"}


@router.post("/{bom_id}/make-primary")
def make_primary(
    bom_id: int,
    request: BomLifecycleRequest,
    _user: AdminUser = Depends(require_permission(BOM_MAKE_PRIMARY_PERMISSION)),
) -> dict[str, str]:
    BomService().make_primary(bom_id, user_name=request.user_name)
    return {"status": "ok"}


@router.post("/{bom_id}/clone", response_model=IdResponse)
def clone_bom(
    bom_id: int,
    request: BomCloneRequest,
    _user: AdminUser = Depends(require_permission(BOM_EDIT_PERMISSION)),
) -> IdResponse:
    return IdResponse(id=BomService().clone_bom(bom_id, request))


@router.post("/{bom_id}/calculate")
def calculate_bom(
    bom_id: int,
    request: BomCalculateRequest,
    _user: AdminUser = Depends(require_permission(BOM_VIEW_PERMISSION)),
) -> dict:
    return BomService().calculate(bom_id, request)
