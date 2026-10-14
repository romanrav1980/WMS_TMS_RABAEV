from pathlib import Path
import json,re
out={};base=Path("db/migrations/2026-10-08_stock_posting_core");dest="db/migrations/2026-10-10_ni061_receiving/"
for old,new in [("431_before119_balance.sql","003_balance_acl.sql"),("432_before119_location.sql","004_location_acl.sql")]:
 s=(base/old).read_text(encoding="utf-8");s=re.sub(r"\n\s*\n","\n",s)
 assert "accessible by(" in s
 out[dest+new]=s.replace("accessible by(","accessible by(package RRL_STOCK_INTERWARE_REC,",1)
s=(base/"430_before119_root.sql").read_text(encoding="utf-8");s=re.sub(r"\n\s*\n","\n",s)
needle="  elsif g_kind='STORE_RETURN_DISPOSE' then"
assert s.count(needle)==2
s=s.replace(needle,"  elsif g_kind in('INTERWARE_UNLOAD','INTERWARE_RECEIVE') then RRL_STOCK_INTERWARE_REC.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n"+needle,1)
s=s.replace(needle+" RRL_STOCK_RETURN_DISPOSE.execute_command", "  elsif g_kind in('INTERWARE_UNLOAD','INTERWARE_RECEIVE') then RRL_STOCK_INTERWARE_REC.execute_command(g_request,g_actor,p_result);\n"+needle+" RRL_STOCK_RETURN_DISPOSE.execute_command",1)
assert s.count("RRL_STOCK_INTERWARE_REC")==2
out[dest+"005_root.sql"]=s
out[dest+"006_guards.sql"]="""create or replace trigger RRL_INTERWARE_UNLOAD_GUARD before insert or update or delete on RRL_INTERWARE_UNLOAD for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');k varchar2(80);st varchar2(20);resolved clob;d json_object_t;
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_UNLOAD_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_UNLOAD_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE,RESOLVED_PLAN_JSON into k,st,resolved from RRL_STOCK_OPERATION where OPERATION_ID=op;d:=json_object_t.parse(resolved).get_object('domain');
 if k!='INTERWARE_UNLOAD' or st!='IN_FLIGHT' or d.get_string('plan_operation_id')!=:new.PLAN_OPERATION_ID or d.get_string('uid')!=:new.ROOT_UID or d.get_number('warehouse_id')!=:new.WARE_ID or d.get_string('vehicle_number')!=:new.VEHICLE_NUMBER or d.get_string('inbound_dock')!=:new.INBOUND_DOCK or :new.ACTOR!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'INTERWARE_UNLOAD_RESOLVED_SOURCE_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INTERWARE_PLAN',:new.PLAN_OPERATION_ID));
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INTERWARE_UNLOAD',op));
end;
/
create or replace trigger RRL_INTERWARE_RECEIPT_GUARD before insert or update or delete on RRL_INTERWARE_RECEIPT for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');k varchar2(80);st varchar2(20);resolved clob;d json_object_t;n number;
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_RECEIPT_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_RECEIPT_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE,RESOLVED_PLAN_JSON into k,st,resolved from RRL_STOCK_OPERATION where OPERATION_ID=op;d:=json_object_t.parse(resolved).get_object('domain');
 if k!='INTERWARE_RECEIVE' or st!='IN_FLIGHT' or d.get_string('plan_operation_id')!=:new.PLAN_OPERATION_ID or d.get_string('uid')!=:new.ROOT_UID or d.get_number('warehouse_id')!=:new.WARE_ID or d.get_string('receive_cell')!=:new.RECEIVE_CELL or d.get_string('article')!=:new.ARTICLE or RRL_STOCK_MATH.quantity(d.get_string('quantity'))!=:new.BASE_QTY or d.get_string('base_uom')!=:new.BASE_UOM or d.get_string('source_load_operation_id')!=:new.SOURCE_LOAD_OPERATION_ID or d.get_string('unload_operation_id')!=:new.UNLOAD_OPERATION_ID or :new.ACTOR!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'INTERWARE_RECEIPT_RESOLVED_SOURCE_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INTERWARE_PLAN',:new.PLAN_OPERATION_ID));
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INTERWARE_UNLOAD',:new.UNLOAD_OPERATION_ID));
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INTERWARE_RECEIPT',op));
 select count(*)into n from RRL_EVENTS where ID_EVENT=:new.STOCK_EVENT_ID and OPERATION_ID=op and UID_POLETA=:new.ROOT_UID and BASE_QTY=:new.BASE_QTY and BASE_UOM=:new.BASE_UOM and CELL_TO=:new.RECEIVE_CELL;
 if n!=1 then raise_application_error(-20863,'INTERWARE_RECEIPT_STOCK_EVENT_REQUIRED');end if;
end;
/
"""
out[dest+"apply.sql"]="""@@001_schema.sql
@@002_command.sql
@@003_balance_acl.sql
@@004_location_acl.sql
@@005_root.sql
@@006_guards.sql
alter package RRL_STOCK_INTERWARE_REC compile body;
alter package RRL_STOCK_POSTING_API compile body;
declare n number;begin select count(*)into n from user_objects where OBJECT_NAME in('RRL_STOCK_INTERWARE_REC','RRL_STOCK_POSTING_API','RRL_STOCK_BALANCE_CORE','RRL_STOCK_LOCATION_CORE','RRL_INTERWARE_UNLOAD_GUARD','RRL_INTERWARE_RECEIPT_GUARD')and STATUS!='VALID';if n!=0 then raise_application_error(-20899,'INTERWARE119_INVALID_OBJECTS');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-119-native-interwarehouse-unload-receipt' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Original departed ordinary cargo unload and same-UID target receipt through sole stock core; no duplicate customer fulfillment',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
"""
out[dest+"rollback.sql"]="""declare n number;begin select(select count(*)from RRL_INTERWARE_RECEIPT)+(select count(*)from RRL_INTERWARE_UNLOAD)into n from dual;if n!=0 then raise_application_error(-20899,'INTERWARE119_FACTS_FORWARD_CORRECTION_REQUIRED');end if;end;
/
@@../2026-10-08_stock_posting_core/430_before119_root.sql
@@../2026-10-08_stock_posting_core/431_before119_balance.sql
@@../2026-10-08_stock_posting_core/432_before119_location.sql
drop table RRL_INTERWARE_RECEIPT;
drop table RRL_INTERWARE_UNLOAD;
drop package RRL_STOCK_INTERWARE_REC;
"""
print(json.dumps(out,ensure_ascii=True))
