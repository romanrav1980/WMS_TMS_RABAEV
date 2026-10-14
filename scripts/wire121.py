from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/contracts_stock.py");s=p.read_text(encoding="utf-8")
if '"INTERWARE_CUSTODY_RELEASE"' not in s:s=s.replace('{"INTERWARE_PUTAWAY_PLAN",','{"INTERWARE_CUSTODY_RELEASE", "INTERWARE_PUTAWAY_PLAN",',1)
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py");s=p.read_text(encoding="utf-8")
if "def release_custody(" not in s:s=s.replace("    def queue(","    def release_custody(self, operation_id: str, receipt_id: str, actor: str) -> dict[str, Any]: ...\n    def queue(",1)
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");s=p.read_text(encoding="utf-8")
if "def release_custody(" not in s:
 s=s.replace("    def queue(",'''    def release_custody(self, operation_id: str, receipt_id: str, actor: str) -> dict[str, Any]:
        try:
            return self.posting.post(StockCommand(operation_id=operation_id,command_type="INTERWARE_CUSTODY_RELEASE",actor=actor,source={"receipt_operation_id":receipt_id},lines=(),metadata={}))
        except oracledb.DatabaseError as exc:
            raise StockPostingError("INTERWARE_TECHNICAL_FAILURE",operation_id,getattr(exc.args[0],"code",None)) from exc

    def queue(''',1)
s=s.replace("PLACED_TASK_ID from RRL_INTERWARE_PLAN p","PLACED_TASK_ID,(select f.OPERATION_ID from RRL_INTERWARE_CUSTODY_PROOF f join RRL_INTERWARE_RECEIPT r on r.OPERATION_ID=f.RECEIPT_OPERATION_ID where r.PLAN_OPERATION_ID=p.OPERATION_ID) CUSTODY_RELEASE_OPERATION_ID from RRL_INTERWARE_PLAN p")
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py");s=p.read_text(encoding="utf-8")
if "def release_custody(" not in s:s+='''
@router.post("/release-custody")
def release_custody(body: PlacementPlan,user: AdminUser=Depends(require_permission("interwarehouse_receive")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:
    from ..contracts_stock import StockPostingError
    try:
        return service.release_custody(body.operation_id,body.receipt_operation_id,user.username)
    except StockPostingError as exc:
        confirmed = exc.oracle_code is not None and 20800<=exc.oracle_code<=20999
        raise HTTPException(403 if exc.oracle_code==20882 else 409 if confirmed else 503,{"code":exc.code,"message":exc.rule_reason or str(exc),"operation_id":body.operation_id,"outcome_confirmed":confirmed}) from exc
'''
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
