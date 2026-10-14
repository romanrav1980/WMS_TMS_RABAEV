from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");s=p.read_text(encoding="utf-8");s+='''
    def prepare_recovery_onward(self,operation_id: str,recovery_id: str,trip_id: int,reason: str,reference: str,actor: str) -> dict[str,Any]:
        from .interwarehouse_recovery_st import prepare_recovery_st
        return prepare_recovery_st(self.gateway,operation_id,recovery_id,trip_id,reason,reference,actor)
''';out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py");s=p.read_text(encoding="utf-8").replace("class InterwarehousePort(Protocol):","class InterwarehousePort(Protocol):\n    def prepare_recovery_onward(self,operation_id: str,recovery_id: str,trip_id: int,reason: str,reference: str,actor: str) -> dict[str,Any]: ...",1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py");s=p.read_text(encoding="utf-8");s+='''
class RecoveryOnward(RecoveryPlacement):
    target_trip_id: int=Field(strict=True,gt=0)
    reason: str=Field(strict=True,min_length=1,max_length=500)
    decision_reference: str=Field(strict=True,min_length=1,max_length=255)

@router.post("/prepare-recovery-onward")
def prepare_recovery_onward(body: RecoveryOnward,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),
                            service: InterwarehousePort=Depends(interwarehouse_service)) -> dict:
    try:return service.prepare_recovery_onward(body.operation_id,body.recovery_operation_id,body.target_trip_id,body.reason,body.decision_reference,user.username)
    except StoreReturnReceiveError as exc:raise HTTPException(exc.status_code,{"code":exc.code,"message":str(exc)})from exc
''';out[p.as_posix()]=s
print(json.dumps(out))
