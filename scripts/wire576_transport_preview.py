from pathlib import Path
p=Path("api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py")
v=p.read_text(encoding="utf-8");anchor="    def transport_facts("
assert "def transport_cost_preview("not in v
v=v.replace(anchor,'''    def transport_cost_preview(self,trip: int,ware: int,price_id: int,actor: str)->dict[str,Any]:
        from .transport_cost_preview import preview_transport_cost
        with self.gateway.transaction("Explain immutable transport cost")as cursor:
            cursor.execute("set transaction read only")
            return preview_transport_cost(cursor,trip,ware,price_id,actor)

'''+anchor,1);p.write_text(v,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/finance/contracts.py");v=p.read_text(encoding="utf-8");anchor="    def transport_facts(";assert anchor in v
v=v.replace(anchor,"    def transport_cost_preview(self,trip: int,ware: int,price_id: int,actor: str)->dict[str,Any]: ...\n"+anchor,1);p.write_text(v,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py");v=p.read_text(encoding="utf-8")
v+='''

@router.get("/trips/{trip_id}/transport-cost-preview")
def transport_cost_preview(trip_id: int,warehouse_id: int=Query(gt=0),source_price_id: int=Query(gt=0),
                           user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                           service: LogisticsCostPort=Depends(logistics_cost_service))->dict[str,Any]:
    if trip_id<1:raise HTTPException(422,"Positive trip ID required")
    try:return service.transport_cost_preview(trip_id,warehouse_id,source_price_id,user.username)
    except LogisticsCostError as exc:raise failure(exc)from exc
''';p.write_text(v,encoding="utf-8")
