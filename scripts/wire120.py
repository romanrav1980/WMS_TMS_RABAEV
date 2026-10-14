from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/contracts_stock.py");s=p.read_text(encoding="utf-8").replace('{"INTERWARE_UNLOAD",','{"INTERWARE_PUTAWAY_PLAN", "INTERWARE_UNLOAD",',1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py");s=p.read_text(encoding="utf-8")
if "def plan_placement(" not in s:s=s.replace("    def queue(","    def plan_placement(self, operation_id: str, receipt_id: str, actor: str) -> dict[str, Any]: ...\n    def queue(",1)
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");s=p.read_text(encoding="utf-8")
if "def plan_placement(" not in s:
 s=s.replace("    def queue(",'''    def plan_placement(self, operation_id: str, receipt_id: str, actor: str) -> dict[str, Any]:
        try:
            return self.posting.post(StockCommand(operation_id=operation_id,command_type="INTERWARE_PUTAWAY_PLAN",actor=actor,source={"receipt_operation_id":receipt_id},lines=(),metadata={}))
        except oracledb.DatabaseError as exc:
            raise StockPostingError("INTERWARE_TECHNICAL_FAILURE",operation_id,getattr(exc.args[0],"code",None)) from exc

    def queue(''',1)
s=s.replace("RECEIPT_OPERATION_ID from RRL_INTERWARE_PLAN p","RECEIPT_OPERATION_ID,(select f.TASK_ID from RRL_INTERWARE_PLACEMENT f join RRL_INTERWARE_RECEIPT r on r.OPERATION_ID=f.RECEIPT_OPERATION_ID where r.PLAN_OPERATION_ID=p.OPERATION_ID) PLACED_TASK_ID from RRL_INTERWARE_PLAN p")
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py");s=p.read_text(encoding="utf-8")
if "def placement(" not in s:s+='''
class PlacementPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    receipt_operation_id: str = Field(strict=True,min_length=1,max_length=100)

@router.post("/placement")
def placement(body: PlacementPlan,user: AdminUser=Depends(require_permission("interwarehouse_receive")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:
    from ..contracts_stock import StockPostingError
    try:
        return service.plan_placement(body.operation_id,body.receipt_operation_id,user.username)
    except StockPostingError as exc:
        confirmed = exc.oracle_code is not None and 20800<=exc.oracle_code<=20999
        raise HTTPException(403 if exc.oracle_code==20882 else 409 if confirmed else 503,{"code":exc.code,"message":exc.rule_reason or str(exc),"operation_id":body.operation_id,"outcome_confirmed":confirmed}) from exc
'''
out[str(p)]=s
p=Path("db/migrations/2026-10-10_ni061_placement/007_guards.sql");s=p.read_text(encoding="utf-8")
original=Path("db/migrations/2026-10-10_ni062_return_putaway/007_guards.sql").read_text(encoding="utf-8")
identity=original[original.index("create or replace trigger RRL_STORE_RETURN_TASK_ID_GUARD"):]
identity=identity.replace("RRL_STORE_RETURN_TASK_ID_GUARD","RRL_INTERWARE_TASK_ID_GUARD").replace("'STORE_RETURN'","'INTERWARE'").replace("STORE_RETURN_","INTERWARE_").replace("INTERWARE_PUTAWAY_PLAN","INTERWARE_PUTAWAY_PLAN")
if "RRL_INTERWARE_TASK_ID_GUARD" not in s:s+=identity
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
