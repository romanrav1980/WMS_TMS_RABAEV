raise SystemExit("Retired authoring generator: use final223 owners/fresh checkpoint; never overwrite live source")
from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni052_single_load_slot_release");out={}
out["wiki/database/nicora_ni052_single_slot_release_design_20261011.md"]="""# NI05.2: самостоятельная погрузка освобождает измеренный слот
223 existing SINGLE_LOAD_CMD currently has no source claim handling for STOCK; whole HU shipping already releases its source claim and CASE shipping uses existing release_case. Extend same placement owner with exact frozen stock source occupancy declaration/release; private SINGLE caller only, same LOAD_SHIPMENT transaction. One current source OCCUPIED claim max (otherwise explicit conflict), current UID/cell/task/slot/measures/epochs/signature frozen; ROW claim/SLOT and source CELL X declared. Before shipping quantity writer, fresh source claim is rechecked and released; guard/current native op/root/locks enforced. Late rollback restores claim and P/H; old actual PUTAWAY task/history retained, no duplicate movement or new placement.
"""
s=(f/"000_before_rrl_stock_hu_placement_core.sql").read_text(encoding="utf-8")
s=s.replace("accessible by(package RRL_STOCK_UNLOAD_CMD","accessible by(package RRL_STOCK_SINGLE_LOAD_CMD,package RRL_STOCK_UNLOAD_CMD",1)
anchor=" procedure declare_existing_case";idx=s.index(anchor)
s=s[:idx]+""" procedure declare_stock_source(r in out nocopy json_array_t,p_uid varchar2,p_cell varchar2,p_claims out clob);
 procedure release_stock_source(p_uid varchar2,p_cell varchar2,p_claims clob);
"""+s[idx:]
idx=s.index(" function sync_key")
helper=""" function stock_source_claims(p_uid varchar2,p_cell varchar2)return clob is a json_array_t:=json_array_t();x json_object_t;n number:=0;
 begin
  for cl in(select TASK_ID,CELL_SLOT_ID,HU_GROSS_WEIGHT_KG,HU_BOUNDING_VOLUME_M3,HU_COMPOSITION_VERSION,HU_STOCK_COMPOSITION_VERSION,HU_PHYSICAL_VERSION,HU_UNIT_SIGNATURE from RRL_RECEIPT_SLOT_CLAIM where UID_PALLET=p_uid and CELL=p_cell and STATUS='OCCUPIED'order by TASK_ID fetch first 2 rows only)loop
   n:=n+1;
   if n>1 or cl.CELL_SLOT_ID is null then raise_application_error(-20886,'SINGLE_LOAD_ONE_CURRENT_SOURCE_SLOT_REQUIRED');end if;
   x:=json_object_t();x.put('task',cl.TASK_ID);x.put('slot',cl.CELL_SLOT_ID);x.put('mass',cl.HU_GROSS_WEIGHT_KG);x.put('volume',cl.HU_BOUNDING_VOLUME_M3);x.put('content_version',cl.HU_COMPOSITION_VERSION);x.put('stock_version',cl.HU_STOCK_COMPOSITION_VERSION);x.put('physical_version',cl.HU_PHYSICAL_VERSION);x.put('unit_signature',cl.HU_UNIT_SIGNATURE);a.append(x);
  end loop;
  return a.to_clob;
 end;
 procedure declare_stock_source(r in out nocopy json_array_t,p_uid varchar2,p_cell varchar2,p_claims out clob)is a json_array_t;x json_object_t;
 begin
  p_claims:=stock_source_claims(p_uid,p_cell);a:=json_array_t.parse(p_claims);
  for i in 0..a.get_size-1 loop x:=treat(a.get(i)as json_object_t);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('task')));
   RRL_STOCK_PLAN_HELPER.anchor(r,40,'SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('slot')));
  end loop;
 end;
 procedure release_stock_source(p_uid varchar2,p_cell varchar2,p_claims clob)is
  wire clob;domain_json json_object_t;kind varchar2(80);state_value varchar2(20);op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');a json_array_t:=json_array_t.parse(p_claims);x json_object_t;task_no number;
 begin
  select COMMAND_TYPE,STATE,RESOLVED_PLAN_JSON into kind,state_value,wire from RRL_STOCK_OPERATION where OPERATION_ID=op;domain_json:=json_object_t.parse(wire).get_object('domain');
  if kind!='LOAD_SHIPMENT'or state_value!='IN_FLIGHT'or domain_json.get_object('snapshot').get_string('root')!=p_uid or domain_json.get_object('snapshot').get_string('cell')!=p_cell or dbms_lob.compare(domain_json.get_array('source_stock_claims').to_clob,p_claims)!=0 then raise_application_error(-20863,'SINGLE_SOURCE_SLOT_EXACT_PLAN_REQUIRED');end if;
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  if dbms_lob.compare(stock_source_claims(p_uid,p_cell),p_claims)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: standalone source occupancy');end if;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i)as json_object_t);task_no:=x.get_number('task');
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(task_no)));
   RRL_STOCK_LOCK_API.assert_held(40,RRL_STOCK_LOCK_API.resource_key('SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('slot'))));
   delete from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=task_no and UID_PALLET=p_uid and CELL=p_cell and STATUS='OCCUPIED';
   if sql%rowcount!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: standalone source slot');end if;
  end loop;
 end;
"""
s=s[:idx]+helper+s[idx:];out[str(f/"001_placement.sql")]=s
s=(f/"000_before_rrl_stock_single_load_cmd.sql").read_text(encoding="utf-8")
s=s.replace("signature_text varchar2(64);","signature_text varchar2(64);source_claims clob;root_node json_object_t;",1)
anchor="  v.put('shipment',entry);";idx=s.index(anchor);s=s[:idx]+"""  root_node:=treat(tree.get_array('nodes').get(0)as json_object_t);
  if root_node.get_string('kind')='STOCK'then
   RRL_STOCK_HU_PLACEMENT_CORE.declare_stock_source(resources,tree.get_string('root'),tree.get_string('cell'),source_claims);
   v.put('source_stock_claims',json_array_t.parse(source_claims));
   if json_array_t.parse(source_claims).get_size>0 then RRL_STOCK_PLAN_HELPER.fence(f,'CELL',tree.get_string('cell'),6);end if;
  end if;
"""+s[idx:]
anchor="  RRL_STOCK_SHIPPING_CORE.execute_resolved";idx=s.index(anchor);s=s[:idx]+"""  if root_node.get_string('kind')='STOCK'then RRL_STOCK_HU_PLACEMENT_CORE.release_stock_source(tree.get_string('root'),tree.get_string('cell'),v.get_array('source_stock_claims').to_clob);end if;
"""+s[idx:];out[str(f/"002_single_load.sql")]=s
out[str(f/"003_recompile.sql")]="""alter package RRL_STOCK_CASE_MOVE_CMD compile body;
alter package RRL_STOCK_CASE_RETURN_CMD compile body;
alter package RRL_STOCK_SHIPPING_CORE compile body;
alter package RRL_STOCK_HU_REPACK_CMD compile body;
alter package RRL_STOCK_HU_UNPACK_CMD compile body;
alter package RRL_STOCK_HU_SLOT_MOVE_CMD compile body;
alter package RRL_STOCK_UNLOAD_CMD compile body;
alter package RRL_STOCK_POSTING_API compile body;
"""
out[str(f/"apply.sql")]="@@001_placement.sql\n@@002_single_load.sql\n@@003_recompile.sql\n"
out[str(f/"rollback.sql")]="""declare n number;begin
 select count(*)into n from RRL_STOCK_OPERATION o where o.COMMAND_TYPE='LOAD_SHIPMENT'and o.STATE='APPLIED'and json_exists(o.RESOLVED_PLAN_JSON,'$.domain.source_stock_claims[0]');
 if n>0 then raise_application_error(-20863,'SINGLE_SLOT_LOAD_HISTORY_FORWARD_REPAIR_REQUIRED');end if;
end;
/
@@000_before_rrl_stock_hu_placement_core.sql
@@000_before_rrl_stock_single_load_cmd.sql
@@003_recompile.sql
"""
out[str(f/"verify.sql")]="select name,type,line,position,text from user_errors where name not like 'BIN$%';\nselect object_name,object_type from user_objects where status='INVALID';\n"
print(json.dumps(out,ensure_ascii=True))
