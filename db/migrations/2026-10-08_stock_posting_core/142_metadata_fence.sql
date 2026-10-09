-- Rare metadata/placement changes take CONFIG X before any document or slot lock.
-- This grants no stock/configuration write context and cannot conduct quantities.
create or replace package RRL_STOCK_METADATA_TX authid definer as
 procedure begin_change(p_actor varchar2,p_permission varchar2);
 procedure end_change;
end;
/
create or replace package body RRL_STOCK_METADATA_TX as
 procedure begin_change(p_actor varchar2,p_permission varchar2) is
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();state varchar2(20);
 begin
  if p_actor is null or p_permission is null or p_permission not in('warehouse_task_assign','warehouse_task_edit','case_pick_execute','case_pick_short_approve','outgoing_pallet_edit')
   or RRL_HAS_WRIGHT(p_actor,p_permission)!=1 then raise_application_error(-20882,'TASK_METADATA_FORBIDDEN');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE',6);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA');
  RRL_STOCK_LOCK_API.begin_plan;RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if state is null or state not in('PREPARED','ACTIVE') then raise_application_error(-20860,'TASK_METADATA_RELEASE_CLOSED');end if;
 end;
 procedure end_change is begin RRL_STOCK_LOCK_API.clear_plan;end;
end;
/
