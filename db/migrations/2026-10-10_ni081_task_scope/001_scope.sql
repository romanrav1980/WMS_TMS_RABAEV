create or replace package RRL_WAREHOUSE_TASK_ACCESS authid definer as
 procedure assert_scope(p_task number,p_actor varchar2,p_assignee varchar2 default null);
 procedure assert_completion(p_request clob,p_actor varchar2);
end;
/
create or replace package body RRL_WAREHOUSE_TASK_ACCESS as
 procedure assert_scope(p_task number,p_actor varchar2,p_assignee varchar2 default null) is
  v_from number;v_to number;v_ware number;v_group varchar2(100);
  procedure check_user(p_user varchar2) is
  begin
   if trim(p_user) is null then raise_application_error(-20882,'TASK_ACTIVE_USER_REQUIRED');end if;
   begin
    select WARE_ID,USER_GROUP into v_ware,v_group from RUSERS
     where ID=p_user and nvl(DELETED,0)=0;
   exception when no_data_found then raise_application_error(-20882,'TASK_ACTIVE_USER_REQUIRED');end;
   if upper(trim(v_group))='GLOBAL_ADMIN' then return;end if;
   if v_ware is null or (nvl(v_from,-1)!=v_ware and nvl(v_to,-1)!=v_ware) then
    raise_application_error(-20882,'TASK_USER_WAREHOUSE_FORBIDDEN');end if;
  end;
 begin
  select FROM_WARE_ID,TO_WARE_ID into v_from,v_to from RRL_WAREHOUSE_TASK where TASK_ID=p_task;
  check_user(p_actor);
  if p_assignee is not null and p_assignee!=p_actor then check_user(p_assignee);end if;
 end;
 procedure assert_completion(p_request clob,p_actor varchar2) is
  v_doc json_object_t:=json_object_t.parse(p_request);v_source json_object_t;v_meta json_object_t;
  v_task number;v_permission varchar2(100):='warehouse_task_execute';v_task_source varchar2(40);
 begin
  v_source:=v_doc.get_object('source');v_task:=v_source.get_number('task_id');
  assert_scope(v_task,p_actor);
  v_meta:=v_doc.get_object('metadata');
  if v_meta.get_number('document_confirmation')=1 then
   select TASK_SOURCE into v_task_source from RRL_WAREHOUSE_TASK where TASK_ID=v_task;
   if v_task_source!='MES_RAW_SUPPLY' or v_task_source is null then
    raise_application_error(-20882,'MES_DOCUMENT_CONFIRM_FORBIDDEN');end if;
   v_permission:='mes_raw_transfer_confirm';
  end if;
  if RRL_HAS_WRIGHT(p_actor,v_permission)!=1 then
   raise_application_error(-20882,'TASK_CURRENT_EXECUTE_FORBIDDEN');end if;
 end;
end;
/
