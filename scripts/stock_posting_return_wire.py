import json
from pathlib import Path
from stock_posting_sql_json_binds import transform
d=Path("db/migrations/2026-10-08_stock_posting_core");out={}
for name in ("020_reservations.sql","032_transfer_core.sql","039_unit_core.sql","160_case_pick_command.sql"):
 p=d/name;s=p.read_text(encoding="utf-8").replace("accessible by(","accessible by(package RRL_STOCK_CASE_RETURN_CMD,",1);out[str(p)]=s
p=d/"024_posting.sql";s=p.read_text(encoding="utf-8")
s=s.replace("elsif g_kind='CASE_CARRIER_MOVE' then RRL_STOCK_CASE_MOVE_CMD.compile_command","elsif g_kind='CASE_CARRIER_RETURN' then RRL_STOCK_CASE_RETURN_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n   elsif g_kind='CASE_CARRIER_MOVE' then RRL_STOCK_CASE_MOVE_CMD.compile_command",1)
s=s.replace("elsif g_kind='CASE_CARRIER_MOVE' then RRL_STOCK_CASE_MOVE_CMD.execute_command","elsif g_kind='CASE_CARRIER_RETURN' then RRL_STOCK_CASE_RETURN_CMD.execute_command(g_request,g_actor,p_result);\n   elsif g_kind='CASE_CARRIER_MOVE' then RRL_STOCK_CASE_MOVE_CMD.execute_command",1)
s=s.replace("else 'mes_apply_wms' end","else 'mes_wms_bridge_apply' end",1)
out[str(p)]=s
p=d/"209_case_return.sql";s=p.read_text(encoding="utf-8")
s=s.replace("v.put('before',json_array_t.parse(RRL_STOCK_CASE_PICK_CMD.carrier_rows(tid)));","""v.put('before',json_array_t.parse(RRL_STOCK_CASE_PICK_CMD.carrier_rows(tid)));
  declare unused json_array_t:=json_array_t();item json_object_t;begin
   for h in(select sr.RESERVATION_ID,sr.UID_PALLET,sr.CELL,sr.BASE_UOM,sr.BASE_QTY,p.ARTICUL
    from RRL_STOCK_RESERVATION sr join RRL_PALLETS p on p.UID_PALLET=sr.UID_PALLET
    where sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.SOURCE_DOC_ID=ct.PICK_WAVE_ID
     and sr.RESERVATION_KIND='HARD' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING') and sr.BASE_QTY>0
     and exists(select 1 from RRL_CASE_PICK_LINE l where l.CASE_PICK_TASK_ID=tid and l.PICK_TASK_ID=sr.SOURCE_LINE_ID)
     and not exists(select 1 from RRL_CASE_CARRIER_LOT cl where cl.LOT_UID=sr.UID_PALLET)
    order by sr.RESERVATION_ID fetch first 201 rows only) loop
    if unused.get_size=200 then raise_application_error(-20881,'CASE_RETURN_UNUSED_RESERVE_BOUND');end if;
    RRL_STOCK_PLAN_HELPER.stock_closure(f,r,h.UID_PALLET,h.ARTICUL,h.CELL,null);
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(h.RESERVATION_ID));
    item:=json_object_t();item.put('id',h.RESERVATION_ID);item.put('uid',h.UID_PALLET);item.put('article',h.ARTICUL);item.put('base',h.BASE_UOM);item.put('cell',h.CELL);
    unused.append(item);
   end loop;
   for sh in(select CASE_PICK_SHORT_ID from RRL_CASE_PICK_SHORT where CASE_PICK_TASK_ID=tid order by CASE_PICK_SHORT_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_SHORT',RRL_STOCK_PLAN_HELPER.decimal_text(sh.CASE_PICK_SHORT_ID));
   end loop;
   v.put('unused',unused);
  end;""",1)
needle="  for l in(select CASE_PICK_LINE_ID,PICK_TASK_ID,PICK_WAVE_TASK_ID from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=tid) loop"
assert s.count(needle)==1
s=s.replace(needle,"""  ids:=v.get_array('unused');
  for i in 0..ids.get_size-1 loop
   x:=treat(ids.get(i) as json_object_t);sid:=x.get_number('id');
   select * into sr from RRL_STOCK_RESERVATION where RESERVATION_ID=sid for update;
   if sr.SOURCE_DOC_TYPE!='PICK_WAVE' or sr.SOURCE_DOC_ID!=wave or sr.UID_PALLET!=x.get_string('uid') or sr.CELL!=x.get_string('cell')
    or sr.STATUS not in('ACTIVE','ALLOCATED','PICKING') then raise_application_error(-20890,'CLOSURE_CHANGED: CASE unused reserve');end if;
   article:=x.get_string('article');base:=x.get_string('base');
   select max(POLICY_VERSION) into version from RRL_STOCK_UOM_CONVERSION where ARTICUL=article and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
   if version is null then raise_application_error(-20868,'CASE_RETURN_BASE_POLICY_REQUIRED');end if;
   RRL_STOCK_UNIT_CORE.release_units(sid,sr.BASE_QTY,null,0);
   RRL_STOCK_RESERVE_CORE.release_hard(sid,sr.BASE_QTY,version,'PICK_WAVE',wave,p_actor);
  end loop;
  update RRL_CASE_PICK_SHORT set STATUS='CANCELLED',CANCELLED_AT=systimestamp,CANCELLED_BY=p_actor
   where CASE_PICK_TASK_ID=tid and STATUS in('CREATED','PENDING_APPROVAL');
"""+needle,1)
out[str(p)]=transform(s)[0]
p=Path("api/wms_api_server/app/modules/inventory/contracts_stock.py");s=p.read_text(encoding="utf-8").replace('{"CASE_CARRIER_MOVE",','{"CASE_CARRIER_RETURN", "CASE_CARRIER_MOVE",',1);out[str(p)]=s
p=Path("api/wms_api_server/app/routers/case_pick.py");s=p.read_text(encoding="utf-8")
s+='''

class CaseCarrierReturnRequest(BaseModel):
    operation_id: str = Field(min_length=1,max_length=100)
    scan_container: str = Field(min_length=1,max_length=150)
    expected_content_version: int = Field(ge=0,strict=True)
    destinations: dict[str,str]


@router.post("/tasks/{case_pick_task_id}/return-carrier")
def return_case_carrier(case_pick_task_id:int,request:CaseCarrierReturnRequest,
    user:AdminUser=Depends(require_permission(CASE_PICK_MANAGE_PERMISSION))) -> dict:
    from ..modules.inventory.public import return_existing_case_carrier
    return return_existing_case_carrier(case_pick_task_id,request,user.username)
'''
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/public.py");s=p.read_text(encoding="utf-8")
s+='''

def return_existing_case_carrier(task_id:int,request,actor:str):
    from .infrastructure.stock_posting_uow import StockPosting
    from .contracts_stock import StockCommand
    if not 1 <= len(request.destinations) <= 200 or any(not k or not v or len(v)>60 for k,v in request.destinations.items()):
        raise ValueError("Bounded scanned destinations required")
    return StockPosting().post(StockCommand(operation_id=request.operation_id,command_type="CASE_CARRIER_RETURN",
        actor=actor,lines=(),source={"case_task_id":task_id},
        metadata=request.model_dump(mode="json",exclude={"operation_id"})))
'''
out[str(p)]=s
p=d/"current_runtime_manifest.json";m=json.loads(p.read_text(encoding="utf-8"))
m["packages"].append("RRL_STOCK_CASE_RETURN_CMD");m["components"].append("209_case_return.sql")
out[str(p)]=json.dumps(m,indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
