create or replace package RRL_PICKER_TIME_AUTH authid definer accessible by(package RRL_PICKER_TIME_API,package RRL_PICKER_TIME_READ) as
 procedure actor_required(p_actor varchar2);
 procedure ware_required(p_actor varchar2,p_ware number);
 procedure source_permission(p_actor varchar2,p_kind varchar2,p_ware number);
 procedure session_required(p_actor varchar2,p_session number,p_active boolean,p_ware out number,p_resource out number);
 function source_allowed(p_actor varchar2,p_kind varchar2,p_id number,p_session number,p_ware number,p_resource number)return number;
end;
/
create or replace package body RRL_PICKER_TIME_AUTH as
 procedure actor_required(p_actor varchar2)is n number;begin
  if p_actor is null or length(p_actor)>100 then raise_application_error(-20882,'PICKER_TIME_CURRENT_ACTOR_REQUIRED');end if;
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  if n!=1 then raise_application_error(-20882,'PICKER_TIME_CURRENT_ACTOR_REQUIRED');end if;
 end;
 procedure ware_required(p_actor varchar2,p_ware number)is w varchar2(100);begin
  actor_required(p_actor);
  if p_ware is null or p_ware<1 then raise_application_error(-20882,'PICKER_TIME_ACTUAL_WARE_REQUIRED');end if;
  w:=RRL_STOCK_PLAN_HELPER.decimal_text(p_ware);
  if RRL_ACCESS_API.allowed(p_actor,'case_pick_execute','WAREHOUSE',w,p_actor)!=1
   and RRL_ACCESS_API.allowed(p_actor,'warehouse_task_execute','WAREHOUSE',w,p_actor)!=1
   then raise_application_error(-20882,'PICKER_TIME_CURRENT_WARE_SCOPE_REQUIRED');end if;
 end;
 procedure source_permission(p_actor varchar2,p_kind varchar2,p_ware number)is permission_name varchar2(100);begin
  ware_required(p_actor,p_ware);
  if p_kind='CASE_PICK_TASK'then permission_name:='case_pick_execute';
  elsif p_kind='WAREHOUSE_TASK'then permission_name:='warehouse_task_execute';
  else raise_application_error(-20882,'PICKER_TIME_SOURCE_SCOPE_REQUIRED');end if;
  if RRL_ACCESS_API.allowed(p_actor,permission_name,'WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(p_ware),p_actor)!=1
   then raise_application_error(-20882,'PICKER_TIME_SOURCE_SCOPE_REQUIRED');end if;
 end;
 procedure session_required(p_actor varchar2,p_session number,p_active boolean,p_ware out number,p_resource out number)is
  s RRL_RESOURCE_SESSION%rowtype;r RRL_RESOURCE%rowtype;sh RRL_RESOURCE_SHIFT%rowtype;
 begin
  actor_required(p_actor);
  select *into s from RRL_RESOURCE_SESSION where SESSION_ID=p_session;
  if s.OPERATOR_USER_ID is null or s.OPERATOR_USER_ID!=p_actor then raise_application_error(-20882,'PICKER_TIME_OWN_SESSION_REQUIRED');end if;
  select *into r from RRL_RESOURCE where RESOURCE_ID=s.RESOURCE_ID;
  select *into sh from RRL_RESOURCE_SHIFT where SHIFT_ID=s.SHIFT_ID;
  if r.WARE_ID is null or sh.WARE_ID is null or r.WARE_ID!=sh.WARE_ID then raise_application_error(-20886,'PICKER_TIME_SESSION_WARE_CONFLICT');end if;
  ware_required(p_actor,r.WARE_ID);
  if p_active and(s.STATUS is null or s.STATUS!='ACTIVE'or nvl(r.ACTIVE,0)!=1 or sh.STATUS is null or sh.STATUS!='OPEN'
   or(r.USER_ID is not null and r.USER_ID!=p_actor))then raise_application_error(-20886,'PICKER_TIME_ACTIVE_OWN_SESSION_REQUIRED');end if;
  if s.STATUS is null or s.STATUS not in('ACTIVE','PAUSED','CLOSED','ERROR')then raise_application_error(-20886,'PICKER_TIME_SESSION_UNAVAILABLE');end if;
  p_ware:=r.WARE_ID;p_resource:=r.RESOURCE_ID;
 exception when no_data_found then raise_application_error(-20886,'PICKER_TIME_SESSION_MISSING');
 end;
 function source_allowed(p_actor varchar2,p_kind varchar2,p_id number,p_session number,p_ware number,p_resource number)return number is n number;begin
  if p_kind='CASE_PICK_TASK'then
   select count(*)into n from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_id and ASSIGNED_TO=p_actor
    and RESOURCE_SESSION_ID=p_session and ASSIGNED_RESOURCE_ID=p_resource and WARE_ID=p_ware
    and STATUS in('IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT');
  elsif p_kind='WAREHOUSE_TASK'then
   select count(*)into n from RRL_WAREHOUSE_TASK t join RRL_CELLS fc on fc.CELL=t.FROM_CELL join RRL_CELLS tc on tc.CELL=t.TO_CELL
    where t.TASK_ID=p_id and t.ASSIGNED_TO=p_actor and t.RESOURCE_SESSION_ID=p_session and t.RESOURCE_ID=p_resource
     and t.STATUS='IN_PROGRESS'and t.TASK_TYPE in('PICK','PICKING_MOVE')
     and fc.WARE_ID=p_ware and tc.WARE_ID=p_ware and t.FROM_WARE_ID=p_ware and t.TO_WARE_ID=p_ware;
  else return 0;end if;
  return case when n=1 then 1 else 0 end;
 end;
end;
/
