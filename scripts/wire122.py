from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py");s=p.read_text(encoding="utf-8")
if "def prepare_onward(" not in s:s=s.replace("    def queue(","    def prepare_onward(self, operation_id: str, receipt_id: str, reason: str, reference: str, actor: str) -> dict[str, Any]: ...\n    def queue(",1)
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");s=p.read_text(encoding="utf-8")
if "def prepare_onward(" not in s:s=s.replace("    def queue(",'''    def prepare_onward(self, operation_id: str, receipt_id: str, reason: str, reference: str, actor: str) -> dict[str, Any]:
        from .interwarehouse_onward import InterwarehouseOnward
        return InterwarehouseOnward(self.gateway).prepare(operation_id,receipt_id,reason,reference,actor)

    def queue(''',1)
s=s.replace("CUSTODY_RELEASE_OPERATION_ID from RRL_INTERWARE_PLAN p","CUSTODY_RELEASE_OPERATION_ID,(select b.ST_IDENTIFIER from RRL_INTERWARE_ONWARD_BIND b join RRL_INTERWARE_RECEIPT r on r.OPERATION_ID=b.RECEIPT_OPERATION_ID where r.PLAN_OPERATION_ID=p.OPERATION_ID) ONWARD_ST_IDENTIFIER from RRL_INTERWARE_PLAN p")
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py");s=p.read_text(encoding="utf-8")
if "def prepare_onward(" not in s:s+='''
class OnwardPlan(PlacementPlan):
    reason: str = Field(strict=True,min_length=1,max_length=500)
    decision_reference: str = Field(strict=True,min_length=1,max_length=60)

@router.post("/prepare-onward")
def prepare_onward(body: OnwardPlan,user: AdminUser=Depends(require_permission("outgoing_pallet_edit")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:
    try:
        return service.prepare_onward(body.operation_id,body.receipt_operation_id,body.reason,body.decision_reference,user.username)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id,"outcome_confirmed":exc.status==409}) from exc
'''
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_onward.py");s=p.read_text(encoding="utf-8")
s=s.replace("from hashlib import sha256","from hashlib import sha256\nfrom decimal import Decimal",1)
s=s.replace("r.REMAIN=to_number(:qty,'999999999999999999999999999D999999999','NLS_NUMERIC_CHARACTERS=''.,''')","r.REMAIN=:qty")
s=s.replace("receipt=receipt_id,dock=dock,qty=qty,unit=unit)","receipt=receipt_id,dock=dock,qty=Decimal(qty),unit=unit)")
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
