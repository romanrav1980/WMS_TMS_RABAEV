from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni052_unload_hu");out={}
s=(f/"000_before_unload_guard.sql").read_text(encoding="utf-8")
s=s.replace("v.get_number('case_id')!=:new.CASE_PICK_TASK_ID","nvl(v.get_number('case_id'),-1)!=nvl(:new.CASE_PICK_TASK_ID,-1)or nvl(v.get_string('root_uid'),'~')!=nvl(:new.ROOT_UID,'~')")
out[str(f/"003_unload_guard.sql")]=s
s=(f/"000_before_load_guard.sql").read_text(encoding="utf-8").replace("CASE_PICK_TASK_ID=:old.ROOT_CASE_TASK_ID","nvl(CASE_PICK_TASK_ID,-1)=nvl(:old.ROOT_CASE_TASK_ID,-1)and nvl(ROOT_UID,'~')=nvl(:old.ROOT_UID,'~')")
out[str(f/"004_load_guard.sql")]=s
s=(f/"000_before_sample_guard.sql").read_text(encoding="utf-8")
s=s.replace("sid:=json_object_t.parse(wire).get_object('domain').get_number('shipment_id');","select count(*)into sid from json_table(wire,'$.domain.members[*]'columns(SHIPMENT_ID number path '$.shipment_id'))where SHIPMENT_ID=:new.ID;")
s=s.replace("sid!=:new.ID","sid!=1")
out[str(f/"005_sample_guard.sql")]=s
s=(f/"000_before_link_guard.sql").read_text(encoding="utf-8").replace("'HU_UNPACK','HU_REPACK_SLOT'","'HU_UNPACK','HU_REPACK_SLOT','UNLOAD_SHIPMENT'")
marker=" RRL_STOCK_LOCK_API.assert_held(30"
insert=""" if v_kind='UNLOAD_SHIPMENT'then
  if not inserting then raise_application_error(-20863,'UNLOAD_APPEND_NEW_LINK_ONLY');end if;
  declare wire clob;load_id varchar2(100);n number;state_name varchar2(20);child_key varchar2(200):=nvl(:new.CHILD_PALLET_UID,'CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(:new.CHILD_CASE_TASK_ID));begin
   select RESOLVED_PLAN_JSON,STATE into wire,state_name from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
   load_id:=json_object_t.parse(wire).get_object('domain').get_string('load_id');
   select count(*)into n from json_table(wire,'$.domain.recover_links[*]'columns(NEW_ID number path '$.new_id',OLD_ID number path '$.id',P varchar2(150)path '$.parent',C varchar2(200)path '$.child',V number path '$.version'))j join RRL_WMS_HU_LINK old_link on old_link.HU_LINK_ID=j.OLD_ID and old_link.PARENT_UID=j.P and old_link.ACTIVE_FLAG=0 and old_link.UNLINKED_OPERATION_ID=load_id and old_link.LINK_VERSION=j.V+1
    where j.NEW_ID=:new.HU_LINK_ID and j.P=:new.PARENT_UID and j.C=child_key;
   if state_name!='IN_FLIGHT'or n!=1 then raise_application_error(-20863,'UNLOAD_ORIGINAL_LINK_PLAN_REQUIRED');end if;
  end;
 end if;
"""
idx=s.index(marker);s=s[:idx]+insert+s[idx:];out[str(f/"006_link_guard.sql")]=s
s=(f/"000_before_tare_guard.sql").read_text(encoding="utf-8")
marker=" if command_kind not in"
insert=""" if command_kind='UNLOAD_SHIPMENT'and command_state='IN_FLIGHT'then
  domain_json:=json_object_t.parse(plan).get_object('domain');book_id:=null;
  select OPERATION_ID into book_id from RRL_TARE_BOOK where STATUS='HELD'and PLACE_KIND='CASE'and PLACE_ID=RRL_STOCK_PLAN_HELPER.decimal_text(:new.CHILD_CASE_TASK_ID);
  select *into book from RRL_TARE_BOOK where OPERATION_ID=book_id;
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TARE_BOOK',book.OPERATION_ID));
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TARE_BALANCE',rawtohex(book.BALANCE_KEY)));
  select count(*)into n from json_table(plan,'$.domain.recover_links[*]'columns(NEW_ID number path '$.new_id',P varchar2(150)path '$.parent',C varchar2(200)path '$.child'))j where j.NEW_ID=:new.HU_LINK_ID and j.P=:new.PARENT_UID and j.C='CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(:new.CHILD_CASE_TASK_ID);
  if n!=1 or book.OWNER_WARE_ID!=domain_json.get_number('warehouse')then raise_application_error(-20886,'UNLOAD_RETAINED_TARE_PROOF_REQUIRED');end if;
  return;
 end if;
"""
idx=s.index(marker);s=s[:idx]+insert+s[idx:];out[str(f/"007_tare_guard.sql")]=s
s=(f/"000_before_container_guard.sql").read_text(encoding="utf-8").replace("'HU_RELOCATE_SLOT','HU_REPACK_SLOT'","'HU_RELOCATE_SLOT','HU_REPACK_SLOT','UNLOAD_SHIPMENT'")
marker=" RRL_STOCK_LOCK_API.assert_held(30"
insert=""" if v_kind='UNLOAD_SHIPMENT'then
  if not updating then raise_application_error(-20863,'UNLOAD_ORIGINAL_CONTAINER_ONLY');end if;
  declare wire clob;load_id varchar2(100);n number;state_name varchar2(20);cell_text varchar2(60);begin
   select STATE,RESOLVED_PLAN_JSON into state_name,wire from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
   load_id:=json_object_t.parse(wire).get_object('domain').get_string('load_id');cell_text:=json_object_t.parse(wire).get_object('domain').get_object('snapshot').get_string('cell');
   select count(*)into n from json_table(wire,'$.domain.snapshot.nodes[*]'columns(U varchar2(150)path '$.uid',K varchar2(20)path '$.kind',V number path '$.version'))j where j.U=:new.UID_PALLET and j.K='CONTAINER'and j.V+1=:old.HU_CONTENT_VERSION;
   if state_name!='IN_FLIGHT'or n!=1 or :old.HU_SHIPPED_OPERATION!=load_id or :old.HU_CURRENT_CELL is not null or :new.HU_SHIPPED_OPERATION is not null or :new.HU_CURRENT_CELL!=cell_text or nvl(:new.HU_TYPE,'~')!=nvl(:old.HU_TYPE,'~')or nvl(:new.HU_TARE_WEIGHT_KG,-1)!=nvl(:old.HU_TARE_WEIGHT_KG,-1)then raise_application_error(-20863,'UNLOAD_ORIGINAL_CONTAINER_PLAN_REQUIRED');end if;
  end;
 end if;
"""
idx=s.index(marker);s=s[:idx]+insert+s[idx:];out[str(f/"008_container_guard.sql")]=s
out[str(f/"apply.sql")]="".join("@@"+name+"\n"for name in ["001_schema.sql","002_unload.sql","003_unload_guard.sql","004_load_guard.sql","005_sample_guard.sql","006_link_guard.sql","007_tare_guard.sql","008_container_guard.sql"])
out[str(f/"rollback.sql")]="""declare n number;begin select count(*)into n from RRL_TT_UNLOAD_FACT where ROOT_UID is not null;if n>0 then raise_application_error(-20863,'UNLOAD_HU_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_unload.sql
@@000_before_unload_guard.sql
@@000_before_load_guard.sql
@@000_before_sample_guard.sql
@@000_before_link_guard.sql
@@000_before_tare_guard.sql
@@000_before_container_guard.sql
alter table RRL_TT_UNLOAD_FACT drop constraint RRL_TT_UNLOAD_ROOT_CK;
alter table RRL_TT_UNLOAD_FACT drop column ROOT_UID;
alter table RRL_TT_UNLOAD_FACT modify(CASE_PICK_TASK_ID not null);
"""
print(json.dumps(out,ensure_ascii=True))

