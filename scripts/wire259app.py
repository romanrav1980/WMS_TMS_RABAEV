from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/transport/contracts_preflight.py");s=p.read_text(encoding="utf-8").replace('    def coordination(self, trip: int, actor: str) -> dict[str, Any]: ...','    def coordination(self, trip: int, actor: str) -> dict[str, Any]: ...\n    def route_context(self, trip: int, actor: str) -> dict[str, Any]: ...\n    def apply_route_input(self, operation: str, body: dict[str, Any], actor: str) -> dict[str, Any]: ...');out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py");s=p.read_text(encoding="utf-8").replace('    def plan(self, plan: int, actor: str)', '''    def route_context(self, trip: int, actor: str) -> dict[str, Any]:
        from .route_input import route_context
        return route_context(self.gateway, trip, actor)

    def apply_route_input(self, operation: str, body: dict[str, Any], actor: str) -> dict[str, Any]:
        from .route_input import apply_route_input
        return apply_route_input(self.gateway, operation, body, actor)

    def plan(self, plan: int, actor: str)''');out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/api/preflight_routes.py");s=p.read_text(encoding="utf-8")
s+='''

class RouteInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    trip_id: int = Field(strict=True, gt=0)
    expected_version: int = Field(strict=True, ge=0)
    source_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    drive_min: int = Field(strict=True, gt=0, le=1440)
    drive_back_min: int = Field(strict=True, gt=0, le=1440)
    source_reference: str = Field(min_length=8, max_length=500)
    reason: str = Field(min_length=8, max_length=500)


@router.get("/trips/{trip_id}/route-context")
def route_context(trip_id: int, user: AdminUser = Depends(require_permission("transport_dispatch_edit")),
                  service: TransportPreflightPort = Depends(transport_preflight_service)) -> dict[str, Any]:
    if trip_id < 1:
        raise HTTPException(422, "Positive trip required")
    try:
        return service.route_context(trip_id, user.username)
    except TransportPlanError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc


@router.post("/route-inputs")
def route_input(body: RouteInput, user: AdminUser = Depends(require_permission("transport_dispatch_edit")),
                service: TransportPreflightPort = Depends(transport_preflight_service)) -> dict[str, Any]:
    try:
        return service.apply_route_input(body.operation_id, body.model_dump(exclude={"operation_id"}), user.username)
    except TransportPlanError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc
'''
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
