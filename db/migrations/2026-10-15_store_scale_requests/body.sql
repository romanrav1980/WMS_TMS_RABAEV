create or replace package body RRL_STORE_WEIGH_API as
 procedure clear_context is
 begin
  dbms_session.set_context('RRL_STORE_WEIGH_CTX','TX_ID',null);
  dbms_session.set_context('RRL_STORE_WEIGH_CTX','REQUEST_ID',null);
 end;
 function preview(p_load varchar2,p_store varchar2,p_actor varchar2) return json_object_t is raw clob;
 begin
  RRL_STOCK_STORE_RECEIPT_READ.describe_load(p_load,p_actor,p_store,raw);
  return json_object_t.parse(raw);
 end;
 function sender_ready(p_sender nvarchar2) return boolean is n number;
 begin
  select count(*) into n from RUSERS where ID=p_sender and nvl(DELETED,0)=0
   and upper(trim(USER_GROUP))!='GLOBAL_ADMIN' and RRL_HAS_WRIGHT(ID,'store_scale_ingest')=1;
  return n=1;
 end;
 function status_json(r RRL_STORE_WEIGH_REQUEST%rowtype) return json_object_t is
  j json_object_t:=json_object_t();p json_object_t;d RRL_STORE_SCALE_DEVICE%rowtype;
  c RRL_STORE_SCALE_CAPTURE%rowtype;state_name varchar2(20):='REQUESTED';reason_name varchar2(100);capture_key varchar2(64);
 begin
  begin
   p:=preview(r.LOAD_OPERATION_ID,r.STORE_ADDR,r.REQUESTED_BY);
   select * into d from RRL_STORE_SCALE_DEVICE where DEVICE_ID=r.DEVICE_ID;
   if p.get_string('composition_signature')!=r.COMPOSITION_SIGNATURE
    or p.get_number('policy_version')!=r.RECEIPT_POLICY_VERSION or p.get_string('mode')!='WEIGHT_PHOTO'
    or p.get_boolean('already_received') or d.STORE_ADDR!=r.STORE_ADDR
    or d.POLICY_VERSION!=r.DEVICE_POLICY_VERSION or d.CALIBRATION_REF!=r.CALIBRATION_REF
    or d.ACTIVE_FLAG!=1 or d.CALIBRATED_UNTIL<systimestamp or not sender_ready(d.SENDER_ID) then
     state_name:='STALE';reason_name:='SOURCE_POLICY_OR_DEVICE_CHANGED';
   end if;
  exception when others then
   if sqlcode=-20882 or sqlcode=-20886 or sqlcode=-20881 or sqlcode=100 then
    state_name:='STALE';reason_name:='CURRENT_SOURCE_UNAVAILABLE';
   else raise;end if;
  end;
  if state_name='REQUESTED' then
   begin
    select * into c from RRL_STORE_SCALE_CAPTURE where DEVICE_ID=r.DEVICE_ID and CAPTURE_ID=r.REQUEST_ID;
    if c.LOAD_OPERATION_ID!=r.LOAD_OPERATION_ID or c.STORE_ADDR!=r.STORE_ADDR
     or c.DEVICE_POLICY_VERSION!=r.DEVICE_POLICY_VERSION or c.DEVICE_CALIBRATION_REF!=r.CALIBRATION_REF
     or c.RECORDED_BY!=d.SENDER_ID or c.RECEIVED_AT<r.CREATED_AT or c.RECEIVED_AT>r.EXPIRES_AT
     or c.MEASURED_AT<r.CREATED_AT or c.MEASURED_AT>r.EXPIRES_AT then
      state_name:='STALE';reason_name:='CAPTURE_DOES_NOT_MATCH_REQUEST';
    else state_name:='CAPTURED';capture_key:=c.CAPTURE_KEY;end if;
   exception when no_data_found then
    if systimestamp>r.EXPIRES_AT then state_name:='EXPIRED';reason_name:='REQUEST_WINDOW_ELAPSED';end if;
   end;
  end if;
  j.put('request_id',r.REQUEST_ID);j.put('device_id',r.DEVICE_ID);j.put('load_operation_id',r.LOAD_OPERATION_ID);
  j.put('store_address',r.STORE_ADDR);j.put('expected_composition_signature',r.COMPOSITION_SIGNATURE);
  j.put('device_policy_version',r.DEVICE_POLICY_VERSION);j.put('calibration_ref',r.CALIBRATION_REF);
  j.put('created_at',to_char(r.CREATED_AT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));
  j.put('expires_at',to_char(r.EXPIRES_AT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));
  j.put('state',state_name);j.put('capture_key',capture_key);j.put('reason',reason_name);
  j.put('receipt_confirmed',false);return j;
 end;
 procedure request_capture(p_source clob,p_actor varchar2,p_result out clob) is
  j json_object_t;p json_object_t;status_result json_object_t;d RRL_STORE_SCALE_DEVICE%rowtype;r RRL_STORE_WEIGH_REQUEST%rowtype;
  v_request_id varchar2(100);v_device_id varchar2(100);v_load_id varchar2(100);v_store_addr varchar2(255);v_signature varchar2(64);
  n number;now_at timestamp with time zone:=systimestamp;
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null then raise_application_error(-20886,'WEIGH_REQUEST_OUTSIDE_STOCK_REQUIRED');end if;
  if p_source is null or dbms_lob.getlength(p_source)>4000 then raise_application_error(-20881,'WEIGH_REQUEST_BOUND_4000');end if;
  j:=json_object_t.parse(p_source);
  if j.get_size!=5 then raise_application_error(-20886,'WEIGH_REQUEST_EXACT_FIELDS_REQUIRED');end if;
  v_request_id:=j.get_string('request_id');v_device_id:=j.get_string('device_id');v_load_id:=j.get_string('load_operation_id');
  v_store_addr:=j.get_string('store_address');v_signature:=j.get_string('expected_composition_signature');
  if v_request_id is null or v_device_id is null or v_load_id is null or v_store_addr is null or v_signature is null
   or not regexp_like(v_signature,'^[A-F0-9]{64}$','c')then raise_application_error(-20886,'WEIGH_REQUEST_IDENTIFIERS_REQUIRED');end if;
  lock table RRL_ACCESS_REV in share mode wait 2;
  RRL_STOCK_STORE_RECEIPT_READ.require_receiver(p_actor,v_store_addr);
  select * into d from RRL_STORE_SCALE_DEVICE where DEVICE_ID=v_device_id for update wait 2;
  select count(*) into n from RRL_STORE_WEIGH_REQUEST where REQUEST_ID=v_request_id;
  if n=1 then
   select * into r from RRL_STORE_WEIGH_REQUEST where REQUEST_ID=v_request_id;
   if r.REQUESTED_BY!=p_actor then raise_application_error(-20882,'WEIGH_REQUEST_OWNER_REQUIRED');end if;
   if dbms_lob.compare(r.SOURCE_JSON,p_source)!=0 then raise_application_error(-20886,'WEIGH_REQUEST_PAYLOAD_CONFLICT');end if;
   status_result:=status_json(r);p_result:=status_result.to_clob;return;
  end if;
  p:=preview(v_load_id,v_store_addr,p_actor);
  if p.get_string('mode')!='WEIGHT_PHOTO' or p.get_boolean('already_received')then raise_application_error(-20886,'WEIGH_REQUEST_UNRECEIVED_WEIGHT_MODE_REQUIRED');end if;
  if v_signature!=p.get_string('composition_signature')then raise_application_error(-20886,'WEIGH_REQUEST_COMPOSITION_CHANGED');end if;
  if d.STORE_ADDR!=v_store_addr or d.ACTIVE_FLAG!=1 or d.CALIBRATED_UNTIL<now_at or not sender_ready(d.SENDER_ID)then
   raise_application_error(-20886,'WEIGH_DEVICE_NOT_READY');end if;
  n:=0;
  for candidate in(select * from RRL_STORE_WEIGH_REQUEST where DEVICE_ID=v_device_id and EXPIRES_AT>now_at
   order by CREATED_AT desc fetch first 21 rows only)loop
   n:=n+1;status_result:=status_json(candidate);
   if n=21 or status_result.get_string('state')='REQUESTED'then raise_application_error(-20886,'WEIGH_DEVICE_BUSY');end if;
  end loop;
  r.REQUEST_ID:=v_request_id;r.DEVICE_ID:=v_device_id;r.LOAD_OPERATION_ID:=v_load_id;r.STORE_ADDR:=v_store_addr;r.REQUESTED_BY:=p_actor;
  r.COMPOSITION_SIGNATURE:=v_signature;r.RECEIPT_POLICY_VERSION:=p.get_number('policy_version');r.DEVICE_POLICY_VERSION:=d.POLICY_VERSION;
  r.CALIBRATION_REF:=d.CALIBRATION_REF;r.CREATED_AT:=now_at;r.EXPIRES_AT:=now_at+interval '120'second;r.SOURCE_JSON:=p_source;
  dbms_session.set_context('RRL_STORE_WEIGH_CTX','TX_ID',dbms_transaction.local_transaction_id(true));
  dbms_session.set_context('RRL_STORE_WEIGH_CTX','REQUEST_ID',v_request_id);
  insert into RRL_STORE_WEIGH_REQUEST values r;
  clear_context;status_result:=status_json(r);p_result:=status_result.to_clob;
 exception when no_data_found then clear_context;raise_application_error(-20886,'WEIGH_EXPLICIT_DEVICE_REQUIRED');
 when others then clear_context;raise;
 end;
 procedure request_status(p_request varchar2,p_actor varchar2,p_result out clob) is
  r RRL_STORE_WEIGH_REQUEST%rowtype;j json_object_t;
 begin
  select * into r from RRL_STORE_WEIGH_REQUEST where REQUEST_ID=p_request;
  RRL_STOCK_STORE_RECEIPT_READ.require_receiver(p_actor,r.STORE_ADDR);
  if r.REQUESTED_BY!=p_actor then raise_application_error(-20882,'WEIGH_REQUEST_OWNER_REQUIRED');end if;
  j:=status_json(r);p_result:=j.to_clob;
 exception when no_data_found then raise_application_error(-20884,'WEIGH_REQUEST_NOT_FOUND');
 end;
 procedure devices(p_load varchar2,p_store varchar2,p_actor varchar2,p_result out clob) is
  p json_object_t;j json_object_t:=json_object_t();a json_array_t:=json_array_t();x json_object_t;readiness varchar2(40);total_count number:=0;
 begin
  p:=preview(p_load,p_store,p_actor);
  for d in(select * from RRL_STORE_SCALE_DEVICE where STORE_ADDR=p_store order by DEVICE_ID fetch first 51 rows only)loop
   total_count:=total_count+1;if total_count>50 then exit;end if;
   readiness:='READY';
   if p.get_string('mode')!='WEIGHT_PHOTO' or p.get_boolean('already_received')then readiness:='RECEIPT_NOT_ELIGIBLE';
   elsif d.ACTIVE_FLAG!=1 then readiness:='INACTIVE';
   elsif d.CALIBRATED_UNTIL<systimestamp then readiness:='CALIBRATION_EXPIRED';
   elsif not sender_ready(d.SENDER_ID)then readiness:='SENDER_UNAVAILABLE';end if;
   x:=json_object_t();x.put('device_id',d.DEVICE_ID);x.put('device_policy_version',d.POLICY_VERSION);
   x.put('active',d.ACTIVE_FLAG=1);x.put('capacity_kg',RRL_STOCK_PLAN_HELPER.decimal_text(d.CAPACITY_KG));
   x.put('resolution_kg',RRL_STOCK_PLAN_HELPER.decimal_text(d.RESOLUTION_KG));x.put('calibration_ref',d.CALIBRATION_REF);
   x.put('calibrated_until',to_char(d.CALIBRATED_UNTIL,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));
   x.put('readiness',readiness);x.put('connectivity','UNKNOWN');a.append(x);
  end loop;
  j.put('items',a);j.put('limit',50);j.put('has_more',total_count>50);
  j.put('mode',p.get_string('mode'));j.put('load_operation_id',p_load);j.put('store_address',p_store);p_result:=j.to_clob;
 end;
 procedure pending_requests(p_device varchar2,p_actor varchar2,p_result out clob) is
  d RRL_STORE_SCALE_DEVICE%rowtype;j json_object_t:=json_object_t();a json_array_t:=json_array_t();x json_object_t;
 begin
  select * into d from RRL_STORE_SCALE_DEVICE where DEVICE_ID=p_device;
  if d.SENDER_ID!=p_actor or not sender_ready(d.SENDER_ID)then raise_application_error(-20882,'WEIGH_DEDICATED_DEVICE_SENDER_REQUIRED');end if;
  if d.ACTIVE_FLAG!=1 or d.CALIBRATED_UNTIL<systimestamp then raise_application_error(-20886,'WEIGH_DEVICE_NOT_READY');end if;
  for r in(select * from RRL_STORE_WEIGH_REQUEST where DEVICE_ID=p_device and EXPIRES_AT>systimestamp order by CREATED_AT fetch first 20 rows only)loop
   x:=status_json(r);if x.get_string('state')='REQUESTED'then a.append(x);end if;
  end loop;
  j.put('items',a);j.put('limit',20);p_result:=j.to_clob;
 exception when no_data_found then raise_application_error(-20882,'WEIGH_DEDICATED_DEVICE_SENDER_REQUIRED');
 end;
end;
/