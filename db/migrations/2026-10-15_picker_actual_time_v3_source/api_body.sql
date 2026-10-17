create or replace package body RRL_PICKER_TIME_API as
 procedure clear_context(p_owned boolean default false)is begin
  dbms_session.clear_context('RRL_PICKER_TIME_CTX',null);if p_owned then RRL_STOCK_LOCK_API.clear_plan;end if;
 end;
 function write_allowed(p_operator varchar2)return number is t varchar2(100):=sys_context('RRL_PICKER_TIME_CTX','TX_ID');begin
  if p_operator is not null and t is not null and t=dbms_transaction.local_transaction_id(false)
   and sys_context('RRL_PICKER_TIME_CTX','OPERATOR')=p_operator then return 1;end if;return 0;
 end;
 procedure verify_binding is begin
  dbms_session.set_context('RRL_PICKER_TIME_CTX','VERIFY_BINDING','READY');
  if sys_context('RRL_PICKER_TIME_CTX','VERIFY_BINDING')!='READY'then raise_application_error(-20886,'PICKER_TIME_CONTEXT_BINDING_INVALID');end if;
  clear_context;
 exception when others then clear_context;raise;end;
 procedure current_state(p_actor varchar2,p_result out clob)is begin RRL_PICKER_TIME_READ.current_state(p_actor,p_result);end;
 procedure read_window(p_actor varchar2,p_start varchar2,p_finish varchar2,p_result out clob)is begin RRL_PICKER_TIME_READ.read_window(p_actor,p_start,p_finish,p_result);end;
 procedure receipt(p_actor varchar2,p_operation varchar2,p_result out clob)is v RRL_PICKER_TIME_COMMAND%rowtype;j json_object_t;k varchar2(24);begin
  RRL_PICKER_TIME_AUTH.actor_required(p_actor);
  select *into v from RRL_PICKER_TIME_COMMAND where OPERATION_ID=p_operation;
  if v.ACTOR_ID!=p_actor then raise_application_error(-20882,'PICKER_TIME_ORIGINAL_ACTOR_REQUIRED');end if;
  RRL_PICKER_TIME_AUTH.ware_required(p_actor,v.WARE_ID);j:=json_object_t.parse(v.SOURCE_JSON);k:=j.get_string('source_kind');
  if k is not null then RRL_PICKER_TIME_AUTH.source_permission(p_actor,k,v.WARE_ID);end if;p_result:=v.RESULT_JSON;
 end;
 function recoverable(p_code varchar2)return boolean is begin
  return p_code in('PICKER_TIME_EXPECTED_VERSION_CHANGED','PICKER_TIME_TRANSITION_NOT_ALLOWED','PICKER_TIME_ACTUAL_SHIFT_NOT_OPEN',
   'PICKER_TIME_SESSION_CHANGED','PICKER_TIME_SOURCE_CHANGED','PICKER_TIME_WORK_FINISH_REQUIRED',
   'PICKER_TIME_ACTIVE_OWN_SESSION_REQUIRED','PICKER_TIME_SESSION_UNAVAILABLE','PICKER_TIME_SOURCE_NOT_CURRENT');
 end;
 function reply(v RRL_PICKER_TIME_COMMAND%rowtype,s RRL_PICKER_TIME_STREAM%rowtype,p_at timestamp with time zone)return clob is j json_object_t:=json_object_t();begin
  j.put('operation_id',v.OPERATION_ID);j.put('actor',v.ACTOR_ID);j.put('action',v.ACTION);
  j.put('resource_session_id',v.RESOURCE_SESSION_ID);j.put('warehouse_id',v.WARE_ID);j.put('request_sha256',v.SOURCE_SHA256);
  j.put('outcome',v.OUTCOME);j.put('outcome_confirmed',true);j.put('changed',v.OUTCOME='APPLIED');
  j.put('may_create_corrected_operation',v.OUTCOME='REJECTED');j.put('error_code',v.ERROR_CODE);j.put('stock_posted',false);
  j.put('event_at',RRL_PICKER_TIME_READ.stamp(p_at));j.put('before_version',v.BEFORE_VERSION);j.put('after_version',v.AFTER_VERSION);
  j.put('state',RRL_PICKER_TIME_READ.state_json(s));return j.to_clob;
 end;
 procedure execute_command(p_actor varchar2,p_request clob,p_result out clob)is
  j json_object_t;keys json_key_list;v RRL_PICKER_TIME_COMMAND%rowtype;old RRL_PICKER_TIME_COMMAND%rowtype;s RRL_PICKER_TIME_STREAM%rowtype;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();expected number;kind_value varchar2(24);id_value number;reason_text varchar2(4000);
  ware number;res number;locked_id number;source_ok number:=0;active_required boolean;owned boolean:=false;saved boolean:=false;
  release_state varchar2(20);failure_code varchar2(100);at_value timestamp with time zone;locked_actor varchar2(100);
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null then raise_application_error(-20886,'PICKER_TIME_STANDALONE_METADATA_REQUIRED');end if;
  if p_request is null or dbms_lob.getlength(p_request)>16384 then raise_application_error(-20886,'PICKER_TIME_REQUEST_BOUND_16K');end if;
  j:=json_object_t.parse(p_request);keys:=j.get_keys;
  if keys.count!=7 then raise_application_error(-20886,'PICKER_TIME_EXACT_FIELDS_REQUIRED');end if;
  for i in 1..keys.count loop if keys(i)not in('operation_id','action','expected_version','resource_session_id','source_kind','source_id','reason')then raise_application_error(-20886,'PICKER_TIME_EXACT_FIELDS_REQUIRED');end if;end loop;
  if not j.get('operation_id').is_string or not j.get('action').is_string or not j.get('expected_version').is_number
   or not j.get('resource_session_id').is_number or not j.get('reason').is_string
   or not(j.get('source_kind').is_null or j.get('source_kind').is_string)
   or not(j.get('source_id').is_null or j.get('source_id').is_number)then raise_application_error(-20886,'PICKER_TIME_STRICT_JSON_TYPES_REQUIRED');end if;
  j.on_error(1);v.OPERATION_ID:=j.get_string('operation_id');v.ACTION:=j.get_string('action');expected:=j.get_number('expected_version');
  v.RESOURCE_SESSION_ID:=j.get_number('resource_session_id');kind_value:=j.get_string('source_kind');id_value:=j.get_number('source_id');reason_text:=j.get_string('reason');v.ACTOR_ID:=p_actor;
  if v.OPERATION_ID is null or not regexp_like(v.OPERATION_ID,'^[A-Za-z0-9_.:-]{1,100}$','c')or v.ACTION is null
   or v.ACTION not in('ACTUAL_SHIFT_START','ACTUAL_SHIFT_FINISH','WORK_START','PAUSE','RESUME','WORK_FINISH')
   or expected is null or expected<0 or expected!=trunc(expected)or expected>9007199254740991
   or v.RESOURCE_SESSION_ID is null or v.RESOURCE_SESSION_ID<1 or v.RESOURCE_SESSION_ID!=trunc(v.RESOURCE_SESSION_ID)or v.RESOURCE_SESSION_ID>9007199254740991
   or reason_text is null or length(trim(reason_text))not between 8 and 500 then raise_application_error(-20886,'PICKER_TIME_EXPLICIT_INTENT_REQUIRED');end if;
  if v.ACTION in('ACTUAL_SHIFT_START','ACTUAL_SHIFT_FINISH')then
   if kind_value is not null or id_value is not null then raise_application_error(-20886,'PICKER_TIME_SHIFT_SOURCE_FORBIDDEN');end if;
  elsif kind_value is null or kind_value not in('CASE_PICK_TASK','WAREHOUSE_TASK')or id_value is null or id_value<1 or id_value!=trunc(id_value)or id_value>9007199254740991 then raise_application_error(-20886,'PICKER_TIME_WORK_SOURCE_REQUIRED');end if;
  RRL_PICKER_TIME_AUTH.session_required(p_actor,v.RESOURCE_SESSION_ID,false,ware,res);
  if kind_value is not null then RRL_PICKER_TIME_AUTH.source_permission(p_actor,kind_value,ware);end if;
  RRL_PICKER_TIME_READ.load_state(p_actor,s);if s.WARE_ID is not null then RRL_PICKER_TIME_AUTH.ware_required(p_actor,s.WARE_ID);end if;
  active_required:=v.ACTION in('ACTUAL_SHIFT_START','WORK_START','RESUME');
  if v.ACTION in('WORK_START','RESUME')then source_ok:=RRL_PICKER_TIME_AUTH.source_allowed(p_actor,kind_value,id_value,v.RESOURCE_SESSION_ID,ware,res);end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE',6);
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP','PICKER.TIME:'||v.OPERATION_ID);
  if source_ok=1 then RRL_STOCK_PLAN_HELPER.row_key(r,case when kind_value='CASE_PICK_TASK'then'RRL_CASE_PICK_TASK'else'RRL_WAREHOUSE_TASK'end,RRL_STOCK_PLAN_HELPER.decimal_text(id_value));end if;
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RESOURCE_SESSION',RRL_STOCK_PLAN_HELPER.decimal_text(v.RESOURCE_SESSION_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICKER_TIME_STREAM',p_actor);RRL_STOCK_PLAN_HELPER.row_key(r,'RUSERS',p_actor);
  RRL_STOCK_LOCK_API.begin_plan;owned:=true;lock table RRL_ACCESS_REV in share mode wait 2;
  RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  select STATE into release_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if release_state is null or release_state not in('PREPARED','ACTIVE')then raise_application_error(-20886,'PICKER_TIME_RELEASE_CLOSED');end if;
  if source_ok=1 then
   if kind_value='CASE_PICK_TASK'then select CASE_PICK_TASK_ID into locked_id from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=id_value for update;
   else select TASK_ID into locked_id from RRL_WAREHOUSE_TASK where TASK_ID=id_value for update;end if;
  end if;
  select ID into locked_actor from RUSERS where ID=p_actor for update;
  select SESSION_ID into locked_id from RRL_RESOURCE_SESSION where SESSION_ID=v.RESOURCE_SESSION_ID for update;
  begin select *into s from RRL_PICKER_TIME_STREAM where OPERATOR_ID=p_actor for update;
  exception when no_data_found then RRL_PICKER_TIME_READ.load_state(p_actor,s);end;
  RRL_PICKER_TIME_AUTH.session_required(p_actor,v.RESOURCE_SESSION_ID,false,ware,res);
  if kind_value is not null then RRL_PICKER_TIME_AUTH.source_permission(p_actor,kind_value,ware);end if;
  if s.WARE_ID is not null then RRL_PICKER_TIME_AUTH.ware_required(p_actor,s.WARE_ID);end if;
  begin select *into old from RRL_PICKER_TIME_COMMAND where OPERATION_ID=v.OPERATION_ID;
   RRL_PICKER_TIME_AUTH.ware_required(p_actor,old.WARE_ID);
   if old.ACTOR_ID!=p_actor or dbms_lob.compare(old.SOURCE_JSON,p_request)!=0 then raise_application_error(-20886,'PICKER_TIME_OPERATION_CONFLICT');end if;
   p_result:=old.RESULT_JSON;clear_context(owned);return;exception when no_data_found then null;end;
  v.WARE_ID:=ware;v.BEFORE_VERSION:=s.STREAM_VERSION;v.SOURCE_JSON:=p_request;
  v.SOURCE_SHA256:=rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256));
  dbms_session.set_context('RRL_PICKER_TIME_CTX','TX_ID',dbms_transaction.local_transaction_id(true));dbms_session.set_context('RRL_PICKER_TIME_CTX','OPERATOR',p_actor);
  savepoint picker_time_effect;saved:=true;
  begin
   if expected!=s.STREAM_VERSION then raise_application_error(-20886,'PICKER_TIME_EXPECTED_VERSION_CHANGED');end if;
   RRL_PICKER_TIME_AUTH.session_required(p_actor,v.RESOURCE_SESSION_ID,active_required,ware,res);
   if v.ACTION in('WORK_START','RESUME')and(source_ok!=1 or RRL_PICKER_TIME_AUTH.source_allowed(p_actor,kind_value,id_value,v.RESOURCE_SESSION_ID,ware,res)!=1)then raise_application_error(-20886,'PICKER_TIME_SOURCE_NOT_CURRENT');end if;
   at_value:=systimestamp;
   RRL_PICKER_TIME_WRITE.apply_transition(p_actor,v.ACTION,v.OPERATION_ID,v.RESOURCE_SESSION_ID,ware,res,kind_value,id_value,reason_text,at_value,s);
   v.OUTCOME:='APPLIED';v.AFTER_VERSION:=s.STREAM_VERSION;
  exception when others then
   failure_code:=regexp_substr(sqlerrm,'PICKER_TIME_[A-Z0-9_]+');
   if sqlcode!=-20886 or failure_code is null or not recoverable(failure_code)then raise;end if;
   rollback to picker_time_effect;RRL_PICKER_TIME_READ.load_state(p_actor,s);
   v.OUTCOME:='REJECTED';v.ERROR_CODE:=failure_code;v.AFTER_VERSION:=s.STREAM_VERSION;at_value:=null;
  end;
  v.RESULT_JSON:=reply(v,s,at_value);
  insert into RRL_PICKER_TIME_COMMAND(OPERATION_ID,ACTOR_ID,WARE_ID,RESOURCE_SESSION_ID,ACTION,OUTCOME,ERROR_CODE,SOURCE_SHA256,SOURCE_JSON,RESULT_JSON,BEFORE_VERSION,AFTER_VERSION)
   values(v.OPERATION_ID,v.ACTOR_ID,v.WARE_ID,v.RESOURCE_SESSION_ID,v.ACTION,v.OUTCOME,v.ERROR_CODE,v.SOURCE_SHA256,v.SOURCE_JSON,v.RESULT_JSON,v.BEFORE_VERSION,v.AFTER_VERSION);
  p_result:=v.RESULT_JSON;clear_context(owned);
 exception when others then if saved then rollback to picker_time_effect;end if;clear_context(owned);raise;
 end;
end;
/
