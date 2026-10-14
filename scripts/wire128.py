from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/contracts_trace_manifest.py");s=p.read_text(encoding="utf-8")
needle="    def list(self,ware_id: int,actor: str) -> list[dict[str,Any]]: ..."
s=s.replace(needle,needle+"\n    def capture_context(self,kind: str,document_id: int,article: str,cell: str,pallet: str,actor: str) -> dict[str,Any]: ...",1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/trace_sender_manifest.py");s=p.read_text(encoding="utf-8");s+="""
    def capture_context(self,kind: str,document_id: int,article: str,cell: str,pallet: str,actor: str) -> dict[str,Any]:
        from .trace_capture_context import capture_context
        return capture_context(self.gateway,kind,document_id,article,cell,pallet,actor)
""";out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/api/trace_manifest_routes.py");s=p.read_text(encoding="utf-8");s+="""
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
""";out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/receiving_marks.py");s=p.read_text(encoding="utf-8")
s=s.replace("from ..domain.mark_identity import canonical_mark","from ..domain.mark_identity import canonical_mark\nfrom ..domain.capture_policy import assert_capture_policy",1)
s=s.replace('        manifest_id=payload.get("manifest_operation_id")','        assert_capture_policy(payload,policy[0],profiles)\n        manifest_id=payload.get("manifest_operation_id")',1);out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
