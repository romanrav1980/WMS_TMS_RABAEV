from pathlib import Path
import json
out={}
p=Path('api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_incoming.py');t=p.read_text(encoding='utf-8')
t=t.replace('INCOMING_SQL=Path(__file__).with_suffix(".sql").read_text(encoding="utf-8")','INCOMING_SQL=Path(__file__).with_suffix(".sql").read_text(encoding="utf-8")\nGROUP_INCOMING_SQL=Path(__file__).with_name("interwarehouse_group_incoming.sql").read_text(encoding="utf-8")')
needle='    rows=[dict(zip(columns,values)) for values in cur.fetchall()]'
t=t.replace(needle,needle+'\n    cur.execute(GROUP_INCOMING_SQL,trip=trip_id)\n    columns=[column[0].lower()for column in cur.description]\n    rows.extend(dict(zip(columns,values))for values in cur.fetchall())',1)
t=t.replace('union select PLAN_OPERATION_ID from RRL_INTERWARE_DECISION where TARGET_TT_ID=:trip)','union select PLAN_OPERATION_ID from RRL_INTERWARE_DECISION where TARGET_TT_ID=:trip\n        union select OPERATION_ID from RRL_IW_GROUP_PLAN where TARGET_TT_ID=:trip)',1)
out[p.as_posix()]=t
p=Path('api/wms_api_server/app/modules/inventory/domain/interwarehouse_readiness.py');t=p.read_text(encoding='utf-8').replace('row["load_status"]=="LOADED"','row["load_status"]in("LOADED","DEPARTED")')
out[p.as_posix()]=t
p=Path('api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py');t=p.read_text(encoding='utf-8')
addition='''    def prepare_group_onward(self,operation: str,receipt: str,reason: str,reference: str,actor: str)->dict[str,Any]:
        from .interwarehouse_group_onward import InterwarehouseGroupOnward
        return InterwarehouseGroupOnward(self.gateway).prepare(operation,receipt,reason,reference,actor)

'''
if 'def prepare_group_onward('not in t:t=t.replace('    def group_queue(',addition+'    def group_queue(',1)
out[p.as_posix()]=t
p=Path('api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py');t=p.read_text(encoding='utf-8').replace('class InterwarehousePort(Protocol):','class InterwarehousePort(Protocol):\n    def prepare_group_onward(self,operation: str,receipt: str,reason: str,reference: str,actor: str)->dict[str,Any]: ...');out[p.as_posix()]=t
p=Path('api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py');t=p.read_text(encoding='utf-8')
addition='''class GroupOnward(PlacementPlan):
    reason: str=Field(strict=True,min_length=1,max_length=500)
    decision_reference: str=Field(strict=True,min_length=1,max_length=60)

@router.post("/group-onward")
def group_onward(body: GroupOnward,user: AdminUser=Depends(require_permission("outgoing_pallet_edit")),service: InterwarehousePort=Depends(interwarehouse_service))->dict[str,Any]:
    try:return service.prepare_group_onward(body.operation_id,body.receipt_operation_id,body.reason,body.decision_reference,user.username)
    except StoreReturnReceiveError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id,"outcome_confirmed":True})from exc

'''
if 'class GroupOnward('not in t:t=t.replace('class PlacementReplan(PlacementPlan):',addition+'class PlacementReplan(PlacementPlan):',1)
out[p.as_posix()]=t
print(json.dumps(out))
