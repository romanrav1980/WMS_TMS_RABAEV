create or replace package RRL_STORE_SCALE_API authid definer as
 procedure capture(p_source clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_STORE_SCALE_API as
 procedure clear_context is
 begin
  dbms_session.set_context('RRL_STORE_SCALE_CTX','TX_ID',null);
  dbms_session.set_context('RRL_STORE_SCALE_CTX','CAPTURE_KEY',null);
 end;
 function stamp(p_text varchar2) return timestamp with time zone is
 begin
  if not regexp_like(p_text,'^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[.][0-9]{6}[+]00:00$','c') then raise_application_error(-20886,'SCALE_UTC_TIMESTAMP_REQUIRED');end if;
  return to_timestamp_tz(p_text,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');
 end;
 procedure capture(p_source clob,p_actor varchar2,p_result out clob) is
  j json_object_t;reading json_object_t;result_json json_object_t:=json_object_t();identity_json json_array_t:=json_array_t();samples json_array_t;x json_object_t;
  device RRL_STORE_SCALE_DEVICE%rowtype;existing RRL_STORE_SCALE_CAPTURE%rowtype;
  v_device_id varchar2(100);v_capture_id varchar2(100);v_load_op varchar2(100);v_store_addr varchar2(255);v_capture_key varchar2(64);sha varchar2(64);n number;
  min_kg number;max_kg number;last_kg number;offset_no number;previous_offset number:=-1;first_offset number;span_ms number;zero_kg number;sample_no number;zero_text varchar2(30);
  measured_at timestamp with time zone;zero_at timestamp with time zone;now_at timestamp with time zone:=systimestamp;
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is not null then raise_application_error(-20886,'SCALE_CAPTURE_OUTSIDE_STOCK_TRANSACTION_REQUIRED');end if;
  if RRL_HAS_WRIGHT(p_actor,'store_scale_ingest')!=1 then raise_application_error(-20882,'SCALE_SENDER_FORBIDDEN');end if;
  if p_source is null or dbms_lob.getlength(p_source)>32000 then raise_application_error(-20881,'SCALE_PACKET_BOUND_32000');end if;
  j:=json_object_t.parse(p_source);v_device_id:=j.get_string('device_id');v_capture_id:=j.get_string('capture_id');v_load_op:=j.get_string('load_operation_id');v_store_addr:=j.get_string('store_address');
  if v_device_id is null or v_capture_id is null or v_load_op is null or v_store_addr is null then raise_application_error(-20886,'SCALE_SOURCE_IDENTIFIERS_REQUIRED');end if;
  select * into device from RRL_STORE_SCALE_DEVICE where DEVICE_ID=v_device_id for update;
  if device.SENDER_ID!=p_actor or device.STORE_ADDR!=v_store_addr then raise_application_error(-20882,'SCALE_DEVICE_SENDER_ADDRESS_MISMATCH');end if;
  identity_json.append(v_device_id);identity_json.append(v_capture_id);
  v_capture_key:=rawtohex(sys.dbms_crypto.hash(identity_json.to_clob,sys.dbms_crypto.hash_sh256));sha:=rawtohex(sys.dbms_crypto.hash(p_source,sys.dbms_crypto.hash_sh256));
  select count(*) into n from RRL_STORE_SCALE_CAPTURE where CAPTURE_KEY=v_capture_key;
  if n=1 then
   select * into existing from RRL_STORE_SCALE_CAPTURE where CAPTURE_KEY=v_capture_key;
   if existing.SOURCE_SHA256!=sha or dbms_lob.compare(existing.SOURCE_JSON,p_source)!=0 then raise_application_error(-20886,'SCALE_CAPTURE_PAYLOAD_CONFLICT');end if;
   p_result:=existing.RESULT_JSON;return;
  end if;
  if j.get_number('device_policy_version') is null or j.get_number('device_policy_version')!=device.POLICY_VERSION or j.get_string('calibration_ref') is null or j.get_string('calibration_ref')!=device.CALIBRATION_REF then raise_application_error(-20886,'SCALE_DEVICE_POLICY_CHANGED');end if;
  if device.ACTIVE_FLAG!=1 or device.CALIBRATED_UNTIL<now_at then raise_application_error(-20886,'SCALE_INACTIVE_OR_CALIBRATION_EXPIRED');end if;
  reading:=json_object_t.parse(RRL_SCALE_PACKET_READ.validate_json(p_source,device.CAPACITY_KG,device.RESOLUTION_KG));
  last_kg:=RRL_STOCK_MATH.quantity(reading.get_string('weight_kg'));
  min_kg:=RRL_STOCK_MATH.quantity(reading.get_string('sample_min_kg'));max_kg:=RRL_STOCK_MATH.quantity(reading.get_string('sample_max_kg'));
  sample_no:=reading.get_number('sample_count');span_ms:=reading.get_number('span_ms');
  measured_at:=RRL_SCALE_PACKET_READ.utc_stamp(reading.get_string('measured_at'));zero_at:=RRL_SCALE_PACKET_READ.utc_stamp(reading.get_string('zero_check_at'));
  select count(*) into n from RRL_TT_HU_LOAD_FACT lf where lf.LOAD_OPERATION_ID=v_load_op and lf.STATUS='DEPARTED'
   and exists(select 1 from RRL_STOCK_OPERATION op where op.OPERATION_ID=lf.LOAD_OPERATION_ID and op.STATE='APPLIED')
   and exists(select 1 from RRL_STOCK_OPERATION op where op.OPERATION_ID=lf.DEPARTURE_OPERATION_ID and op.STATE='APPLIED')
   and exists(select 1 from RRL_TT_HU_LOAD_ST st where st.LOAD_OPERATION_ID=lf.LOAD_OPERATION_ID and st.ACTIVE_FLAG=1 and st.DESTINATION_ADDR=v_store_addr)
   and not exists(select 1 from RRL_TT_HU_LOAD_ST st where st.LOAD_OPERATION_ID=lf.LOAD_OPERATION_ID and st.ACTIVE_FLAG=1 and (st.DESTINATION_ADDR is null or st.DESTINATION_ADDR!=v_store_addr));
  if n!=1 then raise_application_error(-20886,'SCALE_ACTUAL_DEPARTED_DESTINATION_REQUIRED');end if;
  result_json.put('capture_key',v_capture_key);result_json.put('device_id',v_device_id);result_json.put('capture_id',v_capture_id);result_json.put('load_operation_id',v_load_op);result_json.put('store_address',v_store_addr);
  result_json.put('gross_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(last_kg));result_json.put('device_policy_version',device.POLICY_VERSION);
  result_json.put('source_sha256',sha);result_json.put('measured_at',j.get_string('measured_at'));result_json.put('received_at',to_char(now_at,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));
  result_json.put('calibration_ref',device.CALIBRATION_REF);result_json.put('resolution_kg',RRL_STOCK_PLAN_HELPER.decimal_text(device.RESOLUTION_KG));result_json.put('sample_count',sample_no);result_json.put('span_ms',span_ms);
  result_json.put('status','ARCHIVED');result_json.put('receipt_confirmed',false);p_result:=result_json.to_clob;
  dbms_session.set_context('RRL_STORE_SCALE_CTX','TX_ID',dbms_transaction.local_transaction_id(true));dbms_session.set_context('RRL_STORE_SCALE_CTX','CAPTURE_KEY',v_capture_key);
  insert into RRL_STORE_SCALE_CAPTURE(CAPTURE_KEY,DEVICE_ID,CAPTURE_ID,LOAD_OPERATION_ID,STORE_ADDR,DEVICE_POLICY_VERSION,DEVICE_CALIBRATION_REF,CAPACITY_KG,RESOLUTION_KG,GROSS_WEIGHT_KG,SAMPLE_MIN_KG,SAMPLE_MAX_KG,SAMPLE_COUNT,SPAN_MS,MEASURED_AT,ZERO_CHECK_AT,RECEIVED_AT,RECORDED_BY,SOURCE_SHA256,SOURCE_JSON,RESULT_JSON)
  values(v_capture_key,v_device_id,v_capture_id,v_load_op,v_store_addr,device.POLICY_VERSION,device.CALIBRATION_REF,device.CAPACITY_KG,device.RESOLUTION_KG,last_kg,min_kg,max_kg,sample_no,span_ms,measured_at,zero_at,now_at,p_actor,sha,p_source,p_result);
  clear_context;
 exception when no_data_found then clear_context;raise_application_error(-20886,'SCALE_EXPLICIT_DEVICE_REQUIRED');
 when others then clear_context;raise;
 end;
end;
/
