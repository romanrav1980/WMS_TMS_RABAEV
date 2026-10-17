create or replace package body RRL_WTASK_ASSIGN_API as
 procedure clear_context(p_owned boolean default false)is begin
  dbms_session.clear_context('RRL_WTASK_ASSIGN_CTX',null);if p_owned then RRL_STOCK_LOCK_API.clear_plan;end if;end;
 procedure verify_binding is begin dbms_session.set_context('RRL_WTASK_ASSIGN_CTX','VERIFY_BINDING','READY');
  if sys_context('RRL_WTASK_ASSIGN_CTX','VERIFY_BINDING')!='READY'then raise_application_error(-20886,'WTASK_CONTEXT_BINDING_INVALID');end if;
  dbms_session.clear_context('RRL_WTASK_ASSIGN_CTX',null);end;
 function ledger_write_allowed return number is v varchar2(100):=sys_context('RRL_WTASK_ASSIGN_CTX','TX_ID');begin
  if v is not null and v=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;end;
 function policy_allowed(p_task number,p_action varchar2,p_actor varchar2,p_target varchar2)return number is begin
  if ledger_write_allowed=1 and sys_context('RRL_WTASK_ASSIGN_CTX','TASK_ID')=RRL_STOCK_PLAN_HELPER.decimal_text(p_task)
   and sys_context('RRL_WTASK_ASSIGN_CTX','ACTION')=p_action and sys_context('RRL_WTASK_ASSIGN_CTX','ACTOR')=p_actor
   and sys_context('RRL_WTASK_ASSIGN_CTX','TARGET')=p_target then return 1;end if;return 0;end;
 procedure current_authority(p_task number,p_action varchar2,p_actor varchar2,p_target varchar2)is begin
  if RRL_WAREHOUSE_TASK_ACCESS.scoped_metadata_actor(p_task,p_action,p_actor,p_target)!=1 then
   raise_application_error(-20882,'WTASK_CURRENT_SCOPED_AUTHORITY_REQUIRED');end if;end;
 function version_of(p_task number)return number is n number;begin
  select ASSIGNMENT_VERSION into n from RRL_WTASK_ASSIGN_VERSION where TASK_ID=p_task;return n;
 exception when no_data_found then return 0;end;
 function state_json(t RRL_WAREHOUSE_TASK%rowtype)return json_object_t is j json_object_t:=json_object_t();begin
  j.put('task_id',t.TASK_ID);j.put('status',t.STATUS);j.put('assignment_version',version_of(t.TASK_ID));
  j.put('task_signature',RRL_WAREHOUSE_TASK_ACCESS.task_signature(t.TASK_ID));j.put('assigned_to',t.ASSIGNED_TO);
  j.put('resource_id',t.RESOURCE_ID);j.put('resource_session_id',t.RESOURCE_SESSION_ID);j.put('equipment_id',t.EQUIPMENT_ID);
  j.put('started_shift_time_zone',t.STARTED_SHIFT_TIME_ZONE);
  if t.STARTED_AT_INSTANT is null then j.put_null('started_at_instant');else
   j.put('started_at_instant',to_char(t.STARTED_AT_INSTANT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));end if;return j;
 end;
 procedure task_context(p_task number,p_actor varchar2,p_target varchar2,p_result out clob)is t RRL_WAREHOUSE_TASK%rowtype;j json_object_t;begin
  select *into t from RRL_WAREHOUSE_TASK where TASK_ID=p_task;
  current_authority(p_task,case when t.ASSIGNED_TO is null or p_target!=p_actor then 'ASSIGN'else'START'end,p_actor,p_target);
  j:=state_json(t);j.put('current_actor',p_actor);j.put('target',p_target);p_result:=j.to_clob;
 end;
 procedure receipt(p_operation varchar2,p_actor varchar2,p_result out clob)is v RRL_WTASK_RESOURCE_COMMAND%rowtype;begin
  select *into v from RRL_WTASK_RESOURCE_COMMAND where OPERATION_ID=p_operation;
  if p_actor is null or v.ACTOR_ID!=p_actor then raise_application_error(-20882,'WTASK_ORIGINAL_ACTOR_REQUIRED');end if;
  current_authority(v.TASK_ID,v.ACTION,p_actor,v.TARGET_ID);p_result:=v.RESULT_JSON;
 end;
 function recoverable(code varchar2)return boolean is begin
  return code in('WTASK_PHYSICAL_WAREHOUSE_REQUIRED','WTASK_EXPECTED_VERSION_CHANGED','WTASK_EXPECTED_SIGNATURE_CHANGED','WTASK_STATE_CONFLICT','WTASK_SOURCE_CHANGED',
   'WTASK_EXPLICIT_RESOURCE_TRANSFER_REQUIRED','WTASK_PHYSICAL_SESSION_REQUIRED','WTASK_SOURCE_CANCELLED','WAVE_PICK_RELEASE_REQUIRED',
   'TASK_ASSIGN_STATE_CONFLICT','TASK_START_STATE_CONFLICT','TASK_SESSION_NOT_ACTIVE','TASK_SHIFT_UNAVAILABLE',
   'TASK_RESOURCE_UNAVAILABLE','TASK_RESOURCE_TYPE_UNSUITABLE','TASK_RESOURCE_QUALIFICATION_REQUIRED','TASK_RESOURCE_EQUIPMENT_REQUIRED',
   'TASK_RESOURCE_EQUIPMENT_BINDING_CONFLICT','TASK_RESOURCE_WAREHOUSE_CONFLICT','TASK_EQUIPMENT_UNAVAILABLE',
   'TASK_EQUIPMENT_WAREHOUSE_CONFLICT','TASK_START_ALREADY_IN_PROGRESS','TASK_SESSION_RESOURCE_IDENTITY_CONFLICT',
   'FINISH_OTHER_OPERATOR_PHYSICAL_STEP_FIRST','FINISH_OPERATOR_CASE_CARRIER_FIRST','FINISH_CURRENT_PHYSICAL_STEP_FIRST',
   'FINISH_CURRENT_INVENTORY_STEP_FIRST','TASK_RESOURCE_IDENTITY_NOT_FOUND');
 end;
 procedure execute_command(p_task number,p_request clob,p_actor varchar2,p_result out clob)is
  j json_object_t;t RRL_WAREHOUSE_TASK%rowtype;old RRL_WTASK_RESOURCE_COMMAND%rowtype;v RRL_WTASK_RESOURCE_COMMAND%rowtype;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();ctx json_object_t;reply json_object_t;keys json_key_list;
  expected_version number;expected_signature varchar2(64);res number;ses number;eq number;resolved_res number;resolved_ses number;resolved_eq number;
  old_source varchar2(40);old_doc number;domain_status varchar2(40);n number;release_state varchar2(20);owned boolean:=false;changed boolean:=false;failure_code varchar2(100);
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null then raise_application_error(-20886,'WTASK_METADATA_OUTSIDE_STOCK_REQUIRED');end if;
  if p_request is null or dbms_lob.getlength(p_request)>16384 then raise_application_error(-20886,'WTASK_REQUEST_BOUND_16K');end if;
  j:=json_object_t.parse(p_request);keys:=j.get_keys;
  for k in 1..keys.count loop if keys(k)not in('operation_id','action','target','expected_assignment_version','expected_task_signature','resource_id','resource_session_id','equipment_id')then
   raise_application_error(-20886,'WTASK_UNKNOWN_REQUEST_FIELD');end if;end loop;
  v.OPERATION_ID:=j.get_string('operation_id');v.ACTION:=j.get_string('action');v.TASK_ID:=p_task;v.ACTOR_ID:=p_actor;v.TARGET_ID:=j.get_string('target');
  expected_version:=j.get_number('expected_assignment_version');expected_signature:=j.get_string('expected_task_signature');
  res:=j.get_number('resource_id');ses:=j.get_number('resource_session_id');eq:=j.get_number('equipment_id');
  if v.OPERATION_ID is null or not regexp_like(v.OPERATION_ID,'^[A-Za-z0-9_.:-]{1,100}$','c')or v.ACTION is null or v.ACTION not in('ASSIGN','START')
   or v.TARGET_ID is null or length(v.TARGET_ID)>100 or expected_version is null or expected_version<0 or expected_version!=trunc(expected_version)
   or expected_signature is null or not regexp_like(expected_signature,'^[A-Fa-f0-9]{64}$','c')or ses is null or ses<1 or ses!=trunc(ses)
   or(res is not null and(res<1 or res!=trunc(res)))or(eq is not null and(eq<1 or eq!=trunc(eq)))then raise_application_error(-20886,'WTASK_EXPLICIT_INTENT_REQUIRED');end if;
  current_authority(p_task,v.ACTION,p_actor,v.TARGET_ID);
  select TASK_SOURCE,SOURCE_DOC_ID into old_source,old_doc from RRL_WAREHOUSE_TASK where TASK_ID=p_task;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE',6);
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP','WTASK.RESOURCE:'||v.OPERATION_ID);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA');
  if old_source='WAVE'then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(old_doc));end if;
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(p_task));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RESOURCE_SESSION',RRL_STOCK_PLAN_HELPER.decimal_text(ses));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RUSERS',p_actor);RRL_STOCK_PLAN_HELPER.row_key(r,'RUSERS',v.TARGET_ID);
  RRL_STOCK_LOCK_API.begin_plan;owned:=true;lock table RRL_ACCESS_REV in share mode wait 2;
  RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  select STATE into release_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if release_state is null or release_state not in('PREPARED','ACTIVE')then raise_application_error(-20886,'WTASK_RELEASE_CLOSED');end if;
  if old_source='WAVE'then select STATUS into domain_status from RRL_PICK_WAVE where PICK_WAVE_ID=old_doc for update;end if;
  select *into t from RRL_WAREHOUSE_TASK where TASK_ID=p_task for update;
  for u in(select ID from RUSERS where ID in(p_actor,v.TARGET_ID)order by ID for update)loop null;end loop;
  current_authority(p_task,v.ACTION,p_actor,v.TARGET_ID);
  begin select *into old from RRL_WTASK_RESOURCE_COMMAND where OPERATION_ID=v.OPERATION_ID;
   if old.ACTOR_ID!=p_actor or old.TASK_ID!=p_task or dbms_lob.compare(old.SOURCE_JSON,p_request)!=0 then raise_application_error(-20886,'WTASK_OPERATION_CONFLICT');end if;
   p_result:=old.RESULT_JSON;clear_context(owned);return;exception when no_data_found then null;end;
  v.BEFORE_VERSION:=version_of(p_task);savepoint wtask_resource_effect;
  begin
   if t.TASK_SOURCE!=old_source or nvl(t.SOURCE_DOC_ID,-1)!=nvl(old_doc,-1)then raise_application_error(-20886,'WTASK_SOURCE_CHANGED');end if;
   if domain_status='CANCELLED'then raise_application_error(-20886,'WTASK_SOURCE_CANCELLED');end if;
   if v.BEFORE_VERSION!=expected_version then raise_application_error(-20886,'WTASK_EXPECTED_VERSION_CHANGED');end if;
   if upper(expected_signature)!=upper(RRL_WAREHOUSE_TASK_ACCESS.task_signature(p_task))then raise_application_error(-20886,'WTASK_EXPECTED_SIGNATURE_CHANGED');end if;
   if(v.ACTION='ASSIGN'and t.STATUS not in('PLANNED','ASSIGNED'))or(v.ACTION='START'and t.STATUS not in('ASSIGNED','IN_PROGRESS'))then raise_application_error(-20886,'WTASK_STATE_CONFLICT');end if;
   begin select SESSION_ID into n from RRL_RESOURCE_SESSION where SESSION_ID=ses for update;
   exception when no_data_found then raise_application_error(-20886,'TASK_RESOURCE_IDENTITY_NOT_FOUND');end;
   dbms_session.set_context('RRL_WTASK_ASSIGN_CTX','TX_ID',dbms_transaction.local_transaction_id(true));
   dbms_session.set_context('RRL_WTASK_ASSIGN_CTX','TASK_ID',RRL_STOCK_PLAN_HELPER.decimal_text(p_task));
   dbms_session.set_context('RRL_WTASK_ASSIGN_CTX','ACTION',v.ACTION);dbms_session.set_context('RRL_WTASK_ASSIGN_CTX','ACTOR',p_actor);
   dbms_session.set_context('RRL_WTASK_ASSIGN_CTX','TARGET',v.TARGET_ID);
   ctx:=json_object_t.parse(RRL_TASK_RESOURCE_POLICY.context_json(p_task,v.ACTION,p_actor,v.TARGET_ID,res,ses,eq));
   resolved_res:=ctx.get_number('resource_id');resolved_ses:=ctx.get_number('resource_session_id');resolved_eq:=ctx.get_number('equipment_id');
   if resolved_res is null or resolved_ses is null or resolved_ses!=ses then raise_application_error(-20886,'WTASK_PHYSICAL_SESSION_REQUIRED');end if;
   select count(*)into n from RRL_RESOURCE_SESSION ss join RRL_RESOURCE rr on rr.RESOURCE_ID=ss.RESOURCE_ID
    join RRL_RESOURCE_SHIFT sh on sh.SHIFT_ID=ss.SHIFT_ID join RRL_CELLS fc on fc.CELL=t.FROM_CELL join RRL_CELLS tc on tc.CELL=t.TO_CELL
    where ss.SESSION_ID=resolved_ses and rr.WARE_ID in(fc.WARE_ID,tc.WARE_ID)and sh.WARE_ID in(fc.WARE_ID,tc.WARE_ID);
   if n!=1 then raise_application_error(-20886,'WTASK_PHYSICAL_WAREHOUSE_REQUIRED');end if;
   if t.ASSIGNED_TO is not null and(nvl(t.RESOURCE_ID,-1)!=nvl(resolved_res,-1)
    or nvl(t.RESOURCE_SESSION_ID,-1)!=nvl(resolved_ses,-1)or nvl(t.EQUIPMENT_ID,-1)!=nvl(resolved_eq,-1))then raise_application_error(-20886,'WTASK_EXPLICIT_RESOURCE_TRANSFER_REQUIRED');end if;
   if v.ACTION='ASSIGN'then
    if t.ASSIGNED_TO is null then update RRL_WAREHOUSE_TASK set STATUS='ASSIGNED',ASSIGNED_TO=v.TARGET_ID,
     RESOURCE_ID=resolved_res,RESOURCE_SESSION_ID=resolved_ses,EQUIPMENT_ID=resolved_eq,LAST_ERROR=null where TASK_ID=p_task;end if;
   elsif t.STATUS!='IN_PROGRESS'then
    update RRL_WAREHOUSE_TASK set STATUS='IN_PROGRESS',STARTED_AT=nvl(STARTED_AT,systimestamp),STARTED_AT_INSTANT=nvl(STARTED_AT_INSTANT,systimestamp),
     STARTED_SHIFT_TIME_ZONE=nvl(STARTED_SHIFT_TIME_ZONE,sessiontimezone),LAST_ERROR=null where TASK_ID=p_task;
    update RRL_RESOURCE_SESSION set CURRENT_TASK_ID=p_task where SESSION_ID=resolved_ses;

   end if;
   select *into t from RRL_WAREHOUSE_TASK where TASK_ID=p_task;v.AFTER_VERSION:=version_of(p_task);changed:=v.AFTER_VERSION!=v.BEFORE_VERSION;
   if changed then
    if t.TASK_SOURCE='WAVE'and t.TASK_TYPE='REPLENISHMENT'then update RRL_PICK_WAVE_REPLENISH_TASK set STATUS=t.STATUS,UPDATED_AT=sysdate,UPDATED_BY=substr(v.TARGET_ID,1,50)where PICK_WAVE_REPLENISH_TASK_ID=t.SOURCE_TASK_ID;
    elsif t.TASK_SOURCE='WAVE'and t.TASK_TYPE='PICKING_MOVE'then update RRL_PICK_WAVE_TASK set STATUS=t.STATUS,UPDATED_AT=sysdate,UPDATED_BY=substr(v.TARGET_ID,1,50)where PICK_WAVE_TASK_ID=t.SOURCE_TASK_ID;end if;
    insert into RRL_RESOURCE_FACT_EVENT(EVENT_ID,TASK_ID,SESSION_ID,RESOURCE_ID,EVENT_TYPE,EVENT_AT,EVENT_BY,PAYLOAD_JSON)
    values(RRL_RESOURCE_FACT_EVENT_SQ.nextval,p_task,resolved_ses,resolved_res,case when v.ACTION='ASSIGN'then'ASSIGNED'else'STARTED'end,systimestamp,p_actor,p_request);end if;
   v.OUTCOME:='APPLIED';
  exception when others then
   failure_code:=regexp_replace(substr(sqlerrm,1,instr(sqlerrm||chr(10),chr(10))-1),'^ORA-[0-9]+: *','');
   if sqlcode!=-20886 or not recoverable(failure_code)then raise;end if;
   rollback to wtask_resource_effect;clear_context;select *into t from RRL_WAREHOUSE_TASK where TASK_ID=p_task;
   v.OUTCOME:='REJECTED';v.ERROR_CODE:=failure_code;v.AFTER_VERSION:=version_of(p_task);changed:=false;
  end;
  v.SOURCE_SHA256:=rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256));v.SOURCE_JSON:=p_request;
  reply:=state_json(t);reply.put('operation_id',v.OPERATION_ID);reply.put('action',v.ACTION);reply.put('actor',p_actor);reply.put('target',v.TARGET_ID);
  reply.put('outcome',v.OUTCOME);reply.put('error_code',v.ERROR_CODE);reply.put('outcome_confirmed',true);reply.put('stock_posted',false);
  reply.put('changed',changed);reply.put('request_sha256',v.SOURCE_SHA256);reply.put('may_create_corrected_operation',v.OUTCOME='REJECTED');
  v.RESULT_JSON:=reply.to_clob;v.RECORDED_AT:=systimestamp;
  dbms_session.set_context('RRL_WTASK_ASSIGN_CTX','TX_ID',dbms_transaction.local_transaction_id(true));
  insert into RRL_WTASK_RESOURCE_COMMAND values v;p_result:=v.RESULT_JSON;clear_context(owned);
 exception when others then clear_context(owned);raise;end;
end;
/
