create or replace package RRL_PICK_PLAN_ACCESS authid definer as
 procedure assert_scope(p_order number,p_actor varchar2,p_permission varchar2 default 'pick_plan_create');
end;
/
create or replace package body RRL_PICK_PLAN_ACCESS as
 procedure assert_scope(p_order number,p_actor varchar2,p_permission varchar2 default 'pick_plan_create')is
  ware number;uware number;grp varchar2(100);n number;
 begin
  begin select WARE_ID into ware from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=p_order;
  exception when no_data_found then raise_application_error(-20886,'PICK_ORDER_IDENTITY_MISSING');end;
  if ware is null or ware<1 then raise_application_error(-20886,'PICK_ORDER_WARE_REQUIRED');end if;
  select count(*),max(WARE_ID),max(USER_GROUP)into n,uware,grp from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  if n!=1 then raise_application_error(-20882,'PICK_PLAN_ACTIVE_UNIQUE_ACTOR_REQUIRED');end if;
  if nvl(upper(trim(grp)),'-')!='GLOBAL_ADMIN'and(uware is null or uware!=ware)then raise_application_error(-20882,'PICK_PLAN_CURRENT_WARE_FORBIDDEN');end if;
  if p_permission is null or RRL_HAS_WRIGHT(p_actor,p_permission)!=1 then raise_application_error(-20882,'PICK_PLAN_PERMISSION_REQUIRED');end if;
 end;
end;
/
