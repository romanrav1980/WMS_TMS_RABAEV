create or replace package body RRL_CASE_ASSIGNMENT_API as
 procedure clear_context(p_owned_plan boolean default false)is begin dbms_session.clear_context('RRL_CASE_ASSIGNMENT_CTX',null);if p_owned_plan then RRL_STOCK_LOCK_API.clear_plan;end if;end;
 function ledger_write_allowed return number is v varchar2(100):=sys_context('RRL_CASE_ASSIGNMENT_CTX','TX_ID');begin
  if v is not null and v=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;
 end;
 function write_allowed(p_task number,p_actor nvarchar2,p_action varchar2)return number is begin
  if ledger_write_allowed=1 and p_task is not null and p_actor is not null and p_action is not null
   and sys_context('RRL_CASE_ASSIGNMENT_CTX','TASK_ID')=RRL_STOCK_PLAN_HELPER.decimal_text(p_task)
   and sys_context('RRL_CASE_ASSIGNMENT_CTX','ACTOR')=p_actor and sys_context('RRL_CASE_ASSIGNMENT_CTX','ACTION')=p_action then return 1;end if;return 0;
 end;
 procedure current_authority(p_task number,p_actor nvarchar2,p_action varchar2)is t RRL_CASE_PICK_TASK%rowtype;n number;begin
  if p_task is null or p_actor is null or p_action is null or p_action not in('CLAIM','START')then raise_application_error(-20882,'CASE_RESOURCE_CURRENT_ACTOR_REQUIRED');end if;
  RRL_TRADE_CASE_ACCESS.assert_scope(p_task,p_actor,1);
  if RRL_CASE_TASK_ACCESS.legacy_executor(p_task,p_actor)=1 then RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,'case_pick_execute');return;end if;
  select *into t from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  if RRL_CASE_TASK_ACCESS.has_current_scoped_execute(p_task,p_actor)=1 then return;end if;
  -- Unassigned CLAIM authorization is scope-only here. New-execution eligibility follows after receipt lookup.
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  if p_action='CLAIM'and n=1 and t.ASSIGNED_TO is null and t.WARE_ID is not null and t.WARE_ID>0
   and RRL_ACCESS_API.allowed(p_actor,'case_pick_execute','WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(t.WARE_ID),null)=1 then return;end if;
  raise_application_error(-20882,'CASE_RESOURCE_CURRENT_SCOPE_REQUIRED');
 exception when no_data_found then raise_application_error(-20886,'CASE_RESOURCE_TASK_MISSING');end;
 function state_json(t RRL_CASE_PICK_TASK%rowtype)return json_object_t is j json_object_t:=json_object_t();begin
  j.put('task_id',t.CASE_PICK_TASK_ID);j.put('warehouse_id',t.WARE_ID);j.put('status',t.STATUS);
  j.put('assignment_version',t.ASSIGNMENT_VERSION);j.put('content_version',t.CONTENT_VERSION);
  j.put('assigned_to',t.ASSIGNED_TO);j.put('resource_id',t.ASSIGNED_RESOURCE_ID);j.put('resource_session_id',t.RESOURCE_SESSION_ID);j.put('equipment_id',t.EQUIPMENT_ID);
  if t.STARTED_AT_INSTANT is null then j.put_null('started_at_instant');
  else j.put('started_at_instant',to_char(t.STARTED_AT_INSTANT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));end if;
  j.put('started_shift_time_zone',t.STARTED_SHIFT_TIME_ZONE);return j;
 end;
 procedure task_context(p_task number,p_actor nvarchar2,p_result out clob)is t RRL_CASE_PICK_TASK%rowtype;j json_object_t;begin
  select *into t from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  current_authority(p_task,p_actor,case when t.ASSIGNED_TO is null then 'CLAIM'else'START'end);
  j:=state_json(t);j.put('current_actor',p_actor);p_result:=j.to_clob;
 end;
 procedure receipt(p_operation varchar2,p_actor nvarchar2,p_result out clob)is v RRL_CASE_RESOURCE_COMMAND%rowtype;begin
  select *into v from RRL_CASE_RESOURCE_COMMAND where OPERATION_ID=p_operation;
  if p_actor is null or v.ACTOR_ID!=p_actor then raise_application_error(-20882,'CASE_RESOURCE_ORIGINAL_ACTOR_REQUIRED');end if;
  current_authority(v.CASE_PICK_TASK_ID,p_actor,v.ACTION);p_result:=v.RESULT_JSON;
 end;
 function recoverable(p_code varchar2)return boolean is begin
  return p_code in('CASE_RESOURCE_ASSIGNMENT_VERSION_CHANGED','CASE_RESOURCE_TASK_STATE_CONFLICT','CASE_SESSION_UNAVAILABLE',
   'CASE_SHIFT_UNAVAILABLE','CASE_OPERATOR_BUSY_WITH_OTHER_PHYSICAL_STEP','CASE_RESOURCE_UNAVAILABLE','CASE_RESOURCE_TYPE_UNSUITABLE',
   'CASE_RESOURCE_QUALIFICATION_REQUIRED','CASE_RESOURCE_EQUIPMENT_BINDING_CONFLICT','CASE_EQUIPMENT_UNAVAILABLE',
   'CASE_RESOURCE_CONTEXT_CONFLICT','CASE_SESSION_CONTEXT_CONFLICT','CASE_CARRIER_NEEDS_EXPLICIT_TRANSFER','CASE_RESOURCE_IDENTITY_MISSING',
   'CASE_USE_EXPLICIT_TRANSFER','CASE_SCOPED_ACTIVE_SESSION_REQUIRED','WAVE_PICK_RELEASE_REQUIRED',
   'CASE_ASSEMBLY_GOOD_TARE_BOOK_REQUIRED','CASE_RESOURCE_UNSUPPORTED_CONTEXT','CASE_SCOPED_SHIFT_WAREHOUSE_CONFLICT','CASE_SCOPED_PHYSICAL_SESSION_REQUIRED');
 end;
 procedure execute_command(p_task number,p_request clob,p_actor nvarchar2,p_result out clob)is
  j json_object_t;t RRL_CASE_PICK_TASK%rowtype;old RRL_CASE_RESOURCE_COMMAND%rowtype;v RRL_CASE_RESOURCE_COMMAND%rowtype;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();ctx json_object_t;reply json_object_t;
  expected_version number;resource_value number;session_value number;equipment_value number;resolved_resource number;resolved_session number;resolved_equipment number;
  target nvarchar2(50);reason_text varchar2(4000);release_state varchar2(20);changed boolean:=false;event_type varchar2(20);wave_id number;n number;failure_code varchar2(100);owned_plan boolean:=false;locked_actor nvarchar2(50);
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null then raise_application_error(-20886,'CASE_RESOURCE_METADATA_OUTSIDE_STOCK_REQUIRED');end if;
  if p_request is null or dbms_lob.getlength(p_request)>16384 then raise_application_error(-20886,'CASE_RESOURCE_REQUEST_BOUND_16K');end if;
  j:=json_object_t.parse(p_request);v.OPERATION_ID:=j.get_string('operation_id');v.ACTION:=j.get_string('action');v.CASE_PICK_TASK_ID:=p_task;v.ACTOR_ID:=p_actor;
  expected_version:=j.get_number('expected_assignment_version');session_value:=j.get_number('resource_session_id');resource_value:=j.get_number('resource_id');equipment_value:=j.get_number('equipment_id');reason_text:=j.get_string('reason');
  if v.OPERATION_ID is null or not regexp_like(v.OPERATION_ID,'^[A-Za-z0-9_.:-]{1,100}$','c')or v.ACTION is null or v.ACTION not in('CLAIM','START')
   or expected_version is null or expected_version<0 or expected_version!=trunc(expected_version)or session_value is null or session_value<1 or session_value!=trunc(session_value)
   or(resource_value is not null and(resource_value<1 or resource_value!=trunc(resource_value)))or(equipment_value is not null and(equipment_value<1 or equipment_value!=trunc(equipment_value)))
   or reason_text is null or length(trim(reason_text))not between 8 and 500 then raise_application_error(-20886,'CASE_RESOURCE_EXPLICIT_INTENT_REQUIRED');end if;
  current_authority(p_task,p_actor,v.ACTION);
  select PICK_WAVE_ID into wave_id from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  if wave_id is null then raise_application_error(-20886,'CASE_RESOURCE_WAVE_REQUIRED');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE',6);
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP','CASE.RESOURCE:'||v.OPERATION_ID);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA');
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(wave_id));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(p_task));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RESOURCE_SESSION',RRL_STOCK_PLAN_HELPER.decimal_text(session_value));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RUSERS',p_actor);
  RRL_STOCK_LOCK_API.begin_plan;owned_plan:=true;lock table RRL_ACCESS_REV in share mode wait 2;
  RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  select STATE into release_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if release_state is null or release_state not in('PREPARED','ACTIVE')then raise_application_error(-20886,'CASE_RESOURCE_RELEASE_CLOSED');end if;
  select PICK_WAVE_ID into n from RRL_PICK_WAVE where PICK_WAVE_ID=wave_id for update;
  select *into t from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task for update;
  select ID into locked_actor from RUSERS where ID=p_actor for update;
  if t.PICK_WAVE_ID is null or t.PICK_WAVE_ID!=wave_id then raise_application_error(-20886,'CASE_RESOURCE_WAVE_CHANGED');end if;
  current_authority(p_task,p_actor,v.ACTION);
  begin select *into old from RRL_CASE_RESOURCE_COMMAND where OPERATION_ID=v.OPERATION_ID;
   if old.ACTOR_ID!=p_actor or old.CASE_PICK_TASK_ID!=p_task or dbms_lob.compare(old.SOURCE_JSON,p_request)!=0 then raise_application_error(-20886,'CASE_RESOURCE_OPERATION_CONFLICT');end if;
   p_result:=old.RESULT_JSON;clear_context(owned_plan);return;exception when no_data_found then null;end;
  RRL_RESOURCE_INTENT_API.assert_available('CASE',p_task,p_actor,v.OPERATION_ID,p_request);
  v.BEFORE_VERSION:=t.ASSIGNMENT_VERSION;v.RESOURCE_SESSION_ID:=session_value;
  savepoint case_resource_effect;
  begin
  if t.ASSIGNMENT_VERSION is null or t.ASSIGNMENT_VERSION!=expected_version then raise_application_error(-20886,'CASE_RESOURCE_ASSIGNMENT_VERSION_CHANGED');end if;
  if RRL_CASE_TASK_ACCESS.legacy_executor(p_task,p_actor)!=1 and RRL_CASE_TASK_ACCESS.ordinary_execution_task(p_task)!=1 and RRL_TRADE_CASE_ACCESS.execution_allowed(p_task,p_actor)!=1 then raise_application_error(-20886,'CASE_RESOURCE_UNSUPPORTED_CONTEXT');end if;
  if RRL_CASE_TASK_ACCESS.legacy_executor(p_task,p_actor)!=1 and RRL_CASE_TASK_ACCESS.scoped_metadata_actor(p_task,v.ACTION,p_actor)!=1 then raise_application_error(-20882,'CASE_RESOURCE_SCOPED_EXECUTION_FORBIDDEN');end if;
  begin select SESSION_ID into n from RRL_RESOURCE_SESSION where SESSION_ID=session_value for update;
  exception when no_data_found then raise_application_error(-20886,'CASE_RESOURCE_IDENTITY_MISSING');end;
  ctx:=json_object_t.parse(RRL_CASE_RESOURCE_POLICY.context_json(p_task,v.ACTION,p_actor,resource_value,session_value,equipment_value));
  resolved_resource:=ctx.get_number('resource_id');resolved_session:=ctx.get_number('resource_session_id');resolved_equipment:=ctx.get_number('equipment_id');target:=ctx.get_string('assigned_to');
  if target is null or resolved_session is null or resolved_session!=session_value then raise_application_error(-20886,'CASE_RESOURCE_PHYSICAL_CONTEXT_REQUIRED');end if;
  if t.ASSIGNED_RESOURCE_ID is not null and(t.ASSIGNED_RESOURCE_ID!=resolved_resource or resolved_resource is null)then raise_application_error(-20886,'CASE_USE_EXPLICIT_TRANSFER');end if;
  if RRL_CASE_TASK_ACCESS.legacy_executor(p_task,p_actor)!=1 and(
   (t.RESOURCE_SESSION_ID is not null and t.RESOURCE_SESSION_ID!=resolved_session)
   or(t.EQUIPMENT_ID is not null and(t.EQUIPMENT_ID!=resolved_equipment or resolved_equipment is null)))then
   raise_application_error(-20886,'CASE_USE_EXPLICIT_TRANSFER');end if;
  v.BEFORE_VERSION:=t.ASSIGNMENT_VERSION;v.RESOURCE_SESSION_ID:=resolved_session;
  dbms_session.set_context('RRL_CASE_ASSIGNMENT_CTX','TX_ID',dbms_transaction.local_transaction_id(true));
  dbms_session.set_context('RRL_CASE_ASSIGNMENT_CTX','TASK_ID',RRL_STOCK_PLAN_HELPER.decimal_text(p_task));
  dbms_session.set_context('RRL_CASE_ASSIGNMENT_CTX','ACTOR',p_actor);dbms_session.set_context('RRL_CASE_ASSIGNMENT_CTX','ACTION',v.ACTION);
  if v.ACTION='CLAIM'then
   update RRL_CASE_PICK_TASK set STATUS=case when STATUS='NEW'then'ASSIGNED'else STATUS end,ASSIGNED_TO=target,
    ASSIGNED_RESOURCE_ID=resolved_resource,RESOURCE_SESSION_ID=resolved_session,EQUIPMENT_ID=resolved_equipment,UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_TASK_ID=p_task;
   event_type:='CLAIMED';
  elsif t.STARTED_AT is null then
   update RRL_CASE_PICK_TASK set STATUS=case when STATUS in('NEW','ASSIGNED')then'IN_PROGRESS'else STATUS end,
    ASSIGNED_TO=target,ASSIGNED_RESOURCE_ID=resolved_resource,RESOURCE_SESSION_ID=resolved_session,EQUIPMENT_ID=resolved_equipment,
    STARTED_AT=systimestamp,STARTED_AT_INSTANT=systimestamp,STARTED_SHIFT_TIME_ZONE=null,UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_TASK_ID=p_task;
   event_type:='STARTED';
  end if;
  select *into t from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  changed:=t.ASSIGNMENT_VERSION!=v.BEFORE_VERSION;v.AFTER_VERSION:=t.ASSIGNMENT_VERSION;
  if changed then
   insert into RRL_CASE_PICK_EVENT(CASE_PICK_EVENT_ID,CASE_PICK_TASK_ID,EVENT_TYPE,RESOURCE_ID,RESOURCE_SESSION_ID,EQUIPMENT_ID,MESSAGE_TEXT,PAYLOAD_JSON,CREATED_BY)
    values(RRL_CASE_PICK_EVENT_SQ.nextval,p_task,event_type,resolved_resource,resolved_session,resolved_equipment,substr(reason_text,1,250),p_request,p_actor);
  end if;
  v.OUTCOME:='APPLIED';
  exception when others then
   failure_code:=regexp_replace(substr(sqlerrm,1,instr(sqlerrm||chr(10),chr(10))-1),'^ORA-[0-9]+: *','');
   if sqlcode!=-20886 or not recoverable(failure_code)then raise;end if;
   rollback to case_resource_effect;clear_context;
   select *into t from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
   v.OUTCOME:='REJECTED';v.ERROR_CODE:=failure_code;v.AFTER_VERSION:=t.ASSIGNMENT_VERSION;changed:=false;
  end;
  dbms_session.set_context('RRL_CASE_ASSIGNMENT_CTX','TX_ID',dbms_transaction.local_transaction_id(true));
  v.SOURCE_SHA256:=rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256));
  reply:=state_json(t);reply.put('outcome',v.OUTCOME);reply.put('request_sha256',v.SOURCE_SHA256);reply.put('outcome_confirmed',true);
  reply.put('may_create_corrected_operation',v.OUTCOME='REJECTED');
  if v.ERROR_CODE is null then reply.put_null('error_code');else reply.put('error_code',v.ERROR_CODE);end if;
  reply.put('operation_id',v.OPERATION_ID);reply.put('action',v.ACTION);reply.put('actor',p_actor);reply.put('changed',changed);reply.put('stock_posted',false);
  v.SOURCE_JSON:=p_request;v.RESULT_JSON:=reply.to_clob;v.RECORDED_AT:=systimestamp;
  insert into RRL_CASE_RESOURCE_COMMAND values v;p_result:=v.RESULT_JSON;clear_context(owned_plan);
 exception when others then clear_context(owned_plan);raise;end;
 procedure intent_authority(p_task number,p_actor nvarchar2,p_action varchar2,p_target nvarchar2,p_version out number)is begin
  if p_actor is null or p_target is null or p_target!=p_actor then raise_application_error(-20882,'RESOURCE_INTENT_ORIGINAL_ACTOR_REQUIRED');end if;
  current_authority(p_task,p_actor,p_action);
  select ASSIGNMENT_VERSION into p_version from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
 end;
end;
/
