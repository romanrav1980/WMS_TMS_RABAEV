create table RRL_WH_SCALE_USE(
 CAPTURE_KEY varchar2(64)primary key references RRL_WH_SCALE_CAPTURE(CAPTURE_KEY),
 STOCK_OPERATION_ID varchar2(100)not null unique references RRL_STOCK_OPERATION(OPERATION_ID),
 CASE_PICK_TASK_ID number not null,CASE_PICK_LINE_ID number not null,
 ACTOR varchar2(50)not null,APPLIED_AT timestamp with time zone default systimestamp not null);
create or replace package RRL_CASE_SCALE_ADMISSION authid definer as
 procedure assert_capture(p_request clob,p_previous number);
 procedure claim_capture(p_request clob,p_operation varchar2,p_previous number);
end;
/
create or replace package body RRL_CASE_SCALE_ADMISSION as
 procedure assert_capture(p_request clob,p_previous number)is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');
  c RRL_WH_SCALE_CAPTURE%rowtype;v RRL_WH_SCALE_DEVICE%rowtype;
  t RRL_CASE_PICK_TASK%rowtype;l RRL_CASE_PICK_LINE%rowtype;
  k varchar2(64);task_id number;line_id number;n number;serial_flag number;marked number;
  delta_qty number;unit_key varchar2(64);gross number;
 begin
  if not m.has('warehouse_scale_capture')then return;end if;
  k:=m.get_string('warehouse_scale_capture');
  if k is null or not regexp_like(k,'^[A-F0-9]{64}$')then raise_application_error(-20886,'WAREHOUSE_SCALE_CAPTURE_KEY_REQUIRED');end if;
  task_id:=d.get_object('source').get_number('case_task_id');line_id:=d.get_object('source').get_number('case_line_id');
  select *into c from RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=k;
  select *into v from RRL_WH_SCALE_DEVICE where DEVICE_ID=c.DEVICE_ID;
  select *into t from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_id;
  select *into l from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=task_id and CASE_PICK_LINE_ID=line_id;
  if c.CASE_PICK_TASK_ID!=task_id or c.CASE_PICK_LINE_ID!=line_id or c.WARE_ID!=t.WARE_ID
   or c.CASE_CONTENT_VERSION!=t.CONTENT_VERSION or c.ARTICLE!=l.ARTICUL
   or c.SOURCE_CELL!=l.CELL_CODE or c.CARRIER_IDENTIFIER!=t.SSCC
   or m.get_string('scan_cell')is null or m.get_string('scan_cell')!=c.SOURCE_CELL
   or m.get_string('scan_container')is null or m.get_string('scan_container')!=c.CARRIER_IDENTIFIER
   then raise_application_error(-20886,'WAREHOUSE_SCALE_CASE_SOURCE_CHANGED');end if;
  if v.ACTIVE_FLAG!=1 or v.POLICY_VERSION!=c.DEVICE_POLICY_VERSION or v.WARE_ID!=c.WARE_ID
   or v.POST_CELL!=c.POST_CELL or v.MEASUREMENT_BASIS!=c.MEASUREMENT_BASIS
   or v.DEVICE_MODE!=c.DEVICE_MODE or v.CALIBRATED_UNTIL<systimestamp
   or c.MEASURED_AT<systimestamp-numtodsinterval(120,'SECOND')
   or c.MEASURED_AT>systimestamp+numtodsinterval(2,'SECOND')
   then raise_application_error(-20886,'WAREHOUSE_SCALE_CURRENT_FRESH_DEVICE_REQUIRED');end if;
  select count(*)into n from RUSERS where ID=v.SENDER_ID and ID=c.RECORDED_BY and nvl(DELETED,0)=0
   and WARE_ID=c.WARE_ID and upper(trim(USER_GROUP))!='GLOBAL_ADMIN'and RRL_HAS_WRIGHT(ID,'warehouse_scale_ingest')=1;
  if n!=1 then raise_application_error(-20882,'WAREHOUSE_SCALE_CURRENT_SENDER_REQUIRED');end if;
  select count(*)into n from RRL_WH_SCALE_USE where CAPTURE_KEY=k;
  if n!=0 then raise_application_error(-20886,'WAREHOUSE_SCALE_CAPTURE_ALREADY_USED');end if;
  select nvl(max(SERIALIZED_WEIGHT_BOXES),0),nvl(max(MARKING_REQUIRED),0)into serial_flag,marked
   from RRL_SKU_RECEIPT_POLICY where ARTICUL=l.ARTICUL;
  delta_qty:=RRL_STOCK_MATH.quantity(m.get_string('fact_qty'))-p_previous;
  if serial_flag=1 then
   if c.MEASUREMENT_BASIS!='GROSS' or not m.has('weighted_box_scan')
    or m.get_string('weighted_box_scan')is null or m.get_string('weighted_box_scan')!=c.SCANNED_PRODUCT
    or d.get_array('units').get_size!=1 then raise_application_error(-20886,'WAREHOUSE_SCALE_SAME_SEALED_BOX_REQUIRED');end if;
   unit_key:=d.get_array('units').get_string(0);
   select GROSS_WEIGHT_KG into gross from RRL_WMS_RECEIPT_UNIT where PHYSICAL_UNIT_KEY=unit_key
    and BASE_UOM='KG'and GROSS_WEIGHT_KG>=BASE_QTY and MEASUREMENT_REFERENCE is not null and WEIGHT_LABEL_SCAN is not null;
   if abs(gross-c.WEIGHT_KG)>v.RESOLUTION_KG then raise_application_error(-20886,'WAREHOUSE_SCALE_BOX_GROSS_MISMATCH');end if;
  else
   select count(*)into n from RRL_SKU_RECEIPT_PROFILE where ARTICUL=l.ARTICUL;
   if marked!=0 or n!=0 or c.MEASUREMENT_BASIS!='NET' or d.get_array('units').get_size!=0 or delta_qty!=c.WEIGHT_KG
    then raise_application_error(-20886,'WAREHOUSE_SCALE_UNMARKED_NET_QUANTITY_REQUIRED');end if;
  end if;
 exception when no_data_found or too_many_rows then raise_application_error(-20886,'WAREHOUSE_SCALE_CURRENT_SOURCE_NOT_UNIQUE');
 end;
 procedure claim_capture(p_request clob,p_operation varchar2,p_previous number)is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');
  k varchar2(64);task_id number;line_id number;actor_value varchar2(50);
 begin
  if not m.has('warehouse_scale_capture')then return;end if;
  assert_capture(p_request,p_previous);k:=m.get_string('warehouse_scale_capture');
  RRL_STOCK_LOCK_API.assert_held(70,RRL_STOCK_LOCK_API.resource_key('UNIQUE','WH.SCALE.USE:'||k));
  task_id:=d.get_object('source').get_number('case_task_id');line_id:=d.get_object('source').get_number('case_line_id');
  actor_value:=d.get_string('actor');
  insert into RRL_WH_SCALE_USE(CAPTURE_KEY,STOCK_OPERATION_ID,CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,ACTOR)
   values(k,p_operation,task_id,line_id,actor_value);
 end;
end;
/
create or replace trigger RRL_WH_SCALE_USE_GUARD before insert or update or delete on RRL_WH_SCALE_USE for each row
declare d json_object_t;wire clob;command_value varchar2(50);state_value varchar2(20);
begin
 if not inserting then raise_application_error(-20863,'WAREHOUSE_SCALE_USE_IMMUTABLE');end if;
 if sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null
  or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
  or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is null
  or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')!=:new.STOCK_OPERATION_ID then raise_application_error(-20863,'WAREHOUSE_SCALE_ROOT_TRANSACTION_REQUIRED');end if;
  select CANONICAL_REQUEST,COMMAND_TYPE,STATE into wire,command_value,state_value from RRL_STOCK_OPERATION where OPERATION_ID=:new.STOCK_OPERATION_ID;
  d:=json_object_t.parse(wire);
  if command_value!='CASE_PICK_CONFIRM'or state_value!='IN_FLIGHT' or d.get_string('actor')!=:new.ACTOR
   or d.get_object('metadata').get_string('warehouse_scale_capture')is null
   or d.get_object('metadata').get_string('warehouse_scale_capture')!=:new.CAPTURE_KEY
   or d.get_object('source').get_number('case_task_id')!=:new.CASE_PICK_TASK_ID
   or d.get_object('source').get_number('case_line_id')!=:new.CASE_PICK_LINE_ID
   then raise_application_error(-20863,'WAREHOUSE_SCALE_CASE_ROOT_REQUIRED');end if;
  RRL_STOCK_LOCK_API.assert_held(70,RRL_STOCK_LOCK_API.resource_key('UNIQUE','WH.SCALE.USE:'||:new.CAPTURE_KEY));
end;
/
