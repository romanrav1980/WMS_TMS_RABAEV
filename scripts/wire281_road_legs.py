from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/transport/contracts_preflight.py");s=p.read_text(encoding="utf-8").replace("class TransportPreflightPort(Protocol):","class TransportPreflightPort(Protocol):\n    def road_legs(self,trip: int,depot: str,max_age: int,actor: str) -> dict[str,Any]: ...");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py");s=p.read_text(encoding="utf-8")
s+="\n    def road_legs(self,trip: int,depot: str,max_age: int,actor: str) -> dict[str,Any]:\n        from .road_leg_estimate import road_leg_estimate\n        return road_leg_estimate(self.gateway,trip,depot,max_age,actor)\n";out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/api/preflight_routes.py");s=p.read_text(encoding="utf-8").replace("from fastapi import APIRouter, Depends, HTTPException","from fastapi import APIRouter, Depends, HTTPException, Query")
s+="""
@router.get("/trips/{trip_id}/road-legs")
def road_legs(trip_id: int,depot_address: str=Query(min_length=1,max_length=200),max_age_hours: int=Query(default=24,ge=1,le=720),
              user: AdminUser=Depends(require_permission("transport_dispatch_edit")),
              service: TransportPreflightPort=Depends(transport_preflight_service)) -> dict:
    if trip_id<1 or not depot_address.strip():raise HTTPException(422,"Positive trip and explicit depot address required")
    try:return service.road_legs(trip_id,depot_address,max_age_hours,user.username)
    except TransportPlanError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc
""";out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
