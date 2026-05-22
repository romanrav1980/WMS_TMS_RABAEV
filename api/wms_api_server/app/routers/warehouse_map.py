from fastapi import APIRouter, Depends

from ..auth import AdminUser, WAREHOUSE_TOPOLOGY_EDIT_PERMISSION, WAREHOUSE_TOPOLOGY_VIEW_PERMISSION, require_permission
from ..schemas import (
    WarehouseMapArchiveRequest,
    WarehouseMapCameraCloneRequest,
    WarehouseMapCameraLinksPatchRequest,
    WarehouseMapCameraCreateRequest,
    WarehouseMapCanvasCreateRequest,
    WarehouseMapObjectsPatchRequest,
    WarehouseMapPassagesPatchRequest,
)
from ..services.warehouse_map_service import WarehouseMapService

router = APIRouter(prefix="/api/admin/warehouse-map", tags=["warehouse-map"])


@router.get("/warehouses/{ware_id}/canvases")
def list_warehouse_map_canvases(
    ware_id: int,
    _user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_VIEW_PERMISSION)),
) -> list[dict]:
    return WarehouseMapService().list_canvases(ware_id)


@router.get("/warehouses/{ware_id}/state")
def get_warehouse_map_state(
    ware_id: int,
    canvas_id: int | None = None,
    _user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_VIEW_PERMISSION)),
) -> dict:
    return WarehouseMapService().get_warehouse_state(ware_id, canvas_id)


@router.get("/canvases/{canvas_id}")
def get_warehouse_map_canvas_state(
    canvas_id: int,
    _user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_VIEW_PERMISSION)),
) -> dict:
    return WarehouseMapService().get_canvas_state(canvas_id)


@router.post("/warehouses/{ware_id}/canvases")
def create_warehouse_map_canvas(
    ware_id: int,
    request: WarehouseMapCanvasCreateRequest,
    user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION)),
) -> dict:
    return WarehouseMapService().create_canvas(ware_id, request, user.username)


@router.post("/canvases/{canvas_id}/cameras")
def create_warehouse_map_camera(
    canvas_id: int,
    request: WarehouseMapCameraCreateRequest,
    user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION)),
) -> dict:
    return WarehouseMapService().create_camera(canvas_id, request, user.username)


@router.post("/cameras/{camera_id}/clone")
def clone_warehouse_map_camera(
    camera_id: int,
    request: WarehouseMapCameraCloneRequest,
    user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION)),
) -> dict:
    return WarehouseMapService().clone_camera(camera_id, request, user.username)


@router.post("/cameras/{camera_id}/archive")
def archive_warehouse_map_camera(
    camera_id: int,
    request: WarehouseMapArchiveRequest,
    user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION)),
) -> dict:
    return WarehouseMapService().archive_camera(camera_id, request, user.username)


@router.patch("/cameras/{camera_id}/objects")
def patch_warehouse_map_camera_objects(
    camera_id: int,
    request: WarehouseMapObjectsPatchRequest,
    user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION)),
) -> dict:
    return WarehouseMapService().replace_camera_objects(camera_id, request, user.username)


@router.patch("/cameras/{camera_id}/passages")
def patch_warehouse_map_camera_passages(
    camera_id: int,
    request: WarehouseMapPassagesPatchRequest,
    user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION)),
) -> dict:
    return WarehouseMapService().replace_camera_passages(camera_id, request, user.username)


@router.patch("/canvases/{canvas_id}/camera-links")
def patch_warehouse_map_camera_links(
    canvas_id: int,
    request: WarehouseMapCameraLinksPatchRequest,
    user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION)),
) -> dict:
    return WarehouseMapService().replace_camera_links(canvas_id, request, user.username)
