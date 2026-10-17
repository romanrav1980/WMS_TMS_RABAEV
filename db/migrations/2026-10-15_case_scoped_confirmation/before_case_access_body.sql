create or replace package body RRL_CASE_TASK_ACCESS as
 procedure assert_scope(p_task number,p_actor varchar2,p_permission varchar2,p_assignee varchar2 default null)is
  v_ware number;v_user_ware number;v_group varchar2(100);v_permission varchar2(100):=lower(trim(p_permission));
  procedure check_user(p_user varchar2)is begin
   begin
    select WARE_ID,USER_GROUP into v_user_ware,v_group from RUSERS where ID=p_user and nvl(DELETED,0)=0;
   exception when no_data_found then raise_application_error(-20882,'CASE_ACTIVE_USER_REQUIRED');end;
   if upper(trim(v_group))='GLOBAL_ADMIN'then return;end if;
   if v_user_ware is null or v_user_ware!=v_ware then raise_application_error(-20882,'CASE_USER_WAREHOUSE_FORBIDDEN');end if;
  end;
 begin
  if v_permission is null or v_permission not in('case_pick_view','case_pick_execute','case_pick_manage','case_pick_short_approve','case_move')then
   raise_application_error(-20882,'CASE_ACCESS_PERMISSION_REQUIRED');end if;
  select WARE_ID into v_ware from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  if v_ware is null or v_ware<1 then raise_application_error(-20886,'CASE_TASK_WARE_REQUIRED');end if;
  check_user(p_actor);
  if v_permission='case_move'then
   if RRL_HAS_WRIGHT(p_actor,'case_pick_execute')!=1 and RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 then
    raise_application_error(-20882,'CASE_CURRENT_MOVE_FORBIDDEN');end if;
  elsif RRL_HAS_WRIGHT(p_actor,v_permission)!=1 then raise_application_error(-20882,'CASE_CURRENT_ACTION_FORBIDDEN');end if;
  if p_assignee is not null and p_assignee!=p_actor then check_user(p_assignee);end if;
 exception when no_data_found then raise_application_error(-20886,'CASE_TASK_IDENTITY_MISSING');
 end;
 procedure assert_command(p_request clob,p_actor varchar2)is
  d json_object_t:=json_object_t.parse(p_request);s json_object_t;v_kind varchar2(80);v_task number;v_short number;v_permission varchar2(100);
 begin
  v_kind:=d.get_string('command_type');
  if v_kind is null or v_kind not in('CASE_PICK_CONFIRM','CASE_CARRIER_MOVE','CASE_CARRIER_RETURN','CASE_SHORT_APPROVE')then return;end if;
  s:=d.get_object('source');
  if v_kind='CASE_SHORT_APPROVE'then
   v_short:=s.get_number('short_id');select CASE_PICK_TASK_ID into v_task from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=v_short;
   v_permission:='case_pick_short_approve';
  else
   v_task:=s.get_number('case_task_id');
   v_permission:=case v_kind when 'CASE_CARRIER_MOVE'then'case_move'when'CASE_CARRIER_RETURN'then'case_pick_manage'else'case_pick_execute'end;
  end if;
  assert_scope(v_task,p_actor,v_permission);
 exception when no_data_found then raise_application_error(-20886,'CASE_TASK_IDENTITY_MISSING');
 end;
end;
/
