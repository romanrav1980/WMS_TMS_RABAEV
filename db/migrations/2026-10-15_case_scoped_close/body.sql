create or replace package body RRL_CASE_LIFECYCLE_API as
 g_tx varchar2(100);g_task number;g_wave number;g_actor nvarchar2(100);
 procedure forget is begin g_tx:=null;g_task:=null;g_wave:=null;g_actor:=null;end;
 procedure authority(p_task number,p_actor nvarchar2)is begin
  if p_task is null or p_task<1 or p_task!=trunc(p_task)or p_actor is null then raise_application_error(-20882,'CASE_CLOSE_CURRENT_ACTOR_REQUIRED');end if;
  if RRL_HAS_WRIGHT(p_actor,'case_pick_execute')=1 then RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,'case_pick_execute');return;end if;
  if RRL_CASE_TASK_ACCESS.has_current_scoped_execute(p_task,p_actor)!=1 then raise_application_error(-20882,'CASE_CLOSE_CURRENT_SCOPE_REQUIRED');end if;
 end;
 procedure held(p_task number,p_actor nvarchar2)is begin
  if p_task is null or p_actor is null or g_tx is null or dbms_transaction.local_transaction_id(false)is null
   or g_tx!=dbms_transaction.local_transaction_id(false)or g_task is null or g_task!=p_task
   or g_actor is null or g_actor!=p_actor then raise_application_error(-20882,'CASE_CLOSE_OWN_CONTEXT_REQUIRED');end if;
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('RELEASE','STOCK'),4);
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA'));
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(g_wave)));
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(p_task)));
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RUSERS',p_actor));
 end;
 procedure task_current_scope(p_task number,p_actor nvarchar2)is wave_value number;begin
  held(p_task,p_actor);authority(p_task,p_actor);
  select PICK_WAVE_ID into wave_value from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  if wave_value is null or wave_value!=g_wave then raise_application_error(-20886,'CASE_CLOSE_SOURCE_CHANGED');end if;
 end;
 procedure assert_new_close(p_task number,p_actor nvarchar2)is n number;begin
  task_current_scope(p_task,p_actor);
  if RRL_HAS_WRIGHT(p_actor,'case_pick_execute')=1 then return;end if;
  if RRL_CASE_TASK_ACCESS.scoped_executor(p_task,p_actor)!=1 then raise_application_error(-20886,'CASE_CLOSE_ORDINARY_SCOPED_CONTEXT_REQUIRED');end if;
  select count(*)into n from RRL_ASSEMBLY_SESSION where CASE_PICK_TASK_ID=p_task and STATE in('OPEN','BLOCKED','HOLD');
  if n!=0 then raise_application_error(-20886,'CASE_CLOSE_ASSEMBLY_OWNER_REQUIRED');end if;
 end;
 procedure begin_close(p_task number,p_actor nvarchar2)is
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();wave_value number;current_wave number;n number;
  release_state varchar2(20);locked_actor nvarchar2(100);owned boolean:=false;
 begin
  if g_tx is not null and g_tx=dbms_transaction.local_transaction_id(false)then raise_application_error(-20886,'CASE_CLOSE_NESTED_CONTEXT_FORBIDDEN');end if;
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null then raise_application_error(-20886,'CASE_CLOSE_OUTSIDE_STOCK_REQUIRED');end if;
  authority(p_task,p_actor);
  select PICK_WAVE_ID into wave_value from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  if wave_value is null then raise_application_error(-20886,'CASE_CLOSE_WAVE_REQUIRED');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE',6);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA');
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(wave_value));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(p_task));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RUSERS',p_actor);
  RRL_STOCK_LOCK_API.begin_plan;owned:=true;lock table RRL_ACCESS_REV in share mode wait 2;
  RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  select STATE into release_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if release_state is null or release_state not in('PREPARED','ACTIVE')then raise_application_error(-20860,'CASE_CLOSE_RELEASE_CLOSED');end if;
  select PICK_WAVE_ID into n from RRL_PICK_WAVE where PICK_WAVE_ID=wave_value for update;
  select PICK_WAVE_ID into current_wave from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task for update;
  select ID into locked_actor from RUSERS where ID=p_actor for update;
  if current_wave is null or current_wave!=wave_value then raise_application_error(-20886,'CASE_CLOSE_SOURCE_CHANGED');end if;
  g_tx:=dbms_transaction.local_transaction_id(true);g_task:=p_task;g_wave:=wave_value;g_actor:=p_actor;
  task_current_scope(p_task,p_actor);
 exception when others then if owned then forget;RRL_STOCK_LOCK_API.clear_plan;end if;raise;end;
 procedure end_close is begin
  if g_tx is not null and g_tx=dbms_transaction.local_transaction_id(false)then RRL_STOCK_LOCK_API.clear_plan;end if;
  forget;
 end;
end;
/
