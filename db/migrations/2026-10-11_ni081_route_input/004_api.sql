create or replace package RRL_TT_ROUTE_API authid definer as
 function write_allowed(p_operation varchar2)return number;
 procedure context(p_trip number,p_actor varchar2,p_result out clob);
 procedure apply_input(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob);
end;
/
create or replace package body RRL_TT_ROUTE_API as
 g_operation varchar2(100);g_tx varchar2(100);
 function write_allowed(p_operation varchar2)return number is begin
  if g_operation=p_operation and g_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;
 end;
 procedure context(p_trip number,p_actor varchar2,p_result out clob)is
  src clob;hash varchar2(64);v_version number;saved RRL_TT_ROUTE_INPUT%rowtype;b json_object_t:=json_object_t();
 begin
  RRL_TT_ROUTE_SOURCE.snapshot(p_trip,p_actor,src,hash);
  select nvl(max(VERSION_NO),0)into v_version from RRL_TT_ROUTE_INPUT where TT_ID=p_trip;
  b.put('trip_id',p_trip);b.put('source_hash',hash);b.put('version',v_version);b.put('source',json_object_t.parse(src));
  b.put('route_status','NO_INPUT');b.put('route_duration_verified',false);b.put('operational_admission',false);
  if v_version>0 then
   select *into saved from RRL_TT_ROUTE_INPUT where TT_ID=p_trip and VERSION_NO=v_version;
   b.put('last_input',json_object_t.parse(saved.RESULT_JSON));
   if saved.SOURCE_HASH=hash then b.put('route_status','CURRENT_DISPATCH_ESTIMATE');else b.put('route_status','SOURCE_CHANGED');end if;
  end if;
  p_result:=b.to_clob;
 end;
 procedure apply_input(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob)is
  b json_object_t;v_trip number;v_version number;v_req_hash varchar2(64);src clob;hash varchar2(64);
  w RRL_TRANSPORT_TASK%rowtype;saved RRL_TT_ROUTE_INPUT%rowtype;
  v_drive number;v_back number;v_ref nvarchar2(500);v_reason nvarchar2(500);
  v_before varchar2(50);v_vehicle number;v_locked number;n number;v_meta boolean:=false;
  result json_object_t:=json_object_t();ops clob;
 begin
  if p_operation is null or lengthb(p_operation)>100 or not regexp_like(p_operation,'^[A-Za-z0-9_.:-]+$')or p_body is null or dbms_lob.getlength(p_body)>4000 then raise_application_error(-20886,'TT_ROUTE_INPUT_BOUND');end if;
  b:=json_object_t.parse(p_body);v_trip:=b.get_number('trip_id');
  RRL_TT_ROUTE_SOURCE.snapshot(v_trip,p_actor,src,hash);
  v_req_hash:=lower(rawtohex(sys.dbms_crypto.hash(p_body,sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_METADATA_TX.begin_change(p_actor,'transport_dispatch_edit');v_meta:=true;savepoint RRL_TT_ROUTE259;
  select TRANSPORT into v_before from RRL_TRANSPORT_TASK where ID=v_trip;
  if v_before is null then raise_application_error(-20886,'TT_ROUTE_VEHICLE_REQUIRED');end if;
  select ID into v_vehicle from RRL_TR_VEHICLE where NUM=v_before;
  select ID into v_locked from RRL_TR_VEHICLE where ID=v_vehicle for update;
  select *into w from RRL_TRANSPORT_TASK where ID=v_trip for update;
  if nvl(w.TRANSPORT,'~')!=nvl(v_before,'~')then raise_application_error(-20886,'TT_ROUTE_VEHICLE_CHANGED_RETRY');end if;
  RRL_TT_ROUTE_SOURCE.snapshot(v_trip,p_actor,src,hash);
  begin
   select *into saved from RRL_TT_ROUTE_INPUT where OPERATION_ID=p_operation;
   if saved.ACTOR!=p_actor or saved.TT_ID!=v_trip or saved.REQUEST_HASH!=v_req_hash then raise_application_error(-20886,'TT_ROUTE_OPERATION_PAYLOAD_CONFLICT');end if;
   p_result:=saved.RESULT_JSON;RRL_STOCK_METADATA_TX.end_change;return;
  exception when no_data_found then null;end;
  select nvl(max(VERSION_NO),0)into v_version from RRL_TT_ROUTE_INPUT where TT_ID=v_trip;
  if b.get_number('expected_version')is null or b.get_number('expected_version')!=v_version or b.get_string('source_hash')is null or b.get_string('source_hash')!=hash then raise_application_error(-20886,'TT_ROUTE_SOURCE_CHANGED');end if;
  if nvl(w.DELETED,0)!=0 or w.CONDITION is null or w.CONDITION!='Спланирован'or nvl(w.PAY_ORDER_ID,0)>0 then raise_application_error(-20886,'TT_ROUTE_PLANNED_UNBILLED_REQUIRED');end if;
  v_drive:=b.get_number('drive_min');v_back:=b.get_number('drive_back_min');v_ref:=b.get_string('source_reference');v_reason:=b.get_string('reason');
  if v_drive is null or v_back is null or v_drive<=0 or v_drive>1440 or v_back<=0 or v_back>1440 or round(v_drive,2)!=v_drive or round(v_back,2)!=v_back or v_ref is null or length(trim(v_ref))<8 or v_reason is null or length(trim(v_reason))<8 then raise_application_error(-20886,'TT_ROUTE_EXPLICIT_ESTIMATE_REQUIRED');end if;
  select count(*)into n from RRL_TT_HU_LOAD_FACT where TT_ID=v_trip and STATUS in('LOADED','DEPARTED');
  if n>0 then raise_application_error(-20886,'TT_ROUTE_PHYSICAL_EXECUTION_FROZEN');end if;
  select count(*)into n from RRL_TT_OPERATIONS where TT_ID=v_trip and(FACT_START is not null or FACT_END is not null);
  if n>0 then raise_application_error(-20886,'TT_ROUTE_OPERATION_EXECUTION_FROZEN');end if;
  result.put('trip_id',v_trip);result.put('version',v_version+1);result.put('operation_id',p_operation);result.put('source_hash',hash);
  result.put('plan_source',json_object_t.parse(src));result.put('drive_min',v_drive);result.put('drive_back_min',v_back);
  result.put('source_reference',v_ref);result.put('reason',v_reason);result.put('actor',p_actor);
  result.put('basis','MANUAL_DISPATCH_ESTIMATE');result.put('route_duration_verified',false);result.put('operational_admission',false);
  p_result:=result.to_clob;g_operation:=p_operation;g_tx:=dbms_transaction.local_transaction_id(false);
  insert into RRL_TT_ROUTE_INPUT(TT_ID,VERSION_NO,OPERATION_ID,ACTOR,REQUEST_HASH,SOURCE_HASH,DRIVE_MIN,DRIVE_BACK_MIN,SOURCE_REFERENCE,REASON,RESULT_JSON)
   values(v_trip,v_version+1,p_operation,p_actor,v_req_hash,hash,v_drive,v_back,v_ref,v_reason,p_result);
  RRL_TT_OPERATION_PLAN_API.generate(v_trip,p_actor,ops);
  g_operation:=null;g_tx:=null;RRL_STOCK_METADATA_TX.end_change;
 exception when others then
  if v_meta then rollback to RRL_TT_ROUTE259;end if;g_operation:=null;g_tx:=null;
  if v_meta then RRL_STOCK_METADATA_TX.end_change;end if;raise;
 end;
end;
/
create or replace trigger RRL_TT_ROUTE_INPUT_GUARD before insert or update or delete on RRL_TT_ROUTE_INPUT for each row
begin
 if not inserting or RRL_TT_ROUTE_API.write_allowed(:new.OPERATION_ID)!=1 then raise_application_error(-20863,'TT_ROUTE_INPUT_IMMUTABLE');end if;
end;
/
