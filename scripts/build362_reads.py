from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/finance/contracts.py");t=p.read_text();t=t.replace("    def rates(self,","    def assembly_period(self,trip: int,ware: int,region: str,actor: str) -> dict[str,Any]: ...\n    def rates(self,");out[p.as_posix()]=t
p=Path("api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py");t=p.read_text(encoding="utf-8");at=t.index("    def rates(");t=t[:at]+'''    def assembly_period(self,trip: int,ware: int,region: str,actor: str) -> dict[str,Any]:
        from .assembly_period import read_assembly_period
        return read_assembly_period(self.gateway,trip,ware,region,actor)

'''+t[at:];out[p.as_posix()]=t
p=Path("api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py");t=p.read_text(encoding="utf-8");t+='''

@router.get("/trips/{trip_id}/assembly-period")
def assembly_period(trip_id: int,warehouse_id: int=Query(gt=0),timezone_region: str=Query(min_length=1,max_length=64,pattern=r"^[A-Za-z0-9_/+:-]+$"),user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str,Any]:
    try:return service.assembly_period(trip_id,warehouse_id,timezone_region,user.username)
    except LogisticsCostError as exc:raise failure(exc)from exc
''';out[p.as_posix()]=t
p=Path("api/wms_api_server/app/modules/resources/infrastructure/case_read_model.py");t=p.read_text(encoding="utf-8");t=t.replace("                   t.STARTED_AT,","                   t.STARTED_AT,\n                   to_char(t.STARTED_AT_INSTANT,'YYYY-MM-DD\"T\"HH24:MI:SS.FF6TZH:TZM') STARTED_AT_INSTANT,\n                   t.STARTED_SHIFT_TIME_ZONE,");out[p.as_posix()]=t
print(json.dumps(out))
