create or replace package RRL_STOCK_CASE_MOVE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_CASE_MOVE_CMD as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t:=json_object_t();
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t;x json_object_t;ct RRL_CASE_PICK_TASK%rowtype;
  task_id number;target varchar2(60);
 begin
  task_id:=d.get_object('source').get_number('case_task_id');select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_id;
  target:=m.get_string('target_cell');
  if target is null or ct.CURRENT_CELL is null or target=ct.CURRENT_CELL or m.get_number('expected_content_version') is null
   or m.get_number('expected_content_version')!=ct.CONTENT_VERSION then raise_application_error(-20886,'CASE_CARRIER_MOVE_SNAPSHOT_TARGET_REQUIRED');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(task_id));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(ct.PICK_WAVE_ID));
  RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU','CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(task_id));
  a:=json_array_t.parse(RRL_STOCK_CASE_PICK_CMD.carrier_rows(task_id));
  if a.get_size=0 then raise_application_error(-20886,'CASE_CARRIER_HAS_NO_PHYSICAL_STOCK');end if;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,x.get_string('uid'),x.get_string('article'),x.get_string('cell'),target);
  end loop;
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  v.put('task',task_id);v.put('warehouse',ct.WARE_ID);v.put('from',ct.CURRENT_CELL);v.put('to',target);
  v.put('carrier_identifier',ct.SSCC);v.put('content_version',ct.CONTENT_VERSION);v.put('stocks',a);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t;x json_object_t;j json_object_t:=json_object_t();
  ct RRL_CASE_PICK_TASK%rowtype;a json_array_t;plan clob;oldrows clob;nowrows clob;op varchar2(100);task_id number;ware number;
  target varchar2(60);from_cell varchar2(60);base varchar2(20);article varchar2(160);version number;system_flag number;event_id number;mode_name varchar2(20);
 begin
  if RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 and RRL_HAS_WRIGHT(p_actor,'case_pick_execute')!=1 then raise_application_error(-20882,'CASE_CARRIER_MOVE_FORBIDDEN');end if;
  op:=d.get_string('operation_id');select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;
  v:=json_object_t.parse(plan).get_object('domain');task_id:=v.get_number('task');ware:=v.get_number('warehouse');target:=v.get_string('to');from_cell:=v.get_string('from');
  select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_id for update;
  if ct.WARE_ID is null or ct.WARE_ID!=ware or ct.CURRENT_CELL is null or ct.CURRENT_CELL!=from_cell
   or ct.CONTENT_VERSION!=v.get_number('content_version') then raise_application_error(-20890,'CLOSURE_CHANGED: carrier move');end if;
  if ct.STATUS is null or ct.STATUS not in('IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT','WAIT_CONTROL','READY_TO_SHIP','CONTROLLED') then
   raise_application_error(-20886,'CASE_CARRIER_MOVE_STATE_CONFLICT');end if;
  if m.get_string('scan_container') is null or m.get_string('scan_container')!=ct.SSCC
   or m.get_string('scanned_to_cell') is null or m.get_string('scanned_to_cell')!=target then raise_application_error(-20886,'CASE_CARRIER_DESTINATION_SCAN_REQUIRED');end if;
  select IS_SYSTEM into system_flag from RRL_CELLS where CELL=target;
  if system_flag is null or system_flag!=1 then raise_application_error(-20886,'CASE_CARRIER_CONTROL_OR_STAGING_ZONE_REQUIRED');end if;
  a:=v.get_array('stocks');oldrows:=a.to_clob;nowrows:=RRL_STOCK_CASE_PICK_CMD.carrier_rows(task_id);
  if dbms_lob.compare(oldrows,nowrows)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: carrier contents');end if;
  mode_name:=case when from_cell='CPT_'||RRL_STOCK_PLAN_HELPER.decimal_text(ware) then 'CASE_EXIT' else 'ORDINARY' end;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   if x.get_string('cell')!=from_cell then raise_application_error(-20887,'CASE_CARRIER_LOCATION_CONFLICT');end if;
   article:=x.get_string('article');base:=x.get_string('base');
   select max(POLICY_VERSION) into version from RRL_STOCK_UOM_CONVERSION where ARTICUL=article and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
   if version is null then raise_application_error(-20868,'CASE_MOVE_BASE_POLICY_REQUIRED');end if;
   RRL_STOCK_TRANSFER_CORE.move(x.get_string('uid'),x.get_string('uid'),from_cell,target,
    RRL_STOCK_MATH.quantity(x.get_string('quantity')),base,version,ware,p_actor,i+1,null,null,null,null,null,mode_name);
  end loop;
  update RRL_CASE_PICK_TASK set CURRENT_CELL=target,CONTENT_VERSION=CONTENT_VERSION+1,UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_TASK_ID=task_id;
  select RRL_CASE_PICK_EVENT_SQ.nextval into event_id from dual;
  insert into RRL_CASE_PICK_EVENT(CASE_PICK_EVENT_ID,CASE_PICK_TASK_ID,EVENT_TYPE,PAYLOAD_JSON,CREATED_BY)
   values(event_id,task_id,'CARRIER_MOVED',p_request,p_actor);
  j.put('operation_id',op);j.put('case_pick_task_id',task_id);j.put('carrier_identifier',ct.SSCC);j.put('from_cell',from_cell);j.put('cell',target);
  j.put('content_version',ct.CONTENT_VERSION+1);j.put('status','MOVED');j.put('lots',a);p_result:=j.to_clob;
 end;
end;
/
