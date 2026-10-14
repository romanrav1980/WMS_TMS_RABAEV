from pathlib import Path
p=Path("api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py");v=p.read_text(encoding="utf-8");anchor="    def transport_cost_preview("
assert "def conduct_transport_cost("not in v
v=v.replace(anchor,'''    def conduct_transport_cost(self,body: dict[str,Any],actor: str)->dict[str,Any]:
        from .transport_cost_preview import conduct_transport_cost
        return conduct_transport_cost(self.gateway,body,actor)

'''+anchor,1);p.write_text(v,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/finance/contracts.py");v=p.read_text(encoding="utf-8")
v=v.replace("    def transport_cost_preview(","    def conduct_transport_cost(self,body: dict[str,Any],actor: str)->dict[str,Any]: ...\n    def transport_cost_preview(",1);p.write_text(v,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py");v=p.read_text(encoding="utf-8")
v+='''

class TransportCostConduct(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    trip_id: int=Field(strict=True,gt=0)
    warehouse_id: int=Field(strict=True,gt=0)
    source_price_id: int=Field(strict=True,gt=0)
    expected_norm_version: int=Field(strict=True,gt=0)
    currency: str=Field(strict=True,pattern=r"^[A-Z]{3}$")

@router.post("/transport-costs/conduct")
def conduct_transport_cost(body: TransportCostConduct,
                           user: AdminUser=Depends(require_permission("calc_tt_price")),
                           service: LogisticsCostPort=Depends(logistics_cost_service))->dict[str,Any]:
    try:return service.conduct_transport_cost(body.model_dump(mode="json"),user.username)
    except LogisticsCostError as exc:raise failure(exc,body.operation_id)from exc
''';p.write_text(v,encoding="utf-8")
