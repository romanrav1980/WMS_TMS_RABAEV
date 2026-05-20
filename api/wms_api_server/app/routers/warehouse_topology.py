from fastapi import APIRouter, Depends, HTTPException

from ..auth import (
    AdminUser,
    PICK_ROUTE_ADMIN_EDIT_PERMISSION,
    PICK_ROUTE_ADMIN_PUBLISH_PERMISSION,
    PICK_ROUTE_ADMIN_VIEW_PERMISSION,
    WAREHOUSE_TOPOLOGY_EDIT_PERMISSION,
    WAREHOUSE_TOPOLOGY_PUBLISH_PERMISSION,
    WAREHOUSE_TOPOLOGY_VIEW_PERMISSION,
    require_permission,
)
from ..schemas import (
    PickRouteBuildRequest,
    TopologyCellPatchRequest,
    TopologyDistanceRecalculateRequest,
    TopologyGateGenerateRequest,
    WarehouseTopologyCreateRequest,
    WarehouseTopologyGenerateRequest,
)
from ..services.warehouse_topology_service import WarehouseTopologyService

router = APIRouter(prefix="/api/admin", tags=["warehouse-topology"])


@router.get("/warehouse-topologies")
def list_topologies(
    ware_id: int | None = None,
    status: str | None = None,
    _user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_VIEW_PERMISSION)),
) -> list[dict]:
    return WarehouseTopologyService().list_topologies(ware_id=ware_id, status=status)


@router.post("/warehouse-topologies")
def create_topology(
    request: WarehouseTopologyCreateRequest,
    user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION)),
) -> dict[str, int]:
    request.created_by = request.created_by or user.username
    topology_id = WarehouseTopologyService().create_topology(request)
    return {"topology_id": topology_id}


@router.get("/warehouse-topologies/{topology_id}/map")
def get_topology_map(
    topology_id: int,
    _user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_VIEW_PERMISSION)),
) -> dict:
    topology_map = WarehouseTopologyService().get_topology_map(topology_id)
    if not topology_map:
        raise HTTPException(status_code=404, detail="Warehouse topology not found.")
    return topology_map


@router.post("/warehouse-topologies/{topology_id}/generate-cells")
def generate_cells(
    topology_id: int,
    request: WarehouseTopologyGenerateRequest,
    user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION)),
) -> dict[str, int]:
    request.updated_by = request.updated_by or user.username
    return WarehouseTopologyService().generate_cells(topology_id, request)


@router.post("/warehouse-topologies/{topology_id}/generate-gates")
def generate_gates(
    topology_id: int,
    request: TopologyGateGenerateRequest,
    user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION)),
) -> dict[str, int]:
    request.updated_by = request.updated_by or user.username
    return WarehouseTopologyService().generate_gates(topology_id, request)


@router.post("/warehouse-topologies/{topology_id}/distances/recalculate")
def recalculate_gate_distances(
    topology_id: int,
    request: TopologyDistanceRecalculateRequest,
    user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION)),
) -> dict[str, int]:
    request.updated_by = request.updated_by or user.username
    return WarehouseTopologyService().recalculate_gate_distances(topology_id, request)


@router.post("/warehouse-topologies/{topology_id}/validate")
def validate_topology(
    topology_id: int,
    _user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_VIEW_PERMISSION)),
) -> dict:
    return WarehouseTopologyService().validate_topology(topology_id)


@router.post("/warehouse-topologies/{topology_id}/publish")
def publish_topology(
    topology_id: int,
    user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_PUBLISH_PERMISSION)),
) -> dict[str, int | str]:
    WarehouseTopologyService().publish_topology(topology_id, user.username)
    return {"topology_id": topology_id, "status": "PUBLISHED"}


@router.patch("/topology-cells/{topology_cell_id}")
def patch_topology_cell(
    topology_cell_id: int,
    request: TopologyCellPatchRequest,
    user: AdminUser = Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION)),
) -> dict[str, int]:
    request.updated_by = request.updated_by or user.username
    WarehouseTopologyService().patch_cell(topology_cell_id, request)
    return {"topology_cell_id": topology_cell_id}


@router.get("/pick-routes")
def list_admin_pick_routes(
    topology_id: int | None = None,
    ware_id: int | None = None,
    status: str | None = None,
    _user: AdminUser = Depends(require_permission(PICK_ROUTE_ADMIN_VIEW_PERMISSION)),
) -> list[dict]:
    return WarehouseTopologyService().list_pick_routes(topology_id=topology_id, ware_id=ware_id, status=status)


@router.post("/pick-routes/build")
def build_pick_route(
    request: PickRouteBuildRequest,
    user: AdminUser = Depends(require_permission(PICK_ROUTE_ADMIN_EDIT_PERMISSION)),
) -> dict[str, int]:
    request.updated_by = request.updated_by or user.username
    return WarehouseTopologyService().build_pick_route(request)


@router.post("/pick-routes/{pick_route_id}/publish")
def publish_pick_route(
    pick_route_id: int,
    user: AdminUser = Depends(require_permission(PICK_ROUTE_ADMIN_PUBLISH_PERMISSION)),
) -> dict[str, int | str]:
    WarehouseTopologyService().publish_pick_route(pick_route_id, user.username)
    return {"pick_route_id": pick_route_id, "status": "PUBLISHED"}
