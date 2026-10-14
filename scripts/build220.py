raise SystemExit("Retired authoring generator: use final220 SQL/fresh owner checkpoint; do not overwrite live source")
from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni063_hu_load_recovery");out={}
out["wiki/database/nicora_ni063_hu_recovery_design_20261011.md"]="""# NI06.3: возврат тары исходного HU/FULLPAL
220 extends original216 recovery owner and existing TARE_BOOK, not a new balance. Accepted outbound original root book/transferred ->accepted exact vehicle return/current warehouse/type/GOOD ->one new HELD original place. CASE proof unchanged; additive nullable ROOT_UID/FK/XOR retains existing CASE history. Whole original archived ROOT_UID only. CONTAINER verifies original shipped epoch/owner/nullcell; STOCK verifies original zero physical/held across UID, original bound FF/actual DONE task/active wave and archived kind/UID/current article. Original scan SSCC or internal UID accepted according to archived root. Existing original goods unloader requires new HELD recovery and remains sole quantity writer. Current owner/replay/declared locks/unit history preserved; transferred record never rewritten.
"""
out[str(f/"001_schema.sql")]="""alter table RRL_TARE_LOAD_RECOVERY modify(CASE_PICK_TASK_ID null);
alter table RRL_TARE_LOAD_RECOVERY add(ROOT_UID varchar2(150)references RRL_PALLETS(UID_PALLET));
alter table RRL_TARE_LOAD_RECOVERY add constraint RRL_TARE_RECOVERY_PLACE_CK check((CASE_PICK_TASK_ID is not null and ROOT_UID is null)or(CASE_PICK_TASK_ID is null and ROOT_UID is not null));
"""
s=(f/"000_before_rrl_tare_load_recovery_api.sql").read_text(encoding="utf-8")
s=s.replace("original_version number;","original_version number;pp RRL_PALLETS%rowtype;root_uid varchar2(150);root_kind varchar2(20);cell_value varchar2(60);p_total number;h_total number;stock_version number;task_id number;wave_id number;node json_object_t;tree json_object_t;",1)
s=s.replace("old_book.PLACE_KIND!='CASE'","old_book.PLACE_KIND not in('CASE','HU')",1).replace("s.get_string('place_kind')!='CASE'","s.get_string('place_kind')!=old_book.PLACE_KIND",1).replace("'TARE_RECOVERY_ORIGINAL_TRANSFERRED_CASE_REQUIRED'","'TARE_RECOVERY_ORIGINAL_TRANSFERRED_PLACE_REQUIRED'",1)
start=s.index("  case_id:=to_number(old_book.PLACE_ID);");end=s.index("  select count(*)into n from RRL_TARE_LOAD_RECOVERY",start);case=s[start:end]
hu="""  else
   root_uid:=old_book.PLACE_ID;
   if load_fact.ROOT_UID is null or load_fact.ROOT_UID!=root_uid or load_fact.ROOT_CASE_TASK_ID is not null then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_WHOLE_ROOT_REQUIRED');end if;
   tree:=json_object_t.parse(load_fact.COMPOSITION_JSON);node:=treat(tree.get_array('nodes').get(0)as json_object_t);
   root_kind:=node.get_string('kind');original_version:=node.get_number('version');cell_value:=tree.get_string('cell');
   if node.get_string('uid')!=root_uid or root_kind not in('CONTAINER','STOCK')then raise_application_error(-20886,'TARE_RECOVERY_ARCHIVED_ROOT_KIND_REQUIRED');end if;
   scan_value:=nvl(node.get_string('sscc'),root_uid);
   if v.get_string('scan_place')is null or v.get_string('scan_place')!=scan_value then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_ROOT_SCAN_REQUIRED');end if;
   select *into pp from RRL_PALLETS where UID_PALLET=root_uid;
   if nvl(pp.HU_KIND,'STOCK')!=root_kind then raise_application_error(-20886,'TARE_RECOVERY_CURRENT_ROOT_KIND_REQUIRED');end if;
   select count(*)into n from RRL_WMS_HU_LINK where CHILD_PALLET_UID=root_uid and ACTIVE_FLAG=1;
   if n!=0 then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_ROOT_NOT_FREE');end if;
   if root_kind='CONTAINER'then
    if pp.HU_SHIPPED_OPERATION is null or pp.HU_SHIPPED_OPERATION!=load_id or pp.HU_CONTENT_VERSION!=original_version+1 or pp.HU_CURRENT_CELL is not null then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_CONTAINER_EPOCH_REQUIRED');end if;
   else
    select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)into p_total,h_total from RRL_REMAINS where UID_POLETA=root_uid;
    if p_total!=0 or h_total!=0 or pp.HU_CONTENT_VERSION!=original_version then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_FULLPAL_ZERO_EPOCH_REQUIRED');end if;
    select count(*),max(PICKED_WAREHOUSE_TASK_ID)into n,task_id from RRL_CUSTOMER_ORDER_FULFILLMENT where PICKED_CASE_TASK_ID is null and PICKED_PALLET_UID=root_uid and STATUS='SHIPPED'and SHIPPED_OPERATION_ID=load_id;
    if n!=1 or task_id is null then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_FULLPAL_BIND_REQUIRED');end if;
    select count(*),max(SOURCE_DOC_ID)into n,wave_id from RRL_WAREHOUSE_TASK where TASK_ID=task_id and STATUS='DONE'and TASK_TYPE='PICKING_MOVE'and UID_PALLET=root_uid and SOURCE_DOC_TYPE='PICK_WAVE'and TO_WARE_ID=load_fact.WARE_ID;
    if n!=1 then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_FULLPAL_TASK_REQUIRED');end if;
    select count(*)into n from RRL_PICK_WAVE where PICK_WAVE_ID=wave_id and STATUS='LAUNCHED';
    if n!=1 then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_FULLPAL_WAVE_REQUIRED');end if;
    select STOCK_VERSION into stock_version from RRL_REMAINS where UID_POLETA=root_uid and CELL=cell_value;
   end if;
   select count(*)into n from RRL_CELLS where CELL=cell_value and WARE_ID=load_fact.WARE_ID;
   if n!=1 then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_ROOT_CELL_WARE_REQUIRED');end if;
   j.put('root_uid',root_uid);j.put('root_kind',root_kind);j.put('root_cell',cell_value);j.put('root_article',pp.ARTICUL);j.put('root_stock_version',stock_version);j.put('root_version',pp.HU_CONTENT_VERSION);
   j.put('fullpal_task_id',task_id);j.put('fullpal_wave_id',wave_id);
  end if;
  j.put('place_kind',old_book.PLACE_KIND);j.put('place_id',old_book.PLACE_ID);
"""
s=s[:start]+"  if old_book.PLACE_KIND='CASE'then\n"+case+hu+s[end:]
s=s.replace("j.put('case_version',ct.CONTENT_VERSION);","j.put('case_version',ct.CONTENT_VERSION);",1)
old="  RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU','CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('case_id')));";assert old in s
s=s.replace(old,"""  if v.get_string('place_kind')='CASE'then
   RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU','CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('case_id')));
  else
   RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',v.get_string('root_uid'));
   if v.get_number('fullpal_task_id')is not null then
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('fullpal_task_id')));
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('fullpal_wave_id')));
   end if;
  end if;""",1)
s=s.replace("ct number:=v.get_number('case_id');","ct number:=v.get_number('case_id');root_id varchar2(150):=v.get_string('root_uid');",1)
s=s.replace("PALLET_TYPE_ID,CASE_PICK_TASK_ID,CREATED_BY)values","PALLET_TYPE_ID,CASE_PICK_TASK_ID,ROOT_UID,CREATED_BY)values",1).replace("ware,typ,ct,p_actor);","ware,typ,ct,root_id,p_actor);",1)
out[str(f/"002_recovery.sql")]=s
s=(f/"000_before_rrl_stock_tare_book_cmd.sql").read_text(encoding="utf-8")
anchor="  if v_goods_kind='CONTAINER' then";assert anchor in s
s=s.replace(anchor,"""  if recovery_json is not null then
   v_cell:=recovery_json.get_string('root_cell');v_ware:=recovery_json.get_number('warehouse_id');v_stock_version:=recovery_json.get_number('root_stock_version');
   v_status:=case when v_goods_kind='CONTAINER'then pp.HU_TYPE else 'STOCK_PALLET_SHIPPED'end;
   if v_goods_kind!=recovery_json.get_string('root_kind')or(v_goods_kind='CONTAINER'and pp.HU_TYPE not in('PALLET','ROLL_CAGE'))then raise_application_error(-20886,'TARE_RECOVERY_RETURNABLE_ROOT_TYPE_REQUIRED');end if;
  elsif v_goods_kind='CONTAINER' then""",1)
s=s.replace("if n!=0 then raise_application_error(-20886,'TARE_BOOK_PLACE_ALREADY_ON_VEHICLE');","if n!=0 and recovery_json is null then raise_application_error(-20886,'TARE_BOOK_PLACE_ALREADY_ON_VEHICLE');",1)
out[str(f/"003_book.sql")]=s
s=(f/"000_before_guard.sql").read_text(encoding="utf-8");old="v.get_number('case_id')!=:new.CASE_PICK_TASK_ID";assert old in s;s=s.replace(old,"nvl(v.get_number('case_id'),-1)!=nvl(:new.CASE_PICK_TASK_ID,-1) or nvl(v.get_string('root_uid'),'-')!=nvl(:new.ROOT_UID,'-')",1)
old="and PLACE_KIND='CASE'and PLACE_ID=RRL_STOCK_PLAN_HELPER.decimal_text(:new.CASE_PICK_TASK_ID)";assert old in s;s=s.replace(old,"and((PLACE_KIND='CASE'and :new.CASE_PICK_TASK_ID is not null and PLACE_ID=RRL_STOCK_PLAN_HELPER.decimal_text(:new.CASE_PICK_TASK_ID))or(PLACE_KIND='HU'and :new.ROOT_UID is not null and PLACE_ID=:new.ROOT_UID))",1);out[str(f/"004_guard.sql")]=s
out[str(f/"apply.sql")]="@@001_schema.sql\n@@002_recovery.sql\n@@003_book.sql\n@@004_guard.sql\n"
out[str(f/"rollback.sql")]="""declare n number;begin select count(*)into n from RRL_TARE_LOAD_RECOVERY where ROOT_UID is not null;if n>0 then raise_application_error(-20863,'HU_TARE_RECOVERY_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_rrl_tare_load_recovery_api.sql
@@000_before_rrl_stock_tare_book_cmd.sql
@@000_before_guard.sql
alter table RRL_TARE_LOAD_RECOVERY drop constraint RRL_TARE_RECOVERY_PLACE_CK;
alter table RRL_TARE_LOAD_RECOVERY drop column ROOT_UID;
alter table RRL_TARE_LOAD_RECOVERY modify(CASE_PICK_TASK_ID not null);
"""
out[str(f/"verify.sql")]="select name,type,line,position,text from user_errors where name not like 'BIN$%';\nselect object_name,object_type from user_objects where status='INVALID';\n"
print(json.dumps(out,ensure_ascii=True))
