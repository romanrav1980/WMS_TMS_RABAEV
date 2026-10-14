import json
from pathlib import Path
d=Path("db/migrations/2026-10-11_ni063_nested_tare");out={}
def change(t,old,new):
 assert old in t,old
 return t.replace(old,new)
t=(d/"000_before_hu.sql").read_text(encoding="utf-8")
anchor="   add_tree(f,r,s);add_tree(f,r,t);"
section="""   if v_kind='HU_ATTACH'and m.get_string('retained_tare_booking_operation_id')is not null then
    if v_case is null then raise_application_error(-20886,'NESTED_TARE_DIRECT_CASE_REQUIRED');end if;
    declare book RRL_TARE_BOOK%rowtype;begin
     select *into book from RRL_TARE_BOOK where OPERATION_ID=m.get_string('retained_tare_booking_operation_id')and STATUS='HELD';
     if book.PLACE_KIND!='CASE'or book.PLACE_ID!=RRL_STOCK_PLAN_HELPER.decimal_text(v_case)or book.OWNER_WARE_ID!=ps.get_number('warehouse')then raise_application_error(-20886,'NESTED_TARE_ORIGINAL_CASE_BOOK_REQUIRED');end if;
     RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_BOOK',book.OPERATION_ID);
     RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_BALANCE',rawtohex(book.BALANCE_KEY));
     v.put('retained_tare_booking_operation_id',book.OPERATION_ID);
    exception when no_data_found then raise_application_error(-20886,'NESTED_TARE_ACTIVE_BOOK_REQUIRED');end;
   end if;
"""
t=change(t,anchor,section+anchor)
out[str(d/"001_hu_contract.sql")]=t;out[str(d/"001_hu_body.sql")]=t[t.index("create or replace package body"):]
t=(d/"000_before_root.sql").read_text(encoding="utf-8")
old="""  if d.get_string('command_type')!='HU_RELOCATE_SLOT'then return;end if;
  m:=d.get_object('metadata');v_case:=m.get_number('case_task_id');"""
new="""  if d.get_string('command_type')not in('HU_RELOCATE_SLOT','HU_ATTACH','HU_DETACH','HU_UNPACK')then return;end if;
  m:=d.get_object('metadata');
  if d.get_string('command_type')='HU_RELOCATE_SLOT'then v_case:=m.get_number('case_task_id');
  else v_case:=m.get_number('child_case_task_id');end if;"""
t=change(t,old,new)
out[str(d/"002_root_contract.sql")]=t;out[str(d/"002_root_body.sql")]=t[t.index("create or replace package body"):]
t=(d/"000_before_handover.sql").read_text(encoding="utf-8")
old="""  select LOAD_OPERATION_ID into v_load from RRL_TT_HU_LOAD_FACT where TT_ID=p_trip and VEHICLE_ID=p_vehicle and WARE_ID=p_owner and STATUS in('LOADED','DEPARTED')
   and((book.PLACE_KIND='HU' and ROOT_UID=book.PLACE_ID)or(book.PLACE_KIND='CASE' and ROOT_CASE_TASK_ID=case_no));"""
new="""  select count(*),min(lf.LOAD_OPERATION_ID)into n,v_load from RRL_TT_HU_LOAD_FACT lf
   where lf.TT_ID=p_trip and lf.VEHICLE_ID=p_vehicle and lf.WARE_ID=p_owner and lf.STATUS in('LOADED','DEPARTED')
   and((book.PLACE_KIND='HU'and lf.ROOT_UID=book.PLACE_ID)or(book.PLACE_KIND='CASE'and lf.ROOT_CASE_TASK_ID=case_no)
    or(book.PLACE_KIND='CASE'and exists(select 1 from json_table(lf.COMPOSITION_JSON,'$.nodes[*]'
     columns(K varchar2(20)path '$.kind',CASE_ID number path '$.case_task_id'))node where node.K='CASE'and node.CASE_ID=case_no)));
  if n!=1 then raise_application_error(-20886,'TARE_HANDOVER_ONE_ARCHIVED_PHYSICAL_LOAD_REQUIRED');end if;"""
t=change(t,old,new)
out[str(d/"003_handover_contract.sql")]=t;out[str(d/"003_handover_body.sql")]=t[t.index("create or replace package body"):]
guard="""create or replace trigger RRL_HU_TARE_LINK_GUARD before insert or update on RRL_WMS_HU_LINK for each row
declare n number;book RRL_TARE_BOOK%rowtype;op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
 command_kind varchar2(80);command_state varchar2(20);request clob;plan clob;d json_object_t;m json_object_t;domain_json json_object_t;
begin
 if :new.ACTIVE_FLAG!=1 then return;end if;
 if updating and :old.ACTIVE_FLAG=1 and :old.PARENT_UID=:new.PARENT_UID and nvl(:old.CHILD_PALLET_UID,'~')=nvl(:new.CHILD_PALLET_UID,'~') and nvl(:old.CHILD_CASE_TASK_ID,-1)=nvl(:new.CHILD_CASE_TASK_ID,-1)then return;end if;
 select count(*)into n from RRL_TARE_BOOK where STATUS='HELD'and((PLACE_KIND='HU'and PLACE_ID=:new.CHILD_PALLET_UID)or(PLACE_KIND='CASE'and PLACE_ID=to_char(:new.CHILD_CASE_TASK_ID,'TM9')));
 if n=0 then return;end if;
 if n!=1 or :new.CHILD_CASE_TASK_ID is null or op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20886,'TARE_BOOKED_CHILD_REPACK_PROOF_REQUIRED');end if;
 select COMMAND_TYPE,STATE,CANONICAL_REQUEST,RESOLVED_PLAN_JSON into command_kind,command_state,request,plan from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if command_kind!='HU_ATTACH'or command_state!='IN_FLIGHT'then raise_application_error(-20886,'TARE_BOOKED_CHILD_REPACK_PROOF_REQUIRED');end if;
 d:=json_object_t.parse(request);m:=d.get_object('metadata');domain_json:=json_object_t.parse(plan).get_object('domain');
 if d.get_object('source').get_string('uid')!=:new.PARENT_UID or m.get_number('child_case_task_id')!=:new.CHILD_CASE_TASK_ID or m.get_string('retained_tare_booking_operation_id')is null
  or domain_json.get_string('retained_tare_booking_operation_id')!=m.get_string('retained_tare_booking_operation_id')then raise_application_error(-20886,'NESTED_TARE_DECLARED_PROOF_REQUIRED');end if;
 select *into book from RRL_TARE_BOOK where OPERATION_ID=m.get_string('retained_tare_booking_operation_id')and STATUS='HELD'and PLACE_KIND='CASE'and PLACE_ID=to_char(:new.CHILD_CASE_TASK_ID,'TM9');
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TARE_BOOK',book.OPERATION_ID));
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TARE_BALANCE',rawtohex(book.BALANCE_KEY)));
 if book.OWNER_WARE_ID!=domain_json.get_object('parent_snapshot').get_number('warehouse')then raise_application_error(-20886,'NESTED_TARE_WARE_CONFLICT');end if;
exception when no_data_found then raise_application_error(-20886,'NESTED_TARE_ACTIVE_BOOK_REQUIRED');
end;
/
"""
out[str(d/"004_guard.sql")]=guard
out[str(d/"apply.sql")]="-- MIGRATION_ID:2026-10-11-176-nested-tare-preservation\n@@001_hu_body.sql\n@@002_root_body.sql\n@@003_handover_body.sql\n@@004_guard.sql\n"
out[str(d/"rollback.sql")]="-- Refuse operational rollback while retained booked CASE links exist; forward repair preserves facts.\ndeclare n number;begin select count(*)into n from RRL_WMS_HU_LINK h join RRL_TARE_BOOK b on b.PLACE_KIND='CASE'and b.PLACE_ID=to_char(h.CHILD_CASE_TASK_ID,'TM9')and b.STATUS='HELD'where h.ACTIVE_FLAG=1;if n>0 then raise_application_error(-20808,'NESTED_TARE_FORWARD_REPAIR_REQUIRED');end if;end;\n/\n@@000_before_hu.sql\n@@000_before_root.sql\n@@000_before_handover.sql\n@@000_before_guard.sql\n"
out[str(d/"verify.sql")]="select OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_HU_CMD','RRL_STOCK_POSTING_API','RRL_STOCK_TARE_HANDOVER','RRL_HU_TARE_LINK_GUARD');\nselect NAME,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_HU_CMD','RRL_STOCK_POSTING_API','RRL_STOCK_TARE_HANDOVER','RRL_HU_TARE_LINK_GUARD');\n"
print(json.dumps(out))
