create or replace package RRL_WH_SCALE_API authid definer as
 procedure capture(p_source clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_WH_SCALE_API as
 procedure clear_context is begin
  dbms_session.set_context('RRL_WH_SCALE_CTX','TX_ID',null);dbms_session.set_context('RRL_WH_SCALE_CTX','CAPTURE_KEY',null);
 end;
 procedure capture(p_source clob,p_actor varchar2,p_result out clob)is
  j json_object_t;reading json_object_t;result_json json_object_t:=json_object_t();identity_json json_array_t:=json_array_t();
  device RRL_WH_SCALE_DEVICE%rowtype;existing RRL_WH_SCALE_CAPTURE%rowtype;ct RRL_CASE_PICK_TASK%rowtype;l RRL_CASE_PICK_LINE%rowtype;
  device_id_value varchar2(100);capture_id_value varchar2(100);capture_key_value varchar2(64);hash_value varchar2(64);
  task_id number;line_id number;n number;scanned_product varchar2(512);measured_weight number;measured_at timestamp with time zone;now_at timestamp with time zone:=systimestamp;
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null then raise_application_error(-20886,'SCALE_CAPTURE_OUTSIDE_STOCK_TRANSACTION_REQUIRED');end if;
  if RRL_HAS_WRIGHT(p_actor,'warehouse_scale_ingest')!=1 then raise_application_error(-20882,'WAREHOUSE_SCALE_SENDER_FORBIDDEN');end if;
  if p_source is null or dbms_lob.getlength(p_source)>32000 then raise_application_error(-20881,'SCALE_PACKET_BOUND_32000');end if;
  j:=json_object_t.parse(p_source);device_id_value:=j.get_string('device_id');capture_id_value:=j.get_string('capture_id');
  if device_id_value is null or capture_id_value is null then raise_application_error(-20886,'SCALE_SOURCE_IDENTIFIERS_REQUIRED');end if;
  select *into device from RRL_WH_SCALE_DEVICE where DEVICE_ID=device_id_value for update;
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and WARE_ID=device.WARE_ID and upper(trim(USER_GROUP))!='GLOBAL_ADMIN';
  if n!=1 or device.SENDER_ID!=p_actor then raise_application_error(-20882,'WAREHOUSE_SCALE_CURRENT_SENDER_WARE_REQUIRED');end if;
  identity_json.append(device_id_value);identity_json.append(capture_id_value);
  capture_key_value:=rawtohex(sys.dbms_crypto.hash(identity_json.to_clob,sys.dbms_crypto.hash_sh256));hash_value:=rawtohex(sys.dbms_crypto.hash(p_source,sys.dbms_crypto.hash_sh256));
  select count(*)into n from RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=capture_key_value;
  if n=1 then
   select *into existing from RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=capture_key_value;
   if existing.SOURCE_SHA256!=hash_value or dbms_lob.compare(existing.SOURCE_JSON,p_source)!=0 then raise_application_error(-20886,'SCALE_CAPTURE_PAYLOAD_CONFLICT');end if;
   if existing.WARE_ID!=device.WARE_ID or existing.POST_CELL!=device.POST_CELL then raise_application_error(-20882,'WAREHOUSE_SCALE_ORIGINAL_SCOPE_CHANGED');end if;
   p_result:=existing.RESULT_JSON;return;
  end if;
  if j.get_number('device_policy_version')is null or j.get_number('device_policy_version')!=device.POLICY_VERSION
   or j.get_string('calibration_ref')is null or j.get_string('calibration_ref')!=device.CALIBRATION_REF then raise_application_error(-20886,'SCALE_DEVICE_POLICY_CHANGED');end if;
  if device.ACTIVE_FLAG!=1 or device.CALIBRATED_UNTIL<now_at then raise_application_error(-20886,'SCALE_INACTIVE_OR_CALIBRATION_EXPIRED');end if;
  if j.get_string('post_cell')is null or j.get_string('post_cell')!=device.POST_CELL then raise_application_error(-20886,'WAREHOUSE_SCALE_POST_SCAN_REQUIRED');end if;
  task_id:=j.get_number('case_task_id');line_id:=j.get_number('case_line_id');
  select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_id;
  select *into l from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=line_id and CASE_PICK_TASK_ID=task_id;
  if ct.WARE_ID is null or l.ARTICUL is null or l.CELL_CODE is null or ct.WARE_ID!=device.WARE_ID or ct.STATUS not in('IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT')
   or ct.STATUS is null or j.get_number('expected_content_version')is null or ct.CONTENT_VERSION!=j.get_number('expected_content_version')
   or j.get_string('scan_source_cell')is null or j.get_string('scan_source_cell')!=l.CELL_CODE
   or j.get_string('scan_container')is null or j.get_string('scan_container')!=ct.SSCC then raise_application_error(-20886,'WAREHOUSE_SCALE_CURRENT_CASE_SOURCE_REQUIRED');end if;
  scanned_product:=j.get_string('scan_product');
  select count(*)into n from RRL_ARTICULS where ACTICUL=l.ARTICUL and TYPE_W in(2,3,5,6,7);
  if n!=1 then raise_application_error(-20886,'WAREHOUSE_SCALE_WEIGHTED_SKU_REQUIRED');end if;
  if RRL_WEIGHT_BOX_CAPACITY.enabled(l.ARTICUL)=1 then
   if device.MEASUREMENT_BASIS!='GROSS'then raise_application_error(-20886,'SEALED_WEIGHT_BOX_GROSS_CAPTURE_REQUIRED');end if;
   declare b json_object_t:=json_object_t.parse(RRL_WEIGHT_BOX_READ.decode_json(scanned_product));begin RRL_WEIGHT_BOX_READ.assert_sku(l.ARTICUL,b.get_string('gtin'));end;
  else
   select count(*)into n from RRL_ARTICULS where ACTICUL=l.ARTICUL and scanned_product in(ACTICUL,BARCODE_SHT,BARCODE_KOR,BARCODE_BL);
   if n!=1 or device.MEASUREMENT_BASIS!='NET'then raise_application_error(-20886,'LOOSE_WEIGHT_NET_PRODUCT_CAPTURE_REQUIRED');end if;
   select greatest(nvl((select MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY where ARTICUL=l.ARTICUL),0),
    nvl((select CRPT_REQUIRED from RRL_FINISHED_GOODS_SKU where ARTICUL=l.ARTICUL),0),
    case when exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=l.ARTICUL)then 1 else 0 end)into n from dual;
   if n!=0 then raise_application_error(-20886,'MARKED_UNIT_OPENING_NOT_AUTHORIZED');end if;
  end if;
  reading:=json_object_t.parse(RRL_SCALE_PACKET_READ.validate_json(p_source,device.CAPACITY_KG,device.RESOLUTION_KG,device.MEASUREMENT_BASIS,'weight_kg'));
  measured_weight:=RRL_STOCK_MATH.quantity(reading.get_string('weight_kg'));measured_at:=RRL_SCALE_PACKET_READ.utc_stamp(reading.get_string('measured_at'));
  result_json.put('capture_key',capture_key_value);result_json.put('device_id',device_id_value);result_json.put('capture_id',capture_id_value);
  result_json.put('warehouse_id',device.WARE_ID);result_json.put('post_cell',device.POST_CELL);result_json.put('device_mode',device.DEVICE_MODE);
  result_json.put('case_task_id',task_id);result_json.put('case_line_id',line_id);result_json.put('case_content_version',ct.CONTENT_VERSION);
  result_json.put('article',l.ARTICUL);result_json.put('scan_source_cell',l.CELL_CODE);result_json.put('scan_container',ct.SSCC);result_json.put('scan_product',scanned_product);
  result_json.put('basis',device.MEASUREMENT_BASIS);result_json.put('weight_kg',reading.get_string('weight_kg'));result_json.put('device_policy_version',device.POLICY_VERSION);
  result_json.put('calibration_ref',device.CALIBRATION_REF);result_json.put('resolution_kg',RRL_STOCK_PLAN_HELPER.decimal_text(device.RESOLUTION_KG));
  result_json.put('source_sha256',hash_value);result_json.put('measured_at',j.get_string('measured_at'));result_json.put('received_at',to_char(now_at,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));
  result_json.put('sample_count',reading.get_number('sample_count'));result_json.put('span_ms',reading.get_number('span_ms'));
  result_json.put('status','ARCHIVED');result_json.put('stock_posted',false);p_result:=result_json.to_clob;
  dbms_session.set_context('RRL_WH_SCALE_CTX','TX_ID',dbms_transaction.local_transaction_id(true));dbms_session.set_context('RRL_WH_SCALE_CTX','CAPTURE_KEY',capture_key_value);
  insert into RRL_WH_SCALE_CAPTURE(CAPTURE_KEY,DEVICE_ID,CAPTURE_ID,WARE_ID,POST_CELL,CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,CASE_CONTENT_VERSION,ARTICLE,SOURCE_CELL,CARRIER_IDENTIFIER,SCANNED_PRODUCT,
   DEVICE_POLICY_VERSION,DEVICE_MODE,MEASUREMENT_BASIS,WEIGHT_KG,RESOLUTION_KG,CALIBRATION_REF,MEASURED_AT,RECEIVED_AT,RECORDED_BY,SOURCE_SHA256,SOURCE_JSON,RESULT_JSON)
   values(capture_key_value,device_id_value,capture_id_value,device.WARE_ID,device.POST_CELL,task_id,line_id,ct.CONTENT_VERSION,l.ARTICUL,l.CELL_CODE,ct.SSCC,scanned_product,
    device.POLICY_VERSION,device.DEVICE_MODE,device.MEASUREMENT_BASIS,measured_weight,device.RESOLUTION_KG,device.CALIBRATION_REF,measured_at,now_at,p_actor,hash_value,p_source,p_result);
  clear_context;
 exception when no_data_found then clear_context;raise_application_error(-20886,'WAREHOUSE_SCALE_DEVICE_AND_CASE_SOURCE_REQUIRED');
 when others then clear_context;raise;
 end;
end;
/
