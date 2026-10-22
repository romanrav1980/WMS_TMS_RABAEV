"""Public boundary for existing trip loading and departure."""
from typing import Any, Protocol


class TransportLoadingError(RuntimeError):
    def __init__(self, code: str, message: str, operation_id: str = "", status: int = 409) -> None:
        self.code = code
        self.operation_id = operation_id
        self.status = status
        super().__init__(message)


class TransportLoadingPort(Protocol):
    def preview_bulk(self, identifier: str, actor: str) -> dict[str, Any]: ...
    def unload(self, operation_id: str, load_operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]: ...
    def preview_reconciliation(self, shipping_operation_id: str) -> dict[str, Any]: ...
    def reconcile(self, operation_id: str, shipping_operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]: ...
    def preview_single(self, shipment_identifier: str, actor: str | None = None) -> dict[str, Any]: ...
    def load_single(self, operation_id: str, shipment_identifier: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]: ...
    def status(self, task_id: int, actor: str) -> dict[str, Any]: ...
    def load(self, operation_id: str, identifier: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]: ...
    def depart(self, operation_id: str, task_id: int, actor: str, temperature_confirmation: dict[str, Any] | None = None) -> dict[str, Any]: ...


def transport_loading_service() -> TransportLoadingPort:
    raise RuntimeError("Transport loading service not wired")

from pydantic import BaseModel, Field

class OperationFactUpdate(BaseModel):
    fact_start: str | None = Field(None, description="ISO datetime YYYY-MM-DD HH:MM")
    fact_end: str | None = Field(None, description="ISO datetime YYYY-MM-DD HH:MM")
    note: str | None = None


from .domain.vrp_models import VrpOrder, VrpVehicle, VrpRoute, VrpPlan
from .infrastructure.vrp_schedule import extract_solver_routes
from .domain.vrp_presentation import route_payload, route_response
from .contracts_vrp import VrpRouteStop, VrpRouteItem, VrpPlanResponse, VrpSolveRequest, VrpApplyRequest
from .domain.vrp_presentation import planner_constraint_evidence
