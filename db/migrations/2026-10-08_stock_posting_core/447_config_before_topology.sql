create or replace package RRL_STOCK_CONFIG_API authid definer as
 procedure begin_change(p_actor varchar2,p_permission varchar2);
 procedure end_change;
end;
/
create or replace package body RRL_STOCK_CONFIG_API as
 procedure begin_change(p_actor varchar2,p_permission varchar2) is
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();v_state varchar2(20);
 begin
  if p_actor is null or p_permission is null or p_permission not in('warehouse_settings_edit','finished_goods_edit','sap_article_import')
   or RRL_HAS_WRIGHT(p_actor,p_permission)!=1 then raise_application_error(-20882,'CONFIGURATION_FORBIDDEN');end if;
  select STATE into v_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if v_state not in('PREPARED','ACTIVE') then raise_application_error(-20860,'CONFIGURATION_RELEASE_CLOSED');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE',6);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_POLICY_GUARD','WAREHOUSE.CONFIGURATION');
  RRL_STOCK_LOCK_API.begin_plan;RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  select STATE into v_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if v_state not in('PREPARED','ACTIVE') then raise_application_error(-20860,'CONFIGURATION_RELEASE_CLOSED');end if;
  RRL_STOCK_CTX_API.open_configuration(p_actor,p_permission);
 end;
 procedure end_change is
 begin RRL_STOCK_CTX_API.clear_operation;RRL_STOCK_LOCK_API.clear_plan;end;
end;
/
