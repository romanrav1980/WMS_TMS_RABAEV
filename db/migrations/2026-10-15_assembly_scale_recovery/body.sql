create or replace package body RRL_ASSEMBLY_RECOVERY_API as
 procedure permit(p_id varchar2 default null)is begin
  dbms_session.set_context('RRL_ASM_RECOVERY_CTX','TX_ID',dbms_transaction.local_transaction_id(true));
  dbms_session.set_context('RRL_ASM_RECOVERY_CTX','APPLY_ID',p_id);
 end;
 procedure finish_change is begin
  dbms_session.clear_context('RRL_ASM_RECOVERY_CTX',null);RRL_STOCK_LOCK_API.clear_plan;
 end;
 function write_allowed return number is tx varchar2(100):=sys_context('RRL_ASM_RECOVERY_CTX','TX_ID');begin
  if tx is not null and tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;
 end;
 procedure lock_step(p_step varchar2,p_actor nvarchar2,p_permission varchar2)is
  t RRL_ASSEMBLY_STEP%rowtype;s RRL_ASSEMBLY_SESSION%rowtype;ct RRL_CASE_PICK_TASK%rowtype;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();n number;release_state varchar2(20);begin
  if p_actor is null or p_permission not in('case_pick_execute','case_pick_manage')then raise_application_error(-20882,'ASSEMBLY_RECOVERY_ACTOR_REQUIRED');end if;
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,p_permission)=1;
  if n!=1 then raise_application_error(-20882,'ASSEMBLY_RECOVERY_CURRENT_PERMISSION_REQUIRED');end if;
  select *into t from RRL_ASSEMBLY_STEP where STEP_ID=p_step;select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=t.SESSION_ID;
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null then raise_application_error(-20886,'ASSEMBLY_RECOVERY_OUTSIDE_STOCK_REQUIRED');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE',6);
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',t.OPERATION_ID);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA');
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(s.CASE_PICK_TASK_ID));
  RRL_STOCK_LOCK_API.begin_plan;lock table RRL_ACCESS_REV in share mode wait 2;
  RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  select STATE into release_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if release_state is null or release_state not in('PREPARED','ACTIVE')then raise_application_error(-20860,'ASSEMBLY_RECOVERY_RELEASE_CLOSED');end if;
  select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=s.CASE_PICK_TASK_ID for update;
  select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=t.SESSION_ID for update;
  select *into t from RRL_ASSEMBLY_STEP where STEP_ID=p_step for update;
  RRL_CASE_TASK_ACCESS.assert_scope(s.CASE_PICK_TASK_ID,p_actor,p_permission);
  RRL_CASE_TASK_ACCESS.assert_scope(s.CASE_PICK_TASK_ID,s.OPERATOR_ID,'case_pick_execute');
  if ct.ASSIGNED_TO is null or ct.ASSIGNED_TO!=s.OPERATOR_ID or(p_permission='case_pick_execute'and p_actor!=s.OPERATOR_ID)then raise_application_error(-20882,'ASSEMBLY_RECOVERY_CURRENT_ASSIGNED_OPERATOR_REQUIRED');end if;permit;
 end;
 procedure unposted(p_step varchar2)is t RRL_ASSEMBLY_STEP%rowtype;n number;begin
  select *into t from RRL_ASSEMBLY_STEP where STEP_ID=p_step;
  RRL_STOCK_LOCK_API.assert_held(10,RRL_STOCK_LOCK_API.resource_key('OP',t.OPERATION_ID));
  select count(*)into n from RRL_ASSEMBLY_STEP_USE where STEP_ID=p_step;
  if n!=0 or t.STATE is null or t.STATE not in('WAITING_BEFORE','ARMED','READY','DISCREPANCY')then raise_application_error(-20886,'ASSEMBLY_RECOVERY_UNPOSTED_STEP_REQUIRED');end if;
  select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=t.OPERATION_ID;
  if n!=0 then raise_application_error(-20886,'ASSEMBLY_RECOVERY_OPERATION_OUTCOME_REQUIRES_REVIEW');end if;
 end;
 procedure operation_free(p_operation varchar2)is n number;begin
  select count(*)into n from RRL_ASM_RECONCILIATION where RECONCILIATION_ID=p_operation or AUTHORIZE_OPERATION_ID=p_operation;
  if n!=0 then raise_application_error(-20886,'ASSEMBLY_RECOVERY_OPERATION_CONFLICT');end if;
 end;
 function as_json(v RRL_ASM_RECONCILIATION%rowtype)return json_object_t is j json_object_t:=json_object_t();task_no number;begin
  select CASE_PICK_TASK_ID into task_no from RRL_ASSEMBLY_SESSION where SESSION_ID=v.SESSION_ID;j.put('case_task_id',task_no);
  j.put('reconciliation_id',v.RECONCILIATION_ID);j.put('session_id',v.SESSION_ID);j.put('step_id',v.STEP_ID);j.put('state',v.STATE);
  j.put('requester_id',v.REQUESTER_ID);j.put('controller_id',v.CONTROLLER_ID);j.put('expected_content_version',v.EXPECTED_CONTENT_VERSION);
  j.put('expected_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(v.EXPECTED_WEIGHT_KG));
  j.put('reason',json_object_t.parse(v.REQUEST_JSON).get_string('reason'));
  j.put('requested_at',to_char(v.REQUESTED_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));return j;
 end;
 procedure request_reconciliation(p_session varchar2,p_request clob,p_actor nvarchar2,p_result out clob)is
  j json_object_t:=json_object_t.parse(p_request);v RRL_ASM_RECONCILIATION%rowtype;s RRL_ASSEMBLY_SESSION%rowtype;t RRL_ASSEMBLY_STEP%rowtype;
  id_value varchar2(100):=j.get_string('operation_id');step_value varchar2(100):=j.get_string('step_id');n number;identity json_array_t:=json_array_t();begin
  lock_step(step_value,p_actor,'case_pick_execute');select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=p_session;
  select *into t from RRL_ASSEMBLY_STEP where STEP_ID=step_value and SESSION_ID=p_session;
  begin select *into v from RRL_ASM_RECONCILIATION where RECONCILIATION_ID=id_value;
   if v.REQUESTER_ID!=p_actor or v.SESSION_ID!=p_session or dbms_lob.compare(v.REQUEST_JSON,p_request)!=0 then raise_application_error(-20886,'ASSEMBLY_RECOVERY_REQUEST_CONFLICT');end if;
   p_result:=v.REQUEST_RESULT;finish_change;return;exception when no_data_found then null;end;
  RRL_ASSEMBLY_SCALE_API.assert_recovery_context(p_session,step_value,p_actor,'case_pick_execute');
  unposted(step_value);operation_free(id_value);
  select count(*)into n from RRL_ASM_RECONCILIATION where SESSION_ID=p_session and STATE in('REQUESTED','AUTHORIZED');
  if n!=0 then raise_application_error(-20886,'ASSEMBLY_RECOVERY_ACTIVE_INTENT_CONFLICT');end if;
  if id_value is null or not regexp_like(id_value,'^[A-Za-z0-9_.:-]{1,100}$','c')or j.get_number('expected_content_version')is null
   or j.get_number('expected_content_version')!=s.LAST_CONTENT_VERSION or j.get_string('reason')is null or length(j.get_string('reason'))not between 8 and 500
   then raise_application_error(-20886,'ASSEMBLY_RECOVERY_EXPLICIT_REQUEST_REQUIRED');end if;
  v.RECONCILIATION_ID:=id_value;v.SESSION_ID:=p_session;v.STEP_ID:=step_value;v.EXPECTED_CONTENT_VERSION:=s.LAST_CONTENT_VERSION;
  v.EXPECTED_WEIGHT_KG:=s.LAST_WEIGHT_KG;v.STATE:='REQUESTED';v.REQUESTER_ID:=p_actor;v.REQUESTED_AT:=systimestamp;v.REQUEST_JSON:=p_request;
  identity.append(id_value);identity.append('RECONCILE');v.CAPTURE_ID:='ASM.RECON.'||rawtohex(sys.dbms_crypto.hash(identity.to_clob,sys.dbms_crypto.hash_sh256));
  v.REQUEST_RESULT:=as_json(v).to_clob;insert into RRL_ASM_RECONCILIATION values v;
  permit(id_value);RRL_ASSEMBLY_SCALE_API.apply_reconciliation(id_value,p_session,step_value);p_result:=v.REQUEST_RESULT;finish_change;
 exception when others then finish_change;raise;end;
 procedure authorize(p_id varchar2,p_request clob,p_actor nvarchar2,p_result out clob)is
  j json_object_t:=json_object_t.parse(p_request);v RRL_ASM_RECONCILIATION%rowtype;op varchar2(100):=j.get_string('operation_id');el json_element_t;begin
  select *into v from RRL_ASM_RECONCILIATION where RECONCILIATION_ID=p_id;lock_step(v.STEP_ID,p_actor,'case_pick_manage');
  select *into v from RRL_ASM_RECONCILIATION where RECONCILIATION_ID=p_id for update;
  if p_actor=v.REQUESTER_ID then raise_application_error(-20882,'ASSEMBLY_RECOVERY_DISTINCT_CONTROLLER_REQUIRED');end if;
  if v.AUTHORIZE_OPERATION_ID=op then
   if v.CONTROLLER_ID!=p_actor or dbms_lob.compare(v.AUTHORIZE_JSON,p_request)!=0 then raise_application_error(-20886,'ASSEMBLY_RECOVERY_AUTHORIZATION_CONFLICT');end if;
   p_result:=v.AUTHORIZE_RESULT;finish_change;return;end if;
  RRL_ASSEMBLY_SCALE_API.assert_recovery_context(v.SESSION_ID,v.STEP_ID,p_actor,'case_pick_manage');
  unposted(v.STEP_ID);operation_free(op);
  if v.STATE!='REQUESTED'or op is null or not regexp_like(op,'^[A-Za-z0-9_.:-]{1,100}$','c')or j.get_string('reason')is null or length(j.get_string('reason'))not between 8 and 500 then raise_application_error(-20886,'ASSEMBLY_RECOVERY_AUTHORIZATION_REQUIRED');end if;
  el:=j.get('unaccepted_goods_removed');
  if el is null or not el.is_boolean then raise_application_error(-20886,'ASSEMBLY_RECOVERY_EXPLICIT_REMOVAL_REQUIRED');end if;
  if j.get_boolean('unaccepted_goods_removed')then null;else raise_application_error(-20886,'ASSEMBLY_RECOVERY_EXPLICIT_REMOVAL_REQUIRED');end if;
  v.AUTHORIZE_OPERATION_ID:=op;v.CONTROLLER_ID:=p_actor;v.AUTHORIZED_AT:=systimestamp;v.AUTHORIZE_JSON:=p_request;v.STATE:='AUTHORIZED';v.AUTHORIZE_RESULT:=as_json(v).to_clob;
  update RRL_ASM_RECONCILIATION set AUTHORIZE_OPERATION_ID=op,CONTROLLER_ID=p_actor,AUTHORIZED_AT=v.AUTHORIZED_AT,AUTHORIZE_JSON=p_request,AUTHORIZE_RESULT=v.AUTHORIZE_RESULT,STATE='AUTHORIZED'where RECONCILIATION_ID=p_id;
  p_result:=v.AUTHORIZE_RESULT;finish_change;
 exception when others then finish_change;raise;end;
 procedure read_reconciliation(p_id varchar2,p_actor nvarchar2,p_result out clob)is v RRL_ASM_RECONCILIATION%rowtype;s RRL_ASSEMBLY_SESSION%rowtype;begin
  select *into v from RRL_ASM_RECONCILIATION where RECONCILIATION_ID=p_id;select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=v.SESSION_ID;
  RRL_CASE_TASK_ACCESS.assert_scope(s.CASE_PICK_TASK_ID,p_actor,case when p_actor=s.OPERATOR_ID then'case_pick_execute'else'case_pick_manage'end);
  p_result:=as_json(v).to_clob;
 end;
 procedure sender_scope(p_device varchar2,p_sender nvarchar2)is d RRL_WH_SCALE_DEVICE%rowtype;n number;begin
  select *into d from RRL_WH_SCALE_DEVICE where DEVICE_ID=p_device;
  select count(*)into n from RUSERS where ID=p_sender and nvl(DELETED,0)=0 and WARE_ID=d.WARE_ID and upper(trim(USER_GROUP))!='GLOBAL_ADMIN'and RRL_HAS_WRIGHT(ID,'warehouse_scale_ingest')=1;
  if p_sender is null or p_sender!=d.SENDER_ID or n!=1 then raise_application_error(-20882,'ASSEMBLY_RECOVERY_DEDICATED_SENDER_REQUIRED');end if;
 end;
 procedure gateway_requests(p_device varchar2,p_sender nvarchar2,p_result out clob)is
  j json_object_t:=json_object_t();items json_array_t:=json_array_t();o json_object_t;s RRL_ASSEMBLY_SESSION%rowtype;t RRL_ASSEMBLY_STEP%rowtype;begin
  sender_scope(p_device,p_sender);
  for v in(select r.*from RRL_ASM_RECONCILIATION r join RRL_ASSEMBLY_SESSION a on a.SESSION_ID=r.SESSION_ID where a.DEVICE_ID=p_device and r.STATE='AUTHORIZED'order by r.REQUESTED_AT fetch first 1 row only)loop
   select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=v.SESSION_ID;select *into t from RRL_ASSEMBLY_STEP where STEP_ID=v.STEP_ID;
   RRL_ASSEMBLY_SCALE_API.assert_recovery_context(s.SESSION_ID,t.STEP_ID,p_sender,'warehouse_scale_ingest');
   RRL_ASSEMBLY_SCALE_API.assert_recovery_context(s.SESSION_ID,t.STEP_ID,v.CONTROLLER_ID,'case_pick_manage');
   o:=json_object_t();o.put('session_id',s.SESSION_ID);o.put('step_id',t.STEP_ID);o.put('operation_id',v.RECONCILIATION_ID);o.put('reconciliation_id',v.RECONCILIATION_ID);
   o.put('case_task_id',s.CASE_PICK_TASK_ID);o.put('scan_container',s.CARRIER_IDENTIFIER);o.put('capture_id',v.CAPTURE_ID);o.put('phase','RECONCILE');
   o.put('device_id',s.DEVICE_ID);o.put('device_policy_version',s.DEVICE_POLICY_VERSION);o.put('calibration_ref',s.CALIBRATION_REF);o.put('confirmation_mode',s.CONFIRMATION_MODE);
   o.put('expected_before_kg',RRL_STOCK_PLAN_HELPER.decimal_text(v.EXPECTED_WEIGHT_KG));o.put('min_delta_kg',RRL_STOCK_PLAN_HELPER.decimal_text(t.MIN_DELTA_KG));
   o.put('expected_content_version',v.EXPECTED_CONTENT_VERSION);o.put('tare_capture_key',s.TARE_CAPTURE_KEY);o.put('expires_at',to_char(s.EXPIRES_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));items.append(o);
  end loop;j.put('items',items);p_result:=j.to_clob;
 end;
 procedure capture_state(p_id varchar2,p_sender nvarchar2,p_result out clob)is v RRL_ASM_RECONCILIATION%rowtype;begin
  select *into v from RRL_ASM_RECONCILIATION where RECONCILIATION_ID=p_id;
  RRL_ASSEMBLY_SCALE_API.read_gateway_state(v.SESSION_ID,v.STEP_ID,p_sender,p_result);
 end;
 procedure assert_apply(p_id varchar2,p_session varchar2,p_step varchar2)is v RRL_ASM_RECONCILIATION%rowtype;s RRL_ASSEMBLY_SESSION%rowtype;c RRL_ASM_RECON_CAPTURE%rowtype;d RRL_WH_SCALE_DEVICE%rowtype;begin
  if write_allowed!=1 or sys_context('RRL_ASM_RECOVERY_CTX','APPLY_ID')is null or sys_context('RRL_ASM_RECOVERY_CTX','APPLY_ID')!=p_id then raise_application_error(-20863,'ASSEMBLY_RECOVERY_TRUSTED_APPLY_REQUIRED');end if;
  select *into v from RRL_ASM_RECONCILIATION where RECONCILIATION_ID=p_id;select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=p_session;
  if v.SESSION_ID!=p_session or v.STEP_ID!=p_step then raise_application_error(-20863,'ASSEMBLY_RECOVERY_TRUSTED_APPLY_REQUIRED');end if;
  unposted(p_step);if v.STATE='REQUESTED'then return;end if;
  select *into c from RRL_ASM_RECON_CAPTURE where RECONCILIATION_ID=p_id;select *into d from RRL_WH_SCALE_DEVICE where DEVICE_ID=s.DEVICE_ID;
  if v.STATE!='AUTHORIZED'or v.SESSION_ID!=p_session or v.STEP_ID!=p_step or c.SESSION_ID!=p_session or c.STEP_ID!=p_step
   or c.RECORDED_BY!=s.SENDER_ID or c.DEVICE_ID!=s.DEVICE_ID or abs(c.WEIGHT_KG-s.LAST_WEIGHT_KG)>d.RESOLUTION_KG then raise_application_error(-20863,'ASSEMBLY_RECOVERY_ADMITTED_OBSERVATION_REQUIRED');end if;
  unposted(p_step);
 end;
 procedure capture(p_request clob,p_sender nvarchar2,p_result out clob)is
  j json_object_t:=json_object_t.parse(p_request);v RRL_ASM_RECONCILIATION%rowtype;s RRL_ASSEMBLY_SESSION%rowtype;d RRL_WH_SCALE_DEVICE%rowtype;c RRL_ASM_RECON_CAPTURE%rowtype;old RRL_ASM_RECON_CAPTURE%rowtype;
  id_value varchar2(100):=j.get_string('reconciliation_id');device_value varchar2(100):=j.get_string('device_id');capture_value varchar2(100):=j.get_string('capture_id');
  hash_value varchar2(64):=rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256));reading json_object_t;r json_object_t:=json_object_t();identity json_array_t:=json_array_t();state_value varchar2(20);begin
  if p_request is null or dbms_lob.getlength(p_request)>32000 then raise_application_error(-20881,'ASSEMBLY_PACKET_BOUND_32000');end if;
  sender_scope(device_value,p_sender);
  begin select *into old from RRL_ASM_RECON_CAPTURE where DEVICE_ID=device_value and CAPTURE_ID=capture_value;
   if old.RECORDED_BY!=p_sender or old.SOURCE_SHA256!=hash_value or dbms_lob.compare(old.SOURCE_JSON,p_request)!=0 then raise_application_error(-20886,'ASSEMBLY_RECOVERY_CAPTURE_CONFLICT');end if;
   lock table RRL_ACCESS_REV in share mode wait 2;
   select *into d from RRL_WH_SCALE_DEVICE where DEVICE_ID=device_value for update wait 2;sender_scope(device_value,p_sender);
   if d.WARE_ID!=old.WARE_ID or d.POST_CELL!=old.POST_CELL then raise_application_error(-20882,'ASSEMBLY_ORIGINAL_CAPTURE_SCOPE_CHANGED');end if;
   p_result:=old.RESULT_JSON;return;exception when no_data_found then null;end;
  select *into v from RRL_ASM_RECONCILIATION where RECONCILIATION_ID=id_value;select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=v.SESSION_ID;
  lock_step(v.STEP_ID,s.OPERATOR_ID,'case_pick_execute');select *into v from RRL_ASM_RECONCILIATION where RECONCILIATION_ID=id_value for update;
  select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=v.SESSION_ID;select *into d from RRL_WH_SCALE_DEVICE where DEVICE_ID=s.DEVICE_ID;
  RRL_ASSEMBLY_SCALE_API.assert_recovery_context(s.SESSION_ID,v.STEP_ID,p_sender,'warehouse_scale_ingest');
  RRL_ASSEMBLY_SCALE_API.assert_recovery_context(s.SESSION_ID,v.STEP_ID,v.CONTROLLER_ID,'case_pick_manage');unposted(v.STEP_ID);
  if v.STATE!='AUTHORIZED'or v.CONTROLLER_ID is null or v.CONTROLLER_ID=v.REQUESTER_ID or j.get_string('phase')is null or j.get_string('phase')!='RECONCILE'
   or device_value!=s.DEVICE_ID or capture_value is null or capture_value!=v.CAPTURE_ID
   or j.get_string('session_id')is null or j.get_string('session_id')!=s.SESSION_ID or j.get_string('step_id')is null or j.get_string('step_id')!=v.STEP_ID
   or j.get_number('device_policy_version')is null or j.get_number('device_policy_version')!=s.DEVICE_POLICY_VERSION
   or j.get_string('calibration_ref')is null or j.get_string('calibration_ref')!=s.CALIBRATION_REF
   or v.EXPECTED_CONTENT_VERSION!=s.LAST_CONTENT_VERSION or v.EXPECTED_WEIGHT_KG!=s.LAST_WEIGHT_KG then raise_application_error(-20886,'ASSEMBLY_RECOVERY_AUTHORIZED_CAPTURE_REQUIRED');end if;
  reading:=json_object_t.parse(RRL_SCALE_PACKET_READ.validate_series_json(p_request,d.CAPACITY_KG,d.RESOLUTION_KG));
  c.WEIGHT_KG:=RRL_STOCK_MATH.quantity(reading.get_string('weight_kg'));c.MEASURED_AT:=RRL_SCALE_PACKET_READ.utc_stamp(j.get_string('measured_at'));
  if c.MEASURED_AT-numtodsinterval(reading.get_number('span_ms')/1000,'SECOND')<v.AUTHORIZED_AT then raise_application_error(-20886,'ASSEMBLY_RECOVERY_WINDOW_AFTER_AUTHORIZATION_REQUIRED');end if;
  state_value:=case when abs(c.WEIGHT_KG-s.LAST_WEIGHT_KG)<=d.RESOLUTION_KG then'COMPLETED'else'DISCREPANCY'end;
  c.DEVICE_ID:=device_value;c.CAPTURE_ID:=capture_value;c.RECONCILIATION_ID:=id_value;c.SESSION_ID:=s.SESSION_ID;c.STEP_ID:=v.STEP_ID;
  c.WARE_ID:=s.WARE_ID;c.POST_CELL:=s.POST_CELL;c.DEVICE_POLICY_VERSION:=s.DEVICE_POLICY_VERSION;c.SOURCE_SHA256:=hash_value;c.SOURCE_JSON:=p_request;c.RECORDED_BY:=p_sender;c.RECORDED_AT:=systimestamp;
  identity.append(device_value);identity.append(capture_value);r.put('capture_key',rawtohex(sys.dbms_crypto.hash(identity.to_clob,sys.dbms_crypto.hash_sh256)));
  r.put('status','ARCHIVED');r.put('case_task_id',s.CASE_PICK_TASK_ID);r.put('state',state_value);r.put('phase','RECONCILE');r.put('reconciliation_id',id_value);r.put('session_id',s.SESSION_ID);r.put('step_id',v.STEP_ID);
  r.put('device_id',device_value);r.put('capture_id',capture_value);r.put('source_sha256',hash_value);r.put('weight_kg',reading.get_string('weight_kg'));r.put('measured_at',j.get_string('measured_at'));
  r.put('device_policy_version',s.DEVICE_POLICY_VERSION);r.put('calibration_ref',s.CALIBRATION_REF);r.put('stock_posted',false);c.RESULT_JSON:=r.to_clob;
  insert into RRL_ASM_RECON_CAPTURE values c;
  if state_value='COMPLETED'then permit(id_value);RRL_ASSEMBLY_SCALE_API.apply_reconciliation(id_value,s.SESSION_ID,v.STEP_ID);end if;
  update RRL_ASM_RECONCILIATION set STATE=state_value,COMPLETED_AT=systimestamp where RECONCILIATION_ID=id_value;p_result:=c.RESULT_JSON;finish_change;
 exception when others then finish_change;raise;end;
end;
/
