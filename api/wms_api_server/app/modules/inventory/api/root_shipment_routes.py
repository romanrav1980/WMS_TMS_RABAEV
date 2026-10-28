"""C-0193 public route: bind one root HU (with its CASE children) to one existing ST for one recipient."""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from ...platform.public import AdminUser, require_permission
from ..contracts_root_shipment import RootShipmentBindRequest, RootShipmentError, RootShipmentPort, root_shipment_service

router = APIRouter(prefix="/api/warehouse-hus", tags=["warehouse-hu"])


@router.post("/bind-shipment")
def bind_root_shipment(body: RootShipmentBindRequest, user: AdminUser = Depends(require_permission("case_pick_execute")),
                       service: RootShipmentPort = Depends(root_shipment_service)) -> dict[str, Any]:
    try:
        return service.bind(body, user.username)
    except RootShipmentError as exc:
        conflict = exc.code == "OPERATION_CONTENT_CONFLICT"
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc), "operation_id": body.operation_id,
                                         "outcome_confirmed": not conflict, "retry_same_operation_id": False,
                                         "operation_id_conflict": conflict}) from exc
