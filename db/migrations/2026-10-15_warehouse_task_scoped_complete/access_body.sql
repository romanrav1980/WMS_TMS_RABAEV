create or replace package body RRL_WAREHOUSE_TASK_ACCESS as

 function scoped_stock_executor(p_task number,p_actor varchar2) return number is
  t RRL_WAREHOUSE_TASK%rowtype;v_from number;v_to number;n number;v_kind varchar2(40);
 begin
  select * into t from RRL_WAREHOUSE_TASK where TASK_ID=p_task;
  if p_actor is null or t.ASSIGNED_TO is null or t.ASSIGNED_TO!=p_actor or t.HU_CONTENT_VERSION is not null then return 0;end if;
  select count(*) into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  if n!=1 then return 0;end if;
  select HU_KIND into v_kind from RRL_PALLETS where UID_PALLET=nvl(t.UID_PALLET,t.SSCC);
  if v_kind is null or v_kind!='STOCK' then return 0;end if;
  select count(*)into n from RRL_ST_DEFER_WAIT_PLAN where TASK_ID=p_task and CASE_TASK_ID is not null;
  if n!=0 then return 0;end if;
  select WARE_ID into v_from from RRL_CELLS where CELL=t.FROM_CELL;
  select WARE_ID into v_to from RRL_CELLS where CELL=t.TO_CELL;
  if v_from is null or v_to is null or(t.FROM_WARE_ID is not null and t.FROM_WARE_ID!=v_from)
   or(t.TO_WARE_ID is not null and t.TO_WARE_ID!=v_to)then return 0;end if;
  if RRL_ACCESS_API.allowed(p_actor,'warehouse_task_execute','WAREHOUSE',to_char(v_from),t.ASSIGNED_TO)!=1
   or RRL_ACCESS_API.allowed(p_actor,'warehouse_task_execute','WAREHOUSE',to_char(v_to),t.ASSIGNED_TO)!=1 then return 0;end if;
  return 1;
 exception when no_data_found then return 0;
 end;
 function task_signature(p_task number) return varchar2 is t RRL_WAREHOUSE_TASK%rowtype;
 begin select * into t from RRL_WAREHOUSE_TASK where TASK_ID=p_task;return RRL_STOCK_TASK_PLAN.signature(t);end;
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
  v_meta:=v_doc.get_object('metadata');
  if v_doc.get_string('command_type')='TASK_COMPLETE' and nvl(v_meta.get_number('document_confirmation'),0)!=1
   and scoped_stock_executor(v_task,p_actor)=1 then return;end if;
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
