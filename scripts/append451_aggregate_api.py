import json
from pathlib import Path
p=Path("api/wms_api_server/app/modules/inventory/api/trace_manifest_routes.py")
s=p.read_text(encoding="utf-8").replace("from typing import Any","from typing import Any,Literal")
assert "class InvalidateAggregate"not in s
s+='''
class InvalidateAggregate(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    warehouse_id: int=Field(strict=True,ge=1)
    origin_pallet_identifier: str=Field(strict=True,min_length=1,max_length=200)
    system_code: str=Field(strict=True,min_length=1,max_length=40)
    profile_code: str=Field(strict=True,min_length=1,max_length=80)
    code_hash: str=Field(strict=True,pattern=r"^[a-f0-9]{64}$")
    reason_code: Literal["OPENED","REPACKED","DAMAGED","COMPOSITION_CHANGED"]
    document_reference: str=Field(strict=True,min_length=1,max_length=200)

@router.post("/aggregations/invalidate")
def invalidate_aggregate(body: InvalidateAggregate,user: AdminUser=Depends(require_permission("trace_manifest_import")),service: TraceManifestPort=Depends(trace_manifest_service))->dict[str,Any]:
    try:
        return service.invalidate_aggregate(body.operation_id,body.model_dump(exclude={"operation_id"}),user.username)
    except TraceManifestError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id,"outcome_confirmed":exc.status in {403,409,422}})from exc

@router.get("/warehouses/{ware_id}/pallets/{origin}/aggregations")
def aggregate_lifecycle(ware_id: int,origin: str,user: AdminUser=Depends(require_permission("traceability_view")),service: TraceManifestPort=Depends(trace_manifest_service))->list[dict[str,Any]]:
    try:
        return service.aggregates(origin,ware_id,user.username)
    except TraceManifestError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc
'''
print(json.dumps({str(p):s}))
