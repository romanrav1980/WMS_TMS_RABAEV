import json
from pathlib import Path
d=Path("db/migrations/2026-10-11_ni041_case_relocation");out={}
def change(t,old,new):
 assert old in t,old
 return t.replace(old,new)
t=(d/"000_before_move.sql").read_text(encoding="utf-8")
t=change(t," function placement("," function snapshot(p_uid varchar2,p_case number)return clob is begin\n  if p_case is null then return RRL_STOCK_HU_READ.snapshot_json(p_uid);end if;\n  if p_uid!='CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(p_case)then raise_application_error(-20886,'CASE_SLOT_IDENTITY_CONFLICT');end if;\n  return RRL_STOCK_HU_READ.case_snapshot_json(p_case);\n end;\n function placement(")
t=change(t,"v_cell varchar2(60);v_placement clob;","v_cell varchar2(60);v_placement clob;v_case number:=m.get_number('case_task_id');")
t=t.replace("RRL_STOCK_HU_READ.snapshot_json(v_uid)","snapshot(v_uid,v_case)")
t=change(t,"not in('CONTAINER','STOCK')","not in('CONTAINER','STOCK','CASE')")
t=change(t,"v.put('uid',v_uid);","v.put('case_task_id',v_case);v.put('uid',v_uid);")
t=change(t,"v_ware number;rid number;","v_ware number;rid number;v_case number;")
t=change(t,"v_uid:=v.get_string('uid');tree:=","v_case:=v.get_number('case_task_id');v_uid:=v.get_string('uid');tree:=")
t=change(t,"  select SSCC into alias from RRL_PALLETS where UID_PALLET=v_uid;","  if v_case is null then select SSCC into alias from RRL_PALLETS where UID_PALLET=v_uid;\n  else select SSCC into alias from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=v_case;end if;")
old="  update RRL_PALLETS set HU_CONTENT_VERSION=HU_CONTENT_VERSION+1 where UID_PALLET=v_uid and HU_SHIPPED_OPERATION is null;"
new="  if v_case is null then\n"+old+"\n  else\n   update RRL_CASE_PICK_TASK set CONTENT_VERSION=CONTENT_VERSION+1,STATUS='WAIT_CONTROL',UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_TASK_ID=v_case and CURRENT_CELL=v_cell and STATUS in('WAIT_CONTROL','CONTROLLED','READY_TO_SHIP');\n  end if;"
t=change(t,old,new)
t=change(t,"v.get_number('sync'),new_placement);","v.get_number('sync'),new_placement,v_case);")
out[str(d/"001_move_contract.sql")]=t
out[str(d/"001_move_body.sql")]=t[t.index("create or replace package body"):]
t=(d/"000_before_slot.sql").read_text(encoding="utf-8")
t=change(t,"tree:=json_object_t.parse(RRL_STOCK_HU_READ.snapshot_json(p_replace_root));a:=tree.get_array('nodes');","if substr(p_replace_root,1,5)='CASE:'then\n    tree:=json_object_t.parse(RRL_STOCK_HU_READ.case_snapshot_json(to_number(substr(p_replace_root,6))));\n   else tree:=json_object_t.parse(RRL_STOCK_HU_READ.snapshot_json(p_replace_root));end if;a:=tree.get_array('nodes');")
t=change(t,"where CURRENT_CELL=p_cell and STATUS in('WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP')","where CURRENT_CELL=p_cell and STATUS in('WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP')\n   and(p_replace_root is null or 'CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(CASE_PICK_TASK_ID)!=p_replace_root)")
out[str(d/"002_slot_contract.sql")]=t
out[str(d/"002_slot_body.sql")]=t[t.index("create or replace package body"):]
t=(d/"000_before_root.sql").read_text(encoding="utf-8")
helper=""" procedure assert_case_slot_actor(p_request clob,p_actor varchar2)is d json_object_t:=json_object_t.parse(p_request);m json_object_t;v_case number;begin
  if d.get_string('command_type')!='HU_RELOCATE_SLOT'then return;end if;
  m:=d.get_object('metadata');v_case:=m.get_number('case_task_id');
  if substr(d.get_object('source').get_string('uid'),1,5)='CASE:'and v_case is null then raise_application_error(-20886,'CASE_SLOT_TASK_ID_REQUIRED');end if;
  if v_case is null then return;end if;
  if RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 then raise_application_error(-20882,'CASE_SLOT_EXECUTION_FORBIDDEN');end if;
  RRL_CASE_TASK_ACCESS.assert_scope(v_case,p_actor,'case_move');
 end;
"""
t=change(t," procedure reset_connection is",helper+" procedure reset_connection is")
t=change(t,"  assert_actor_active(p_actor);","  assert_actor_active(p_actor);assert_case_slot_actor(p_request,p_actor);")
t=change(t,"  assert_actor_active(p_actor);assert_case_slot_actor(p_request,p_actor);\n  if g_kind", "  assert_actor_active(p_actor);assert_case_slot_actor(p_request,p_actor);\n  if g_kind") # stable explicit anchor
# execute_prepared uses p_actor? actual private execute variable is p_actor in wrapper; captured exact source below.
out[str(d/"003_root_contract.sql")]=t
out[str(d/"003_root_body.sql")]=t[t.index("create or replace package body"):]
out[str(d/"apply.sql")]="-- MIGRATION_ID:2026-10-11-175-case-slot-relocation\n@@001_move_body.sql\n@@002_slot_body.sql\n@@003_root_body.sql\n"
out[str(d/"rollback.sql")]="@@000_before_move.sql\n@@000_before_slot.sql\n@@000_before_root.sql\n"
out[str(d/"verify.sql")]="select OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_HU_SLOT_MOVE_CMD','RRL_STOCK_HU_SLOT','RRL_STOCK_POSTING_API');\nselect NAME,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_HU_SLOT_MOVE_CMD','RRL_STOCK_HU_SLOT','RRL_STOCK_POSTING_API');\n"
print(json.dumps(out))
