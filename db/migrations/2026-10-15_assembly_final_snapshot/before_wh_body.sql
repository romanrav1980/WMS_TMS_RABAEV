create or replace package body RRL_WH_SCALE_API as
 procedure clear_context is begin
  RRL_WH_WEIGH_REQUEST_API.clear_capture_context;
  dbms_session.set_context('RRL_WH_SCALE_CTX','TX_ID',null);dbms_session.set_context('RRL_WH_SCALE_CTX','CAPTURE_KEY',null);
 end;

 procedure capture_final(p_source clob,p_actor varchar2,p_device RRL_WH_SCALE_DEVICE%rowtype,p_key varchar2,p_hash varchar2,p_result out clob)is
  j json_object_t:=json_object_t.parse(p_source);reading json_object_t;r json_object_t:=json_object_t();qc json_object_t;
  ct RRL_CASE_PICK_TASK%rowtype;typ RRL_PALLET_TYPE%rowtype;tare RRL_WH_SCALE_CAPTURE%rowtype;
  task_no number;purpose_value varchar2(12);weight_value number;measured timestamp with time zone;signature_value varchar2(64);tare_key varchar2(64);identifier varchar2(150);capture_id_scalar varchar2(100);
 begin
  capture_id_scalar:=j.get_string('capture_id');purpose_value:=j.get_string('purpose');task_no:=j.get_number('case_task_id');
  if purpose_value is null or purpose_value not in('EMPTY_TARE','FINAL_GROSS')or p_device.MEASUREMENT_BASIS!='GROSS'then raise_application_error(-20886,'FINAL_SCALE_EXPLICIT_GROSS_PURPOSE_REQUIRED');end if;
  select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_no;
  select *into typ from RRL_PALLET_TYPE where PALLET_TYPE_ID=ct.PALLET_TYPE_ID;
  if typ.FINAL_WEIGHT_REQUIRED!=1 or upper(typ.LOAD_UNIT_CLASS)!='CONTAINER' or ct.WARE_ID!=p_device.WARE_ID
   or j.get_number('expected_content_version')is null or j.get_number('expected_content_version')!=ct.CONTENT_VERSION
   or j.get_string('scan_container')is null or j.get_string('scan_container')!=ct.SSCC then raise_application_error(-20886,'FINAL_SCALE_CURRENT_SMALL_CASE_REQUIRED');end if;
  RRL_CASE_SSCC_API.assert_ready(task_no);
  reading:=json_object_t.parse(RRL_SCALE_PACKET_READ.validate_json(p_source,p_device.CAPACITY_KG,p_device.RESOLUTION_KG,'GROSS','weight_kg'));
  weight_value:=RRL_STOCK_MATH.quantity(reading.get_string('weight_kg'));measured:=RRL_SCALE_PACKET_READ.utc_stamp(j.get_string('measured_at'));
  if purpose_value='EMPTY_TARE'then
   if ct.STATUS not in('NEW','ASSIGNED','IN_PROGRESS')or nvl(ct.PICKED_QTY,0)!=0 or j.has('tare_capture_key')then raise_application_error(-20886,'EMPTY_CASE_TARE_BEFORE_FIRST_PICK_REQUIRED');end if;
  else
   if ct.STATUS not in('WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP')or nvl(ct.PICKED_QTY,0)<=0 or ct.LEGACY_SBORKA_PALLET_ID is null then raise_application_error(-20886,'FINAL_SCALE_CLOSED_BOUND_CASE_REQUIRED');end if;
   tare_key:=j.get_string('tare_capture_key');
   if tare_key is null then raise_application_error(-20886,'FINAL_SCALE_MEASURED_EMPTY_TARE_REQUIRED');end if;
   select *into tare from RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=tare_key;
   if tare.CAPTURE_PURPOSE!='EMPTY_TARE' or tare.CASE_PICK_TASK_ID!=task_no or tare.CARRIER_IDENTIFIER!=ct.SSCC
    or tare.PALLET_TYPE_ID!=ct.PALLET_TYPE_ID
    or tare.DEVICE_ID!=p_device.DEVICE_ID or tare.WARE_ID!=p_device.WARE_ID or tare.POST_CELL!=p_device.POST_CELL
    or tare.DEVICE_MODE!=p_device.DEVICE_MODE or tare.MEASUREMENT_BASIS!='GROSS' or tare.MEASURED_AT>measured
    or tare.MEASURED_AT<measured-numtodsinterval(24,'HOUR')or tare.WEIGHT_KG>=weight_value
    then raise_application_error(-20886,'FINAL_SCALE_CURRENT_SAME_CASE_TARE_REQUIRED');end if;
   select PALLET_UID into identifier from RRL_SBORKA_PALLETS where ID=ct.LEGACY_SBORKA_PALLET_ID;
   qc:=json_object_t.parse(RRL_STOCK_QC_GATE.status_json(identifier));signature_value:=qc.get_string('composition_signature');
   if signature_value is null then raise_application_error(-20886,'FINAL_SCALE_CURRENT_COMPOSITION_REQUIRED');end if;
   r.put('tare_capture_key',tare_key);r.put('tare_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(tare.WEIGHT_KG));
   r.put('net_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(weight_value-tare.WEIGHT_KG));r.put('composition_signature',signature_value);r.put('composition_signature_version',qc.get_number('composition_signature_version'));
  end if;
  r.put('capture_key',p_key);r.put('device_id',p_device.DEVICE_ID);r.put('capture_id',j.get_string('capture_id'));
  r.put('warehouse_id',ct.WARE_ID);r.put('post_cell',p_device.POST_CELL);r.put('device_mode',p_device.DEVICE_MODE);
  r.put('purpose',purpose_value);r.put('case_task_id',task_no);r.put('case_content_version',ct.CONTENT_VERSION);
  r.put('scan_container',ct.SSCC);r.put('pallet_type_id',ct.PALLET_TYPE_ID);r.put('type_version',typ.TYPE_VERSION);
  r.put('basis','GROSS');r.put('weight_kg',reading.get_string('weight_kg'));r.put('device_policy_version',p_device.POLICY_VERSION);
  r.put('calibration_ref',p_device.CALIBRATION_REF);r.put('resolution_kg',RRL_STOCK_PLAN_HELPER.decimal_text(p_device.RESOLUTION_KG));
  r.put('source_sha256',p_hash);r.put('measured_at',j.get_string('measured_at'));r.put('sample_count',reading.get_number('sample_count'));r.put('span_ms',reading.get_number('span_ms'));
  r.put('status','ARCHIVED');r.put('stock_posted',false);p_result:=r.to_clob;
  dbms_session.set_context('RRL_WH_SCALE_CTX','TX_ID',dbms_transaction.local_transaction_id(true));dbms_session.set_context('RRL_WH_SCALE_CTX','CAPTURE_KEY',p_key);
  insert into RRL_WH_SCALE_CAPTURE(CAPTURE_KEY,DEVICE_ID,CAPTURE_ID,WARE_ID,POST_CELL,CASE_PICK_TASK_ID,CASE_CONTENT_VERSION,CARRIER_IDENTIFIER,
   DEVICE_POLICY_VERSION,DEVICE_MODE,MEASUREMENT_BASIS,WEIGHT_KG,RESOLUTION_KG,CALIBRATION_REF,MEASURED_AT,RECORDED_BY,SOURCE_SHA256,SOURCE_JSON,RESULT_JSON,
   CAPTURE_PURPOSE,TARE_CAPTURE_KEY,PALLET_TYPE_ID,TYPE_VERSION,COMPOSITION_SIGNATURE)
  values(p_key,p_device.DEVICE_ID,capture_id_scalar,ct.WARE_ID,p_device.POST_CELL,task_no,ct.CONTENT_VERSION,ct.SSCC,
   p_device.POLICY_VERSION,p_device.DEVICE_MODE,'GROSS',weight_value,p_device.RESOLUTION_KG,p_device.CALIBRATION_REF,measured,p_actor,p_hash,p_source,p_result,
   purpose_value,tare_key,ct.PALLET_TYPE_ID,typ.TYPE_VERSION,signature_value);
  RRL_WH_WEIGH_REQUEST_API.validate_archived(p_source,p_actor);
  clear_context;
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
  RRL_WH_WEIGH_REQUEST_API.before_capture(p_source,p_actor);
  select *into device from RRL_WH_SCALE_DEVICE where DEVICE_ID=device_id_value for update;
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and WARE_ID=device.WARE_ID and upper(trim(USER_GROUP))!='GLOBAL_ADMIN';
  if n!=1 or device.SENDER_ID!=p_actor or RRL_HAS_WRIGHT(p_actor,'warehouse_scale_ingest')!=1 then raise_application_error(-20882,'WAREHOUSE_SCALE_CURRENT_SENDER_WARE_REQUIRED');end if;
  identity_json.append(device_id_value);identity_json.append(capture_id_value);
  capture_key_value:=rawtohex(sys.dbms_crypto.hash(identity_json.to_clob,sys.dbms_crypto.hash_sh256));hash_value:=rawtohex(sys.dbms_crypto.hash(p_source,sys.dbms_crypto.hash_sh256));
  select count(*)into n from RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=capture_key_value;
  if n=1 then
   select *into existing from RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=capture_key_value;
   if existing.SOURCE_SHA256!=hash_value or dbms_lob.compare(existing.SOURCE_JSON,p_source)!=0 then raise_application_error(-20886,'SCALE_CAPTURE_PAYLOAD_CONFLICT');end if;
   if existing.WARE_ID!=device.WARE_ID or existing.POST_CELL!=device.POST_CELL then raise_application_error(-20882,'WAREHOUSE_SCALE_ORIGINAL_SCOPE_CHANGED');end if;
   select count(*)into n from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=existing.CASE_PICK_TASK_ID and WARE_ID=device.WARE_ID;
   if n!=1 then raise_application_error(-20882,'WAREHOUSE_SCALE_CURRENT_CASE_WARE_REQUIRED');end if;
   if existing.RECORDED_BY!=p_actor then raise_application_error(-20882,'WAREHOUSE_SCALE_ORIGINAL_ARCHIVE_SENDER_REQUIRED');end if;
   RRL_WH_WEIGH_REQUEST_API.assert_archived_sender(p_source,p_actor);
   p_result:=existing.RESULT_JSON;return;
  end if;
  RRL_WH_WEIGH_REQUEST_API.validate_first_capture(p_source,p_actor);
  if j.get_number('device_policy_version')is null or j.get_number('device_policy_version')!=device.POLICY_VERSION
   or j.get_string('calibration_ref')is null or j.get_string('calibration_ref')!=device.CALIBRATION_REF then raise_application_error(-20886,'SCALE_DEVICE_POLICY_CHANGED');end if;
  if device.ACTIVE_FLAG!=1 or device.CALIBRATED_UNTIL<now_at then raise_application_error(-20886,'SCALE_INACTIVE_OR_CALIBRATION_EXPIRED');end if;
  if j.get_string('post_cell')is null or j.get_string('post_cell')!=device.POST_CELL then raise_application_error(-20886,'WAREHOUSE_SCALE_POST_SCAN_REQUIRED');end if;
  if j.has('purpose')then capture_final(p_source,p_actor,device,capture_key_value,hash_value,p_result);return;end if;
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
  RRL_WH_WEIGH_REQUEST_API.validate_archived(p_source,p_actor);
  clear_context;
 exception when no_data_found then clear_context;raise_application_error(-20886,'WAREHOUSE_SCALE_DEVICE_AND_CASE_SOURCE_REQUIRED');
 when others then clear_context;raise;
 end;
end;
/
