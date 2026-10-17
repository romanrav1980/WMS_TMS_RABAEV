create or replace package body RRL_DELIVERY_TIME_API as
 function stamp(p_value timestamp with time zone)return varchar2 is
 begin return to_char(p_value at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');end;
 function time_value(p_value varchar2)return timestamp with time zone is result_value timestamp with time zone;
 begin
  if p_value is null or not regexp_like(p_value,'^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[.][0-9]{6}[+]00:00$')then raise_application_error(-20871,'DELIVERY_AWARE_UTC_INSTANT_REQUIRED');end if;
  result_value:=to_timestamp_tz(p_value,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');return result_value;
 end;
 procedure clean_entry is
 begin
  if dbms_transaction.local_transaction_id(false)is not null or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null
   or sys_context('RRL_DELIVERY_TIME_CTX','OPERATION_ID')is not null then raise_application_error(-20862,'DELIVERY_TIME_CLEAN_TRANSACTION_REQUIRED');end if;
 end;
 procedure enter_write(p_operation varchar2,p_actor varchar2,p_action varchar2)is policies json_array_t:=json_array_t();state_value varchar2(20);
 begin
  RRL_STOCK_LOCK_API.begin_plan;
  lock table RRL_ACCESS_REV in share mode wait 5;
  RRL_STOCK_PLAN_HELPER.fence(policies,'CONFIG','WAREHOUSE');RRL_STOCK_LOCK_API.acquire_policies(policies.to_clob);
  select STATE into state_value from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if state_value!='ACTIVE'then raise_application_error(-20860,'STOCK_RELEASE_NOT_ACTIVE');end if;
  dbms_session.set_context('RRL_DELIVERY_TIME_CTX','OPERATION_ID',p_operation);
  dbms_session.set_context('RRL_DELIVERY_TIME_CTX','ACTOR',p_actor);
  dbms_session.set_context('RRL_DELIVERY_TIME_CTX','ACTION',p_action);
  dbms_session.set_context('RRL_DELIVERY_TIME_CTX','TX_ID',dbms_transaction.local_transaction_id(true));
 end;
 procedure leave_write is
 begin dbms_session.clear_context('RRL_DELIVERY_TIME_CTX',null,null);RRL_STOCK_LOCK_API.clear_plan;end;
 procedure source_scope(p_load varchar2,p_store varchar2,p_actor varchar2,p_action varchar2,
  p_ware out number,p_trip out number,p_status out varchar2)is n number;driver_value number;
 begin
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  if n!=1 then raise_application_error(-20882,'DELIVERY_CURRENT_ACTOR_REQUIRED');end if;
  select WARE_ID,TT_ID,STATUS into p_ware,p_trip,p_status from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=p_load;
  select count(*)into n from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=p_load and DESTINATION_ADDR=p_store;
  if n<1 then raise_application_error(-20882,'DELIVERY_SOURCE_DESTINATION_FORBIDDEN');end if;
  if RRL_ACCESS_API.allowed(p_actor,'transport_dispatch_edit','WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(p_ware))=1 then return;end if;
  if p_action='PLAN'then raise_application_error(-20882,'DELIVERY_WINDOW_DISPATCHER_REQUIRED');end if;
  if p_action='READ'and RRL_ACCESS_API.allowed(p_actor,'transport_dispatch_view','WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(p_ware))=1 then return;end if;
  select VODITEL_ID into driver_value from RRL_TRANSPORT_TASK where ID=p_trip and nvl(DELETED,0)=0;
  select count(*)into n from RRL_TRANSPORT_DRIVER_USER where DRIVER_ID=driver_value and USER_ID=p_actor and ACTIVE=1;
  if n=1 then RRL_TT_OPERATION_PLAN_API.assert_driver(driver_value,p_actor);return;end if;
  RRL_STOCK_STORE_RECEIPT_READ.require_receiver(p_actor,p_store);
 exception when no_data_found then raise_application_error(-20882,'DELIVERY_SOURCE_DESTINATION_FORBIDDEN');
 end;
 procedure request_values(p_request clob,p_op out varchar2,p_load out varchar2,p_store out varchar2,p_reason out varchar2,p_hash out raw)is j json_object_t;
 begin
  if p_request is null or dbms_lob.getlength(p_request)>16384 then raise_application_error(-20871,'DELIVERY_TIME_REQUEST_BOUND');end if;
  j:=json_object_t.parse(p_request);p_op:=j.get_string('operation_id');p_load:=j.get_string('load_operation_id');p_store:=j.get_string('store_address');p_reason:=j.get_string('reason');
  if p_op is null or length(p_op)>100 or not regexp_like(p_op,'^[A-Za-z0-9_.:-]+$')or p_load is null or length(p_load)>100
   or p_store is null or length(p_store)>255 or p_reason is null or length(trim(p_reason))<8 or length(p_reason)>500 then raise_application_error(-20871,'DELIVERY_TIME_REQUEST_INVALID');end if;
  p_hash:=sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256);
 end;
 procedure plan_window(p_request clob,p_actor varchar2,p_result out clob)is
  j json_object_t:=json_object_t.parse(p_request);result_value json_object_t:=json_object_t();op varchar2(100);load_value varchar2(100);store_value varchar2(255);reason_value varchar2(500);
  hash_value raw(32);old_hash raw(32);ware number;trip number;status_value varchar2(20);version_value number;expected_value number;
  left_value timestamp with time zone;right_value timestamp with time zone;recorded_value timestamp with time zone:=systimestamp;owned boolean:=false;lock_value varchar2(100);
 begin
  request_values(p_request,op,load_value,store_value,reason_value,hash_value);clean_entry;owned:=true;enter_write(op,p_actor,'PLAN');
  select LOAD_OPERATION_ID into lock_value from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=load_value for update wait 5;
  source_scope(load_value,store_value,p_actor,'PLAN',ware,trip,status_value);
  begin select PAYLOAD_HASH,RESULT_JSON into old_hash,p_result from RRL_DELIVERY_WINDOW where OPERATION_ID=op;
   if old_hash!=hash_value then raise_application_error(-20886,'DELIVERY_TIME_PAYLOAD_CONFLICT');end if;leave_write;return;
  exception when no_data_found then null;end;
  if status_value!='LOADED'then raise_application_error(-20886,'DELIVERY_WINDOW_FREEZE_BEFORE_DEPARTURE_REQUIRED');end if;
  select nvl(max(VERSION_NO),0)into version_value from RRL_DELIVERY_WINDOW where LOAD_OPERATION_ID=load_value and STORE_ADDR=store_value;
  expected_value:=j.get_number('expected_version');
  if expected_value is null or expected_value!=version_value then raise_application_error(-20886,'DELIVERY_WINDOW_VERSION_CONFLICT');end if;
  left_value:=time_value(j.get_string('window_start'));right_value:=time_value(j.get_string('window_finish'));
  if right_value<left_value or right_value-left_value>numtodsinterval(7,'DAY')then raise_application_error(-20871,'DELIVERY_WINDOW_BOUND_7_DAYS');end if;
  version_value:=version_value+1;result_value.put('operation_id',op);result_value.put('load_operation_id',load_value);result_value.put('store_address',store_value);
  result_value.put('warehouse_id',ware);result_value.put('trip_id',trip);result_value.put('version',version_value);result_value.put('window_start',stamp(left_value));result_value.put('window_finish',stamp(right_value));
  result_value.put('recorded_at',stamp(recorded_value));result_value.put('recorded_by',p_actor);result_value.put('stock_changed',false);p_result:=result_value.to_clob;
  insert into RRL_DELIVERY_WINDOW(OPERATION_ID,PAYLOAD_HASH,LOAD_OPERATION_ID,STORE_ADDR,WARE_ID,TT_ID,VERSION_NO,WINDOW_START,WINDOW_FINISH,ACTOR,REASON_TEXT,RECORDED_AT,PAYLOAD_JSON,RESULT_JSON)
   values(op,hash_value,load_value,store_value,ware,trip,version_value,left_value,right_value,p_actor,reason_value,recorded_value,p_request,p_result);
  leave_write;
 exception when others then if owned then leave_write;end if;raise;
 end;
 procedure record_arrival(p_request clob,p_actor varchar2,p_result out clob)is
  j json_object_t:=json_object_t.parse(p_request);result_value json_object_t:=json_object_t();op varchar2(100);load_value varchar2(100);store_value varchar2(255);reason_value varchar2(500);
  hash_value raw(32);old_hash raw(32);ware number;trip number;status_value varchar2(20);window_value RRL_DELIVERY_WINDOW%rowtype;
  arrived_value timestamp with time zone;departed_value timestamp with time zone;recorded_value timestamp with time zone:=systimestamp;
  owned boolean:=false;lock_value varchar2(100);state_value varchar2(20):='NO_PLAN';n number;
 begin
  request_values(p_request,op,load_value,store_value,reason_value,hash_value);clean_entry;owned:=true;enter_write(op,p_actor,'ARRIVE');
  select LOAD_OPERATION_ID,DEPARTED_AT into lock_value,departed_value from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=load_value for update wait 5;
  source_scope(load_value,store_value,p_actor,'ARRIVE',ware,trip,status_value);
  begin select PAYLOAD_HASH,RESULT_JSON into old_hash,p_result from RRL_DELIVERY_ARRIVAL where OPERATION_ID=op;
   if old_hash!=hash_value then raise_application_error(-20886,'DELIVERY_TIME_PAYLOAD_CONFLICT');end if;leave_write;return;
  exception when no_data_found then null;end;
  if status_value!='DEPARTED'or departed_value is null then raise_application_error(-20886,'DELIVERY_DEPARTED_SOURCE_REQUIRED');end if;
  select count(*)into n from RRL_DELIVERY_ARRIVAL where LOAD_OPERATION_ID=load_value and STORE_ADDR=store_value;
  if n>0 then raise_application_error(-20886,'DELIVERY_ARRIVAL_ALREADY_RECORDED');end if;
  arrived_value:=case when j.get_string('arrived_at')is null then recorded_value else time_value(j.get_string('arrived_at'))end;
  if arrived_value<departed_value or arrived_value>recorded_value+numtodsinterval(30,'SECOND')then raise_application_error(-20871,'DELIVERY_ARRIVAL_AFTER_DEPARTURE_NOT_FUTURE_REQUIRED');end if;
  begin
   select *into window_value from RRL_DELIVERY_WINDOW where LOAD_OPERATION_ID=load_value and STORE_ADDR=store_value order by VERSION_NO desc fetch first 1 row only;
   state_value:=case when arrived_value<window_value.WINDOW_START then 'EARLY'when arrived_value>window_value.WINDOW_FINISH then 'LATE'else 'ON_TIME'end;
  exception when no_data_found then null;end;
  result_value.put('operation_id',op);result_value.put('load_operation_id',load_value);result_value.put('store_address',store_value);result_value.put('warehouse_id',ware);result_value.put('trip_id',trip);
  result_value.put('arrived_at',stamp(arrived_value));result_value.put('recorded_at',stamp(recorded_value));result_value.put('recorded_by',p_actor);result_value.put('origin','MANUAL_CONFIRMED');
  result_value.put('window_operation_id',window_value.OPERATION_ID);result_value.put('on_time_state',state_value);result_value.put('stock_changed',false);p_result:=result_value.to_clob;
  insert into RRL_DELIVERY_ARRIVAL(OPERATION_ID,PAYLOAD_HASH,LOAD_OPERATION_ID,STORE_ADDR,WARE_ID,TT_ID,WINDOW_OPERATION_ID,ARRIVED_AT,ON_TIME_STATE,ACTOR,REASON_TEXT,RECORDED_AT,PAYLOAD_JSON,RESULT_JSON)
   values(op,hash_value,load_value,store_value,ware,trip,window_value.OPERATION_ID,arrived_value,state_value,p_actor,reason_value,recorded_value,p_request,p_result);
  leave_write;
 exception when others then if owned then leave_write;end if;raise;
 end;
 procedure read_times(p_load varchar2,p_store varchar2,p_actor varchar2,p_result out clob)is
  ware number;trip number;status_value varchar2(20);j json_object_t:=json_object_t();wire clob;
 begin
  source_scope(p_load,p_store,p_actor,'READ',ware,trip,status_value);
  j.put('load_operation_id',p_load);j.put('store_address',p_store);j.put('warehouse_id',ware);j.put('trip_id',trip);j.put('load_status',status_value);
  begin select RESULT_JSON into wire from RRL_DELIVERY_WINDOW where LOAD_OPERATION_ID=p_load and STORE_ADDR=p_store order by VERSION_NO desc fetch first 1 row only;j.put('window',json_object_t.parse(wire));
  exception when no_data_found then j.put_null('window');end;
  begin select RESULT_JSON into wire from RRL_DELIVERY_ARRIVAL where LOAD_OPERATION_ID=p_load and STORE_ADDR=p_store;j.put('arrival',json_object_t.parse(wire));
  exception when no_data_found then j.put_null('arrival');end;
  j.put('stock_changed',false);p_result:=j.to_clob;
 end;
end;
/
