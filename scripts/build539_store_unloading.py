import json
from pathlib import Path
d=Path("db/migrations/2026-10-12_ni053_unloading_facts");out={}
out[str(d/"001_schema.sql")]="""begin execute immediate q'[create table RRL_STORE_UNLOAD_START(
 OPERATION_ID varchar2(100)primary key,LOAD_OPERATION_ID varchar2(100)not null unique references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 STORE_ADDR varchar2(255)not null,ROOT_KEY varchar2(200)not null,COMPOSITION_SIGNATURE varchar2(64)not null,
 ACTOR nvarchar2(50)not null,STARTED_AT_INSTANT timestamp with time zone default systimestamp not null,
 REQUEST_JSON clob not null check(REQUEST_JSON is json),RESULT_JSON clob not null check(RESULT_JSON is json))]';
exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_STORE_UNLOAD_FACT(
 RECEIPT_OPERATION_ID varchar2(100)primary key references RRL_STORE_RECEIPT_FACT(OPERATION_ID),
 START_OPERATION_ID varchar2(100)not null unique references RRL_STORE_UNLOAD_START(OPERATION_ID),
 LOAD_OPERATION_ID varchar2(100)not null unique references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 STORE_ADDR varchar2(255)not null,METHOD varchar2(20)not null check(METHOD in('ROLL_CAGE','PALLET','MANUAL')),
 ROLLING_DIFFICULT number(1)not null check(ROLLING_DIFFICULT in(0,1)),
 LOADER_PRESENT number(1)not null check(LOADER_PRESENT in(0,1)),
 EVIDENCE_REFERENCE varchar2(255)not null,ACTOR nvarchar2(50)not null,
 FINISHED_AT_INSTANT timestamp with time zone default systimestamp not null,
 PAYLOAD_JSON clob not null check(PAYLOAD_JSON is json))]';
exception when others then if sqlcode!=-955 then raise;end if;end;
/
"""
out[str(d/"002_start_api.sql")]=r"""create or replace package RRL_STORE_UNLOAD_API authid definer as
 procedure start_unloading(p_request clob,p_actor varchar2,p_result out clob);
 function writing return boolean;
end;
/
create or replace package body RRL_STORE_UNLOAD_API as
 g_writing boolean:=false;
 function writing return boolean is begin return g_writing;end;
 procedure start_unloading(p_request clob,p_actor varchar2,p_result out clob)is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;j json_object_t:=json_object_t();
 op varchar2(100):=d.get_string('operation_id');load_op varchar2(100):=d.get_string('load_operation_id');addr_text varchar2(255):=d.get_string('store_address');
 expected varchar2(64):=d.get_string('expected_composition_signature');raw_domain clob;old_request clob;old_actor nvarchar2(50);n number;trip number;started timestamp with time zone;
 f json_array_t:=json_array_t();r json_array_t:=json_array_t();state varchar2(20);root_node json_object_t;scan_text varchar2(200):=d.get_string('scan_place');root_text varchar2(200);signature varchar2(64);keys json_key_list:=d.get_keys;
 begin
  savepoint store_unload_start;
  if op is null or not regexp_like(op,'^[A-Za-z0-9_.:-]+$')or length(op)>100 or load_op is null or addr_text is null or keys.count!=6
   or expected is null or not regexp_like(expected,'^[A-F0-9]{64}$')
   or d.get_boolean('before_cameras')is null or not d.get_boolean('before_cameras')
   then raise_application_error(-20886,'UNLOAD_START_INPUT_REQUIRED');end if;
  for i in 1..keys.count loop
   if keys(i)not in('operation_id','load_operation_id','store_address','expected_composition_signature','scan_place','before_cameras')
    then raise_application_error(-20886,'UNLOAD_START_UNKNOWN_FIELD');end if;
  end loop;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',op);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_HU_LOAD_FACT',load_op);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STORE.RECEIPT.LOAD:'||load_op);
  RRL_STOCK_LOCK_API.begin_plan;RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if state!='ACTIVE'then raise_application_error(-20860,'UNLOAD_START_RELEASE_CLOSED');end if;
  RRL_STOCK_STORE_RECEIPT_READ.describe_load(load_op,p_actor,addr_text,raw_domain);v:=json_object_t.parse(raw_domain);
  begin
   select REQUEST_JSON,ACTOR,RESULT_JSON into old_request,old_actor,p_result from RRL_STORE_UNLOAD_START where OPERATION_ID=op;
   select count(*)into n from dual where json_equal(old_request,p_request);
   if n!=1 or old_actor!=p_actor then raise_application_error(-20864,'UNLOAD_START_OPERATION_CONFLICT');end if;
   RRL_STOCK_LOCK_API.clear_plan;return;
  exception when no_data_found then null;end;
  if v.get_boolean('already_received')then raise_application_error(-20886,'UNLOAD_START_RECEIPT_ALREADY_COMPLETED');end if;
  if expected!=v.get_string('composition_signature')then raise_application_error(-20890,'CLOSURE_CHANGED: unload manifest');end if;
  root_node:=treat(v.get_object('snapshot').get_array('nodes').get(0)as json_object_t);
  if scan_text is null or(scan_text!=v.get_string('root_scan_identifier')and
    (root_node.get_string('kind')='CASE'or v.get_string('root_sscc')is null or scan_text!=v.get_string('root_sscc')))
   then raise_application_error(-20886,'UNLOAD_START_PHYSICAL_PLACE_SCAN_REQUIRED');end if;
  select count(*)into n from RRL_STORE_UNLOAD_START where LOAD_OPERATION_ID=load_op;
  if n!=0 then raise_application_error(-20886,'UNLOAD_START_EXISTS');end if;
  select TT_ID into trip from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=load_op for update;
  started:=systimestamp;root_text:=v.get_string('root');signature:=v.get_string('composition_signature');
  j.put('operation_id',op);j.put('load_operation_id',load_op);j.put('store_address',addr_text);j.put('root',root_text);j.put('trip_id',trip);
  j.put('started_at_instant',to_char(started,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));
  j.put('time_source','SYSTEM_CAPTURED');j.put('status','STARTED');j.put('stock_changed',false);j.put('cost_posted',false);p_result:=j.to_clob;
  g_writing:=true;
  insert into RRL_STORE_UNLOAD_START(OPERATION_ID,LOAD_OPERATION_ID,STORE_ADDR,ROOT_KEY,COMPOSITION_SIGNATURE,ACTOR,STARTED_AT_INSTANT,REQUEST_JSON,RESULT_JSON)
   values(op,load_op,addr_text,root_text,signature,p_actor,started,p_request,p_result);
  g_writing:=false;RRL_STOCK_LOCK_API.clear_plan;
 exception when others then g_writing:=false;rollback to store_unload_start;RRL_STOCK_LOCK_API.clear_plan;raise;
 end;
end;
/
create or replace trigger RRL_STORE_UNLOAD_START_G before insert or update or delete on RRL_STORE_UNLOAD_START for each row
begin if not inserting or not RRL_STORE_UNLOAD_API.writing then raise_application_error(-20863,'UNLOAD_START_HISTORY_IMMUTABLE');end if;end;
/
"""
out[str(d/"003_receipt_core.sql")]=r"""create or replace package RRL_STORE_UNLOAD_CORE authid definer as
 procedure validate_input(p_metadata json_object_t,p_domain json_object_t);
 procedure capture(p_request clob,p_actor varchar2);
 function writing return boolean;
end;
/
create or replace package body RRL_STORE_UNLOAD_CORE as
 g_writing boolean:=false;
 function writing return boolean is begin return g_writing;end;
 procedure validate_input(p_metadata json_object_t,p_domain json_object_t)is
 m json_object_t;s RRL_STORE_UNLOAD_START%rowtype;n number;root_node json_object_t;keys json_key_list;load_op varchar2(100):=p_domain.get_string('load_operation_id');
 method_value varchar2(20);difficulty boolean;loader boolean;
 begin
  select count(*)into n from RRL_STORE_UNLOAD_START where LOAD_OPERATION_ID=load_op;
  if not p_metadata.has('unloading')or p_metadata.get('unloading').is_null then
   if n!=0 then raise_application_error(-20886,'UNLOAD_FINISH_DETAILS_REQUIRED');end if;return;
  end if;
  m:=p_metadata.get_object('unloading');keys:=m.get_keys;
  if keys.count!=5 then raise_application_error(-20886,'UNLOAD_FINISH_FIELDS_REQUIRED');end if;
  for i in 1..keys.count loop
   if keys(i)not in('start_operation_id','method','rolling_difficult','loader_present','evidence_reference')
    then raise_application_error(-20886,'UNLOAD_FINISH_UNKNOWN_FIELD');end if;
  end loop;
  begin select *into s from RRL_STORE_UNLOAD_START where OPERATION_ID=m.get_string('start_operation_id');
  exception when no_data_found then raise_application_error(-20886,'UNLOAD_SYSTEM_START_REQUIRED');end;
  if s.LOAD_OPERATION_ID!=load_op or s.STORE_ADDR!=p_domain.get_string('store_address')or s.ROOT_KEY!=p_domain.get_string('root')
   or s.COMPOSITION_SIGNATURE!=p_domain.get_string('composition_signature')
   then raise_application_error(-20886,'UNLOAD_ORIGINAL_SOURCE_REQUIRED');end if;
  method_value:=m.get_string('method');difficulty:=m.get_boolean('rolling_difficult');loader:=m.get_boolean('loader_present');
  if method_value is null or method_value not in('ROLL_CAGE','PALLET','MANUAL')or difficulty is null or loader is null
   or trim(m.get_string('evidence_reference'))is null or lengthb(m.get_string('evidence_reference'))>255
   then raise_application_error(-20886,'UNLOAD_ACTUAL_DETAILS_REQUIRED');end if;
  root_node:=treat(p_domain.get_object('snapshot').get_array('nodes').get(0)as json_object_t);
  if method_value='ROLL_CAGE'and(root_node.get_string('kind')!='CONTAINER'or root_node.get_string('type')!='ROLL_CAGE')
   then raise_application_error(-20886,'UNLOAD_ROLL_CAGE_SOURCE_REQUIRED');end if;
  if method_value='PALLET'and(root_node.get_string('kind')!='CONTAINER'or root_node.get_string('type')!='PALLET')
   then raise_application_error(-20886,'UNLOAD_PALLET_SOURCE_REQUIRED');end if;
  if difficulty and(method_value!='ROLL_CAGE'or not loader)then raise_application_error(-20886,'UNLOAD_DIFFICULT_ROLL_REQUIRES_LOADER');end if;
 end;
 procedure capture(p_request clob,p_actor varchar2)is
 d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');u json_object_t;
 op varchar2(100):=d.get_string('operation_id');source_op varchar2(100);method_value varchar2(20);reference_value varchar2(255);difficulty number;loader number;
 s RRL_STORE_UNLOAD_START%rowtype;receipt RRL_STORE_RECEIPT_FACT%rowtype;body clob;kind varchar2(80);state varchar2(20);
 begin
  if not m.has('unloading')or m.get('unloading').is_null then return;end if;
  if nvl(sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID'),'~')!=op or
   sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
   then raise_application_error(-20863,'UNLOAD_FINISH_ROOT_REQUIRED');end if;
  select COMMAND_TYPE,STATE into kind,state from RRL_STOCK_OPERATION where OPERATION_ID=op;
  if kind!='STORE_RECEIPT'or state!='IN_FLIGHT'then raise_application_error(-20863,'UNLOAD_FINISH_RECEIPT_OWNER_REQUIRED');end if;
  u:=m.get_object('unloading');source_op:=u.get_string('start_operation_id');
  select *into s from RRL_STORE_UNLOAD_START where OPERATION_ID=source_op;
  select *into receipt from RRL_STORE_RECEIPT_FACT where OPERATION_ID=op;
  if receipt.LOAD_OPERATION_ID!=s.LOAD_OPERATION_ID or receipt.STORE_ADDR!=s.STORE_ADDR or receipt.RECEIVED_BY!=p_actor
   or receipt.RECEIVED_AT<s.STARTED_AT_INSTANT then raise_application_error(-20886,'UNLOAD_FINISH_ORIGINAL_RECEIPT_REQUIRED');end if;
  method_value:=u.get_string('method');reference_value:=u.get_string('evidence_reference');
  difficulty:=case when u.get_boolean('rolling_difficult')then 1 else 0 end;loader:=case when u.get_boolean('loader_present')then 1 else 0 end;
  body:=u.to_clob;g_writing:=true;
  insert into RRL_STORE_UNLOAD_FACT(RECEIPT_OPERATION_ID,START_OPERATION_ID,LOAD_OPERATION_ID,STORE_ADDR,METHOD,ROLLING_DIFFICULT,LOADER_PRESENT,EVIDENCE_REFERENCE,ACTOR,FINISHED_AT_INSTANT,PAYLOAD_JSON)
  values(op,source_op,s.LOAD_OPERATION_ID,s.STORE_ADDR,method_value,difficulty,loader,reference_value,p_actor,receipt.RECEIVED_AT,body);
  g_writing:=false;
 exception when others then g_writing:=false;raise;
 end;
end;
/
create or replace trigger RRL_STORE_UNLOAD_FACT_G before insert or update or delete on RRL_STORE_UNLOAD_FACT for each row
begin if not inserting or not RRL_STORE_UNLOAD_CORE.writing then raise_application_error(-20863,'UNLOAD_FINISH_HISTORY_IMMUTABLE');end if;end;
/
"""
# Bind scalars before SQL.
v=out[str(d/"003_receipt_core.sql")].replace("difficulty boolean;loader boolean;","difficulty boolean;loader boolean;start_op varchar2(100);")
v=v.replace("  begin select *into s from RRL_STORE_UNLOAD_START where OPERATION_ID=m.get_string('start_operation_id');",
            "  start_op:=m.get_string('start_operation_id');\n  begin select *into s from RRL_STORE_UNLOAD_START where OPERATION_ID=start_op;")
out[str(d/"003_receipt_core.sql")]=v
src=Path("tmp/RRL_STOCK_STORE_RECEIPT_CMD_537.sql").read_text(encoding="utf-8").replace("\r","")
out[str(d/"000_before_receipt.sql")]=src
needle="v:=json_object_t.parse(raw_domain);assert_input(m,v);"
assert src.count(needle)==1
src=src.replace(needle,needle+"RRL_STORE_UNLOAD_CORE.validate_input(m,v);")
needle="  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RECEIPT_FACT',p_operation);"
assert src.count(needle)==1
src=src.replace(needle,needle+"\n  if m.has('unloading')and not m.get('unloading').is_null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_UNLOAD_START',m.get_object('unloading').get_string('start_operation_id'));end if;")
# Validate again after acquiring the root's resource closure.
needle="assert_input(m,v);"
# This now appears twice: compile and execute.
assert src.count(needle)==1
src=src.replace("assert_input(m,now_v);","assert_input(m,now_v);RRL_STORE_UNLOAD_CORE.validate_input(m,now_v);")
src=src.replace("RRL_STORE_UNLOAD_CORE.validate_input(m,v);RRL_STORE_UNLOAD_CORE.validate_input(m,v);","RRL_STORE_UNLOAD_CORE.validate_input(m,v);")
needle="  j.put('operation_id',op);"
assert src.count(needle)==1
src=src.replace(needle,"  RRL_STORE_UNLOAD_CORE.capture(p_request,p_actor);\n  if m.has('unloading')and not m.get('unloading').is_null then j.put('unloading',m.get_object('unloading'));end if;\n"+needle)
out[str(d/"004_receipt_command.sql")]=src
out[str(d/"005_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-539-store-unloading-start-finish-facts' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'System-captured unloading start; actual method/difficulty/loader finished atomically with original STORE_RECEIPT owner',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
out[str(d/"apply.sql")]="@@001_schema.sql\n@@002_start_api.sql\n@@003_receipt_core.sql\n@@004_receipt_command.sql\n@@005_ledger.sql\n"
out[str(d/"rollback.sql")]="""declare n number;begin select count(*)into n from RRL_STORE_UNLOAD_START;
 if n!=0 then raise_application_error(-20886,'UNLOAD_FACT_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_receipt.sql
drop trigger RRL_STORE_UNLOAD_FACT_G;
drop trigger RRL_STORE_UNLOAD_START_G;
drop package RRL_STORE_UNLOAD_CORE;
drop package RRL_STORE_UNLOAD_API;
drop table RRL_STORE_UNLOAD_FACT;
drop table RRL_STORE_UNLOAD_START;
-- Existing receipt, buyer facts, traceability, outbox and stock remain untouched.
"""
print(json.dumps(out))
