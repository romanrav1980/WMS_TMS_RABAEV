from pathlib import Path
p=Path("api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py");v=p.read_text(encoding="utf-8");anchor="    def conduct_transport_cost("
assert "def transport_costs("not in v
v=v.replace(anchor,'''    def transport_costs(self,trip: int,ware: int,actor: str)->dict[str,Any]:
        from .transport_cost_read import transport_costs
        return transport_costs(self.gateway,trip,ware,actor)

'''+anchor,1);p.write_text(v,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/finance/contracts.py");v=p.read_text(encoding="utf-8")
v=v.replace("    def conduct_transport_cost(","    def transport_costs(self,trip: int,ware: int,actor: str)->dict[str,Any]: ...\n    def conduct_transport_cost(",1);p.write_text(v,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py");v=p.read_text(encoding="utf-8")
v+='''

@router.get("/trips/{trip_id}/transport-costs")
def transport_costs(trip_id: int,warehouse_id: int=Query(gt=0),
                    user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                    service: LogisticsCostPort=Depends(logistics_cost_service))->dict[str,Any]:
    if trip_id<1:raise HTTPException(422,"Positive trip ID required")
    try:return service.transport_costs(trip_id,warehouse_id,user.username)
    except LogisticsCostError as exc:raise failure(exc)from exc
''';p.write_text(v,encoding="utf-8")
p=Path("admin/wms_admin_frontend/src/features/finance/TransportCostPreview.tsx");v=p.read_text(encoding="utf-8")
v='import {TransportCostConduct} from "./TransportCostConduct";\n'+v
v=v.replace("cost_posted:false;lines:","cost_posted:false;norm:{version:number}|null;lines:")
v=v.replace('   <p>Итого:', '   {current.complete&&current.norm&&current.currency&&<TransportCostConduct trip={trip} warehouse={warehouse} source={source} version={current.norm.version} currency={current.currency} onRefresh={read}/>}\n   <p>Итого:')
p.write_text(v,encoding="utf-8")
print("585 native conduct/read API and durable existing billing action connected.")
