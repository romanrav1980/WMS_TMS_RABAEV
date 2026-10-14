from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");s=p.read_text(encoding="utf-8");s+='''
    def plan_recovery_placement(self,operation_id: str,recovery_id: str,actor: str) -> dict[str,Any]:
        return self.posting.post(StockCommand(operation_id=operation_id,command_type="INTERWARE_RECOVERY_PUTAWAY_PLAN",actor=actor,source={"recovery_operation_id":recovery_id},lines=(),metadata={}))
''';out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py");s=p.read_text(encoding="utf-8").replace("class InterwarehousePort(Protocol):","class InterwarehousePort(Protocol):\n    def plan_recovery_placement(self,operation_id: str,recovery_id: str,actor: str) -> dict[str,Any]: ...",1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py");s=p.read_text(encoding="utf-8");s+='''
class RecoveryPlacement(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    recovery_operation_id: str=Field(strict=True,min_length=1,max_length=100)

@router.post("/recovery-placement")
def recovery_placement(body: RecoveryPlacement,user: AdminUser=Depends(require_permission("interwarehouse_receive")),
                       service: InterwarehousePort=Depends(interwarehouse_service)) -> dict:
    from ..contracts_stock import StockPostingError
    try:return service.plan_recovery_placement(body.operation_id,body.recovery_operation_id,user.username)
    except StockPostingError as exc:
        confirmed=exc.oracle_code is not None and 20800<=exc.oracle_code<=20999
        raise HTTPException(403 if exc.oracle_code==20882 else 409 if confirmed else 503,{"code":exc.code,"message":exc.rule_reason or str(exc),"operation_id":body.operation_id,"outcome_confirmed":confirmed})from exc
''';out[p.as_posix()]=s
print(json.dumps(out))
