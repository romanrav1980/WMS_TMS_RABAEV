from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni042_final_scale");out={}
s=(f/"000_before_archive.sql").read_text(encoding="utf-8")
private="""
 procedure capture_final(p_source clob,p_actor varchar2,p_device RRL_WH_SCALE_DEVICE%rowtype,p_key varchar2,p_hash varchar2,p_result out clob)is
  j json_object_t:=json_object_t.parse(p_source);reading json_object_t;r json_object_t:=json_object_t();qc json_object_t;
  ct RRL_CASE_PICK_TASK%rowtype;typ RRL_PALLET_TYPE%rowtype;tare RRL_WH_SCALE_CAPTURE%rowtype;
  task_no number;purpose_value varchar2(12);weight_value number;measured timestamp with time zone;signature_value varchar2(64);tare_key varchar2(64);identifier varchar2(150);
 begin
  purpose_value:=j.get_string('purpose');task_no:=j.get_number('case_task_id');
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
   if ct.STATUS not in('WAIT_CONTROL','READY_TO_SHIP')or nvl(ct.PICKED_QTY,0)<=0 or ct.LEGACY_SBORKA_PALLET_ID is null then raise_application_error(-20886,'FINAL_SCALE_CLOSED_BOUND_CASE_REQUIRED');end if;
   tare_key:=j.get_string('tare_capture_key');
   if tare_key is null then raise_application_error(-20886,'FINAL_SCALE_MEASURED_EMPTY_TARE_REQUIRED');end if;
   select *into tare from RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=tare_key;
   if tare.CAPTURE_PURPOSE!='EMPTY_TARE' or tare.CASE_PICK_TASK_ID!=task_no or tare.CARRIER_IDENTIFIER!=ct.SSCC
    or tare.PALLET_TYPE_ID!=ct.PALLET_TYPE_ID or tare.TYPE_VERSION!=typ.TYPE_VERSION
    or tare.DEVICE_ID!=p_device.DEVICE_ID or tare.DEVICE_POLICY_VERSION!=p_device.POLICY_VERSION
    or tare.CALIBRATION_REF!=p_device.CALIBRATION_REF or tare.MEASURED_AT>measured
    or tare.MEASURED_AT<measured-numtodsinterval(24,'HOUR')or tare.WEIGHT_KG>=weight_value
    then raise_application_error(-20886,'FINAL_SCALE_CURRENT_SAME_CASE_TARE_REQUIRED');end if;
   select PALLET_UID into identifier from RRL_SBORKA_PALLETS where ID=ct.LEGACY_SBORKA_PALLET_ID;
   qc:=json_object_t.parse(RRL_STOCK_QC_GATE.status_json(identifier));signature_value:=qc.get_string('composition_signature');
   if signature_value is null then raise_application_error(-20886,'FINAL_SCALE_CURRENT_COMPOSITION_REQUIRED');end if;
   r.put('tare_capture_key',tare_key);r.put('tare_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(tare.WEIGHT_KG));
   r.put('net_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(weight_value-tare.WEIGHT_KG));r.put('composition_signature',signature_value);
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
  values(p_key,p_device.DEVICE_ID,j.get_string('capture_id'),ct.WARE_ID,p_device.POST_CELL,task_no,ct.CONTENT_VERSION,ct.SSCC,
   p_device.POLICY_VERSION,p_device.DEVICE_MODE,'GROSS',weight_value,p_device.RESOLUTION_KG,p_device.CALIBRATION_REF,measured,p_actor,p_hash,p_source,p_result,
   purpose_value,tare_key,ct.PALLET_TYPE_ID,typ.TYPE_VERSION,signature_value);
  clear_context;
 end;
"""
# JSON method calls are not SQL expressions: scalarize capture ID.
private=private.replace("identifier varchar2(150);","identifier varchar2(150);capture_id_scalar varchar2(100);")
private=private.replace("purpose_value:=j.get_string('purpose');", "capture_id_scalar:=j.get_string('capture_id');purpose_value:=j.get_string('purpose');")
private=private.replace("values(p_key,p_device.DEVICE_ID,j.get_string('capture_id'),","values(p_key,p_device.DEVICE_ID,capture_id_scalar,")
needle=" procedure capture(p_source clob,p_actor varchar2,p_result out clob)is"
assert s.count(needle)==1;s=s.replace(needle,private+needle)
needle="  task_id:=j.get_number('case_task_id');line_id:=j.get_number('case_line_id');"
assert s.count(needle)==1;s=s.replace(needle,"""  if j.has('purpose')then capture_final(p_source,p_actor,device,capture_key_value,hash_value,p_result);return;end if;
"""+needle)
# Replay checks current CASE scope as well as the current sender/device.
needle="   p_result:=existing.RESULT_JSON;return;"
assert s.count(needle)==1
s=s.replace(needle,"""   select count(*)into n from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=existing.CASE_PICK_TASK_ID and WARE_ID=device.WARE_ID;
   if n!=1 then raise_application_error(-20882,'WAREHOUSE_SCALE_CURRENT_CASE_WARE_REQUIRED');end if;
"""+needle)
out[str(f/"002_archive.sql")]=s
# Separate contract and body avoid replaying context DDL in current runtime components.
out[str(f/"002_body.sql")]=s
s=(f/"000_before_admission.sql").read_text(encoding="utf-8")
needle="  select *into c from RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=k;"
assert s.count(needle)==1;s=s.replace(needle,needle+"\n  if c.CAPTURE_PURPOSE!='PICK' then raise_application_error(-20886,'CASE_PICK_SCALE_PURPOSE_REQUIRED');end if;")
out[str(f/"003_admission.sql")]=s
out[str(f/"apply.sql")]="@@001_schema.sql\n@@002_archive.sql\n@@003_admission.sql\n"
out[str(f/"rollback.sql")]="""declare n number;begin select count(*)into n from RRL_WH_SCALE_CAPTURE where CAPTURE_PURPOSE!='PICK';if n>0 then raise_application_error(-20863,'FINAL_SCALE_HISTORY_REQUIRES_FORWARD_REPAIR');end if;end;
/
@@000_before_archive.sql
@@000_before_admission.sql
drop index RRL_WH_SCALE_CASE_PURPOSE_I;
alter table RRL_WH_SCALE_CAPTURE drop constraint RRL_WH_SCALE_SOURCE_C;
alter table RRL_WH_SCALE_CAPTURE drop constraint RRL_WH_SCALE_TARE_F;
alter table RRL_WH_SCALE_CAPTURE drop constraint RRL_WH_SCALE_TYPE_F;
alter table RRL_WH_SCALE_CAPTURE drop constraint RRL_WH_SCALE_PURPOSE_C;
alter table RRL_WH_SCALE_CAPTURE modify(CASE_PICK_LINE_ID not null,ARTICLE not null,SOURCE_CELL not null,SCANNED_PRODUCT not null);
alter table RRL_WH_SCALE_CAPTURE drop(CAPTURE_PURPOSE,TARE_CAPTURE_KEY,PALLET_TYPE_ID,TYPE_VERSION,COMPOSITION_SIGNATURE);
"""
out[str(f/"verify.sql")]="select name,type,line,text from user_errors where name not like 'BIN$%';\nselect CAPTURE_PURPOSE,count(*) from RRL_WH_SCALE_CAPTURE group by CAPTURE_PURPOSE;\n"
print(json.dumps(out,ensure_ascii=True))
