from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/contracts_stock.py");s=p.read_text(encoding="utf-8").replace('{"INTERWARE_CUSTODY_RELEASE",','{"STORE_CUSTODY_RELEASE", "INTERWARE_CUSTODY_RELEASE",',1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/delivery/contracts.py");s=p.read_text(encoding="utf-8").replace('    def cases(', '    def release_custody(self, operation_id: str, receipt_id: str, actor: str) -> dict[str, Any]: ...\n    def cases(',1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py");s=p.read_text(encoding="utf-8").replace('    def cases(','''    def release_custody(self,operation_id: str,receipt_id: str,actor: str) -> dict[str,Any]:
        return self.post("STORE_CUSTODY_RELEASE",operation_id,{"receipt_operation_id":receipt_id},{},actor)

    def cases(''',1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py");s=p.read_text(encoding="utf-8");s+='''\nclass StoreCustodyRelease(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    receipt_operation_id: str=Field(strict=True,min_length=1,max_length=100)

@router.post("/load-custody/release")
def release_custody(body: StoreCustodyRelease,user: AdminUser=Depends(require_permission("transport_dispatch_close")),service: StoreReceiptPort=Depends(store_receipt_service)) -> dict[str,Any]:
    try:
        return service.release_custody(body.operation_id,body.receipt_operation_id,user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc
''';out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
