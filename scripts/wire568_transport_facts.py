import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/finance/infrastructure/transport_cost_facts.py");out[str(p)]=p.read_text(encoding="utf-8").replace("u.UNLOAD_METHOD","u.METHOD")
p=Path("api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py");v=p.read_text(encoding="utf-8");assert "def transport_facts("not in v
a="    def transport_tariff_sources(";assert v.count(a)==1
v=v.replace(a,"    def transport_facts(self,trip: int,ware: int,actor: str)->dict[str,Any]:\n        from .transport_cost_facts import transport_facts\n        with self.gateway.transaction('Read immutable transport cost facts')as cursor:\n            cursor.execute('set transaction read only')\n            return transport_facts(cursor,trip,ware,actor)\n\n"+a)
out[str(p)]=v
p=Path("api/wms_api_server/app/modules/finance/contracts.py");v=p.read_text(encoding="utf-8");a="    def transport_tariff_sources(";assert v.count(a)==1
out[str(p)]=v.replace(a,"    def transport_facts(self,trip: int,ware: int,actor: str)->dict[str,Any]: ...\n"+a)
p=Path("api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py");v=p.read_text(encoding="utf-8");assert "transport-cost-facts"not in v
out[str(p)]=v+"""

@router.get("/trips/{trip_id}/transport-cost-facts")
def transport_cost_facts(trip_id: int,warehouse_id: int=Query(gt=0),
                         user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                         service: LogisticsCostPort=Depends(logistics_cost_service))->dict[str,Any]:
    if trip_id<1:raise HTTPException(422,"Укажите рейс")
    try:return service.transport_facts(trip_id,warehouse_id,user.username)
    except LogisticsCostError as exc:raise failure(exc)from exc
"""
print(json.dumps(out))
