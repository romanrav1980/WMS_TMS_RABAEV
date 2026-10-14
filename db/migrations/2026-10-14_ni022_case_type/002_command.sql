create or replace package RRL_STOCK_CASE_TYPE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API,trigger RRL_CASE_PALLET_TYPE_GUARD)as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure assert_writing(p_task number);
end;
/
create or replace package body RRL_STOCK_CASE_TYPE_CMD as
 g_task number;g_op varchar2(100);g_tx varchar2(100);
 function snapshot(p_request clob,p_actor varchar2)return clob is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');src json_object_t:=d.get_object('source');
  j json_object_t;keys json_key_list;task_no number;type_no number;version_no number;n number;scan_value varchar2(200);reason_value varchar2(1000);el json_element_t;
 begin
  keys:=src.get_keys;el:=src.get('case_task_id');
  if keys.count!=1 or el is null or not el.is_number then raise_application_error(-20886,'CASE_TYPE_CANONICAL_TASK_REQUIRED');end if;
  task_no:=src.get_number('case_task_id');
  if task_no is null or task_no<1 or task_no!=trunc(task_no)then raise_application_error(-20886,'CASE_TYPE_TASK_REQUIRED');end if;
  RRL_CASE_TASK_ACCESS.assert_scope(task_no,p_actor,'case_pick_execute');
  if d.get_array('lines').get_size!=0 or d.get_array('units').get_size!=0 then raise_application_error(-20886,'CASE_TYPE_ZERO_QUANTITY_COMMAND_REQUIRED');end if;
  keys:=m.get_keys;
  if keys.count!=4 or not m.has('expected_version')or not m.has('pallet_type_id')or not m.has('scan_container')or not m.has('reason')then
   raise_application_error(-20886,'CASE_TYPE_EXPLICIT_FIELDS_REQUIRED');end if;
  el:=m.get('expected_version');if el is null or not el.is_number then raise_application_error(-20886,'CASE_TYPE_VERSION_REQUIRED');end if;
  el:=m.get('pallet_type_id');if el is null or not el.is_number then raise_application_error(-20886,'CASE_TYPE_TYPE_REQUIRED');end if;
  el:=m.get('scan_container');if el is null or not el.is_string then raise_application_error(-20886,'CASE_TYPE_SCAN_REQUIRED');end if;
  el:=m.get('reason');if el is null or not el.is_string then raise_application_error(-20886,'CASE_TYPE_REASON_REQUIRED');end if;
  version_no:=m.get_number('expected_version');type_no:=m.get_number('pallet_type_id');scan_value:=m.get_string('scan_container');reason_value:=trim(m.get_string('reason'));
  if version_no is null or version_no<0 or version_no!=trunc(version_no)or type_no is null or type_no<1 or type_no!=trunc(type_no)then
   raise_application_error(-20886,'CASE_TYPE_INTEGER_FIELDS_REQUIRED');end if;
  if reason_value is null or length(reason_value)>500 then raise_application_error(-20886,'CASE_TYPE_REASON_REQUIRED');end if;
  j:=json_object_t.parse(RRL_CASE_PALLET_TYPE_READ.describe_type(task_no,p_actor));
  if not j.get_boolean('can_change_empty_type')then raise_application_error(-20886,j.get_string('change_blocker'));end if;
  if j.get_number('version')!=version_no then raise_application_error(-20886,'CASE_TYPE_VERSION_CHANGED');end if;
  if scan_value is null or(scan_value!='CASE:'||to_char(task_no,'TM9')and(scan_value!=j.get_string('sscc')or j.get_string('sscc')is null))then
   raise_application_error(-20886,'CASE_TYPE_CURRENT_CONTAINER_SCAN_REQUIRED');end if;
  if type_no=j.get_number('actual_pallet_type_id')then raise_application_error(-20886,'CASE_TYPE_ALREADY_CURRENT');end if;
  select count(*)into n from RRL_PALLET_TYPE where PALLET_TYPE_ID=type_no and ACTIVE=1;
  if n!=1 then raise_application_error(-20886,'CASE_TYPE_ACTIVE_TYPE_REQUIRED');end if;
  if not j.get('assigned_to').is_null and j.get_string('assigned_to')!=p_actor and RRL_HAS_WRIGHT(p_actor,'case_pick_manage')!=1 then
   raise_application_error(-20882,'CASE_TYPE_ASSIGNED_OPERATOR_REQUIRED');end if;
  j.put('new_pallet_type_id',type_no);j.put('reason',reason_value);return j.to_clob;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob)is
  d json_object_t:=json_object_t.parse(p_request);j json_object_t;value_wire clob;f json_array_t:=json_array_t();r json_array_t:=json_array_t();task_key varchar2(100);
 begin
  value_wire:=snapshot(p_request,d.get_string('actor'));j:=json_object_t.parse(value_wire);task_key:=to_char(j.get_number('case_task_id'),'TM9');
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',task_key);
  RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU','CASE:'||task_key);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  j.put('snapshot_signature',rawtohex(sys.dbms_crypto.hash(value_wire,sys.dbms_crypto.hash_sh256)));
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=j.to_clob;
 end;
 procedure assert_writing(p_task number)is n number;
 begin
  if g_task is null or g_task!=p_task or g_op is null or g_tx is null or g_tx!=dbms_transaction.local_transaction_id(false)
   or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')!=g_op then
   raise_application_error(-20863,'CASE_TYPE_ROOT_OWNER_REQUIRED');end if;
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CASE_PICK_TASK',to_char(p_task,'TM9')));
  select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=g_op and COMMAND_TYPE='CASE_PALLET_TYPE_CHANGE'and STATE='IN_FLIGHT';
  if n!=1 then raise_application_error(-20863,'CASE_TYPE_CURRENT_ROOT_REQUIRED');end if;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);frozen json_object_t;j json_object_t;plan clob;value_wire clob;
  task_no number;new_type number;old_version number;locked_version number;op varchar2(100):=d.get_string('operation_id');
 begin
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;frozen:=json_object_t.parse(plan).get_object('domain');
  task_no:=frozen.get_number('case_task_id');new_type:=frozen.get_number('new_pallet_type_id');old_version:=frozen.get_number('version');
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CASE_PICK_TASK',to_char(task_no,'TM9')));
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU','CASE:'||to_char(task_no,'TM9')));
  begin select nvl(CONTENT_VERSION,0)into locked_version from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_no for update nowait;
  exception when others then if sqlcode=-54 then raise_application_error(-20840,'CASE_TYPE_ROW_BUSY');else raise;end if;end;
  value_wire:=snapshot(p_request,p_actor);
  if rawtohex(sys.dbms_crypto.hash(value_wire,sys.dbms_crypto.hash_sh256))!=frozen.get_string('snapshot_signature')then
   raise_application_error(-20890,'CLOSURE_CHANGED: case pallet type');end if;
  g_task:=task_no;g_op:=op;g_tx:=dbms_transaction.local_transaction_id(false);
  update RRL_CASE_PICK_TASK set PALLET_TYPE_ID=new_type,CONTENT_VERSION=old_version+1 where CASE_PICK_TASK_ID=task_no and nvl(CONTENT_VERSION,0)=old_version;
  if sql%rowcount!=1 then raise_application_error(-20886,'CASE_TYPE_VERSION_CHANGED');end if;
  g_task:=null;g_op:=null;g_tx:=null;
  j:=json_object_t();j.put('operation_id',op);j.put('command_type','CASE_PALLET_TYPE_CHANGE');j.put('case_task_id',task_no);
  j.put('pallet_type_id',new_type);j.put('previous_pallet_type_id',frozen.get_number('actual_pallet_type_id'));j.put('planned_pallet_type_id',frozen.get_number('planned_pallet_type_id'));
  j.put('version',old_version+1);j.put('reason',frozen.get_string('reason'));j.put('stock_changed',false);j.put('status','APPLIED');p_result:=j.to_clob;
 exception when others then g_task:=null;g_op:=null;g_tx:=null;raise;
 end;
end;
/
