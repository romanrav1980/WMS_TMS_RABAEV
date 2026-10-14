from pathlib import Path
import json
out={}
p=Path('api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py');t=p.read_text(encoding='utf-8')
addition='''    def group_queue(self,ware: int,actor: str)->list[dict[str,Any]]:
        from .interwarehouse_group_read import InterwarehouseGroupRead
        return InterwarehouseGroupRead(self.gateway).queue(ware,actor)

    def group_detail(self,plan: str,actor: str)->dict[str,Any]:
        from .interwarehouse_group_read import InterwarehouseGroupRead
        return InterwarehouseGroupRead(self.gateway).detail(plan,actor)

    def plan_group_placement(self,operation: str,receipt: str,metadata: dict[str,Any],actor: str)->dict[str,Any]:
        from .interwarehouse_group_placement import InterwarehouseGroupPlacement
        return InterwarehouseGroupPlacement(self.gateway,self.posting).plan(operation,receipt,metadata,actor)

'''
if 'def group_queue('not in t:t=t.replace('    def plan_group(',addition+'    def plan_group(',1)
out[p.as_posix()]=t
p=Path('api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py');t=p.read_text(encoding='utf-8').replace('class InterwarehousePort(Protocol):','class InterwarehousePort(Protocol):\n    def group_queue(self,ware: int,actor: str)->list[dict[str,Any]]: ...\n    def group_detail(self,plan: str,actor: str)->dict[str,Any]: ...\n    def plan_group_placement(self,operation: str,receipt: str,metadata: dict[str,Any],actor: str)->dict[str,Any]: ...');out[p.as_posix()]=t
p=Path('api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py');t=p.read_text(encoding='utf-8')
addition='''@router.get("/group-warehouses/{ware_id}")
def group_queue(ware_id: int,user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: InterwarehousePort=Depends(interwarehouse_service))->list[dict[str,Any]]:
    try:return service.group_queue(ware_id,user.username)
    except StoreReturnReceiveError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc

@router.get("/group-plans/{plan_id}")
def group_detail(plan_id: str,user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: InterwarehousePort=Depends(interwarehouse_service))->dict[str,Any]:
    try:return service.group_detail(plan_id,user.username)
    except StoreReturnReceiveError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc

'''
if 'def group_queue('not in t:t=t.replace('class Plan(BaseModel):',addition+'class Plan(BaseModel):',1)
addition='''class GroupPlacement(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    receipt_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    expected_version: int=Field(strict=True,ge=0)
    scan_container: str=Field(strict=True,min_length=1,max_length=200)
    scanned_from_cell: str=Field(strict=True,min_length=1,max_length=60)
    scanned_to_cell: str=Field(strict=True,min_length=1,max_length=60)
    measurements: dict[str,Any]
    target_slot_id: int|None=Field(default=None,strict=True,gt=0)
    scanned_to_slot_code: str|None=Field(default=None,strict=True,min_length=1,max_length=100)

@router.post("/group-placement")
def group_placement(body: GroupPlacement,user: AdminUser=Depends(require_permission("warehouse_task_execute")),service: InterwarehousePort=Depends(interwarehouse_service))->dict[str,Any]:
    from ..contracts_stock import StockPostingError
    try:
        return service.plan_group_placement(body.operation_id,body.receipt_operation_id,body.model_dump(exclude={"operation_id","receipt_operation_id"},exclude_none=True),user.username)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"outcome_confirmed":True})from exc
    except StockPostingError as exc:
        confirmed=exc.oracle_code is not None and 20800<=exc.oracle_code<=20999
        raise HTTPException(403 if exc.oracle_code==20882 else 409 if confirmed else 503,{"code":exc.code,"message":exc.rule_reason or str(exc),"operation_id":body.operation_id,"outcome_confirmed":confirmed})from exc

'''
if 'class GroupPlacement('not in t:t=t.replace('class PlacementReplan(PlacementPlan):',addition+'class PlacementReplan(PlacementPlan):',1)
out[p.as_posix()]=t
print(json.dumps(out))
