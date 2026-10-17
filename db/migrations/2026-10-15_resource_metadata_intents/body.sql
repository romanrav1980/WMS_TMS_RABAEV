create or replace package body RRL_RESOURCE_INTENT_API as
 procedure clear_context(p_owned boolean default false)is begin
  dbms_session.clear_context('RRL_RESOURCE_INTENT_CTX',null);if p_owned then RRL_STOCK_LOCK_API.clear_plan;end if;end;
 procedure verify_binding is begin
  dbms_session.set_context('RRL_RESOURCE_INTENT_CTX','VERIFY','READY');
  if sys_context('RRL_RESOURCE_INTENT_CTX','VERIFY')!='READY'then raise_application_error(-20886,'RESOURCE_INTENT_CONTEXT_INVALID');end if;clear_context;
 end;
 function write_allowed(p_control varchar2,p_domain varchar2,p_original varchar2)return number is tx varchar2(100):=sys_context('RRL_RESOURCE_INTENT_CTX','TX_ID');begin
  if tx is not null and tx=dbms_transaction.local_transaction_id(false)
   and sys_context('RRL_RESOURCE_INTENT_CTX','CONTROL')=p_control and sys_context('RRL_RESOURCE_INTENT_CTX','DOMAIN')=p_domain
   and sys_context('RRL_RESOURCE_INTENT_CTX','ORIGINAL')=p_original then return 1;end if;return 0;
 end;
 procedure authority(p_domain varchar2,p_task number,p_actor nvarchar2,p_action varchar2,p_target nvarchar2,p_version out number)is begin
  if p_actor is null or p_task is null or p_task<1 or p_task!=trunc(p_task)or p_target is null then raise_application_error(-20882,'RESOURCE_INTENT_CURRENT_ACTOR_REQUIRED');end if;
  if p_domain='CASE'then RRL_CASE_ASSIGNMENT_API.intent_authority(p_task,p_actor,p_action,p_target,p_version);
  elsif p_domain='TASK'then RRL_WTASK_ASSIGN_API.intent_authority(p_task,p_actor,p_action,p_target,p_version);
  else raise_application_error(-20886,'RESOURCE_INTENT_DOMAIN_REQUIRED');end if;
 end;
 function task_id(v RRL_RESOURCE_INTENT_ABANDON%rowtype)return number is begin return nvl(v.CASE_TASK_ID,v.TASK_ID);end;
 function hash(s clob)return varchar2 is begin return rawtohex(sys.dbms_crypto.hash(s,sys.dbms_crypto.hash_sh256));end;
 function original_lock(p_domain varchar2,p_operation varchar2)return varchar2 is begin
  return case when p_domain='CASE'then'CASE.RESOURCE:'else'WTASK.RESOURCE:'end||p_operation;end;
 procedure assert_available(p_domain varchar2,p_task number,p_actor nvarchar2,p_operation varchar2,p_original clob)is v RRL_RESOURCE_INTENT_ABANDON%rowtype;begin
  RRL_STOCK_LOCK_API.assert_held(10,RRL_STOCK_LOCK_API.resource_key('OP',original_lock(p_domain,p_operation)));
  begin select *into v from RRL_RESOURCE_INTENT_ABANDON where DOMAIN=p_domain and ORIGINAL_OPERATION_ID=p_operation;
  exception when no_data_found then return;end;
  if v.ACTOR_ID!=p_actor or task_id(v)!=p_task or dbms_lob.compare(v.ORIGINAL_JSON,p_original)!=0 then raise_application_error(-20886,'RESOURCE_INTENT_ORIGINAL_CONFLICT');end if;
  raise_application_error(-20886,'RESOURCE_INTENT_ABANDONED_READ_PROOF');
 end;
 procedure number_field(j json_object_t,k varchar2,minimum number,p_number out number)is element json_element_t;begin
  if not j.has(k)then raise_application_error(-20886,'RESOURCE_INTENT_ORIGINAL_FIELDS_REQUIRED');end if;element:=j.get(k);
  if element is null or not element.is_number then raise_application_error(-20886,'RESOURCE_INTENT_ORIGINAL_NUMBER_REQUIRED');end if;
  p_number:=j.get_number(k);if p_number is null or p_number<minimum or p_number!=trunc(p_number)then raise_application_error(-20886,'RESOURCE_INTENT_ORIGINAL_NUMBER_REQUIRED');end if;
 end;
 procedure parse_original(p_request clob,p_actor nvarchar2,v in out RRL_RESOURCE_INTENT_ABANDON%rowtype)is
  j json_object_t;old json_object_t;keys json_key_list;n number;domain_value varchar2(4);original_text varchar2(16384);task_value number;reason_value varchar2(4000);
 begin
  if p_request is null or dbms_lob.getlength(p_request)>32768 then raise_application_error(-20886,'RESOURCE_INTENT_BOUND_32K');end if;
  j:=json_object_t.parse(p_request);keys:=j.get_keys;
  for k in 1..keys.count loop if keys(k)not in('operation_id','domain','task_id','reason','original_wire')then raise_application_error(-20886,'RESOURCE_INTENT_UNKNOWN_FIELD');end if;end loop;
  v.CONTROL_OPERATION_ID:=j.get_string('operation_id');v.DOMAIN:=j.get_string('domain');v.ACTOR_ID:=p_actor;reason_value:=j.get_string('reason');
  number_field(j,'task_id',1,task_value);
  if v.DOMAIN='CASE'then v.CASE_TASK_ID:=task_value;elsif v.DOMAIN='TASK'then v.TASK_ID:=task_value;else raise_application_error(-20886,'RESOURCE_INTENT_DOMAIN_REQUIRED');end if;
  original_text:=j.get_string('original_wire');v.ORIGINAL_JSON:=original_text;
  if v.CONTROL_OPERATION_ID is null or not regexp_like(v.CONTROL_OPERATION_ID,'^[A-Za-z0-9_.:-]{1,100}$','c')
   or reason_value is null or length(trim(reason_value))not between 8 and 500 or original_text is null or lengthb(original_text)>16384 then raise_application_error(-20886,'RESOURCE_INTENT_EXPLICIT_CONTROL_REQUIRED');end if;
  old:=json_object_t.parse(v.ORIGINAL_JSON);keys:=old.get_keys;
  for k in 1..keys.count loop
   if keys(k)not in('operation_id','action','expected_assignment_version','resource_session_id','resource_id','equipment_id','reason','target','expected_task_signature')
    or(v.DOMAIN='CASE'and keys(k)in('target','expected_task_signature'))or(v.DOMAIN='TASK'and keys(k)='reason')then raise_application_error(-20886,'RESOURCE_INTENT_ORIGINAL_UNKNOWN_FIELD');end if;
  end loop;
  v.ORIGINAL_OPERATION_ID:=old.get_string('operation_id');v.ACTION:=old.get_string('action');
  number_field(old,'expected_assignment_version',0,v.ORIGINAL_EXPECTED_VERSION);number_field(old,'resource_session_id',1,n);
  if v.ORIGINAL_OPERATION_ID is null or not regexp_like(v.ORIGINAL_OPERATION_ID,'^[A-Za-z0-9_.:-]{1,100}$','c')or v.ORIGINAL_OPERATION_ID=v.CONTROL_OPERATION_ID
   or v.ACTION is null then raise_application_error(-20886,'RESOURCE_INTENT_ORIGINAL_ID_REQUIRED');end if;
  for key_value in(select 'resource_id' K from dual union all select 'equipment_id'from dual)loop
   if not old.has(key_value.K)then raise_application_error(-20886,'RESOURCE_INTENT_ORIGINAL_FIELDS_REQUIRED');end if;
   if not old.get(key_value.K).is_null then number_field(old,key_value.K,1,n);end if;
  end loop;
  if v.DOMAIN='CASE'then
   if v.ACTION not in('CLAIM','START')or old.get_string('reason')is null or length(trim(old.get_string('reason')))not between 8 and 500 then raise_application_error(-20886,'RESOURCE_INTENT_CASE_ORIGINAL_REQUIRED');end if;v.TARGET_ID:=p_actor;
  else
   v.TARGET_ID:=old.get_string('target');
   if v.ACTION not in('ASSIGN','START')or v.TARGET_ID is null or length(v.TARGET_ID)>100 or old.get_string('expected_task_signature')is null
    or not regexp_like(old.get_string('expected_task_signature'),'^[A-Fa-f0-9]{64}$','c')then raise_application_error(-20886,'RESOURCE_INTENT_TASK_ORIGINAL_REQUIRED');end if;
  end if;
  v.ORIGINAL_SHA256:=hash(v.ORIGINAL_JSON);v.CONTROL_SHA256:=hash(p_request);v.SOURCE_JSON:=p_request;v.RECORDED_AT:=systimestamp;
 end;
 procedure original_receipt(p_domain varchar2,p_task number,p_operation varchar2,p_actor nvarchar2,p_action varchar2,p_target nvarchar2,p_sha varchar2,p_result out clob)is
  c RRL_CASE_RESOURCE_COMMAND%rowtype;t RRL_WTASK_RESOURCE_COMMAND%rowtype;
 begin
  if p_domain='CASE'then
   select *into c from RRL_CASE_RESOURCE_COMMAND where OPERATION_ID=p_operation;
   if c.ACTOR_ID!=p_actor or c.CASE_PICK_TASK_ID!=p_task then raise_application_error(-20882,'RESOURCE_INTENT_ORIGINAL_ACTOR_REQUIRED');end if;
   if c.ACTION!=p_action or p_target!=p_actor or c.SOURCE_SHA256!=p_sha then raise_application_error(-20886,'RESOURCE_INTENT_ORIGINAL_CONFLICT');end if;p_result:=c.RESULT_JSON;
  else
   select *into t from RRL_WTASK_RESOURCE_COMMAND where OPERATION_ID=p_operation;
   if t.ACTOR_ID!=p_actor or t.TASK_ID!=p_task then raise_application_error(-20882,'RESOURCE_INTENT_ORIGINAL_ACTOR_REQUIRED');end if;
   if t.ACTION!=p_action or t.TARGET_ID!=p_target or t.SOURCE_SHA256!=p_sha then raise_application_error(-20886,'RESOURCE_INTENT_ORIGINAL_CONFLICT');end if;p_result:=t.RESULT_JSON;
  end if;
 end;
 procedure describe(p_control varchar2,p_actor nvarchar2,p_result out clob)is v RRL_RESOURCE_INTENT_ABANDON%rowtype;n number;begin
  select *into v from RRL_RESOURCE_INTENT_ABANDON where CONTROL_OPERATION_ID=p_control;
  if p_actor is null or v.ACTOR_ID!=p_actor then raise_application_error(-20882,'RESOURCE_INTENT_ORIGINAL_ACTOR_REQUIRED');end if;
  authority(v.DOMAIN,task_id(v),p_actor,v.ACTION,v.TARGET_ID,n);p_result:=v.RESULT_JSON;
 end;
 procedure resolve(p_domain varchar2,p_task number,p_operation varchar2,p_action varchar2,p_target nvarchar2,p_sha varchar2,p_actor nvarchar2,p_result out clob)is
  v RRL_RESOURCE_INTENT_ABANDON%rowtype;j json_object_t:=json_object_t();wire clob;n number;
 begin
  if p_operation is null or p_sha is null or not regexp_like(p_sha,'^[A-F0-9]{64}$','c')then raise_application_error(-20886,'RESOURCE_INTENT_QUERY_REQUIRED');end if;
  authority(p_domain,p_task,p_actor,p_action,p_target,n);
  j.put('domain',p_domain);j.put('task_id',p_task);j.put('actor',p_actor);j.put('original_operation_id',p_operation);j.put('original_request_sha256',p_sha);
  begin original_receipt(p_domain,p_task,p_operation,p_actor,p_action,p_target,p_sha,wire);
   j.put('status','RECORDED');j.put('original_receipt',json_object_t.parse(wire));j.put_null('abandonment');p_result:=j.to_clob;return;
  exception when no_data_found then null;end;
  select *into v from RRL_RESOURCE_INTENT_ABANDON where DOMAIN=p_domain and ORIGINAL_OPERATION_ID=p_operation;
  if v.ACTOR_ID!=p_actor or task_id(v)!=p_task then raise_application_error(-20882,'RESOURCE_INTENT_ORIGINAL_ACTOR_REQUIRED');end if;
  if v.ACTION!=p_action or v.TARGET_ID!=p_target or v.ORIGINAL_SHA256!=p_sha then raise_application_error(-20886,'RESOURCE_INTENT_ORIGINAL_CONFLICT');end if;
  j.put('status','ABANDONED');j.put_null('original_receipt');j.put('abandonment',json_object_t.parse(v.RESULT_JSON));p_result:=j.to_clob;
 end;
 procedure locks(v RRL_RESOURCE_INTENT_ABANDON%rowtype,p_owned out boolean)is
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();wave_id number;n number;source_value varchar2(40);doc_id number;release_state varchar2(20);user_value nvarchar2(100);local_owned boolean:=false;
 begin
  p_owned:=false;
  if v.DOMAIN='CASE'then
   select PICK_WAVE_ID into wave_id from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=v.CASE_TASK_ID;
   if wave_id is null then raise_application_error(-20886,'RESOURCE_INTENT_WAVE_REQUIRED');end if;
  else select TASK_SOURCE,SOURCE_DOC_ID into source_value,doc_id from RRL_WAREHOUSE_TASK where TASK_ID=v.TASK_ID;end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE',6);
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',original_lock(v.DOMAIN,v.ORIGINAL_OPERATION_ID));
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP','RESOURCE.INTENT:'||v.CONTROL_OPERATION_ID);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA');
  if v.DOMAIN='CASE'or source_value='WAVE'then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(nvl(wave_id,doc_id)));end if;
  if v.DOMAIN='CASE'then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v.CASE_TASK_ID));
  else RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v.TASK_ID));end if;
  RRL_STOCK_PLAN_HELPER.row_key(r,'RUSERS',v.ACTOR_ID);RRL_STOCK_PLAN_HELPER.row_key(r,'RUSERS',v.TARGET_ID);
  RRL_STOCK_LOCK_API.begin_plan;local_owned:=true;p_owned:=true;lock table RRL_ACCESS_REV in share mode wait 2;
  RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  select STATE into release_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if release_state is null or release_state not in('PREPARED','ACTIVE')then raise_application_error(-20886,'RESOURCE_INTENT_RELEASE_CLOSED');end if;
  if v.DOMAIN='CASE'or source_value='WAVE'then select PICK_WAVE_ID into n from RRL_PICK_WAVE where PICK_WAVE_ID=nvl(wave_id,doc_id)for update;end if;
  if v.DOMAIN='CASE'then
   select PICK_WAVE_ID into n from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=v.CASE_TASK_ID for update;
   if n is null or n!=wave_id then raise_application_error(-20886,'RESOURCE_INTENT_SOURCE_CHANGED');end if;
  else
   declare current_source varchar2(40);current_doc number;begin
    select TASK_SOURCE,SOURCE_DOC_ID into current_source,current_doc from RRL_WAREHOUSE_TASK where TASK_ID=v.TASK_ID for update;
    if current_source is null or current_source!=source_value or nvl(current_doc,-1)!=nvl(doc_id,-1)then raise_application_error(-20886,'RESOURCE_INTENT_SOURCE_CHANGED');end if;
   end;
  end if;
  for u in(select ID from RUSERS where ID in(v.ACTOR_ID,v.TARGET_ID)order by ID for update)loop user_value:=u.ID;end loop;
 exception when others then if local_owned then RRL_STOCK_LOCK_API.clear_plan;end if;raise;end;
 procedure abandon(p_request clob,p_actor nvarchar2,p_result out clob)is
  v RRL_RESOURCE_INTENT_ABANDON%rowtype;old RRL_RESOURCE_INTENT_ABANDON%rowtype;j json_object_t:=json_object_t();wire clob;owned boolean:=false;n number;
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null then raise_application_error(-20886,'RESOURCE_INTENT_OUTSIDE_STOCK_REQUIRED');end if;
  parse_original(p_request,p_actor,v);authority(v.DOMAIN,task_id(v),p_actor,v.ACTION,v.TARGET_ID,n);
  locks(v,owned);authority(v.DOMAIN,task_id(v),p_actor,v.ACTION,v.TARGET_ID,v.VERSION_AT_ABANDON);
  begin select *into old from RRL_RESOURCE_INTENT_ABANDON where CONTROL_OPERATION_ID=v.CONTROL_OPERATION_ID;
   if old.ACTOR_ID!=p_actor then raise_application_error(-20882,'RESOURCE_INTENT_ORIGINAL_ACTOR_REQUIRED');end if;
   if dbms_lob.compare(old.SOURCE_JSON,p_request)!=0 then raise_application_error(-20886,'RESOURCE_INTENT_CONTROL_CONFLICT');end if;
   p_result:=old.RESULT_JSON;clear_context(owned);return;exception when no_data_found then null;end;
  begin original_receipt(v.DOMAIN,task_id(v),v.ORIGINAL_OPERATION_ID,p_actor,v.ACTION,v.TARGET_ID,v.ORIGINAL_SHA256,wire);
   raise_application_error(-20886,'RESOURCE_INTENT_RECORDED_READ_REQUIRED');exception when no_data_found then null;end;
  begin select *into old from RRL_RESOURCE_INTENT_ABANDON where DOMAIN=v.DOMAIN and ORIGINAL_OPERATION_ID=v.ORIGINAL_OPERATION_ID;
   raise_application_error(-20886,'RESOURCE_INTENT_ALREADY_ABANDONED_READ_ORIGINAL_CONTROL');exception when no_data_found then null;end;
  j.put('operation_id',v.CONTROL_OPERATION_ID);j.put('status','ABANDONED');j.put('domain',v.DOMAIN);j.put('task_id',task_id(v));j.put('actor',p_actor);j.put('action',v.ACTION);j.put('target',v.TARGET_ID);
  j.put('original_operation_id',v.ORIGINAL_OPERATION_ID);j.put('original_wire',dbms_lob.substr(v.ORIGINAL_JSON,16384,1));j.put('original_request_sha256',v.ORIGINAL_SHA256);j.put('control_request_sha256',v.CONTROL_SHA256);
  j.put('original_expected_assignment_version',v.ORIGINAL_EXPECTED_VERSION);j.put('assignment_version_at_abandon',v.VERSION_AT_ABANDON);j.put('outcome_confirmed',true);j.put('stock_posted',false);v.RESULT_JSON:=j.to_clob;
  dbms_session.set_context('RRL_RESOURCE_INTENT_CTX','TX_ID',dbms_transaction.local_transaction_id(true));dbms_session.set_context('RRL_RESOURCE_INTENT_CTX','CONTROL',v.CONTROL_OPERATION_ID);
  dbms_session.set_context('RRL_RESOURCE_INTENT_CTX','DOMAIN',v.DOMAIN);dbms_session.set_context('RRL_RESOURCE_INTENT_CTX','ORIGINAL',v.ORIGINAL_OPERATION_ID);
  insert into RRL_RESOURCE_INTENT_ABANDON values v;p_result:=v.RESULT_JSON;clear_context(owned);
 exception when others then clear_context(owned);raise;end;
end;
/


