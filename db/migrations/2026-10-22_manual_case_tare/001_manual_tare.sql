create table RRL_CASE_MANUAL_TARE(
 OPERATION_ID varchar2(100) primary key,CASE_PICK_TASK_ID number not null references RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID),
 WARE_ID number not null,SSCC varchar2(150) not null,PALLET_TYPE_ID number not null,TYPE_VERSION number not null,
 CONTENT_VERSION number not null,TARE_KG number(18,9) not null check(TARE_KG>0),
 MEASUREMENT_REF varchar2(100) not null,RECORDED_BY varchar2(100) not null,
 RECORDED_AT timestamp with time zone default systimestamp not null,
 REQUEST_JSON clob not null check(REQUEST_JSON is json),RESULT_JSON clob not null check(RESULT_JSON is json)
);
create index RRL_CASE_MANUAL_TARE_IX on RRL_CASE_MANUAL_TARE(CASE_PICK_TASK_ID,RECORDED_AT);
create or replace package RRL_CASE_MANUAL_TARE_API authid definer as
 procedure record_tare(p_task number,p_request clob,p_actor varchar2,p_result out clob);
 function current_tare(p_task number)return number;
end;
/
create or replace package body RRL_CASE_MANUAL_TARE_API as
 function current_tare(p_task number)return number is weight_value number;begin
  select TARE_KG into weight_value from(
   select m.TARE_KG from RRL_CASE_MANUAL_TARE m
    join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=m.CASE_PICK_TASK_ID
    join RRL_PALLET_TYPE pt on pt.PALLET_TYPE_ID=ct.PALLET_TYPE_ID
   where m.CASE_PICK_TASK_ID=p_task and m.WARE_ID=ct.WARE_ID and m.SSCC=ct.SSCC
    and m.PALLET_TYPE_ID=ct.PALLET_TYPE_ID and m.TYPE_VERSION=pt.TYPE_VERSION
    and m.RECORDED_AT>=systimestamp-numtodsinterval(24,'HOUR')and m.RECORDED_AT<=systimestamp
   order by m.RECORDED_AT desc,m.OPERATION_ID desc)where rownum=1;
  return weight_value;
 exception when no_data_found then return null;end;
 procedure record_tare(p_task number,p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);ct RRL_CASE_PICK_TASK%rowtype;old RRL_CASE_MANUAL_TARE%rowtype;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();result_value json_object_t:=json_object_t();
  op varchar2(100);reference_value varchar2(100);weight_value number;required number;type_version number;state varchar2(20);n number;
 begin
  RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,'case_pick_execute');
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE',6);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA');
  RRL_STOCK_LOCK_API.begin_plan;lock table RRL_ACCESS_REV in share mode wait 2;
  RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if state is null or state not in('PREPARED','ACTIVE')then raise_application_error(-20860,'TASK_METADATA_RELEASE_CLOSED');end if;
  select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task for update;
  RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,'case_pick_execute');
  op:=d.get_string('operation_id');reference_value:=trim(d.get_string('measurement_ref'));
  if op is null or length(op)>100 or not regexp_like(op,'^[A-Za-z0-9_.:-]+$')or d.get_size<>5
   or reference_value is null or length(reference_value)>100 then raise_application_error(-20887,'MANUAL_TARE_REQUEST_REQUIRED');end if;
  begin
   select *into old from RRL_CASE_MANUAL_TARE where OPERATION_ID=op;
   if old.CASE_PICK_TASK_ID<>p_task or old.RECORDED_BY<>p_actor or dbms_lob.compare(old.REQUEST_JSON,p_request)<>0 then raise_application_error(-20873,'MANUAL_TARE_OPERATION_CONFLICT');end if;
   p_result:=old.RESULT_JSON;RRL_STOCK_LOCK_API.clear_plan;return;
  exception when no_data_found then null;end;
  if ct.ASSIGNED_TO<>p_actor or ct.ASSIGNED_TO is null or ct.STATUS not in('NEW','ASSIGNED','IN_PROGRESS')
   or nvl(ct.PICKED_QTY,0)<>0 or d.get_number('expected_content_version')is null or ct.CONTENT_VERSION<>d.get_number('expected_content_version')
   or d.get_string('scan_container')is null or ct.SSCC<>d.get_string('scan_container')or ct.LEGACY_SBORKA_PALLET_ID is not null
   then raise_application_error(-20873,'MANUAL_TARE_EMPTY_CURRENT_CASE_REQUIRED');end if;
  RRL_CASE_SSCC_API.assert_ready(p_task);
  select case when FINAL_WEIGHT_REQUIRED=1 and upper(LOAD_UNIT_CLASS)='CONTAINER'and ACTIVE=1 then 1 else 0 end,TYPE_VERSION
   into required,type_version from RRL_PALLET_TYPE where PALLET_TYPE_ID=ct.PALLET_TYPE_ID;
  select count(*)into n from RRL_WMS_HU_LINK where CHILD_CASE_TASK_ID=p_task and ACTIVE_FLAG=1;
  if required<>1 or n<>0 then raise_application_error(-20887,'MANUAL_TARE_INDEPENDENT_CARTON_REQUIRED');end if;
  weight_value:=RRL_STOCK_MATH.quantity(d.get_string('tare_weight_kg'));
  result_value.put('operation_id',op);result_value.put('case_pick_task_id',p_task);result_value.put('sscc',ct.SSCC);
  result_value.put('content_version',ct.CONTENT_VERSION);result_value.put('tare_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(weight_value));
  result_value.put('origin','MANUAL_CONFIRMED');result_value.put('recorded_by',p_actor);result_value.put('measurement_ref',reference_value);
  result_value.put('stock_changed',false);p_result:=result_value.to_clob;
  dbms_session.set_context('RRL_MANUAL_TARE_CTX','TX_ID',dbms_transaction.local_transaction_id(true));
  insert into RRL_CASE_MANUAL_TARE(OPERATION_ID,CASE_PICK_TASK_ID,WARE_ID,SSCC,PALLET_TYPE_ID,TYPE_VERSION,CONTENT_VERSION,TARE_KG,MEASUREMENT_REF,RECORDED_BY,REQUEST_JSON,RESULT_JSON)
   values(op,p_task,ct.WARE_ID,ct.SSCC,ct.PALLET_TYPE_ID,type_version,ct.CONTENT_VERSION,weight_value,reference_value,p_actor,p_request,p_result);
  dbms_session.clear_context('RRL_MANUAL_TARE_CTX',null);RRL_STOCK_LOCK_API.clear_plan;
 exception when others then dbms_session.clear_context('RRL_MANUAL_TARE_CTX',null);RRL_STOCK_LOCK_API.clear_plan;raise;end;
end;
/
create context RRL_MANUAL_TARE_CTX using RRL_CASE_MANUAL_TARE_API;
create or replace trigger RRL_CASE_MANUAL_TARE_GUARD before insert or update or delete on RRL_CASE_MANUAL_TARE
begin
 if updating or deleting or sys_context('RRL_MANUAL_TARE_CTX','TX_ID')is null
  or sys_context('RRL_MANUAL_TARE_CTX','TX_ID')<>dbms_transaction.local_transaction_id(false)
  then raise_application_error(-20882,'MANUAL_TARE_APPEND_ONLY_NATIVE_REQUIRED');end if;
end;
/
