from pathlib import Path
import json
out={}
p=Path('api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py');t=p.read_text(encoding='utf-8')
needle='    def group_source('
addition='''    def plan_group(self,operation: str,body: dict[str,Any],actor: str)->dict[str,Any]:
        from .interwarehouse_group_plan import InterwarehouseGroupPlan
        return InterwarehouseGroupPlan(self.gateway).plan(operation,body,actor)

    def group_source_proof(self,load: str,actor: str)->dict[str,Any]:
        from .interwarehouse_group_plan import InterwarehouseGroupPlan
        return InterwarehouseGroupPlan(self.gateway).source(load,actor)

'''
if 'def plan_group('not in t:t=t.replace(needle,addition+needle,1)
out[p.as_posix()]=t
p=Path('api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py');t=p.read_text(encoding='utf-8').replace('class InterwarehousePort(Protocol):','class InterwarehousePort(Protocol):\n    def plan_group(self,operation: str,body: dict[str,Any],actor: str)->dict[str,Any]: ...\n    def group_source_proof(self,load: str,actor: str)->dict[str,Any]: ...');out[p.as_posix()]=t
p=Path('api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py');t=p.read_text(encoding='utf-8')
addition='''class GroupPlan(Plan):
    expected_source_signature: str=Field(strict=True,min_length=64,max_length=64,pattern=r"^[0-9a-f]{64}$")

@router.get("/source-loads/{load_id}/group-proof")
def group_proof(load_id: str,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),service: InterwarehousePort=Depends(interwarehouse_service))->dict[str,Any]:
    try:
        return service.group_source_proof(load_id,user.username)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc

@router.post("/group-plan")
def group_plan(body: GroupPlan,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),service: InterwarehousePort=Depends(interwarehouse_service))->dict[str,Any]:
    try:
        return service.plan_group(body.operation_id,body.model_dump(exclude={"operation_id"}),user.username)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id,"outcome_confirmed":True})from exc

'''
if 'class GroupPlan('not in t:t=t.replace('@router.post("/plan")',addition+'@router.post("/plan")',1)
out[p.as_posix()]=t
p=Path('db/migrations/2026-10-12_ni061_group_source/rollback.sql');t=p.read_text(encoding='utf-8').replace('RRL_DB_MIGRATION','RRL_SCHEMA_MIGRATIONS');out[p.as_posix()]=t
print(json.dumps(out))
