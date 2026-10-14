import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/finance/contracts.py");v=p.read_text(encoding="utf-8");a=v.index("    def rate(")
v=v[:a]+'''    def publish_transport_norm(self,body: dict[str,Any],actor: str)->dict[str,Any]: ...
    def transport_norm_history(self,ware: int,price_id: int,before: int|None,limit: int,actor: str)->dict[str,Any]: ...
'''+v[a:];out[str(p)]=v
p=Path("api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py");v=p.read_text(encoding="utf-8");a=v.index("    def rate(")
v=v[:a]+'''    def publish_transport_norm(self,body: dict[str,Any],actor: str)->dict[str,Any]:
        from .transport_norms import publish_transport_norm
        return publish_transport_norm(self.gateway,body,actor)

    def transport_norm_history(self,ware: int,price_id: int,before: int|None,limit: int,actor: str)->dict[str,Any]:
        from .transport_norms import transport_norm_history
        return transport_norm_history(self.gateway,ware,price_id,before,limit,actor)

'''+v[a:];out[str(p)]=v
p=Path("api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py");v=p.read_text(encoding="utf-8")
v+='''\nclass TransportNorm(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    source_price_id: int=Field(strict=True,gt=0)
    warehouse_id: int=Field(strict=True,gt=0)
    currency: str=Field(strict=True,pattern=r"^[A-Z]{3}$")
    effective_from: date
    timezone_region: str=Field(strict=True,min_length=1,max_length=64,pattern=r"^[A-Za-z0-9_/+:-]+$")
    vehicle_type: str=Field(strict=True,min_length=1,max_length=40)
    vehicle_size_class: str=Field(strict=True,min_length=1,max_length=40)
    rolling_unload_rate: str=Field(strict=True,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")
    manual_unload_rate: str=Field(strict=True,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")
    loader_rate: str=Field(strict=True,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")
    expected_version: int=Field(strict=True,ge=0)
    reason: str=Field(strict=True,min_length=1,max_length=500)
    decision_reference: str=Field(strict=True,min_length=1,max_length=60)


@router.post("/transport-norms")
def publish_transport_norm(body: TransportNorm,user: AdminUser=Depends(require_permission("create_tt_price")),
                           service: LogisticsCostPort=Depends(logistics_cost_service))->dict[str,Any]:
    try:return service.publish_transport_norm(body.model_dump(mode="json"),user.username)
    except LogisticsCostError as exc:raise failure(exc,body.operation_id)from exc


@router.get("/warehouses/{ware_id}/transport-norms/{source_price_id}/history")
def transport_norm_history(ware_id: int,source_price_id: int,before_version: int|None=Query(default=None,gt=0),
                           limit: int=Query(default=30,ge=1,le=100),
                           user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                           service: LogisticsCostPort=Depends(logistics_cost_service))->dict[str,Any]:
    try:return service.transport_norm_history(ware_id,source_price_id,before_version,limit,user.username)
    except LogisticsCostError as exc:raise failure(exc)from exc
'''
out[str(p)]=v
print(json.dumps(out))
