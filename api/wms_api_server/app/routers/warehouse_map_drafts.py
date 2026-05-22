from fastapi import APIRouter, Depends

from ..auth import AdminUser, WAREHOUSE_TOPOLOGY_EDIT_PERMISSION, WAREHOUSE_TOPOLOGY_VIEW_PERMISSION, require_permission
from ..schemas import (
    WarehouseMapBulkRoleRequest,
    WarehouseMapDraftCellsPatchRequest,
    WarehouseMapDraftCreateRequest,
    WarehouseMapPickFaceAddressRequest,
    WarehouseMapSmallPickFaceGenerateRequest,
    WarehouseMapSmallPickFacePatchRequest,
    WarehouseMapSmallPickFaceRenumberRequest,
)
from ..services.warehouse_map_draft_service import WarehouseMapDraftService

router = APIRouter(prefix="/api/admin/warehouse-map-drafts", tags=["warehouse-map-drafts"])


@router.get("")
def list_warehouse_map_drafts(
    _user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_VIEW_PERMISSION)),
) -> list[dict]:
    return WarehouseMapDraftService().list_drafts()


@router.post("")
def create_warehouse_map_draft(
    request: WarehouseMapDraftCreateRequest,
    user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION)),
) -> dict:
    return WarehouseMapDraftService().create_draft(request, user.username)


@router.get("/{draft_id}")
def get_warehouse_map_draft(
    draft_id: str,
    _user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_VIEW_PERMISSION)),
) -> dict:
    return WarehouseMapDraftService().get_draft(draft_id)


@router.patch("/{draft_id}/cells")
def patch_warehouse_map_draft_cells(
    draft_id: str,
    request: WarehouseMapDraftCellsPatchRequest,
    user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION)),
) -> dict:
    return WarehouseMapDraftService().patch_cells(draft_id, request, user.username)


@router.post("/{draft_id}/bulk-role")
def apply_warehouse_map_bulk_role(
    draft_id: str,
    request: WarehouseMapBulkRoleRequest,
    user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION)),
) -> dict:
    return WarehouseMapDraftService().bulk_role(draft_id, request, user.username)


@router.post("/{draft_id}/pick-face-addresses/generate")
def generate_warehouse_map_pick_face_addresses(
    draft_id: str,
    request: WarehouseMapPickFaceAddressRequest,
    user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION)),
) -> dict:
    return WarehouseMapDraftService().generate_pick_face_addresses(draft_id, request, user.username)


@router.post("/{draft_id}/small-pick-faces/generate")
def generate_warehouse_map_small_pick_faces(
    draft_id: str,
    request: WarehouseMapSmallPickFaceGenerateRequest,
    user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION)),
) -> dict:
    return WarehouseMapDraftService().generate_small_pick_faces(draft_id, request, user.username)


@router.patch("/{draft_id}/small-pick-faces/{small_pick_face_id}")
def patch_warehouse_map_small_pick_face(
    draft_id: str,
    small_pick_face_id: str,
    request: WarehouseMapSmallPickFacePatchRequest,
    user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION)),
) -> dict:
    return WarehouseMapDraftService().patch_small_pick_face(draft_id, small_pick_face_id, request, user.username)


@router.post("/{draft_id}/small-pick-faces/renumber")
def renumber_warehouse_map_small_pick_faces(
    draft_id: str,
    request: WarehouseMapSmallPickFaceRenumberRequest,
    user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION)),
) -> dict:
    return WarehouseMapDraftService().renumber_small_pick_faces(draft_id, request, user.username)


@router.post("/{draft_id}/validate")
def validate_warehouse_map_draft(
    draft_id: str,
    _user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_VIEW_PERMISSION)),
) -> dict:
    return WarehouseMapDraftService().validate_draft(draft_id)


@router.post("/{draft_id}/publish")
def publish_warehouse_map_draft(
    draft_id: str,
    user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION)),
) -> dict:
    return WarehouseMapDraftService().publish_draft(draft_id, user.username)
