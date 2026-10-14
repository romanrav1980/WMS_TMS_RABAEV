raise SystemExit("Retired authoring draft: use checked-in final SQL/fixture sources; do not regenerate over verified fixes.")
from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni052_unload");out={}
p=f/"004_reserve.sql";s=p.read_text(encoding="utf-8")
anchor=" procedure create_hard(p_id number"
pos=s.index(anchor)
s=s[:pos]+" procedure restore_consumed(p_id number,p_new_id number,p_qty number,p_uom_version number,p_actor varchar2);\n"+s[pos:]
pos=s.rfind("end;\n/");assert pos>0
s=s[:pos]+""" procedure restore_consumed(p_id number,p_new_id number,p_qty number,p_uom_version number,p_actor varchar2)is
  old_row RRL_STOCK_RESERVATION%rowtype;new_row RRL_STOCK_RESERVATION%rowtype;
  op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;qty_text varchar2(60):=RRL_STOCK_PLAN_HELPER.decimal_text(p_qty);
 begin
  lock_identity(p_id);lock_identity(p_new_id);
  select *into old_row from RRL_STOCK_RESERVATION where RESERVATION_ID=p_id for update;
  if p_qty<=0 or old_row.STATUS!='CONSUMED'or old_row.BASE_QTY!=0 or old_row.RESERVATION_KIND!='HARD'or old_row.SOURCE_DOC_TYPE!='PICK_WAVE'then raise_application_error(-20869,'UNLOAD_CONSUMED_CASE_RESERVATION_REQUIRED');end if;
  select count(*)into n from RRL_STOCK_OPERATION operation
   join json_table(operation.RESOLVED_PLAN_JSON,'$.domain.legs[*]'columns(OLD_ID number path '$.reservation_id',NEW_ID number path '$.new_reservation',UID_TEXT varchar2(150)path '$.uid',QTY_TEXT varchar2(60)path '$.quantity'))leg
    on leg.OLD_ID=p_id and leg.NEW_ID=p_new_id and leg.UID_TEXT=old_row.UID_PALLET and leg.QTY_TEXT=qty_text
   where operation.OPERATION_ID=op and operation.COMMAND_TYPE='UNLOAD_SHIPMENT'and operation.STATE='IN_FLIGHT';
  if n!=1 then raise_application_error(-20863,'UNLOAD_RESERVED_RECOVERY_PLAN_REQUIRED');end if;
  RRL_STOCK_BALANCE_CORE.apply_delta(old_row.UID_PALLET,old_row.CELL,0,p_qty,old_row.BASE_UOM,p_uom_version);
  new_row:=old_row;new_row.RESERVATION_ID:=p_new_id;new_row.QTY:=p_qty;new_row.BASE_QTY:=p_qty;new_row.STATUS:='ACTIVE';new_row.RESERVATION_VERSION:=0;
  new_row.CREATED_AT:=systimestamp;new_row.CREATED_BY:=p_actor;new_row.CONSUMED_AT:=null;new_row.CONSUMED_BY:=null;
  new_row.RELEASED_AT:=null;new_row.RELEASED_BY:=null;new_row.RELEASE_REASON:=null;new_row.LOCK_OWNER:=null;new_row.LOCKED_AT:=null;new_row.LAST_ERROR:=null;
  insert into RRL_STOCK_RESERVATION values new_row;
 end;
"""+s[pos:];out[str(p)]=s
p=f/"002_command.sql";s=p.read_text(encoding="utf-8")
anchor="   RRL_STOCK_RESERVE_CORE.create_hard(new_id,uid_text,cell_text,qty,uom_text,uom_version,history.SOURCE_DOC_TYPE,history.SOURCE_DOC_ID,history.SOURCE_LINE_ID,history.RESERVATION_DOMAIN,p_actor,details.to_clob);"
assert anchor in s;s=s.replace(anchor,"   RRL_STOCK_RESERVE_CORE.restore_consumed(history.RESERVATION_ID,new_id,qty,uom_version,p_actor);")
out[str(p)]=s
# Only the original load status may be changed, exact source and immutable archive proof required.
p=f/"000_before_load_guard.sql";s=p.read_text(encoding="utf-8")
anchor=" elsif kind_name='INTERWARE_CUSTODY_RELEASE' then";assert anchor in s
s=s.replace(anchor,""" elsif kind_name='UNLOAD_SHIPMENT'then
  if :old.STATUS!='LOADED'or :new.STATUS!='UNLOADED'or :old.DEPARTURE_OPERATION_ID is not null or :old.DEPARTED_AT is not null
   or :new.LOAD_OPERATION_ID!=:old.LOAD_OPERATION_ID or :new.TT_ID!=:old.TT_ID
   or nvl(:new.ROOT_UID,chr(0))!=nvl(:old.ROOT_UID,chr(0))or nvl(:new.ROOT_CASE_TASK_ID,-1)!=nvl(:old.ROOT_CASE_TASK_ID,-1)
   or :new.VEHICLE_ID!=:old.VEHICLE_ID or :new.VEHICLE_NUMBER!=:old.VEHICLE_NUMBER or :new.DOCK!=:old.DOCK or :new.WARE_ID!=:old.WARE_ID
   or :new.GROSS_WEIGHT_KG!=:old.GROSS_WEIGHT_KG or :new.BOUNDING_VOLUME_M3!=:old.BOUNDING_VOLUME_M3 or :new.CONTENT_VERSION!=:old.CONTENT_VERSION
   or :new.LOADED_BY!=:old.LOADED_BY or :new.LOADED_AT!=:old.LOADED_AT or :new.DEPARTURE_OPERATION_ID is not null or :new.DEPARTED_AT is not null
   or :new.CUSTODY_RELEASED_AT is not null or :new.CUSTODY_RELEASE_OPERATION_ID is not null or dbms_lob.compare(:new.COMPOSITION_JSON,:old.COMPOSITION_JSON)!=0 then raise_application_error(-20863,'UNLOAD_ORIGINAL_LOAD_ARCHIVE_REQUIRED');end if;
  declare n number;begin select count(*)into n from RRL_TT_UNLOAD_FACT where OPERATION_ID=op and LOAD_OPERATION_ID=:old.LOAD_OPERATION_ID and TT_ID=:old.TT_ID and CASE_PICK_TASK_ID=:old.ROOT_CASE_TASK_ID and WARE_ID=:old.WARE_ID;
   if n!=1 then raise_application_error(-20863,'UNLOAD_IMMUTABLE_PROOF_REQUIRED');end if;end;
"""+anchor)
out[str(f/"007_load_guard.sql")]=s
out[str(f/"008_member_guard.sql")]="""create or replace trigger RRL_TT_HU_LOAD_ST_GUARD before insert or update or delete on RRL_TT_HU_LOAD_ST for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind_name varchar2(80);state_name varchar2(20);n number;source_load varchar2(100);
begin
 if deleting then raise_application_error(-20863,'PHYSICAL_LOAD_MEMBERS_IMMUTABLE');end if;
 if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'PHYSICAL_LOAD_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into kind_name,state_name from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if state_name!='IN_FLIGHT'then raise_application_error(-20863,'PHYSICAL_LOAD_MEMBER_SHIPMENT_REQUIRED');end if;
 if inserting then
  if kind_name not in('HU_SHIP','LOAD_SHIPMENT','RECONCILE_HU_LOAD')or :new.LOAD_OPERATION_ID!=op or :new.DESTINATION_ADDR is null then raise_application_error(-20863,'PHYSICAL_LOAD_MEMBER_SHIPMENT_REQUIRED');end if;
  source_load:=op;
 else
  source_load:=:old.LOAD_OPERATION_ID;
  if kind_name!='UNLOAD_SHIPMENT'or :old.ACTIVE_FLAG!=1 or :new.ACTIVE_FLAG!=0 or :new.LOAD_OPERATION_ID!=:old.LOAD_OPERATION_ID or :new.SBORKA_PALLET_ID!=:old.SBORKA_PALLET_ID or nvl(:new.DESTINATION_ADDR,chr(0))!=nvl(:old.DESTINATION_ADDR,chr(0))then raise_application_error(-20863,'PHYSICAL_LOAD_MEMBERS_IMMUTABLE');end if;
  select count(*)into n from RRL_TT_UNLOAD_FACT u join RRL_TT_HU_LOAD_FACT lf on lf.LOAD_OPERATION_ID=u.LOAD_OPERATION_ID where u.OPERATION_ID=op and u.LOAD_OPERATION_ID=source_load and lf.STATUS='UNLOADED';
  if n!=1 then raise_application_error(-20863,'UNLOAD_IMMUTABLE_PROOF_REQUIRED');end if;
 end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TT_HU_LOAD_ST',source_load||':'||RRL_STOCK_PLAN_HELPER.decimal_text(:new.SBORKA_PALLET_ID)));
end;
/
"""
out[str(f/"009_unload_guard.sql")]="""create or replace trigger RRL_TT_UNLOAD_FACT_GUARD before insert or update or delete on RRL_TT_UNLOAD_FACT for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind_name varchar2(80);state_name varchar2(20);wire clob;v json_object_t;
begin
 if not inserting then raise_application_error(-20863,'UNLOAD_FACT_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'UNLOAD_NATIVE_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE,RESOLVED_PLAN_JSON into kind_name,state_name,wire from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if kind_name!='UNLOAD_SHIPMENT'or state_name!='IN_FLIGHT'then raise_application_error(-20863,'UNLOAD_NATIVE_ROOT_REQUIRED');end if;
 v:=json_object_t.parse(wire).get_object('domain');
 if v.get_string('load_id')!=:new.LOAD_OPERATION_ID or v.get_number('trip_id')!=:new.TT_ID or v.get_number('case_id')!=:new.CASE_PICK_TASK_ID or v.get_number('warehouse')!=:new.WARE_ID
  or v.get_object('snapshot').get_string('cell')!=:new.CELL_CODE or dbms_lob.compare(v.get_object('snapshot').to_clob,:new.COMPOSITION_JSON)!=0 then raise_application_error(-20863,'UNLOAD_SOURCE_PLAN_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TT_UNLOAD_FACT',op));
end;
/
"""
out[str(f/"apply.sql")]="".join("@@"+x+"\n"for x in["001_schema.sql","002_command.sql","003_balance.sql","004_reserve.sql","005_fulfillment.sql","006_root.sql","007_load_guard.sql","008_member_guard.sql","009_unload_guard.sql"])
out[str(f/"rollback.sql")]="""declare n number;begin select count(*)into n from RRL_TT_UNLOAD_FACT;if n>0 then raise_application_error(-20863,'UNLOAD_ACTUAL_HISTORY_RETAIN_FORWARD_REPAIR');end if;end;
/
@@000_before_root.sql
@@000_before_balance.sql
@@000_before_reserve.sql
@@000_before_fulfillment.sql
@@000_before_load_guard.sql
@@000_before_member_guard.sql
drop package RRL_STOCK_UNLOAD_CMD;
drop table RRL_TT_UNLOAD_FACT;
"""
out[str(f/"verify.sql")]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_UNLOAD_CMD','RRL_STOCK_POSTING_API','RRL_TT_UNLOAD_FACT_GUARD','RRL_STOCK_FULFILLMENT_FACT','RRL_STOCK_RESERVE_CORE');\nselect OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME like 'RRL%';\n"
print(json.dumps(out,ensure_ascii=True))
