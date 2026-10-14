create or replace package RRL_TASK_RESOURCE_POLICY authid definer as
 function context_json(p_task number,p_action varchar2,p_actor varchar2,p_assignee varchar2,
  p_resource number default null,p_session number default null,p_equipment number default null) return clob;
end;
/

create or replace package body RRL_TASK_RESOURCE_POLICY as
 function context_json(p_task number,p_action varchar2,p_actor varchar2,p_assignee varchar2,
  p_resource number default null,p_session number default null,p_equipment number default null) return clob is
  t RRL_WAREHOUSE_TASK%rowtype;s RRL_RESOURCE_SESSION%rowtype;r RRL_RESOURCE%rowtype;e RRL_RESOURCE_EQUIPMENT%rowtype;
  sh RRL_RESOURCE_SHIFT%rowtype;v_other_status varchar2(40);j json_object_t:=json_object_t();v_resource number:=p_resource;v_session number:=p_session;v_equipment number:=p_equipment;
  v_target varchar2(100):=trim(p_assignee);v_n number;v_actor varchar2(100):=trim(p_actor);v_types varchar2(1000);
 begin
  if p_action is null or p_action not in('ASSIGN','START','COMPLETE','COMPLETE_DOCUMENT') or v_actor is null or v_target is null then
   raise_application_error(-20881,'TASK_ASSIGNMENT_INPUT_REQUIRED');end if;
  select * into t from RRL_WAREHOUSE_TASK where TASK_ID=p_task;
  if p_action='COMPLETE_DOCUMENT' then
   if t.TASK_SOURCE!='MES_RAW_SUPPLY' or RRL_HAS_WRIGHT(v_actor,'mes_raw_transfer_confirm')!=1 then
    raise_application_error(-20882,'MES_DOCUMENT_CONFIRM_FORBIDDEN');end if;
   if p_resource is not null or p_session is not null or p_equipment is not null then
    raise_application_error(-20881,'DOCUMENT_CONFIRM_HAS_NO_RESOURCE_SESSION');end if;
   j.put_null('resource_id');j.put_null('resource_session_id');j.put_null('equipment_id');return j.to_clob;
  end if;
  if RRL_HAS_WRIGHT(v_actor,'warehouse_task_execute')!=1 then raise_application_error(-20882,'TASK_EXECUTE_FORBIDDEN');end if;
  select count(*) into v_n from RUSERS where ID=v_target and nvl(DELETED,0)=0;
  if v_n!=1 or RRL_HAS_WRIGHT(v_target,'warehouse_task_execute')!=1 then
   raise_application_error(-20882,'TASK_ASSIGNEE_NOT_EXECUTOR');end if;
  if p_action='ASSIGN' and t.STATUS not in('PLANNED','ASSIGNED') then
   raise_application_error(-20886,'TASK_ASSIGN_STATE_CONFLICT');end if;
  if p_action='START' and t.STATUS not in('PLANNED','ASSIGNED','IN_PROGRESS') then
   raise_application_error(-20886,'TASK_START_STATE_CONFLICT');end if;
  if p_action='COMPLETE' and t.STATUS not in('PLANNED','ASSIGNED','IN_PROGRESS') then
   raise_application_error(-20886,'TASK_COMPLETE_STATE_CONFLICT');end if;
  if v_target!=v_actor then
   if p_action!='ASSIGN' or RRL_HAS_WRIGHT(v_actor,'resource_dispatch_manage')!=1 then
    raise_application_error(-20882,'TASK_DISPATCH_PERMISSION_REQUIRED');end if;
  end if;
  if t.ASSIGNED_TO is not null and t.ASSIGNED_TO!=v_target then
   if t.STATUS='IN_PROGRESS' and p_action!='COMPLETE' then
    raise_application_error(-20886,'FINISH_CURRENT_PHYSICAL_STEP_BEFORE_REASSIGN');end if;
   if RRL_HAS_WRIGHT(v_actor,'warehouse_task_force_assign')!=1 then
    raise_application_error(-20882,'TASK_FORCE_ASSIGN_PERMISSION_REQUIRED');end if;
  end if;
  if t.ASSIGNED_TO=v_target then
   v_resource:=nvl(v_resource,t.RESOURCE_ID);v_session:=nvl(v_session,t.RESOURCE_SESSION_ID);v_equipment:=nvl(v_equipment,t.EQUIPMENT_ID);
  end if;
  if p_action!='ASSIGN' and v_session is null and (v_resource is not null or v_equipment is not null) then raise_application_error(-20882,'TASK_RESOURCE_SESSION_REQUIRED');end if;
  if p_action!='ASSIGN' and v_session is null and t.TASK_TYPE in('PUTAWAY','REPLENISHMENT','PICKING_MOVE','FG_TO_STORAGE','RAW_TO_PRODUCTION')
   and RRL_HAS_WRIGHT(v_actor,'warehouse_task_force_assign')!=1 then raise_application_error(-20882,'TASK_MACHINE_SESSION_REQUIRED');end if;
  if p_action!='ASSIGN' then
   select count(*) into v_n from RRL_WAREHOUSE_TASK where ASSIGNED_TO=v_target and STATUS='IN_PROGRESS' and TASK_ID!=p_task;
   if v_n>0 then raise_application_error(-20886,'FINISH_OTHER_OPERATOR_PHYSICAL_STEP_FIRST');end if;
   select count(*) into v_n from RRL_CASE_PICK_TASK where ASSIGNED_TO=v_target and PICKED_QTY>0 and STATUS in('IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT');
   if v_n>0 then raise_application_error(-20886,'FINISH_OPERATOR_CASE_CARRIER_FIRST');end if;
  end if;
  if v_session is not null then
   select * into s from RRL_RESOURCE_SESSION where SESSION_ID=v_session;
   if s.OPERATOR_USER_ID is null or s.OPERATOR_USER_ID!=v_target then
    raise_application_error(-20882,'TASK_SESSION_OWNER_CONFLICT');end if;
   if s.STATUS is null or (p_action='ASSIGN' and s.STATUS not in('ACTIVE','PAUSED'))
     or (p_action!='ASSIGN' and s.STATUS!='ACTIVE') then raise_application_error(-20886,'TASK_SESSION_NOT_ACTIVE');end if;
   if (v_resource is not null and v_resource!=s.RESOURCE_ID) or
      (v_equipment is not null and (s.EQUIPMENT_ID is null or v_equipment!=s.EQUIPMENT_ID)) then
    raise_application_error(-20886,'TASK_SESSION_RESOURCE_IDENTITY_CONFLICT');end if;
   select * into sh from RRL_RESOURCE_SHIFT where SHIFT_ID=s.SHIFT_ID;
   if sh.STATUS is null or sh.STATUS not in('PLANNED','OPEN') or
     (p_action!='ASSIGN' and (sh.STATUS!='OPEN' or sh.START_AT is null or sh.FINISH_AT is null or systimestamp<sh.START_AT or systimestamp>sh.FINISH_AT)) then
    raise_application_error(-20886,'TASK_SHIFT_UNAVAILABLE');end if;
   if p_action!='ASSIGN' and s.CURRENT_TASK_ID is not null and s.CURRENT_TASK_ID!=p_task then
    begin select STATUS into v_other_status from RRL_WAREHOUSE_TASK where TASK_ID=s.CURRENT_TASK_ID;
    exception when no_data_found then v_other_status:='UNKNOWN';end;
    if v_other_status not in('DONE','CANCELLED') then raise_application_error(-20886,'FINISH_CURRENT_PHYSICAL_STEP_FIRST');end if;
   end if;
   if s.CURRENT_INVENTORY_TASK_ID is not null then
    select STATUS into v_other_status from RRL_INVENTORY_TASK where INVENTORY_TASK_ID=s.CURRENT_INVENTORY_TASK_ID;
    if v_other_status not in('DONE','CANCELLED') then raise_application_error(-20886,'FINISH_CURRENT_INVENTORY_STEP_FIRST');end if;
   end if;
   v_resource:=s.RESOURCE_ID;v_equipment:=s.EQUIPMENT_ID;
  end if;
  if v_resource is not null then
   select * into r from RRL_RESOURCE where RESOURCE_ID=v_resource;
   if nvl(r.ACTIVE,0)!=1 or r.STATUS is null or r.STATUS not in('AVAILABLE','IN_WORK','IDLE')
      or (r.USER_ID is not null and r.USER_ID!=v_target) then raise_application_error(-20886,'TASK_RESOURCE_UNAVAILABLE');end if;
   select DEFAULT_TASK_TYPES into v_types from RRL_RESOURCE_TYPE where RESOURCE_TYPE=r.RESOURCE_TYPE and ACTIVE=1;
   if v_types is null or instr(','||replace(v_types,' ','')||',',','||t.TASK_TYPE||',')=0 then
    raise_application_error(-20886,'TASK_RESOURCE_TYPE_UNSUITABLE');end if;
   select count(*) into v_n from RRL_RESOURCE_TASK_QUAL where RESOURCE_ID=v_resource and TASK_TYPE=t.TASK_TYPE
    and ACTIVE=1 and VALID_FROM<=systimestamp and (VALID_UNTIL is null or VALID_UNTIL>systimestamp);
   if v_n!=1 then raise_application_error(-20886,'TASK_RESOURCE_QUALIFICATION_REQUIRED');end if;
   if v_equipment is null and r.EQUIPMENT_ID is not null then raise_application_error(-20886,'TASK_RESOURCE_EQUIPMENT_REQUIRED');end if;
   if r.EQUIPMENT_ID is not null and r.EQUIPMENT_ID!=v_equipment then raise_application_error(-20886,'TASK_RESOURCE_EQUIPMENT_BINDING_CONFLICT');end if;
   if r.WARE_ID is not null and r.WARE_ID not in(nvl(t.FROM_WARE_ID,r.WARE_ID),nvl(t.TO_WARE_ID,r.WARE_ID)) then
    raise_application_error(-20886,'TASK_RESOURCE_WAREHOUSE_CONFLICT');end if;
  end if;
  if v_equipment is not null then
   select * into e from RRL_RESOURCE_EQUIPMENT where EQUIPMENT_ID=v_equipment;
   if nvl(e.ACTIVE,0)!=1 or e.SERVICE_STATUS is null or e.SERVICE_STATUS!='ACTIVE' then
    raise_application_error(-20886,'TASK_EQUIPMENT_UNAVAILABLE');end if;
   if e.WARE_ID is not null and e.WARE_ID not in(nvl(t.FROM_WARE_ID,e.WARE_ID),nvl(t.TO_WARE_ID,e.WARE_ID)) then
    raise_application_error(-20886,'TASK_EQUIPMENT_WAREHOUSE_CONFLICT');end if;
  end if;
  if p_action='START' and t.STATUS='IN_PROGRESS' and
   (nvl(t.ASSIGNED_TO,chr(0))!=v_target or nvl(t.RESOURCE_SESSION_ID,-1)!=nvl(v_session,-1)
    or nvl(t.RESOURCE_ID,-1)!=nvl(v_resource,-1) or nvl(t.EQUIPMENT_ID,-1)!=nvl(v_equipment,-1)) then
   raise_application_error(-20886,'TASK_START_ALREADY_IN_PROGRESS');end if;
  j.put('resource_id',v_resource);j.put('resource_session_id',v_session);j.put('equipment_id',v_equipment);
  return j.to_clob;
 exception when no_data_found then raise_application_error(-20886,'TASK_RESOURCE_IDENTITY_NOT_FOUND');
 end;
end;
/
