create or replace package body RRL_WH_WEIGH_REQUEST_API as
 g_write_id varchar2(100);g_write_kind varchar2(10);g_write_tx varchar2(100);
 g_capture_id varchar2(100);g_capture_tx varchar2(100);
 procedure clear_capture_context is begin g_capture_id:=null;g_capture_tx:=null;end;
 procedure end_write is begin g_write_id:=null;g_write_kind:=null;g_write_tx:=null;end;
 procedure begin_write(p_id varchar2,p_kind varchar2)is begin
  g_write_id:=p_id;g_write_kind:=p_kind;g_write_tx:=dbms_transaction.local_transaction_id(true);
 end;
 function writing(p_id varchar2,p_kind varchar2)return number is begin
  if g_write_id=p_id and g_write_kind=p_kind and g_write_tx is not null and g_write_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;
 end;
 function digest(p_source clob)return varchar2 is begin return rawtohex(sys.dbms_crypto.hash(p_source,sys.dbms_crypto.hash_sh256));end;
 procedure outside_stock is begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null then raise_application_error(-20886,'WH_WEIGH_OUTSIDE_STOCK_REQUIRED');end if;
 end;
 procedure case_lock(p_task number)is n number;begin
  lock table RRL_ACCESS_REV in share mode wait 2;
  select CASE_PICK_TASK_ID into n from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task for update wait 2;
 end;
 procedure sender(p_device RRL_WH_SCALE_DEVICE%rowtype,p_actor varchar2)is n number;begin
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and WARE_ID=p_device.WARE_ID
   and upper(trim(USER_GROUP))!='GLOBAL_ADMIN'and RRL_HAS_WRIGHT(ID,'warehouse_scale_ingest')=1;
  if n!=1 or p_device.SENDER_ID!=p_actor then raise_application_error(-20882,'WH_WEIGH_CURRENT_DEDICATED_SENDER_REQUIRED');end if;
 end;
 function own_final_session(p_task number,p_device varchar2,p_actor varchar2)return varchar2 is
  ct RRL_CASE_PICK_TASK%rowtype;sid varchar2(100);n number;
 begin
  select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  if ct.ASSIGNED_TO is null or ct.ASSIGNED_TO!=p_actor or ct.STATUS is null or ct.STATUS not in('WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP')then return null;end if;
  for s in(select *from RRL_ASSEMBLY_SESSION where CASE_PICK_TASK_ID=p_task and DEVICE_ID=p_device and OPERATOR_ID=p_actor
   and STATE='OPEN'and EXPIRES_AT>=systimestamp and LAST_CONTENT_VERSION=ct.CONTENT_VERSION and CARRIER_IDENTIFIER=ct.SSCC)loop
   select count(*)into n from RRL_ASSEMBLY_STEP where SESSION_ID=s.SESSION_ID and STATE not in('APPLIED','CANCELLED');
   if n=0 then
    if sid is not null then raise_application_error(-20886,'WH_WEIGH_AMBIGUOUS_ASSEMBLY_SESSION');end if;sid:=s.SESSION_ID;
   end if;
  end loop;
  if sid is not null then RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,'case_pick_execute');end if;
  return sid;
 end;
 function final_authority(p_task number,p_device varchar2,p_actor varchar2)return varchar2 is sid varchar2(100);identifier varchar2(150);
 begin
  sid:=own_final_session(p_task,p_device,p_actor);
  if sid is not null then return sid;end if;
  select p.PALLET_UID into identifier from RRL_CASE_PICK_TASK ct join RRL_SBORKA_PALLETS p on p.ID=ct.LEGACY_SBORKA_PALLET_ID where ct.CASE_PICK_TASK_ID=p_task;
  RRL_OUTGOING_QC_ACCESS.assert_identifier(identifier,p_actor);return null;
 end;
 procedure device_free(p_device varchar2,p_task number,p_purpose varchar2,p_actor varchar2)is n number;sid varchar2(100);
 begin
  select count(*)into n from RRL_ASSEMBLY_SESSION where CASE_PICK_TASK_ID=p_task and DEVICE_ID!=p_device and STATE in('OPEN','BLOCKED');
  if n>0 then raise_application_error(-20886,'WH_WEIGH_CASE_ASSEMBLY_OTHER_DEVICE_BUSY');end if;
  if p_purpose='FINAL_GROSS'then sid:=own_final_session(p_task,p_device,p_actor);end if;
  select count(*)into n from RRL_ASSEMBLY_SESSION where DEVICE_ID=p_device and STATE in('OPEN','BLOCKED')
   and(sid is null or SESSION_ID!=sid);
  if n>0 then raise_application_error(-20886,'WH_WEIGH_ASSEMBLY_DEVICE_BUSY');end if;
 end;
 function snapshot(p_source clob,p_actor varchar2)return json_object_t is
  j json_object_t:=json_object_t.parse(p_source);s json_object_t:=json_object_t();resource_context json_object_t;qc json_object_t;
  ct RRL_CASE_PICK_TASK%rowtype;ln RRL_CASE_PICK_LINE%rowtype;typ RRL_PALLET_TYPE%rowtype;
  d RRL_WH_SCALE_DEVICE%rowtype;tare RRL_WH_SCALE_CAPTURE%rowtype;
  purpose_value varchar2(12):=j.get_string('purpose');identifier varchar2(150);permission_value varchar2(50);n number;
  keys json_key_list:=j.get_keys;
 begin
  if j.get_string('request_id')is null or length(j.get_string('request_id'))>100 or j.get_string('device_id')is null
   or purpose_value is null or purpose_value not in('PICK','EMPTY_TARE','FINAL_GROSS')then raise_application_error(-20886,'WH_WEIGH_INTENT_IDENTIFIERS_REQUIRED');end if;
  for k in 1..keys.count loop
   if keys(k)not in('request_id','device_id','purpose','case_task_id','expected_content_version','scan_container','case_line_id','scan_source_cell','scan_product',
    'resource_session_id','tare_capture_key','expected_composition_signature')then raise_application_error(-20886,'WH_WEIGH_MASS_FREE_EXACT_FIELDS_REQUIRED');end if;
  end loop;
  select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=json_value(p_source,'$.case_task_id' returning number);
  select *into d from RRL_WH_SCALE_DEVICE where DEVICE_ID=json_value(p_source,'$.device_id' returning varchar2(512));
  select *into typ from RRL_PALLET_TYPE where PALLET_TYPE_ID=ct.PALLET_TYPE_ID;
  if j.get_number('expected_content_version')is null or ct.CONTENT_VERSION!=j.get_number('expected_content_version')
   or j.get_string('scan_container')is null or ct.SSCC!=j.get_string('scan_container')or ct.SSCC is null or ct.WARE_ID!=d.WARE_ID then
   raise_application_error(-20886,'WH_WEIGH_SOURCE_CHANGED_RECREATE_REQUEST');end if;
  if d.ACTIVE_FLAG!=1 or d.CALIBRATED_UNTIL<systimestamp then raise_application_error(-20886,'WH_WEIGH_DEVICE_NOT_READY');end if;
  sender(d,d.SENDER_ID);
  if purpose_value='FINAL_GROSS'then
   if j.has('resource_session_id')or j.has('case_line_id')or j.has('scan_source_cell')or j.has('scan_product')then raise_application_error(-20886,'WH_WEIGH_FINAL_EXACT_FIELDS_REQUIRED');end if;
   if ct.LEGACY_SBORKA_PALLET_ID is null or ct.STATUS not in('WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP')or nvl(ct.PICKED_QTY,0)<=0 then
    raise_application_error(-20886,'WH_WEIGH_FINAL_CLOSED_BOUND_CASE_REQUIRED');end if;
   select PALLET_UID into identifier from RRL_SBORKA_PALLETS where ID=ct.LEGACY_SBORKA_PALLET_ID;
   s.put('assembly_session_id',final_authority(ct.CASE_PICK_TASK_ID,d.DEVICE_ID,p_actor));
   s.put('qc_identifier',identifier);
   qc:=json_object_t.parse(RRL_STOCK_QC_GATE.status_json(identifier));
   if j.get_string('expected_composition_signature')is null or qc.get_string('composition_signature')is null
    or qc.get_string('composition_signature')!=j.get_string('expected_composition_signature')then raise_application_error(-20886,'WH_WEIGH_COMPOSITION_CHANGED');end if;
   if j.get_string('tare_capture_key')is null then raise_application_error(-20886,'WH_WEIGH_MEASURED_TARE_REQUIRED');end if;
   select *into tare from RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=json_value(p_source,'$.tare_capture_key' returning varchar2(512));
   if tare.CAPTURE_PURPOSE!='EMPTY_TARE'or tare.CASE_PICK_TASK_ID!=ct.CASE_PICK_TASK_ID or tare.CARRIER_IDENTIFIER!=ct.SSCC
    or tare.PALLET_TYPE_ID!=ct.PALLET_TYPE_ID or tare.DEVICE_ID!=d.DEVICE_ID or tare.WARE_ID!=d.WARE_ID or tare.POST_CELL!=d.POST_CELL
    or tare.DEVICE_MODE!=d.DEVICE_MODE or tare.MEASUREMENT_BASIS!='GROSS'or tare.MEASURED_AT<systimestamp-numtodsinterval(24,'HOUR')then
    raise_application_error(-20886,'WH_WEIGH_CURRENT_SAME_CASE_TARE_REQUIRED');end if;
   s.put('composition_signature',qc.get_string('composition_signature'));s.put('composition_signature_version',qc.get_number('composition_signature_version'));
  else
   permission_value:=case when purpose_value='PICK'then'case_pick_execute'else'case_pick_execute'end;
   RRL_CASE_TASK_ACCESS.assert_scope(ct.CASE_PICK_TASK_ID,p_actor,permission_value);
   if ct.ASSIGNED_TO is not null and ct.ASSIGNED_TO!=p_actor then raise_application_error(-20882,'WH_WEIGH_ASSIGNED_OPERATOR_REQUIRED');end if;
   if purpose_value='PICK'then
    if ct.ASSIGNED_TO is null or ct.STATUS not in('IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT')then raise_application_error(-20882,'WH_WEIGH_ACTIVE_OWN_PICK_REQUIRED');end if;
    if j.get_number('case_line_id')is null or j.get_string('scan_source_cell')is null or j.get_string('scan_product')is null then raise_application_error(-20886,'WH_WEIGH_PICK_SCANS_REQUIRED');end if;
    select *into ln from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=json_value(p_source,'$.case_line_id' returning number)and CASE_PICK_TASK_ID=ct.CASE_PICK_TASK_ID;
    if ln.CELL_CODE!=j.get_string('scan_source_cell')or ln.CELL_CODE is null then raise_application_error(-20886,'WH_WEIGH_SOURCE_SCAN_CHANGED');end if;
    select count(*)into n from RRL_ARTICULS where ACTICUL=ln.ARTICUL and TYPE_W in(2,3,5,6,7);
    if n!=1 then raise_application_error(-20886,'WH_WEIGH_WEIGHTED_SKU_REQUIRED');end if;
    s.put('line_article',ln.ARTICUL);s.put('line_source',ln.CELL_CODE);s.put('line_status',ln.STATUS);
    s.put('line_planned_qty',ln.PLANNED_QTY);s.put('line_picked_qty',ln.PICKED_QTY);
   else
    if j.has('case_line_id')or j.has('scan_source_cell')or j.has('scan_product')then raise_application_error(-20886,'WH_WEIGH_EMPTY_EXACT_FIELDS_REQUIRED');end if;
    if ct.STATUS not in('NEW','ASSIGNED','IN_PROGRESS')or nvl(ct.PICKED_QTY,0)!=0 then raise_application_error(-20886,'WH_WEIGH_EMPTY_BEFORE_FIRST_PICK_REQUIRED');end if;
   end if;
   resource_context:=json_object_t.parse(RRL_CASE_RESOURCE_POLICY.context_json(ct.CASE_PICK_TASK_ID,'REPORT',p_actor,null,j.get_number('resource_session_id'),null));
   s.put('resource_context',resource_context);
   if j.has('tare_capture_key')or j.has('expected_composition_signature')then raise_application_error(-20886,'WH_WEIGH_FINAL_FIELDS_FORBIDDEN');end if;
  end if;
  if purpose_value!='PICK'and(typ.FINAL_WEIGHT_REQUIRED!=1 or upper(typ.LOAD_UNIT_CLASS)!='CONTAINER'or d.MEASUREMENT_BASIS!='GROSS')then
   raise_application_error(-20886,'WH_WEIGH_SMALL_CONTAINER_GROSS_REQUIRED');end if;
  RRL_CASE_SSCC_API.assert_ready(ct.CASE_PICK_TASK_ID);
  s.put('warehouse_id',ct.WARE_ID);s.put('content_version',ct.CONTENT_VERSION);s.put('status',ct.STATUS);s.put('assigned_to',ct.ASSIGNED_TO);
  s.put('carrier',ct.SSCC);s.put('type_id',ct.PALLET_TYPE_ID);s.put('type_version',typ.TYPE_VERSION);
  s.put('resource_session_id',ct.RESOURCE_SESSION_ID);s.put('resource_id',ct.ASSIGNED_RESOURCE_ID);s.put('equipment_id',ct.EQUIPMENT_ID);
  s.put('device_policy_version',d.POLICY_VERSION);s.put('calibration_ref',d.CALIBRATION_REF);s.put('sender_id',d.SENDER_ID);
  s.put('post_cell',d.POST_CELL);s.put('device_mode',d.DEVICE_MODE);s.put('basis',d.MEASUREMENT_BASIS);
  return s;
 end;
 function context_json(j json_object_t,s json_object_t)return json_object_t is c json_object_t:=json_object_t();keys json_key_list:=j.get_keys;
 begin
  for k in 1..keys.count loop
   if keys(k)not in('request_id','resource_session_id','expected_composition_signature','purpose')then c.put(keys(k),j.get(keys(k)));end if;
  end loop;
  if j.get_string('purpose')!='PICK'then c.put('purpose',j.get_string('purpose'));end if;
  c.put('post_cell',s.get_string('post_cell'));c.put('device_policy_version',s.get_number('device_policy_version'));c.put('calibration_ref',s.get_string('calibration_ref'));
  c.put('unit','KG');c.put('basis',s.get_string('basis'));c.put('preset_tare_kg','0');return c;
 end;
 procedure assert_current(r RRL_WH_WEIGH_REQUEST%rowtype)is s json_object_t;n number;
 begin
  select count(*)into n from RRL_WH_WEIGH_REQUEST newer where newer.DEVICE_ID=r.DEVICE_ID and newer.REQUEST_ID!=r.REQUEST_ID
   and newer.CREATED_AT>=r.CREATED_AT
   and not exists(select 1 from RRL_WH_WEIGH_CLAIM cl join RRL_WH_SCALE_CAPTURE c on c.DEVICE_ID=cl.DEVICE_ID and c.CAPTURE_ID=cl.CLAIM_ID where cl.REQUEST_ID=r.REQUEST_ID);
  if n>0 then raise_application_error(-20886,'WH_WEIGH_PENDING_INTENT_SUPERSEDED');end if;
  s:=snapshot(r.SOURCE_JSON,r.REQUESTED_BY);
  if digest(s.to_clob)!=r.SNAPSHOT_SHA256 then raise_application_error(-20886,'WH_WEIGH_SOURCE_ASSIGNMENT_OR_POLICY_CHANGED_RECREATE_REQUEST');end if;
 end;
 function state_json(r RRL_WH_WEIGH_REQUEST%rowtype)return json_object_t is
  o json_object_t:=json_object_t();state_value varchar2(20):='REQUESTED';context_value varchar2(10):='CURRENT';reason_value varchar2(200);key_value varchar2(64);claim_value varchar2(100);
  n number;c RRL_WH_SCALE_CAPTURE%rowtype;cl RRL_WH_WEIGH_CLAIM%rowtype;expected json_object_t:=json_object_t.parse(r.CAPTURE_CONTEXT);
 begin
  begin assert_current(r);exception when others then
   if sqlcode in(-20881,-20882,-20884,-20886,100)then context_value:='STALE';reason_value:='CURRENT_SOURCE_ASSIGNMENT_OR_POLICY_CHANGED';else raise;end if;
  end;
  select count(*)into n from RRL_WH_SCALE_CAPTURE a join RRL_WH_WEIGH_CLAIM lease on lease.CLAIM_ID=a.CAPTURE_ID and lease.DEVICE_ID=a.DEVICE_ID where lease.REQUEST_ID=r.REQUEST_ID;
  if n>1 then state_value:='STALE';reason_value:='MULTIPLE_CAPTURE_BINDINGS';
  elsif n=1 then
   select a.*into c from RRL_WH_SCALE_CAPTURE a join RRL_WH_WEIGH_CLAIM lease on lease.CLAIM_ID=a.CAPTURE_ID and lease.DEVICE_ID=a.DEVICE_ID where lease.REQUEST_ID=r.REQUEST_ID;
   select *into cl from RRL_WH_WEIGH_CLAIM where CLAIM_ID=c.CAPTURE_ID;
   if c.CASE_PICK_TASK_ID!=r.CASE_PICK_TASK_ID or nvl(c.CAPTURE_PURPOSE,'PICK')!=r.PURPOSE or c.RECORDED_BY!=cl.CLAIMED_BY
    or c.CASE_CONTENT_VERSION!=expected.get_number('expected_content_version')or c.CARRIER_IDENTIFIER!=expected.get_string('scan_container')
    or c.DEVICE_POLICY_VERSION!=expected.get_number('device_policy_version')or c.CALIBRATION_REF!=expected.get_string('calibration_ref')
    or c.MEASURED_AT<cl.CREATED_AT or c.MEASURED_AT>cl.EXPIRES_AT or c.RECEIVED_AT<cl.CREATED_AT or c.RECEIVED_AT>cl.EXPIRES_AT then
    state_value:='STALE';reason_value:='CAPTURE_BINDING_MISMATCH';
   else state_value:='CAPTURED';key_value:=c.CAPTURE_KEY;claim_value:=c.CAPTURE_ID;end if;
  elsif context_value='STALE'then state_value:='STALE';
  elsif r.EXPIRES_AT<systimestamp then state_value:='EXPIRED';reason_value:='REQUEST_WINDOW_ELAPSED';
  else
   for lease in(select *from RRL_WH_WEIGH_CLAIM where REQUEST_ID=r.REQUEST_ID and EXPIRES_AT>=systimestamp order by CREATED_AT desc fetch first 1 row only)loop
    state_value:='CLAIMED';claim_value:=lease.CLAIM_ID;
   end loop;
  end if;
  o.put('request_id',r.REQUEST_ID);o.put('device_id',r.DEVICE_ID);o.put('case_task_id',r.CASE_PICK_TASK_ID);o.put('purpose',r.PURPOSE);
  o.put('state',state_value);o.put('current_context',context_value);o.put('admissible',state_value='CAPTURED'and context_value='CURRENT');
  o.put('reason',reason_value);o.put('capture_key',key_value);o.put('claim_id',claim_value);
  o.put('created_at',to_char(r.CREATED_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));
  o.put('expires_at',to_char(r.EXPIRES_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));o.put('stock_posted',false);return o;
 end;
 procedure request_capture(p_source clob,p_actor varchar2,p_result out clob)is
  j json_object_t;s json_object_t;result_json json_object_t;r RRL_WH_WEIGH_REQUEST%rowtype;d RRL_WH_SCALE_DEVICE%rowtype;n number;now_at timestamp with time zone;
 begin
  outside_stock;
  if p_source is null or dbms_lob.getlength(p_source)>8000 then raise_application_error(-20881,'WH_WEIGH_REQUEST_BOUND_8000');end if;
  j:=json_object_t.parse(p_source);case_lock(j.get_number('case_task_id'));
  select *into d from RRL_WH_SCALE_DEVICE where DEVICE_ID=json_value(p_source,'$.device_id' returning varchar2(512))for update wait 2;
  select count(*)into n from RRL_WH_WEIGH_REQUEST where REQUEST_ID=json_value(p_source,'$.request_id' returning varchar2(512));
  if n=1 then
   select *into r from RRL_WH_WEIGH_REQUEST where REQUEST_ID=json_value(p_source,'$.request_id' returning varchar2(512));
   if r.REQUESTED_BY!=p_actor then raise_application_error(-20882,'WH_WEIGH_ORIGINAL_ACTOR_REQUIRED');end if;
   if dbms_lob.compare(r.SOURCE_JSON,p_source)!=0 then raise_application_error(-20886,'WH_WEIGH_REQUEST_PAYLOAD_CONFLICT');end if;
   request_status(r.REQUEST_ID,p_actor,p_result);return;
  end if;
  s:=snapshot(p_source,p_actor);device_free(d.DEVICE_ID,j.get_number('case_task_id'),j.get_string('purpose'),p_actor);
  for previous in(select *from RRL_WH_WEIGH_REQUEST where DEVICE_ID=d.DEVICE_ID and EXPIRES_AT>=systimestamp order by CREATED_AT desc)loop
   result_json:=state_json(previous);
   if result_json.get_string('state')in('REQUESTED','CLAIMED')then raise_application_error(-20886,'WH_WEIGH_DEVICE_BUSY');end if;
  end loop;
  now_at:=systimestamp;r.REQUEST_ID:=j.get_string('request_id');r.DEVICE_ID:=d.DEVICE_ID;r.CASE_PICK_TASK_ID:=j.get_number('case_task_id');
  r.PURPOSE:=j.get_string('purpose');r.REQUESTED_BY:=p_actor;r.SOURCE_JSON:=p_source;r.SNAPSHOT_JSON:=s.to_clob;r.SNAPSHOT_SHA256:=digest(r.SNAPSHOT_JSON);
  r.CAPTURE_CONTEXT:=context_json(j,s).to_clob;r.CREATED_AT:=now_at;r.EXPIRES_AT:=now_at+interval '120' second;
  begin_write(r.REQUEST_ID,'REQUEST');insert into RRL_WH_WEIGH_REQUEST values r;end_write;
  p_result:=state_json(r).to_clob;
 exception when no_data_found then end_write;raise_application_error(-20884,'WH_WEIGH_SOURCE_NOT_FOUND');when others then end_write;raise;
 end;
 procedure request_status(p_request varchar2,p_actor varchar2,p_result out clob)is r RRL_WH_WEIGH_REQUEST%rowtype;s json_object_t;n number;actual_ware number;begin
  select *into r from RRL_WH_WEIGH_REQUEST where REQUEST_ID=p_request;
  if r.REQUESTED_BY!=p_actor and RRL_HAS_WRIGHT(p_actor,'warehouse_settings_edit')!=1 then raise_application_error(-20882,'WH_WEIGH_REQUEST_OWNER_REQUIRED');end if;
  -- Authorize the current reader without demanding that the frozen source still be fresh.
  if r.PURPOSE='FINAL_GROSS'then
   s:=json_object_t.parse(r.SNAPSHOT_JSON);
   select WARE_ID into actual_ware from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=r.CASE_PICK_TASK_ID;
   if actual_ware!=s.get_number('warehouse_id')then raise_application_error(-20882,'WH_WEIGH_ORIGINAL_CASE_WARE_CHANGED');end if;
   select count(*)into n from RRL_ASSEMBLY_SESSION where SESSION_ID=json_value(r.SNAPSHOT_JSON,'$.assembly_session_id' returning varchar2(512))
    and CASE_PICK_TASK_ID=r.CASE_PICK_TASK_ID and DEVICE_ID=r.DEVICE_ID and(OPERATOR_ID=p_actor or RRL_HAS_WRIGHT(p_actor,'case_pick_manage')=1);
   if n=1 then RRL_CASE_TASK_ACCESS.assert_scope(r.CASE_PICK_TASK_ID,p_actor,'case_pick_execute');
   else RRL_OUTGOING_QC_ACCESS.assert_identifier(s.get_string('qc_identifier'),p_actor);end if;
  else RRL_CASE_TASK_ACCESS.assert_scope(r.CASE_PICK_TASK_ID,p_actor,case when r.PURPOSE='PICK'then'case_pick_execute'else'case_pick_execute'end);end if;
  p_result:=state_json(r).to_clob;
 exception when no_data_found then raise_application_error(-20884,'WH_WEIGH_REQUEST_NOT_FOUND');end;
 procedure assert_device_available(p_device varchar2)is s json_object_t;begin
  for pending in(select *from RRL_WH_WEIGH_REQUEST where DEVICE_ID=p_device and EXPIRES_AT>=systimestamp)loop
   s:=state_json(pending);
   if s.get_string('state')in('REQUESTED','CLAIMED')then raise_application_error(-20886,'ASSEMBLY_WAREHOUSE_WEIGH_REQUEST_BUSY');end if;
  end loop;
 end;
 procedure devices(p_task number,p_purpose varchar2,p_actor varchar2,p_result out clob)is
  ct RRL_CASE_PICK_TASK%rowtype;o json_object_t:=json_object_t();items json_array_t:=json_array_t();d json_object_t;identifier varchar2(150);reason_value varchar2(100);n number;
 begin
  if p_purpose is null or p_purpose not in('PICK','EMPTY_TARE','FINAL_GROSS')then raise_application_error(-20886,'WH_WEIGH_SUPPORTED_PURPOSE_REQUIRED');end if;
  select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  if p_purpose='FINAL_GROSS'then
   begin
    select PALLET_UID into identifier from RRL_SBORKA_PALLETS where ID=ct.LEGACY_SBORKA_PALLET_ID;
    RRL_OUTGOING_QC_ACCESS.assert_identifier(identifier,p_actor);
   exception when others then
    if sqlcode!=-20882 then raise;end if;
    select count(*)into n from RRL_ASSEMBLY_SESSION where CASE_PICK_TASK_ID=p_task and OPERATOR_ID=p_actor and STATE='OPEN'and EXPIRES_AT>=systimestamp;
    if n=0 then raise;end if;
    RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,'case_pick_execute');
    if ct.ASSIGNED_TO is null or ct.ASSIGNED_TO!=p_actor then raise_application_error(-20882,'WH_WEIGH_ASSIGNED_OPERATOR_REQUIRED');end if;
   end;
  else
   RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,case when p_purpose='PICK'then'case_pick_execute'else'case_pick_execute'end);
   if(ct.ASSIGNED_TO is not null and ct.ASSIGNED_TO!=p_actor)or(p_purpose='PICK'and ct.ASSIGNED_TO is null)then
    raise_application_error(-20882,'WH_WEIGH_ASSIGNED_OPERATOR_REQUIRED');end if;
  end if;
  for device in(select *from RRL_WH_SCALE_DEVICE where WARE_ID=ct.WARE_ID order by DEVICE_ID fetch first 50 rows only)loop
   reason_value:=null;
   if device.ACTIVE_FLAG!=1 then reason_value:='INACTIVE';
   elsif device.CALIBRATED_UNTIL<systimestamp then reason_value:='CALIBRATION_EXPIRED';
   elsif p_purpose!='PICK'and device.MEASUREMENT_BASIS!='GROSS'then reason_value:='GROSS_REQUIRED';end if;
   if reason_value is null then
    begin sender(device,device.SENDER_ID);exception when others then if sqlcode=-20882 then reason_value:='SENDER_UNAVAILABLE';else raise;end if;end;
   end if;
   begin
    if p_purpose='FINAL_GROSS'then declare sid varchar2(100);begin sid:=final_authority(p_task,device.DEVICE_ID,p_actor);end;end if;
    device_free(device.DEVICE_ID,p_task,p_purpose,p_actor);
   exception when others then if sqlcode in(-20882,-20886)then reason_value:='ASSEMBLY_BUSY_OR_FINAL_AUTHORITY_UNAVAILABLE';else raise;end if;end;
   if reason_value is null then
    for pending in(select *from RRL_WH_WEIGH_REQUEST where DEVICE_ID=device.DEVICE_ID and EXPIRES_AT>=systimestamp)loop
     d:=state_json(pending);if d.get_string('state')in('REQUESTED','CLAIMED')then reason_value:='REQUEST_BUSY';exit;end if;
    end loop;
   end if;
   d:=json_object_t();d.put('device_id',device.DEVICE_ID);d.put('warehouse_id',device.WARE_ID);d.put('post_cell',device.POST_CELL);
   d.put('active',device.ACTIVE_FLAG=1);d.put('device_mode',device.DEVICE_MODE);d.put('basis',device.MEASUREMENT_BASIS);
   d.put('policy_version',device.POLICY_VERSION);d.put('calibration_ref',device.CALIBRATION_REF);
   d.put('calibrated_until',to_char(device.CALIBRATED_UNTIL at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));
   d.put('capacity_kg',RRL_STOCK_PLAN_HELPER.decimal_text(device.CAPACITY_KG));d.put('resolution_kg',RRL_STOCK_PLAN_HELPER.decimal_text(device.RESOLUTION_KG));
   d.put('ready',reason_value is null);d.put('reason',reason_value);d.put('connectivity','UNKNOWN');items.append(d);
  end loop;
  o.put('items',items);o.put('limit',50);p_result:=o.to_clob;
 end;
 procedure pending_requests(p_device varchar2,p_actor varchar2,p_result out clob)is
  d RRL_WH_SCALE_DEVICE%rowtype;o json_object_t:=json_object_t();items json_array_t:=json_array_t();s json_object_t;
 begin
  select *into d from RRL_WH_SCALE_DEVICE where DEVICE_ID=p_device;sender(d,p_actor);
  for r in(select *from RRL_WH_WEIGH_REQUEST where DEVICE_ID=p_device and EXPIRES_AT>=systimestamp order by CREATED_AT desc,REQUEST_ID desc fetch first 20 rows only)loop
   s:=state_json(r);if s.get_string('state')in('REQUESTED','CLAIMED')then items.append(s);end if;
  end loop;
  o.put('device_id',p_device);o.put('items',items);o.put('limit',20);o.put('connectivity','UNKNOWN');p_result:=o.to_clob;
 end;
 function claim_json(cl RRL_WH_WEIGH_CLAIM%rowtype,r RRL_WH_WEIGH_REQUEST%rowtype)return json_object_t is
  o json_object_t:=state_json(r);c json_object_t:=json_object_t.parse(r.CAPTURE_CONTEXT);
 begin
  c.put('capture_id',cl.CLAIM_ID);o.put('capture_context',c);o.put('claim_id',cl.CLAIM_ID);
  o.put('claim_expires_at',to_char(cl.EXPIRES_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));
  o.put('claim_active',cl.EXPIRES_AT>=systimestamp and o.get_string('state')in('REQUESTED','CLAIMED'));return o;
 end;
 procedure claim_request(p_request varchar2,p_source clob,p_actor varchar2,p_result out clob)is
  j json_object_t;r RRL_WH_WEIGH_REQUEST%rowtype;cl RRL_WH_WEIGH_CLAIM%rowtype;d RRL_WH_SCALE_DEVICE%rowtype;s json_object_t;n number;
 begin
  outside_stock;if p_source is null or dbms_lob.getlength(p_source)>1000 then raise_application_error(-20881,'WH_WEIGH_CLAIM_BOUND_1000');end if;
  j:=json_object_t.parse(p_source);
  if j.get_size!=2 or j.get_string('claim_id')is null or j.get_string('device_id')is null then raise_application_error(-20886,'WH_WEIGH_CLAIM_EXACT_FIELDS_REQUIRED');end if;
  select *into r from RRL_WH_WEIGH_REQUEST where REQUEST_ID=p_request;case_lock(r.CASE_PICK_TASK_ID);
  select *into d from RRL_WH_SCALE_DEVICE where DEVICE_ID=r.DEVICE_ID for update wait 2;sender(d,p_actor);
  select *into r from RRL_WH_WEIGH_REQUEST where REQUEST_ID=p_request for update wait 2;
  if j.get_string('device_id')!=d.DEVICE_ID then raise_application_error(-20882,'WH_WEIGH_CLAIM_DEVICE_MISMATCH');end if;
  select count(*)into n from RRL_WH_WEIGH_CLAIM where CLAIM_ID=json_value(p_source,'$.claim_id' returning varchar2(512));
  if n=1 then
   select *into cl from RRL_WH_WEIGH_CLAIM where CLAIM_ID=json_value(p_source,'$.claim_id' returning varchar2(512));
   if cl.REQUEST_ID!=r.REQUEST_ID or cl.CLAIMED_BY!=p_actor or dbms_lob.compare(cl.SOURCE_JSON,p_source)!=0 then raise_application_error(-20886,'WH_WEIGH_CLAIM_PAYLOAD_CONFLICT');end if;
   p_result:=claim_json(cl,r).to_clob;return;
  end if;
  device_free(d.DEVICE_ID,r.CASE_PICK_TASK_ID,r.PURPOSE,r.REQUESTED_BY);assert_current(r);s:=state_json(r);
  if s.get_string('state')!='REQUESTED'then raise_application_error(-20886,'WH_WEIGH_REQUEST_NOT_CLAIMABLE');end if;
  select count(*)into n from RRL_WH_WEIGH_CLAIM where REQUEST_ID=p_request;
  if n>=5 then raise_application_error(-20886,'WH_WEIGH_CLAIM_ATTEMPT_BOUND_5');end if;
  select count(*)into n from RRL_WH_SCALE_CAPTURE where DEVICE_ID=d.DEVICE_ID and CAPTURE_ID=json_value(p_source,'$.claim_id' returning varchar2(512));
  if n!=0 then raise_application_error(-20886,'WH_WEIGH_CLAIM_CAPTURE_ID_ALREADY_USED');end if;
  cl.CLAIM_ID:=j.get_string('claim_id');cl.REQUEST_ID:=p_request;cl.DEVICE_ID:=d.DEVICE_ID;cl.CLAIMED_BY:=p_actor;cl.SOURCE_JSON:=p_source;
  cl.CREATED_AT:=systimestamp;cl.EXPIRES_AT:=least(r.EXPIRES_AT,cl.CREATED_AT+interval '30' second);
  begin_write(cl.CLAIM_ID,'CLAIM');insert into RRL_WH_WEIGH_CLAIM values cl;end_write;
  p_result:=claim_json(cl,r).to_clob;
 exception when no_data_found then end_write;raise_application_error(-20884,'WH_WEIGH_REQUEST_NOT_FOUND');when others then end_write;raise;
 end;
 procedure before_capture(p_source clob,p_actor varchar2)is
  j json_object_t:=json_object_t.parse(p_source);r RRL_WH_WEIGH_REQUEST%rowtype;cl RRL_WH_WEIGH_CLAIM%rowtype;d RRL_WH_SCALE_DEVICE%rowtype;n number;
 begin
  clear_capture_context;
  lock table RRL_ACCESS_REV in share mode wait 2;
  select count(*)into n from RRL_WH_WEIGH_CLAIM where CLAIM_ID=json_value(p_source,'$.capture_id' returning varchar2(512))and DEVICE_ID=json_value(p_source,'$.device_id' returning varchar2(512));
  if n=0 then return;end if;
  -- Fast immutable ACK path need not obtain CASE locks or revive the original operator.
  select count(*)into n from RRL_WH_SCALE_CAPTURE where DEVICE_ID=json_value(p_source,'$.device_id' returning varchar2(512))and CAPTURE_ID=json_value(p_source,'$.capture_id' returning varchar2(512));
  if n=1 then return;end if;
  select *into cl from RRL_WH_WEIGH_CLAIM where CLAIM_ID=json_value(p_source,'$.capture_id' returning varchar2(512));
  select *into r from RRL_WH_WEIGH_REQUEST where REQUEST_ID=cl.REQUEST_ID;
  case_lock(r.CASE_PICK_TASK_ID);
  select *into d from RRL_WH_SCALE_DEVICE where DEVICE_ID=cl.DEVICE_ID;sender(d,p_actor);
  g_capture_id:=cl.CLAIM_ID;g_capture_tx:=dbms_transaction.local_transaction_id(true);
 end;
 procedure validate_first_capture(p_source clob,p_actor varchar2)is
  j json_object_t:=json_object_t.parse(p_source);r RRL_WH_WEIGH_REQUEST%rowtype;cl RRL_WH_WEIGH_CLAIM%rowtype;
  expected json_object_t;keys json_key_list;n number;measured timestamp with time zone;samples json_array_t;last_sample json_object_t;first_at timestamp with time zone;
 begin
  select count(*)into n from RRL_WH_WEIGH_CLAIM where CLAIM_ID=json_value(p_source,'$.capture_id' returning varchar2(512))and DEVICE_ID=json_value(p_source,'$.device_id' returning varchar2(512));
  if n=0 then
   for pending in(select *from RRL_WH_WEIGH_REQUEST where DEVICE_ID=json_value(p_source,'$.device_id' returning varchar2(512))and EXPIRES_AT>=systimestamp)loop
    expected:=state_json(pending);
    if expected.get_string('state')in('REQUESTED','CLAIMED')then raise_application_error(-20886,'WH_WEIGH_ACTIVE_REQUEST_CLAIM_REQUIRED');end if;
   end loop;return;
  end if;
  if g_capture_id is null or g_capture_id!=j.get_string('capture_id')or g_capture_tx is null or g_capture_tx!=dbms_transaction.local_transaction_id(false)then
   raise_application_error(-20882,'WH_WEIGH_CAPTURE_CASE_LOCK_REQUIRED');end if;
  select *into cl from RRL_WH_WEIGH_CLAIM where CLAIM_ID=g_capture_id;
  select *into r from RRL_WH_WEIGH_REQUEST where REQUEST_ID=cl.REQUEST_ID for update wait 2;
  if cl.CLAIMED_BY!=p_actor then raise_application_error(-20882,'WH_WEIGH_ORIGINAL_CLAIM_SENDER_REQUIRED');end if;
  if cl.EXPIRES_AT<systimestamp or r.EXPIRES_AT<systimestamp then raise_application_error(-20886,'WH_WEIGH_LATE_FIRST_CAPTURE_REJECTED');end if;
  assert_current(r);device_free(r.DEVICE_ID,r.CASE_PICK_TASK_ID,r.PURPOSE,r.REQUESTED_BY);
  expected:=json_object_t.parse(r.CAPTURE_CONTEXT);expected.put('capture_id',cl.CLAIM_ID);keys:=expected.get_keys;
  for k in 1..keys.count loop
   if not j.has(keys(k))or j.get(keys(k)).to_string!=expected.get(keys(k)).to_string then raise_application_error(-20886,'WH_WEIGH_CAPTURE_INTENT_MISMATCH');end if;
  end loop;
  if r.PURPOSE='PICK'and j.has('purpose')then raise_application_error(-20886,'WH_WEIGH_PICK_PURPOSE_MISMATCH');end if;
  measured:=RRL_SCALE_PACKET_READ.utc_stamp(j.get_string('measured_at'));samples:=j.get_array('samples');
  last_sample:=treat(samples.get(samples.get_size-1)as json_object_t);
  first_at:=measured-numtodsinterval(last_sample.get_number('offset_ms')/1000,'SECOND');
  -- The prior empty-platform zero check keeps the existing packet validator's freshness rule.
  -- All observations themselves must belong to this claim, not a cached pre-claim window.
  if measured<cl.CREATED_AT or measured>cl.EXPIRES_AT or first_at<cl.CREATED_AT then raise_application_error(-20886,'WH_WEIGH_OBSERVATION_OUTSIDE_CLAIM');end if;
  select count(*)into n from RRL_WH_SCALE_CAPTURE a join RRL_WH_WEIGH_CLAIM old on old.CLAIM_ID=a.CAPTURE_ID and old.DEVICE_ID=a.DEVICE_ID where old.REQUEST_ID=r.REQUEST_ID;
  if n!=0 then raise_application_error(-20886,'WH_WEIGH_REQUEST_ALREADY_CAPTURED');end if;
 end;
 procedure assert_archived_sender(p_source clob,p_actor varchar2)is j json_object_t:=json_object_t.parse(p_source);n number;
 begin
  select count(*)into n from RRL_WH_WEIGH_CLAIM where CLAIM_ID=json_value(p_source,'$.capture_id' returning varchar2(512))and DEVICE_ID=json_value(p_source,'$.device_id' returning varchar2(512))and CLAIMED_BY!=p_actor;
  if n!=0 then raise_application_error(-20882,'WH_WEIGH_ORIGINAL_ARCHIVE_SENDER_REQUIRED');end if;
 end;
 procedure validate_archived(p_source clob,p_actor varchar2)is
  j json_object_t:=json_object_t.parse(p_source);cl RRL_WH_WEIGH_CLAIM%rowtype;r RRL_WH_WEIGH_REQUEST%rowtype;c RRL_WH_SCALE_CAPTURE%rowtype;expected json_object_t;n number;
 begin
  select count(*)into n from RRL_WH_WEIGH_CLAIM where CLAIM_ID=json_value(p_source,'$.capture_id' returning varchar2(512))and DEVICE_ID=json_value(p_source,'$.device_id' returning varchar2(512));
  if n=0 then return;end if;
  select *into cl from RRL_WH_WEIGH_CLAIM where CLAIM_ID=json_value(p_source,'$.capture_id' returning varchar2(512));
  select *into r from RRL_WH_WEIGH_REQUEST where REQUEST_ID=cl.REQUEST_ID;
  assert_current(r);expected:=json_object_t.parse(r.CAPTURE_CONTEXT);
  select *into c from RRL_WH_SCALE_CAPTURE where DEVICE_ID=cl.DEVICE_ID and CAPTURE_ID=cl.CLAIM_ID;
  if c.CASE_PICK_TASK_ID!=r.CASE_PICK_TASK_ID or nvl(c.CAPTURE_PURPOSE,'PICK')!=r.PURPOSE or c.RECORDED_BY!=cl.CLAIMED_BY or c.RECORDED_BY!=p_actor
   or c.CASE_CONTENT_VERSION!=expected.get_number('expected_content_version')or c.CARRIER_IDENTIFIER!=expected.get_string('scan_container')
   or c.DEVICE_POLICY_VERSION!=expected.get_number('device_policy_version')or c.CALIBRATION_REF!=expected.get_string('calibration_ref')
   or c.RECEIVED_AT<cl.CREATED_AT or c.RECEIVED_AT>cl.EXPIRES_AT or c.SOURCE_SHA256!=digest(p_source)or dbms_lob.compare(c.SOURCE_JSON,p_source)!=0 then
   raise_application_error(-20886,'WH_WEIGH_ARCHIVE_BINDING_MISMATCH');end if;
  if r.PURPOSE='FINAL_GROSS'then
   j:=json_object_t.parse(r.SOURCE_JSON);
   if c.COMPOSITION_SIGNATURE is null or c.COMPOSITION_SIGNATURE!=j.get_string('expected_composition_signature')
    or c.TARE_CAPTURE_KEY is null or c.TARE_CAPTURE_KEY!=j.get_string('tare_capture_key')then raise_application_error(-20886,'WH_WEIGH_FINAL_ARCHIVE_BINDING_MISMATCH');end if;
  end if;
 end;
end;
/
