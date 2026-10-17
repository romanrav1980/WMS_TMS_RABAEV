create or replace package body RRL_CASE_REPORT_SCOPE as
 procedure admission(p_task number,p_actor varchar2)is begin
  RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,'case_pick_execute',p_actor);
 end;
 procedure begin_change(p_task number,p_actor varchar2)is
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();release_state varchar2(20);owned boolean:=false;
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null then raise_application_error(-20886,'CASE_REPORT_OUTSIDE_STOCK_REQUIRED');end if;
  admission(p_task,p_actor);
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE',6);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA');
  RRL_STOCK_LOCK_API.begin_plan;owned:=true;lock table RRL_ACCESS_REV in share mode wait 2;
  RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  select STATE into release_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if release_state is null or release_state not in('PREPARED','ACTIVE')then raise_application_error(-20860,'CASE_REPORT_RELEASE_CLOSED');end if;
  admission(p_task,p_actor);
 exception when others then if owned then RRL_STOCK_LOCK_API.clear_plan;end if;raise;end;
end;
/
