create or replace package body RRL_ASM_META_SCOPE as
 procedure begin_change(p_task number,p_actor nvarchar2)is
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();release_state varchar2(20);owned boolean:=false;
  procedure authority is begin
   if RRL_HAS_WRIGHT(p_actor,'case_pick_execute')=1 then return;end if;
   if RRL_CASE_TASK_ACCESS.scoped_assembly_executor(p_task,p_actor)!=1 then raise_application_error(-20882,'ASSEMBLY_CURRENT_SCOPED_OPERATOR_REQUIRED');end if;
  end;
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null then raise_application_error(-20886,'ASSEMBLY_METADATA_OUTSIDE_STOCK_REQUIRED');end if;
  authority;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE',6);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA');
  RRL_STOCK_LOCK_API.begin_plan;owned:=true;
  lock table RRL_ACCESS_REV in share mode wait 2;
  RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  select STATE into release_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if release_state is null or release_state not in('PREPARED','ACTIVE')then raise_application_error(-20860,'ASSEMBLY_METADATA_RELEASE_CLOSED');end if;
  authority;
 exception when others then if owned then RRL_STOCK_LOCK_API.clear_plan;end if;raise;
 end;
end;
/
