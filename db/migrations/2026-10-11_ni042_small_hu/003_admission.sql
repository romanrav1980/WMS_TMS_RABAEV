create or replace package RRL_WH_FINAL_SCALE_ADMISSION authid definer accessible by(package RRL_STOCK_PALLET_QC_CMD,package RRL_STOCK_QC_GATE,package RRL_STOCK_HU_CMD) as
 procedure assert_capture(p_request clob,p_domain clob);
 procedure claim_capture(p_request clob,p_domain clob,p_operation varchar2);
 function approved(p_domain clob,p_operation varchar2)return number;
 function preserve_case(p_task number)return number;
end;
/

create or replace package body RRL_WH_FINAL_SCALE_ADMISSION as
 function required(p_domain clob)return number is
  d json_object_t:=json_object_t.parse(p_domain);task_no number:=d.get_number('case_task');n number;
 begin
  if task_no is null then return 0;end if;
  select case when p.FINAL_WEIGHT_REQUIRED=1 and upper(p.LOAD_UNIT_CLASS)='CONTAINER'then 1 else 0 end into n
   from RRL_CASE_PICK_TASK c join RRL_PALLET_TYPE p on p.PALLET_TYPE_ID=c.PALLET_TYPE_ID where c.CASE_PICK_TASK_ID=task_no;
  return n;
 end;
 procedure assert_capture(p_request clob,p_domain clob)is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');dom json_object_t:=json_object_t.parse(p_domain);
  capture RRL_WH_SCALE_CAPTURE%rowtype;tare RRL_WH_SCALE_CAPTURE%rowtype;dev RRL_WH_SCALE_DEVICE%rowtype;ct RRL_CASE_PICK_TASK%rowtype;
  key_value varchar2(64);signature_value varchar2(64);task_no number;n number;gross number;wood number;needed number;kind varchar2(20):=m.get_string('quality_kind');
 begin
  if kind not in('WEIGHT','WEIGHT2')then
   if m.has('final_scale_capture')then raise_application_error(-20886,'FINAL_SCALE_WEIGHT_CONTROL_REQUIRED');end if;return;
  end if;
  needed:=required(p_domain);
  if needed=0 and not m.has('final_scale_capture')then return;end if;
  key_value:=m.get_string('final_scale_capture');
  if key_value is null or not regexp_like(key_value,'^[A-F0-9]{64}$')then raise_application_error(-20886,'SMALL_BOX_FINAL_SCALE_CAPTURE_REQUIRED');end if;
  select *into capture from RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=key_value;
  task_no:=dom.get_number('case_task');
  select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_no;
  select *into dev from RRL_WH_SCALE_DEVICE where DEVICE_ID=capture.DEVICE_ID;
  if capture.CAPTURE_PURPOSE!='FINAL_GROSS' or capture.TARE_CAPTURE_KEY is null or capture.MEASUREMENT_BASIS!='GROSS'
   or capture.CASE_PICK_TASK_ID!=ct.CASE_PICK_TASK_ID or capture.WARE_ID!=ct.WARE_ID or capture.CARRIER_IDENTIFIER!=ct.SSCC
   or capture.CASE_CONTENT_VERSION!=ct.CONTENT_VERSION or capture.PALLET_TYPE_ID!=ct.PALLET_TYPE_ID
   or ct.CONTENT_VERSION!=dom.get_number('case_version')or ct.LEGACY_SBORKA_PALLET_ID!=dom.get_number('document_id')
   or ct.STATUS not in('WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP') then raise_application_error(-20886,'FINAL_SCALE_CURRENT_CASE_CHANGED');end if;
  signature_value:=RRL_STOCK_QC_GATE.signature_for_plan(p_domain);
  if capture.COMPOSITION_SIGNATURE!=signature_value then raise_application_error(-20886,'FINAL_SCALE_CURRENT_COMPOSITION_CHANGED');end if;
  if dev.ACTIVE_FLAG!=1 or dev.POLICY_VERSION!=capture.DEVICE_POLICY_VERSION or dev.WARE_ID!=capture.WARE_ID
   or dev.POST_CELL!=capture.POST_CELL or dev.DEVICE_MODE!=capture.DEVICE_MODE or dev.MEASUREMENT_BASIS!='GROSS'
   or dev.CALIBRATION_REF!=capture.CALIBRATION_REF or dev.CALIBRATED_UNTIL<systimestamp
   or capture.MEASURED_AT<systimestamp-numtodsinterval(120,'SECOND')or capture.MEASURED_AT>systimestamp+numtodsinterval(2,'SECOND')
   then raise_application_error(-20886,'FINAL_SCALE_CURRENT_FRESH_DEVICE_REQUIRED');end if;
  select count(*)into n from RUSERS where ID=dev.SENDER_ID and ID=capture.RECORDED_BY and nvl(DELETED,0)=0 and WARE_ID=ct.WARE_ID
   and upper(trim(USER_GROUP))!='GLOBAL_ADMIN'and RRL_HAS_WRIGHT(ID,'warehouse_scale_ingest')=1;
  if n!=1 then raise_application_error(-20882,'FINAL_SCALE_CURRENT_SENDER_REQUIRED');end if;
  select *into tare from RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=capture.TARE_CAPTURE_KEY;
  if tare.CAPTURE_PURPOSE!='EMPTY_TARE' or tare.CASE_PICK_TASK_ID!=ct.CASE_PICK_TASK_ID or tare.CARRIER_IDENTIFIER!=ct.SSCC
   or tare.WARE_ID!=capture.WARE_ID or tare.POST_CELL!=capture.POST_CELL or tare.DEVICE_ID!=capture.DEVICE_ID or tare.DEVICE_MODE!=capture.DEVICE_MODE
   or tare.PALLET_TYPE_ID!=ct.PALLET_TYPE_ID or tare.MEASURED_AT>capture.MEASURED_AT
   or tare.MEASURED_AT<capture.MEASURED_AT-numtodsinterval(24,'HOUR')or tare.WEIGHT_KG>=capture.WEIGHT_KG
   then raise_application_error(-20886,'FINAL_SCALE_SAME_EMPTY_TARE_REQUIRED');end if;
  gross:=RRL_STOCK_MATH.quantity(m.get_string('gross_weight'));
  wood:=case when regexp_like(m.get_string('wood_weight'),'^0([.]0{1,9})?$')then 0 else RRL_STOCK_MATH.quantity(m.get_string('wood_weight'))end;
  if gross!=capture.WEIGHT_KG or wood!=tare.WEIGHT_KG then raise_application_error(-20886,'FINAL_SCALE_ORIGINAL_GROSS_TARE_REQUIRED');end if;
  select count(*)into n from RRL_WH_FINAL_SCALE_USE where CAPTURE_KEY=key_value;
  if n>0 then raise_application_error(-20886,'FINAL_SCALE_CAPTURE_ALREADY_USED');end if;
 exception when no_data_found or too_many_rows then raise_application_error(-20886,'FINAL_SCALE_CURRENT_SOURCE_REQUIRED');
 end;
 procedure claim_capture(p_request clob,p_domain clob,p_operation varchar2)is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');dom json_object_t:=json_object_t.parse(p_domain);
  key_value varchar2(64);tare_key varchar2(64);task_no number;version_no number;signature_value varchar2(64);actor_value varchar2(50);signature_version number;
 begin
  if not m.has('final_scale_capture')then return;end if;
  assert_capture(p_request,p_domain);key_value:=m.get_string('final_scale_capture');
  RRL_STOCK_LOCK_API.assert_held(70,RRL_STOCK_LOCK_API.resource_key('UNIQUE','WH.FINAL.SCALE.USE:'||key_value));
  if sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
   or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')!=p_operation then raise_application_error(-20863,'FINAL_SCALE_CURRENT_STOCK_OWNER_REQUIRED');end if;
  select TARE_CAPTURE_KEY into tare_key from RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=key_value;
  task_no:=dom.get_number('case_task');version_no:=dom.get_number('case_version');signature_value:=RRL_STOCK_QC_GATE.signature_for_plan(p_domain);actor_value:=d.get_string('actor');
  signature_version:=RRL_STOCK_QC_GATE.signature_version_for_plan(p_domain);
  insert into RRL_WH_FINAL_SCALE_USE(CAPTURE_KEY,STOCK_OPERATION_ID,TARE_CAPTURE_KEY,CASE_PICK_TASK_ID,CASE_CONTENT_VERSION,COMPOSITION_SIGNATURE,ACTOR,SIGNATURE_VERSION)
   values(key_value,p_operation,tare_key,task_no,version_no,signature_value,actor_value,signature_version);
 end;
 function approved(p_domain clob,p_operation varchar2)return number is
  dom json_object_t:=json_object_t.parse(p_domain);task_no number:=dom.get_number('case_task');version_no number:=dom.get_number('case_version');
  signature_value varchar2(64);n number;tx_id_value varchar2(100);current_signature_version number;
 begin
  tx_id_value:=dbms_transaction.local_transaction_id(false);current_signature_version:=RRL_STOCK_QC_GATE.signature_version_for_plan(p_domain);
  if required(p_domain)=0 then return 1;end if;
  if p_operation is null then return 0;end if;signature_value:=RRL_STOCK_QC_GATE.signature_for_plan(p_domain);
  select count(*)into n from RRL_WH_FINAL_SCALE_USE u join RRL_WH_SCALE_CAPTURE c on c.CAPTURE_KEY=u.CAPTURE_KEY
   join RRL_STOCK_OPERATION o on o.OPERATION_ID=u.STOCK_OPERATION_ID
   where u.STOCK_OPERATION_ID=p_operation and u.CASE_PICK_TASK_ID=task_no and u.CASE_CONTENT_VERSION<=version_no and u.SIGNATURE_VERSION=current_signature_version and u.COMPOSITION_SIGNATURE=signature_value
    and c.CAPTURE_PURPOSE='FINAL_GROSS' and c.COMPOSITION_SIGNATURE=signature_value and c.TARE_CAPTURE_KEY=u.TARE_CAPTURE_KEY
    and(o.STATE='APPLIED'or(o.OPERATION_ID=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')
     and sys_context('RRL_STOCK_WRITE_CTX','TX_ID')=tx_id_value));
  return case when n=1 then 1 else 0 end;
 end;
 function preserve_case(p_task number)return number is
  required_flag number;identifier varchar2(150);qc json_object_t;
 begin
  select case when p.FINAL_WEIGHT_REQUIRED=1 and upper(p.LOAD_UNIT_CLASS)='CONTAINER'then 1 else 0 end,s.PALLET_UID into required_flag,identifier
   from RRL_CASE_PICK_TASK c join RRL_PALLET_TYPE p on p.PALLET_TYPE_ID=c.PALLET_TYPE_ID left join RRL_SBORKA_PALLETS s on s.ID=c.LEGACY_SBORKA_PALLET_ID
   where c.CASE_PICK_TASK_ID=p_task;
  if required_flag=0 or identifier is null then return 0;end if;
  qc:=json_object_t.parse(RRL_STOCK_QC_GATE.status_json(identifier));
  return case when qc.get_boolean('ready')then 1 else 0 end;
 end;

end;
/
