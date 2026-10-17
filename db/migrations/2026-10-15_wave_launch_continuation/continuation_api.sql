create or replace package RRL_WAVE_CONTINUE_API authid definer as
 procedure assert_launch(p_operation varchar2,p_wave number,p_actor varchar2);
 procedure begin_step(p_operation varchar2,p_wave number,p_actor varchar2,p_step number,p_run out number);
 procedure assert_context(p_wave number,p_actor varchar2);
 procedure freeze_sources(p_requests clob);
 procedure finish_step;
 procedure fail_step(p_code varchar2);
 procedure end_step;
 procedure assert_source(p_request clob,p_actor varchar2);
 function source_allowed(p_request clob,p_actor varchar2)return number;
 function writing return number;
end;
/
create or replace package body RRL_WAVE_CONTINUE_API as
 g_operation varchar2(100);g_wave number;g_actor varchar2(50);g_step number;g_write boolean:=false;g_tx varchar2(100);
 function writing return number is
 begin
  if g_write and g_tx is not null and g_tx=dbms_transaction.local_transaction_id(false) then return 1;end if;return 0;
 end;
 procedure assert_launch(p_operation varchar2,p_wave number,p_actor varchar2)is
  n number;ware number;
 begin
  select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=p_operation and COMMAND_TYPE='WAVE_LAUNCH'
   and STATE='APPLIED' and ACTOR=p_actor
   and json_value(CANONICAL_REQUEST,'$.source.wave_id' returning number null on error)=p_wave;
  if n!=1 then raise_application_error(-20882,'WAVE_CONTINUATION_ORIGINAL_LAUNCH_REQUIRED');end if;
  select WARE_ID into ware from RRL_PICK_WAVE where PICK_WAVE_ID=p_wave;
  if ware is null or RRL_ACCESS_API.allowed(p_actor,'pick_wave_launch','WAREHOUSE',to_char(ware))!=1 then
   raise_application_error(-20882,'WAVE_CONTINUATION_CURRENT_WARE_REQUIRED');end if;
 end;
 procedure assert_context(p_wave number,p_actor varchar2)is
 begin
  if g_operation is null or g_wave!=p_wave or g_actor!=p_actor or g_tx is null
    or nvl(dbms_transaction.local_transaction_id(false),'-')!=g_tx then
   raise_application_error(-20882,'WAVE_CONTINUATION_CONTEXT_REQUIRED');end if;
  assert_launch(g_operation,p_wave,p_actor);
 end;
 procedure begin_step(p_operation varchar2,p_wave number,p_actor varchar2,p_step number,p_run out number)is
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();n number;st varchar2(40);released date;
  previous number;op varchar2(100);nm varchar2(40);release_state varchar2(20);
 begin
  if g_operation is not null then raise_application_error(-20882,'WAVE_CONTINUATION_NESTED_CONTEXT');end if;
  if p_step is null or p_step not between 1 and 7 or p_step!=trunc(p_step) then raise_application_error(-20881,'WAVE_CONTINUATION_STEP_REQUIRED');end if;
  assert_launch(p_operation,p_wave,p_actor);
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE',6);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA');
  RRL_STOCK_LOCK_API.begin_plan;
  g_tx:=dbms_transaction.local_transaction_id(true);
  lock table RRL_ACCESS_REV in share mode wait 5;
  RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  assert_launch(p_operation,p_wave,p_actor);
  select STATE into release_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if release_state!='ACTIVE' or release_state is null then raise_application_error(-20860,'WAVE_CONTINUATION_RELEASE_CLOSED');end if;
  select STATUS,PICK_RELEASED_AT into st,released from RRL_PICK_WAVE where PICK_WAVE_ID=p_wave for update;
  g_operation:=p_operation;g_wave:=p_wave;g_actor:=p_actor;g_step:=p_step;
  select count(*)into n from RRL_WAVE_CONTINUE where LAUNCH_OPERATION_ID=p_operation;
  if n=0 then
   if st!='LAUNCHED' or released is not null then raise_application_error(-20886,'WAVE_CONTINUATION_RECONCILIATION_REQUIRED');end if;
   g_write:=true;
   insert into RRL_WAVE_CONTINUE(LAUNCH_OPERATION_ID,PICK_WAVE_ID,ACTOR,STATE)values(p_operation,p_wave,p_actor,'PENDING');
   for i in 1..7 loop
    nm:=case i when 1 then 'SETTINGS' when 2 then 'DEFICIT' when 3 then 'RESERVE_SOURCES'
     when 4 then 'PICK_FACE_CAPACITY' when 5 then 'RELEASE_QUEUE' when 6 then 'WAREHOUSE_TASKS' else 'CASE_TASKS' end;
    insert into RRL_WAVE_CONTINUE_STEP(LAUNCH_OPERATION_ID,STEP_NO,STEP_NAME,STATE)values(p_operation,i,nm,'PENDING');
   end loop;
   g_write:=false;
  end if;
  select LAUNCH_OPERATION_ID into op from RRL_WAVE_CONTINUE where LAUNCH_OPERATION_ID=p_operation
   and PICK_WAVE_ID=p_wave and ACTOR=p_actor for update;
  select STATE into st from RRL_WAVE_CONTINUE_STEP where LAUNCH_OPERATION_ID=p_operation and STEP_NO=p_step;
  p_run:=case when st='DONE' then 0 else 1 end;
  if p_run=1 then
   select count(*)into previous from RRL_WAVE_CONTINUE_STEP where LAUNCH_OPERATION_ID=p_operation and STEP_NO<p_step and STATE!='DONE';
   if previous!=0 then raise_application_error(-20886,'WAVE_CONTINUATION_PREVIOUS_STEP_PENDING');end if;
   select STATUS,PICK_RELEASED_AT into st,released from RRL_PICK_WAVE where PICK_WAVE_ID=p_wave;
   if st!='LAUNCHED' or released is not null then raise_application_error(-20886,'WAVE_CONTINUATION_RECONCILIATION_REQUIRED');end if;
  end if;
 exception when others then end_step;raise;
 end;
 procedure freeze_sources(p_requests clob)is
  a json_array_t:=json_array_t.parse(p_requests);d json_object_t;m json_object_t;s json_object_t;ids json_array_t;
  raw_body clob;op varchar2(100);row_id number;saved_op varchar2(100);saved_body clob;n number;frozen number;
 begin
  assert_context(g_wave,g_actor);
  if g_step!=3 then raise_application_error(-20882,'WAVE_SOURCE_FREEZE_STEP_REQUIRED');end if;
  select SOURCES_FROZEN into frozen from RRL_WAVE_CONTINUE where LAUNCH_OPERATION_ID=g_operation;
  if frozen=1 then raise_application_error(-20886,'WAVE_SOURCE_INTENTS_ALREADY_FROZEN');end if;
  if a.get_size>200 then raise_application_error(-20881,'WAVE_SOURCE_INTENT_BOUND_200');end if;
  for i in 0..a.get_size-1 loop
   raw_body:=to_clob(a.get_string(i));d:=json_object_t.parse(raw_body);m:=d.get_object('metadata');s:=d.get_object('source');
   if dbms_lob.getlength(raw_body)>4000 then raise_application_error(-20881,'WAVE_SOURCE_SAVED_REQUEST_BOUND_4000');end if;
   ids:=m.get_array('requested_row_ids');op:=d.get_string('operation_id');
   if nvl(d.get_string('command_type'),'-')!='WAVE_RESERVE_SOURCES' or nvl(s.get_number('wave_id'),-1)!=g_wave or ids is null or ids.get_size!=1 then
    raise_application_error(-20882,'WAVE_SOURCE_INTENT_IDENTITY_CONFLICT');end if;
   row_id:=ids.get_number(0);
   select RESERVE_OPERATION_ID,RESERVE_REQUEST_JSON into saved_op,saved_body from RRL_PICK_WAVE_REPLENISH_TASK
    where PICK_WAVE_REPLENISH_TASK_ID=row_id and PICK_WAVE_ID=g_wave for update;
   if saved_op is not null then
    if saved_op!=op or saved_body is null or dbms_lob.compare(saved_body,raw_body)!=0 then
     raise_application_error(-20882,'WAVE_SOURCE_EXISTING_INTENT_IMMUTABLE');end if;
   elsif nvl(d.get_string('actor'),'-')!=g_actor then raise_application_error(-20882,'WAVE_SOURCE_ORIGINAL_ACTOR_REQUIRED');end if;
   if nvl(d.get_string('actor'),'-')!=g_actor then
    select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=op and COMMAND_TYPE='WAVE_RESERVE_SOURCES'
     and STATE='APPLIED' and dbms_lob.compare(CANONICAL_REQUEST,raw_body)=0;
    if n!=1 then raise_application_error(-20882,'WAVE_SOURCE_PENDING_ACTOR_CONFLICT');end if;
   end if;
   g_write:=true;
   insert into RRL_WAVE_CONTINUE_SOURCE(LAUNCH_OPERATION_ID,REPLENISH_TASK_ID,SOURCE_OPERATION_ID,CANONICAL_REQUEST)
    values(g_operation,row_id,op,raw_body);
   if saved_op is null then
    update RRL_PICK_WAVE_REPLENISH_TASK set RESERVE_OPERATION_ID=op,RESERVE_REQUEST_JSON=raw_body,
     STATUS=case when STATUS='FAILED' then 'RELEASED' else STATUS end,
     UPDATED_AT=sysdate,UPDATED_BY=g_actor where PICK_WAVE_REPLENISH_TASK_ID=row_id;
   end if;
   g_write:=false;
  end loop;
  g_write:=true;update RRL_WAVE_CONTINUE set SOURCES_FROZEN=1,UPDATED_AT=systimestamp where LAUNCH_OPERATION_ID=g_operation;g_write:=false;
 exception when others then end_step;raise;
 end;
 function source_allowed(p_request clob,p_actor varchar2)return number is
  d json_object_t:=json_object_t.parse(p_request);parent varchar2(100);wave number;actor varchar2(50);saved clob;n number;op varchar2(100);
 begin
  op:=d.get_string('operation_id');
  begin
   select c.LAUNCH_OPERATION_ID,c.PICK_WAVE_ID,c.ACTOR,s.CANONICAL_REQUEST into parent,wave,actor,saved
    from RRL_WAVE_CONTINUE_SOURCE s join RRL_WAVE_CONTINUE c on c.LAUNCH_OPERATION_ID=s.LAUNCH_OPERATION_ID
    where s.SOURCE_OPERATION_ID=op;
  exception when no_data_found then
   if d.get_object('metadata').has('launch_operation_id') then raise_application_error(-20882,'WAVE_SOURCE_FROZEN_INTENT_REQUIRED');end if;
   return 0;
  end;
  if nvl(d.get_string('actor'),'-')!=p_actor or dbms_lob.compare(saved,p_request)!=0 then
   raise_application_error(-20882,'WAVE_SOURCE_FROZEN_IDENTITY_CONFLICT');end if;
  if actor!=p_actor then
   -- Older APPLIED source decisions are references only; preserve their original legacy replay contract.
   select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=op and STATE='APPLIED';
   if n=1 then return 0;end if;
   raise_application_error(-20882,'WAVE_SOURCE_PENDING_ACTOR_CONFLICT');
  end if;
  assert_launch(parent,wave,p_actor);return 1;
 end;
 procedure assert_source(p_request clob,p_actor varchar2)is n number;
 begin n:=source_allowed(p_request,p_actor);end;
 procedure finish_step is n number;
 begin
  assert_context(g_wave,g_actor);
  if g_step=3 then
   select SOURCES_FROZEN into n from RRL_WAVE_CONTINUE where LAUNCH_OPERATION_ID=g_operation;
   if n!=1 then raise_application_error(-20886,'WAVE_SOURCE_INTENTS_NOT_FROZEN');end if;
   select count(*)into n from RRL_WAVE_CONTINUE_SOURCE s where s.LAUNCH_OPERATION_ID=g_operation and not exists(
    select 1 from RRL_STOCK_OPERATION o where o.OPERATION_ID=s.SOURCE_OPERATION_ID and o.COMMAND_TYPE='WAVE_RESERVE_SOURCES'
     and o.STATE='APPLIED' and dbms_lob.compare(o.CANONICAL_REQUEST,s.CANONICAL_REQUEST)=0);
   if n!=0 then raise_application_error(-20886,'WAVE_SOURCE_OUTCOME_UNCONFIRMED');end if;
  end if;
  g_write:=true;
  update RRL_WAVE_CONTINUE_STEP set STATE='DONE',COMPLETED_AT=systimestamp,ERROR_CODE=null
   where LAUNCH_OPERATION_ID=g_operation and STEP_NO=g_step and STATE!='DONE';
  select count(*)into n from RRL_WAVE_CONTINUE_STEP where LAUNCH_OPERATION_ID=g_operation and STATE!='DONE';
  update RRL_WAVE_CONTINUE set STATE=case when n=0 then 'COMPLETE' else 'PENDING' end,UPDATED_AT=systimestamp where LAUNCH_OPERATION_ID=g_operation;
  g_write:=false;
 exception when others then end_step;raise;
 end;
 procedure fail_step(p_code varchar2)is
 begin
  assert_context(g_wave,g_actor);g_write:=true;
  update RRL_WAVE_CONTINUE_STEP set STATE='FAILED',ERROR_CODE=substr(p_code,1,100)
   where LAUNCH_OPERATION_ID=g_operation and STEP_NO=g_step and STATE!='DONE';
  if sql%rowcount=1 then update RRL_WAVE_CONTINUE set STATE='FAILED',UPDATED_AT=systimestamp where LAUNCH_OPERATION_ID=g_operation;end if;
  g_write:=false;
 exception when others then end_step;raise;
 end;
 procedure end_step is
 begin g_operation:=null;g_wave:=null;g_actor:=null;g_step:=null;g_tx:=null;g_write:=false;RRL_STOCK_LOCK_API.clear_plan;end;
end;
/
