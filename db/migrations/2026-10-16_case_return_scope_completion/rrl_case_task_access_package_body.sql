create or replace package body RRL_CASE_TASK_ACCESS as
 function legacy_executor(p_task number,p_actor varchar2)return number is n number;begin
  if p_task is null or p_actor is null or RRL_HAS_WRIGHT(p_actor,'case_pick_execute')!=1 then return 0;end if;
  select count(*)into n from RRL_CASE_PICK_TASK t join RUSERS u on u.ID=p_actor and nvl(u.DELETED,0)=0
   where t.CASE_PICK_TASK_ID=p_task and(u.WARE_ID=t.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
  return least(n,1);
 end;
 function has_current_scoped_execute(p_task number,p_actor varchar2)return number is
  t RRL_CASE_PICK_TASK%rowtype;n number;begin
  if p_task is null or p_actor is null then return 0;end if;
  -- Legacy authority applies at homeWARE/global; foreign WARE needs the current explicit role.
  if legacy_executor(p_task,p_actor)=1 then return 0;end if;
  select *into t from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  if t.ASSIGNED_TO is null or t.ASSIGNED_TO!=p_actor or t.WARE_ID is null or t.WARE_ID<1 then return 0;end if;
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;if n!=1 then return 0;end if;
  if RRL_ACCESS_API.allowed(p_actor,'case_pick_execute','WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(t.WARE_ID),t.ASSIGNED_TO)!=1 then return 0;end if;
  return 1;
 exception when no_data_found or too_many_rows then return 0;end;
 function count_execution_task(p_task number,p_allow_assembly number)return number is
  t RRL_CASE_PICK_TASK%rowtype;n number;begin
  if p_task is null then return 0;end if;
  select *into t from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  if t.WARE_ID is null or t.WARE_ID<1 or t.CONTENT_VERSION is null or t.SHIPPED_OPERATION is not null then return 0;end if;
  select count(*)into n from RRL_WMS_HU_LINK where CHILD_CASE_TASK_ID=p_task and ACTIVE_FLAG=1;if n!=0 then return 0;end if;
  if p_allow_assembly=0 then
   select count(*)into n from RRL_ASSEMBLY_SESSION where CASE_PICK_TASK_ID=p_task and STATE in('OPEN','BLOCKED','HOLD');if n!=0 then return 0;end if;
  end if;
  select count(*)into n from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=p_task;if n=0 then return 0;end if;
  -- One CASE-bound closure query: unknown/weighted/marked/serialized UOM never gains this branch.
  select count(*)into n from RRL_CASE_PICK_LINE l where l.CASE_PICK_TASK_ID=p_task and(
   not exists(select 1 from RRL_ARTICULS a where a.ACTICUL=l.ARTICUL and nvl(a.TYPE_W,0)not in(2,3,5,6,7))
   or not exists(select 1 from RRL_STOCK_UOM_CONVERSION u where u.ARTICUL=l.ARTICUL and u.INPUT_UOM='EA'and u.BASE_UOM='EA'and u.NUMERATOR=1 and u.DENOMINATOR=1)
   or exists(select 1 from RRL_SKU_RECEIPT_POLICY x where x.ARTICUL=l.ARTICUL and(nvl(x.SERIALIZED_WEIGHT_BOXES,0)!=0 or nvl(x.MARKING_REQUIRED,0)!=0))
   or exists(select 1 from RRL_FINISHED_GOODS_SKU x where x.ARTICUL=l.ARTICUL and nvl(x.CRPT_REQUIRED,0)!=0)
   or exists(select 1 from RRL_SKU_RECEIPT_PROFILE x where x.ARTICUL=l.ARTICUL));
  if n!=0 then return 0;end if;return 1;
 exception when no_data_found or too_many_rows then return 0;end;
 function ordinary_execution_task(p_task number)return number is begin return count_execution_task(p_task,0);end;
 function scoped_assembly_executor(p_task number,p_actor varchar2)return number is begin
  if has_current_scoped_execute(p_task,p_actor)!=1 then return 0;end if;
  return count_execution_task(p_task,1);
 end;
 function scoped_executor(p_task number,p_actor varchar2)return number is begin
  if has_current_scoped_execute(p_task,p_actor)!=1 then return 0;end if;return ordinary_execution_task(p_task);
 end;
 function scoped_metadata_actor(p_task number,p_action varchar2,p_actor varchar2)return number is t RRL_CASE_PICK_TASK%rowtype;n number;begin
  if p_task is null or p_actor is null or p_action is null or p_action not in('CLAIM','START')then return 0;end if;
  if legacy_executor(p_task,p_actor)=1 then return 0;end if;
  select *into t from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  if n!=1 or t.WARE_ID is null or t.WARE_ID<1 or(t.ASSIGNED_TO is not null and t.ASSIGNED_TO!=p_actor)then return 0;end if;
  if p_action='START'and(t.ASSIGNED_TO is null or t.ASSIGNED_TO!=p_actor)then return 0;end if;
  -- Unassigned CLAIM uses owner=NULL: SELF does not cover it, actualWARE/group/network grant does.
  if RRL_ACCESS_API.allowed(p_actor,'case_pick_execute','WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(t.WARE_ID),t.ASSIGNED_TO)!=1 then return 0;end if;
  return ordinary_execution_task(p_task);
 exception when no_data_found or too_many_rows then return 0;end;
 procedure assert_scope(p_task number,p_actor varchar2,p_permission varchar2,p_assignee varchar2 default null)is
  v_ware number;v_owner nvarchar2(50);v_user_ware number;v_group varchar2(100);v_permission varchar2(100):=lower(trim(p_permission));
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
  select WARE_ID,ASSIGNED_TO into v_ware,v_owner from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  if v_ware is null or v_ware<1 then raise_application_error(-20886,'CASE_TASK_WARE_REQUIRED');end if;
  if v_permission='case_pick_execute'and(p_assignee is null or p_assignee=p_actor)and has_current_scoped_execute(p_task,p_actor)=1 then return;end if;
  -- Only shortage decisions gain this additive role branch; other manager paths stay unchanged.
  if v_permission='case_pick_short_approve'and RRL_ACCESS_API.allowed(p_actor,v_permission,'WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(v_ware),v_owner)=1 then return;end if;
  if v_permission='case_move'and RRL_ACCESS_API.allowed(p_actor,'warehouse_task_execute','WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(v_ware),v_owner)=1 then return;end if;
  check_user(p_actor);
  if v_permission='case_move'then
   if RRL_HAS_WRIGHT(p_actor,'case_pick_execute')!=1 and RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 then
    raise_application_error(-20882,'CASE_CURRENT_MOVE_FORBIDDEN');end if;
  elsif RRL_HAS_WRIGHT(p_actor,v_permission)!=1 then raise_application_error(-20882,'CASE_CURRENT_ACTION_FORBIDDEN');end if;
  if p_assignee is not null and p_assignee!=p_actor then check_user(p_assignee);end if;
 exception when no_data_found then raise_application_error(-20886,'CASE_TASK_IDENTITY_MISSING');
 end;
 procedure assert_command(p_request clob,p_actor varchar2)is
  d json_object_t:=json_object_t.parse(p_request);s json_object_t;v_kind varchar2(80);v_task number;v_short number;v_author nvarchar2(50);v_permission varchar2(100);
 begin
  v_kind:=d.get_string('command_type');
  if v_kind is null or v_kind not in('CASE_PICK_CONFIRM','CASE_CARRIER_MOVE','CASE_CARRIER_RETURN','CASE_SHORT_APPROVE')then return;end if;
  s:=d.get_object('source');
  if v_kind='CASE_SHORT_APPROVE'then
   v_short:=s.get_number('short_id');select CASE_PICK_TASK_ID,CREATED_BY into v_task,v_author from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=v_short;
   -- READY is recovery readiness, not a new shortage approval.
   if nvl(d.get_object('metadata').get_string('decision'),'ACCEPT_SHORT')!='READY'then RRL_ACCESS_API.assert_independent(p_actor,v_author,'CASE_SHORT_AUTHOR');end if;
   v_permission:='case_pick_short_approve';
  else
   v_task:=s.get_number('case_task_id');
   v_permission:=case v_kind when 'CASE_CARRIER_MOVE'then'case_move'when'CASE_CARRIER_RETURN'then'case_pick_manage'else'case_pick_execute'end;
  end if;
  if v_kind='CASE_PICK_CONFIRM'and has_current_scoped_execute(v_task,p_actor)=1 then return;end if;
  if v_kind='CASE_CARRIER_RETURN'then
   declare w number;owner_value nvarchar2(50);current_cell varchar2(60);n number;begin
    select WARE_ID,ASSIGNED_TO,CURRENT_CELL into w,owner_value,current_cell from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=v_task;
    select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0
     and RRL_HAS_WRIGHT(ID,'case_pick_manage')=1 and(upper(trim(USER_GROUP))='GLOBAL_ADMIN'or WARE_ID=w);
    if n=1 then assert_scope(v_task,p_actor,v_permission);return;end if;
    select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
    if n=1 and w>0 and RRL_ACCESS_API.allowed(p_actor,'case_pick_manage','WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(w),owner_value)=1 then
     if current_cell is not null then
      select count(*)into n from RRL_CELLS where CELL=current_cell and WARE_ID=w;
      if n!=1 then raise_application_error(-20882,'CASE_RETURN_CURRENT_CELL_WARE_REQUIRED');end if;
     end if;
     select count(*)into n from RRL_CASE_PICK_LINE l left join RRL_CELLS c on c.CELL=l.CELL_CODE
      where l.CASE_PICK_TASK_ID=v_task and(c.WARE_ID is null or c.WARE_ID!=w);
     if n!=0 then raise_application_error(-20882,'CASE_RETURN_DESTINATION_WARE_REQUIRED');end if;
     if current_cell is not null then
      select count(*)into n from RRL_CASE_CARRIER_LOT l join RRL_REMAINS rr on rr.UID_POLETA=l.LOT_UID and rr.REMAIN>0
       left join RRL_CELLS c on c.CELL=rr.CELL
       where l.CASE_PICK_TASK_ID=v_task and(c.WARE_ID is null or c.WARE_ID!=w);
      if n!=0 then raise_application_error(-20882,'CASE_RETURN_STOCK_WARE_REQUIRED');end if;
     end if;
     return;
    end if;
   end;
  end if;
  assert_scope(v_task,p_actor,v_permission);
 exception when no_data_found then raise_application_error(-20886,'CASE_TASK_IDENTITY_MISSING');
 end;
end;
/
