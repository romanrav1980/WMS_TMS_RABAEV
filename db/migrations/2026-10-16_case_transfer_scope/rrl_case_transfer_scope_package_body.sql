create or replace package body RRL_CASE_TRANSFER_SCOPE as
 procedure authority(p_task number,p_actor varchar2,p_permission varchar2)is
  w number;owner_value nvarchar2(50);n number;
 begin
  select WARE_ID,ASSIGNED_TO into w,owner_value from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  if w is null or w<1 then raise_application_error(-20886,'CASE_TRANSFER_WARE_REQUIRED');end if;
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  if n!=1 then raise_application_error(-20882,'CASE_TRANSFER_ACTIVE_USER_REQUIRED');end if;
  select count(*)into n from RUSERS where ID=p_actor and RRL_HAS_WRIGHT(ID,p_permission)=1
   and(upper(trim(USER_GROUP))='GLOBAL_ADMIN'or WARE_ID=w);
  if n=1 then return;end if;
  if p_permission='case_pick_execute'then owner_value:=p_actor;end if;
  if RRL_ACCESS_API.allowed(p_actor,p_permission,'WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(w),owner_value)!=1
   then raise_application_error(-20882,'CASE_TRANSFER_CURRENT_SCOPE_REQUIRED');end if;
 exception when no_data_found then raise_application_error(-20886,'CASE_TRANSFER_TASK_MISSING');end;
 procedure assert_manager(p_task number,p_actor varchar2)is begin authority(p_task,p_actor,'case_pick_manage');end;
 procedure assert_target(p_task number,p_target varchar2)is begin authority(p_task,p_target,'case_pick_execute');end;
 procedure begin_change(p_task number,p_actor varchar2)is
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();release_state varchar2(20);owned boolean:=false;
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null then raise_application_error(-20886,'CASE_TRANSFER_OUTSIDE_STOCK_REQUIRED');end if;
  assert_manager(p_task,p_actor);
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE',6);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA');
  RRL_STOCK_LOCK_API.begin_plan;owned:=true;lock table RRL_ACCESS_REV in share mode wait 2;
  RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  select STATE into release_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if release_state is null or release_state not in('PREPARED','ACTIVE')then raise_application_error(-20860,'CASE_TRANSFER_RELEASE_CLOSED');end if;
  assert_manager(p_task,p_actor);
 exception when others then if owned then RRL_STOCK_LOCK_API.clear_plan;end if;raise;end;
end;
/
