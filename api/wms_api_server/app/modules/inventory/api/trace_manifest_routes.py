from ...master_data.contracts import MarkingProfileCode
from typing import Any,Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field
from ...platform.public import AdminUser,require_permission
from ..contracts_trace_manifest import TraceManifestError,TraceManifestPort,trace_manifest_service

router=APIRouter(prefix="/api/inventory/trace-manifests",tags=["trace-manifests"])
class ImportManifest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    manifest_json: str=Field(strict=True,min_length=1,max_length=4*1024*1024)

@router.post("")
def import_manifest(body: ImportManifest,user: AdminUser=Depends(require_permission("trace_manifest_import")),service: TraceManifestPort=Depends(trace_manifest_service)) -> dict[str,Any]:
    try:
        return service.import_manifest(body.operation_id,body.manifest_json,user.username)
    except TraceManifestError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id,"outcome_confirmed":exc.status in {409,422}}) from exc

@router.get("/warehouses/{ware_id}")
def manifests(ware_id: int,user: AdminUser=Depends(require_permission("trace_manifest_import")),service: TraceManifestPort=Depends(trace_manifest_service)) -> list[dict[str,Any]]:
    try:
        return service.list(ware_id,user.username)
    except TraceManifestError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc

class CaptureSource(BaseModel):
    model_config=ConfigDict(extra="forbid")
    source_document_id: int=Field(strict=True,ge=1)
    article: str=Field(strict=True,min_length=1,max_length=160)
    cell: str=Field(strict=True,min_length=1,max_length=60)
    pallet_identifier: str=Field(strict=True,min_length=1,max_length=50)

def _context(service: TraceManifestPort,kind: str,body: CaptureSource,user: AdminUser) -> dict[str,Any]:
    try:
        return service.capture_context(kind,body.source_document_id,body.article,body.cell,body.pallet_identifier,user.username)
    except TraceManifestError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc

@router.post("/inventory-context")
def inventory_context(body: CaptureSource,user: AdminUser=Depends(require_permission("stock_inventory_count")),service: TraceManifestPort=Depends(trace_manifest_service)) -> dict[str,Any]:
    return _context(service,"INVENTORY",body,user)

@router.post("/mes-context")
def mes_context(body: CaptureSource,user: AdminUser=Depends(require_permission("mes_wms_bridge_apply")),service: TraceManifestPort=Depends(trace_manifest_service)) -> dict[str,Any]:
    return _context(service,"MES",body,user)

class InvalidateAggregate(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    warehouse_id: int=Field(strict=True,ge=1)
    origin_pallet_identifier: str=Field(strict=True,min_length=1,max_length=200)
    system_code: str=Field(strict=True,min_length=1,max_length=40)
    profile_code: MarkingProfileCode
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
