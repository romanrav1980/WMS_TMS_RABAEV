create or replace package RRL_STORE_ORDER_SCOPE authid definer as
 procedure actor_scope(p_actor varchar2,p_permission varchar2,p_ware out number,p_global out number);
 procedure assert_scope(p_actor varchar2,p_permission varchar2,p_ware number);
 procedure begin_source(p_actor varchar2,p_permission varchar2,p_ware number,p_order number default null);
 procedure end_source;
end;
/
create or replace package body RRL_STORE_ORDER_SCOPE as
 procedure actor_scope(p_actor varchar2,p_permission varchar2,p_ware out number,p_global out number)is begin
  if p_permission is null or p_permission not in('customer_order_view','sap_store_order_import','customer_order_import','sap_store_decision_import')then raise_application_error(-20882,'STORE_ORDER_SCOPE_PERMISSION_REQUIRED');end if;
  begin
   select WARE_ID,case when upper(trim(USER_GROUP))='GLOBAL_ADMIN'
    or(p_permission in('sap_store_order_import','sap_store_decision_import')and RRL_HAS_WRIGHT(ID,'sap_store_all_ware')=1)then 1 else 0 end into p_ware,p_global
    from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,p_permission)=1;
  exception when no_data_found then raise_application_error(-20882,'STORE_ORDER_CURRENT_ACTOR_REQUIRED');end;
  if p_global=0 and(p_ware is null or p_ware<=0)then raise_application_error(-20882,'STORE_ORDER_CURRENT_WARE_REQUIRED');end if;
 end;
 procedure assert_scope(p_actor varchar2,p_permission varchar2,p_ware number)is own_ware number;v_global number;begin
  actor_scope(p_actor,p_permission,own_ware,v_global);
  if p_ware is null or p_ware<=0 or(v_global=0 and p_ware!=own_ware)then raise_application_error(-20882,'STORE_ORDER_CURRENT_WARE_FORBIDDEN');end if;
 end;
 procedure begin_source(p_actor varchar2,p_permission varchar2,p_ware number,p_order number default null)is
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();
 begin
  if p_permission not in('sap_store_order_import','customer_order_import')then raise_application_error(-20882,'STORE_ORDER_SOURCE_COMMAND_REQUIRED');end if;
  assert_scope(p_actor,p_permission,p_ware);
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE',4);
  RRL_STOCK_LOCK_API.begin_plan;RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);
  if p_order is not null then
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(p_order));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SAP_STORE_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(p_order));
  end if;
  RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  assert_scope(p_actor,p_permission,p_ware);
 exception when others then RRL_STOCK_LOCK_API.clear_plan;raise;
 end;
 procedure end_source is begin RRL_STOCK_LOCK_API.clear_plan;end;
end;
/
