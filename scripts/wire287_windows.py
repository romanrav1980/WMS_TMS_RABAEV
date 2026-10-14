from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/transport/infrastructure/road_leg_estimate.py");s=p.read_text(encoding="utf-8")
s=s.replace("def read_snapshot(cur: Any,trip: int,depot: str,max_age: int,actor: str) -> dict:","def read_snapshot(cur: Any,trip: int,depot: str,max_age: int,actor: str,context: dict | None=None) -> dict:")
old='    out=cur.var(oracledb.DB_TYPE_CLOB);cur.callproc("RRL_TT_ROUTE_API.context",[trip,actor,out])\n    context=read_oracle_json(out.getvalue());stops,issues=ordered_stops(context["source"]["members"])'
new='    if context is None:\n        out=cur.var(oracledb.DB_TYPE_CLOB);cur.callproc("RRL_TT_ROUTE_API.context",[trip,actor,out]);context=read_oracle_json(out.getvalue())\n    stops,issues=ordered_stops(context["source"]["members"])'
assert old in s;s=s.replace(old,new);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/transport/contracts_preflight.py");s=p.read_text(encoding="utf-8").replace("class TransportPreflightPort(Protocol):","class TransportPreflightPort(Protocol):\n    def delivery_windows(self,trip: int,depot: str,max_age: int,zone: str,actor: str) -> dict[str,Any]: ...");out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py");s=p.read_text(encoding="utf-8");needle="    def road_legs(self,trip: int,depot: str,max_age: int,actor: str) -> dict[str,Any]:"
assert needle in s;s=s.replace(needle,'    def delivery_windows(self,trip: int,depot: str,max_age: int,zone: str,actor: str) -> dict[str,Any]:\n        from .delivery_window_preview import delivery_window_preview\n        return delivery_window_preview(self.gateway,trip,depot,max_age,zone,actor)\n\n'+needle);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/transport/api/preflight_routes.py");s=p.read_text(encoding="utf-8");s+='''

@router.get("/trips/{trip_id}/delivery-windows")
def delivery_windows(trip_id: int,time_zone: Literal["UTC","Europe/Moscow","Asia/Tbilisi"],
                     depot_address: str=Query(default="",max_length=200),max_age_hours: int=Query(default=24,ge=1,le=720),
                     user: AdminUser=Depends(require_permission("transport_dispatch_edit")),
                     service: TransportPreflightPort=Depends(transport_preflight_service)) -> dict:
    if trip_id<1:raise HTTPException(422,"Positive trip required")
    try:return service.delivery_windows(trip_id,depot_address.strip(),max_age_hours,time_zone,user.username)
    except TransportPlanError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc
'''
out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
