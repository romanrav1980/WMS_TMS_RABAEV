create or replace package RRL_STOCK_PALLET_TYPE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API,trigger RRL_PALLET_FLOOR_GUARD)as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure assert_writing(p_uid varchar2,p_operation varchar2);
end;
/
create or replace package body RRL_STOCK_PALLET_TYPE_CMD as
 g_writing boolean:=false;g_uid varchar2(200);g_operation varchar2(100);g_tx varchar2(100);
 function snapshot(p_request clob,p_actor varchar2)return clob is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');j json_object_t;
  uid_value varchar2(200):=d.get_object('source').get_string('uid');keys json_key_list;el json_element_t;
  version_no number;type_no number;reference_value varchar2(255);scan_value varchar2(200);n number;
 begin
  keys:=d.get_object('source').get_keys;el:=d.get_object('source').get('uid');
  if keys.count!=1 or el is null or not el.is_string then raise_application_error(-20886,'PALLET_FLOOR_CANONICAL_SOURCE_REQUIRED');end if;
  if uid_value is null or length(uid_value)>200 or trim(uid_value)!=uid_value then raise_application_error(-20886,'PALLET_FLOOR_UID_REQUIRED');end if;
  if d.get_array('lines').get_size!=0 or d.get_array('units').get_size!=0 then raise_application_error(-20886,'PALLET_FLOOR_ZERO_QUANTITY_COMMAND_REQUIRED');end if;
  keys:=m.get_keys;
  if keys.count!=5 or not m.has('pallet_type_id')or not m.has('expected_version')or not m.has('scan_pallet')or not m.has('scan_cell')or not m.has('evidence_reference')then
   raise_application_error(-20886,'PALLET_FLOOR_EXPLICIT_FIELDS_REQUIRED');end if;
  el:=m.get('pallet_type_id');if not el.is_number then raise_application_error(-20886,'PALLET_FLOOR_INTEGER_TYPE_REQUIRED');end if;
  el:=m.get('expected_version');if not el.is_number then raise_application_error(-20886,'PALLET_FLOOR_INTEGER_VERSION_REQUIRED');end if;
  el:=m.get('scan_pallet');if not el.is_string then raise_application_error(-20886,'PALLET_FLOOR_SCAN_TEXT_REQUIRED');end if;
  el:=m.get('scan_cell');if not el.is_string then raise_application_error(-20886,'PALLET_FLOOR_SCAN_TEXT_REQUIRED');end if;
  el:=m.get('evidence_reference');if not el.is_string then raise_application_error(-20886,'PALLET_FLOOR_REFERENCE_TEXT_REQUIRED');end if;
  version_no:=m.get_number('expected_version');type_no:=m.get_number('pallet_type_id');
  if version_no is null or version_no<0 or version_no!=trunc(version_no)or type_no is null or type_no<1 or type_no!=trunc(type_no)then
   raise_application_error(-20886,'PALLET_FLOOR_INTEGER_FIELDS_REQUIRED');end if;
  reference_value:=trim(m.get_string('evidence_reference'));
  if reference_value is null or lengthb(reference_value)>255 then raise_application_error(-20886,'PALLET_FLOOR_REFERENCE_REQUIRED');end if;
  j:=json_object_t.parse(RRL_PALLET_FLOOR_READ.describe_type(uid_value,p_actor));
  if not j.get_boolean('has_physical_stock')or j.get_string('cell')is null then raise_application_error(-20886,'PALLET_FLOOR_CURRENT_PHYSICAL_STOCK_REQUIRED');end if;
  if j.get_number('version')!=version_no then raise_application_error(-20886,'PALLET_FLOOR_VERSION_CHANGED');end if;
  scan_value:=m.get_string('scan_pallet');
  if scan_value is null or(scan_value!=uid_value and(j.get_string('sscc')is null or scan_value!=j.get_string('sscc')))then
   raise_application_error(-20886,'PALLET_FLOOR_CURRENT_PALLET_SCAN_REQUIRED');end if;
  if m.get_string('scan_cell')is null or m.get_string('scan_cell')!=j.get_string('cell')then raise_application_error(-20886,'PALLET_FLOOR_CURRENT_CELL_SCAN_REQUIRED');end if;
  select count(*)into n from RRL_PALLET_TYPE where PALLET_TYPE_ID=type_no and ACTIVE=1;
  if n!=1 then raise_application_error(-20886,'PALLET_FLOOR_ACTIVE_TYPE_REQUIRED');end if;
  j.put('new_pallet_type_id',type_no);j.put('evidence_reference',reference_value);return j.to_clob;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob)is
  d json_object_t:=json_object_t.parse(p_request);s clob;j json_object_t;uid_value varchar2(200);f json_array_t:=json_array_t();r json_array_t:=json_array_t();
 begin
  s:=snapshot(p_request,d.get_string('actor'));j:=json_object_t.parse(s);uid_value:=j.get_string('uid');
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PALLETS',j.get_string('uid'));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PALLET_FLOOR_TYPE',j.get_string('uid'));
  RRL_STOCK_PLAN_HELPER.stock_closure(f,r,uid_value,j.get_string('article'),j.get_string('cell'),null);
  j.put('snapshot_signature',rawtohex(sys.dbms_crypto.hash(s,sys.dbms_crypto.hash_sh256)));
  p_domain:=j.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure assert_writing(p_uid varchar2,p_operation varchar2)is n number;
 begin
  if not g_writing or g_uid is null or g_uid!=p_uid or g_operation is null or g_operation!=p_operation
   or g_tx is null or g_tx!=dbms_transaction.local_transaction_id(false)
   or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')!=p_operation then
   raise_application_error(-20863,'PALLET_FLOOR_ROOT_OWNER_REQUIRED');end if;
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_PALLET_FLOOR_TYPE',p_uid));
  select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=p_operation and COMMAND_TYPE='PALLET_FLOOR_TYPE_CONFIRM'and STATE='IN_FLIGHT';
  if n!=1 then raise_application_error(-20863,'PALLET_FLOOR_CURRENT_ROOT_REQUIRED');end if;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);frozen json_object_t;j json_object_t;s clob;plan clob;
  op varchar2(100):=d.get_string('operation_id');uid_value varchar2(200);ware_no number;type_no number;version_no number;
 begin
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;frozen:=json_object_t.parse(plan).get_object('domain');
  s:=snapshot(p_request,p_actor);
  if rawtohex(sys.dbms_crypto.hash(s,sys.dbms_crypto.hash_sh256))!=frozen.get_string('snapshot_signature')then raise_application_error(-20890,'CLOSURE_CHANGED: pallet floor type');end if;
  uid_value:=frozen.get_string('uid');ware_no:=frozen.get_number('warehouse');type_no:=frozen.get_number('new_pallet_type_id');version_no:=frozen.get_number('version')+1;
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_PALLETS',uid_value));
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),4);
  g_writing:=true;g_uid:=uid_value;g_operation:=op;g_tx:=dbms_transaction.local_transaction_id(false);
  merge into RRL_PALLET_FLOOR_TYPE t using(select uid_value UID_PALLET from dual)src on(t.UID_PALLET=src.UID_PALLET)
   when matched then update set PALLET_TYPE_ID=type_no,TYPE_VERSION=version_no,LAST_OPERATION_ID=op,DECLARED_WARE_ID=ware_no
   when not matched then insert(UID_PALLET,PALLET_TYPE_ID,TYPE_VERSION,LAST_OPERATION_ID,DECLARED_WARE_ID)values(uid_value,type_no,version_no,op,ware_no);
  g_writing:=false;g_uid:=null;g_operation:=null;g_tx:=null;
  j:=json_object_t();j.put('operation_id',op);j.put('command_type','PALLET_FLOOR_TYPE_CONFIRM');j.put('uid',uid_value);j.put('warehouse',ware_no);
  j.put('pallet_type_id',type_no);j.put('version',version_no);j.put('evidence_reference',frozen.get_string('evidence_reference'));j.put('actor',p_actor);
  j.put('stock_changed',false);j.put('tare_balance_changed',false);j.put('status','APPLIED');p_result:=j.to_clob;
 exception when others then g_writing:=false;g_uid:=null;g_operation:=null;g_tx:=null;raise;
 end;
end;
/
