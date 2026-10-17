"""Picker intent and a distinct controller authorize physical reconciliation."""
from typing import Any
from fastapi import APIRouter, Depends
from ...platform.public import AdminUser, get_current_user
from ..contracts_assembly_scale import AssemblyScalePort, assembly_scale_service, AssemblyScaleError
from ..contracts_assembly_recovery import AssemblyReconciliationRequest, AssemblyReconciliationAuthorization
from .assembly_scale_routes import failure
router = APIRouter(prefix="/api/inventory/assembly-scale", tags=["assembly-recovery"])


@router.post("/sessions/{session}/reconciliations")
def request_reconciliation(session: str, body: AssemblyReconciliationRequest,
                           user: AdminUser = Depends(get_current_user),
                           service: AssemblyScalePort = Depends(assembly_scale_service)) -> dict[str, Any]:
    try:
        return service.request_reconciliation(session, body, user.username)
    except AssemblyScaleError as exc:
        raise failure(exc) from exc


@router.post("/reconciliations/{identity}/authorize")
def authorize_reconciliation(identity: str, body: AssemblyReconciliationAuthorization,
                             user: AdminUser = Depends(get_current_user),
                             service: AssemblyScalePort = Depends(assembly_scale_service)) -> dict[str, Any]:
    try:
        result = service.authorize_reconciliation(identity, body, user.username)
        return {**result, "operation_id": body.operation_id}
    except AssemblyScaleError as exc:
        raise failure(exc) from exc


@router.get("/reconciliations/{identity}")
def read_reconciliation(identity: str, user: AdminUser = Depends(get_current_user),
                        service: AssemblyScalePort = Depends(assembly_scale_service)) -> dict[str, Any]:
    try:
        return service.read_reconciliation(identity, user.username)
    except AssemblyScaleError as exc:
        raise failure(exc) from exc
