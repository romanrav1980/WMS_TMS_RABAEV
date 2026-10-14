from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");s=p.read_text(encoding="utf-8");s+='''
    def receive_recovery(self,operation: str,approval_id: str,metadata: dict,actor: str) -> dict:
        from ..domain.mark_identity import normalize_unit_scan_codes
        metadata=dict(metadata);scans=metadata.pop("scans",[])
        if scans:metadata["unit_scans"]=normalize_unit_scan_codes(scans)
        return self.posting.post(StockCommand(operation_id=operation,command_type="INTERWARE_SHORTAGE_RECOVER",actor=actor,source={"approval_operation_id":approval_id},lines=(),metadata=metadata))
''';out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py");s=p.read_text(encoding="utf-8").replace("class InterwarehousePort(Protocol):","class InterwarehousePort(Protocol):\n    def receive_recovery(self,operation: str,approval_id: str,metadata: dict,actor: str) -> dict[str,Any]: ...",1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py");s=p.read_text(encoding="utf-8");s+='''
class RecoveryReceipt(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    approval_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    receipt_pallet_identifier: str=Field(strict=True,min_length=1,max_length=50)
    quantity: str=Field(strict=True,min_length=1,max_length=60)
    gross_weight_kg: str=Field(strict=True,min_length=1,max_length=60)
    scan_source_pallet: str=Field(strict=True,min_length=1,max_length=200)
    scan_pallet: str=Field(strict=True,min_length=1,max_length=200)
    scan_cell: str=Field(strict=True,min_length=1,max_length=60)
    scan_article: str=Field(strict=True,min_length=1,max_length=160)
    article: str=Field(strict=True,min_length=1,max_length=160)
    base_uom: str=Field(strict=True,min_length=1,max_length=20)
    discrepancy_reason: str=Field(strict=True,min_length=8,max_length=1000)
    discrepancy_reference: str=Field(strict=True,min_length=1,max_length=255)
    scans: list[UnitScan]=Field(default_factory=list,max_length=20000)

@router.post("/recovery-receipts")
def receive_recovery(body: RecoveryReceipt,user: AdminUser=Depends(require_permission("interwarehouse_receive")),
                     service: InterwarehousePort=Depends(interwarehouse_service)) -> dict:
    from ..contracts_stock import StockPostingError
    try:return service.receive_recovery(body.operation_id,body.approval_operation_id,body.model_dump(exclude={"operation_id","approval_operation_id"},exclude_defaults=True),user.username)
    except ValueError as exc:raise HTTPException(422,str(exc))from exc
    except StockPostingError as exc:
        confirmed=exc.oracle_code is not None and 20800<=exc.oracle_code<=20999
        raise HTTPException(403 if exc.oracle_code==20882 else 409 if confirmed else 503,{"code":exc.code,"message":exc.rule_reason or str(exc),"operation_id":body.operation_id,"outcome_confirmed":confirmed})from exc
''';out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
