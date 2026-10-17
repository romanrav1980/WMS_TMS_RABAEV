create or replace package body RRL_CASE_RESOURCE_POLICY as
 function context_json(p_task number,p_action varchar2,p_actor varchar2,p_resource number default null,p_session number default null,p_equipment number default null) return clob is
  ct RRL_CASE_PICK_TASK%rowtype;s RRL_RESOURCE_SESSION%rowtype;r RRL_RESOURCE%rowtype;e RRL_RESOURCE_EQUIPMENT%rowtype;sh RRL_RESOURCE_SHIFT%rowtype;
  v_resource number:=p_resource;v_session number:=p_session;v_equipment number:=p_equipment;n number;types varchar2(1000);
  target varchar2(100);j json_object_t:=json_object_t();scoped boolean:=false;
 begin
  if p_action not in('CLAIM','START','COMPLETE','REPORT','TRANSFER','EMPTY_TARE') or p_action is null or p_actor is null then raise_application_error(-20881,'CASE_RESOURCE_ACTION_REQUIRED');end if;
  select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  if p_action='EMPTY_TARE'and(ct.ASSIGNED_TO is null or ct.ASSIGNED_TO!=p_actor or ct.STATUS is null
   or ct.STATUS not in('NEW','ASSIGNED','IN_PROGRESS')or ct.PICKED_QTY is null or ct.PICKED_QTY!=0
   or RRL_CASE_TASK_ACCESS.scoped_executor(p_task,p_actor)!=1)then raise_application_error(-20882,'CASE_SCOPED_EMPTY_OWN_ORDINARY_REQUIRED');end if;
  if p_action='EMPTY_TARE'then
   select count(*)into n from RRL_ASSEMBLY_SESSION where CASE_PICK_TASK_ID=p_task and STATE in('OPEN','BLOCKED','HOLD');
   if n!=0 then raise_application_error(-20886,'CASE_SCOPED_EMPTY_ASSEMBLY_BUSY');end if;
  end if;
  scoped:=(p_action='COMPLETE'and RRL_CASE_TASK_ACCESS.scoped_assembly_executor(p_task,p_actor)=1)
   or(p_action in('COMPLETE','EMPTY_TARE')and RRL_CASE_TASK_ACCESS.scoped_executor(p_task,p_actor)=1)
   or(p_action in('CLAIM','START')and RRL_CASE_TASK_ACCESS.scoped_metadata_actor(p_task,p_action,p_actor)=1);
  if not scoped then RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,case when p_action='TRANSFER'then'case_pick_manage'else'case_pick_execute'end);end if;
  if p_action in('CLAIM','START','COMPLETE','EMPTY_TARE') then RRL_STOCK_WAVE_READY.assert_released(ct.PICK_WAVE_ID);end if;
  if p_action='TRANSFER' then
   if RRL_HAS_WRIGHT(p_actor,'case_pick_manage')!=1 then raise_application_error(-20882,'CASE_TRANSFER_FORBIDDEN');end if;
  elsif not scoped and RRL_HAS_WRIGHT(p_actor,'case_pick_execute')!=1 then raise_application_error(-20882,'CASE_EXECUTE_FORBIDDEN');end if;
  if ct.STATUS is null or ct.STATUS not in('NEW','ASSIGNED','IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT') then raise_application_error(-20886,'CASE_RESOURCE_TASK_STATE_CONFLICT');end if;
  if p_action!='TRANSFER' then
   v_resource:=nvl(v_resource,ct.ASSIGNED_RESOURCE_ID);v_session:=nvl(v_session,ct.RESOURCE_SESSION_ID);v_equipment:=nvl(v_equipment,ct.EQUIPMENT_ID);
  end if;
  target:=nvl(ct.ASSIGNED_TO,p_actor);
  if v_session is null then
   if scoped then raise_application_error(-20886,'CASE_SCOPED_PHYSICAL_SESSION_REQUIRED');end if;
   if v_resource is not null or v_equipment is not null or RRL_HAS_WRIGHT(p_actor,'case_pick_manage')!=1 then raise_application_error(-20882,'CASE_PHYSICAL_SESSION_REQUIRED');end if;
   if p_action='TRANSFER' then raise_application_error(-20881,'CASE_TRANSFER_TARGET_SESSION_REQUIRED');end if;
   target:=p_actor;
  else
   select * into s from RRL_RESOURCE_SESSION where SESSION_ID=v_session;
   target:=s.OPERATOR_USER_ID;
   if scoped and s.STATUS!='ACTIVE'then raise_application_error(-20886,'CASE_SCOPED_ACTIVE_SESSION_REQUIRED');end if;
   if target is null or s.STATUS is null or (p_action='CLAIM' and s.STATUS not in('ACTIVE','PAUSED')) or (p_action!='CLAIM' and s.STATUS!='ACTIVE') then raise_application_error(-20886,'CASE_SESSION_UNAVAILABLE');end if;
   if p_action!='TRANSFER' and target!=p_actor and RRL_HAS_WRIGHT(p_actor,'case_pick_manage')!=1 then raise_application_error(-20882,'CASE_SESSION_OWNER_CONFLICT');end if;
   if (v_resource is not null and v_resource!=s.RESOURCE_ID) or (v_equipment is not null and nvl(s.EQUIPMENT_ID,-1)!=v_equipment) then raise_application_error(-20886,'CASE_SESSION_CONTEXT_CONFLICT');end if;
   v_resource:=s.RESOURCE_ID;v_equipment:=s.EQUIPMENT_ID;
   select * into sh from RRL_RESOURCE_SHIFT where SHIFT_ID=s.SHIFT_ID;
   if scoped and(sh.WARE_ID is null or sh.WARE_ID!=ct.WARE_ID)then raise_application_error(-20886,'CASE_SCOPED_SHIFT_WAREHOUSE_CONFLICT');end if;
   if sh.STATUS is null or sh.START_AT is null or sh.FINISH_AT is null or sh.STATUS not in('PLANNED','OPEN') or ((p_action!='CLAIM' or scoped) and (sh.STATUS!='OPEN' or systimestamp<sh.START_AT or systimestamp>sh.FINISH_AT)) then raise_application_error(-20886,'CASE_SHIFT_UNAVAILABLE');end if;
   select count(*) into n from RRL_WAREHOUSE_TASK where ASSIGNED_TO=target and STATUS='IN_PROGRESS';
   if n>0 or s.CURRENT_INVENTORY_TASK_ID is not null then raise_application_error(-20886,'CASE_OPERATOR_BUSY_WITH_OTHER_PHYSICAL_STEP');end if;
   select * into r from RRL_RESOURCE where RESOURCE_ID=v_resource;
   if nvl(r.ACTIVE,0)!=1 or r.STATUS is null or r.STATUS not in('AVAILABLE','IDLE','IN_WORK') or (r.USER_ID is not null and r.USER_ID!=target) or r.WARE_ID is null or ct.WARE_ID is null or r.WARE_ID!=ct.WARE_ID then raise_application_error(-20886,'CASE_RESOURCE_UNAVAILABLE');end if;
   select DEFAULT_TASK_TYPES into types from RRL_RESOURCE_TYPE where RESOURCE_TYPE=r.RESOURCE_TYPE and ACTIVE=1;
   if types is null or instr(','||replace(types,' ','')||',',',CASE_PICK,')=0 then raise_application_error(-20886,'CASE_RESOURCE_TYPE_UNSUITABLE');end if;
   select count(*) into n from RRL_RESOURCE_TASK_QUAL where RESOURCE_ID=v_resource and TASK_TYPE='CASE_PICK' and ACTIVE=1 and VALID_FROM<=systimestamp and (VALID_UNTIL is null or VALID_UNTIL>systimestamp);
   if n!=1 then raise_application_error(-20886,'CASE_RESOURCE_QUALIFICATION_REQUIRED');end if;
   if r.EQUIPMENT_ID is not null and nvl(v_equipment,-1)!=r.EQUIPMENT_ID then raise_application_error(-20886,'CASE_RESOURCE_EQUIPMENT_BINDING_CONFLICT');end if;
   if v_equipment is not null then
    select * into e from RRL_RESOURCE_EQUIPMENT where EQUIPMENT_ID=v_equipment;
    if nvl(e.ACTIVE,0)!=1 or nvl(e.SERVICE_STATUS,'?')!='ACTIVE' or e.WARE_ID is null or e.WARE_ID!=ct.WARE_ID then raise_application_error(-20886,'CASE_EQUIPMENT_UNAVAILABLE');end if;
   end if;
  end if;
  if scoped then
   if target!=p_actor or(p_action='COMPLETE'and RRL_CASE_TASK_ACCESS.scoped_executor(p_task,p_actor)!=1 and RRL_CASE_TASK_ACCESS.scoped_assembly_executor(p_task,p_actor)!=1)
    or(p_action='EMPTY_TARE'and RRL_CASE_TASK_ACCESS.scoped_executor(p_task,p_actor)!=1)
    or(p_action in('CLAIM','START')and RRL_CASE_TASK_ACCESS.scoped_metadata_actor(p_task,p_action,p_actor)!=1)then raise_application_error(-20882,'CASE_SCOPED_SESSION_OWNER_REQUIRED');end if;
  else RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,case when p_action='TRANSFER'then'case_pick_manage'else'case_pick_execute'end,target);end if;
  select count(*) into n from RUSERS where ID=target and nvl(DELETED,0)=0;
  if n!=1 or(not scoped and RRL_HAS_WRIGHT(target,'case_pick_execute')!=1)then raise_application_error(-20882,'CASE_TARGET_NOT_EXECUTOR');end if;
  if p_action in('CLAIM','START') and ct.ASSIGNED_TO is not null and ct.ASSIGNED_TO!=target then raise_application_error(-20886,'CASE_USE_EXPLICIT_TRANSFER');end if;
  if p_action!='TRANSFER' and ct.PICKED_QTY>0 and (nvl(ct.RESOURCE_SESSION_ID,-1)!=nvl(v_session,-1) or nvl(ct.ASSIGNED_RESOURCE_ID,-1)!=nvl(v_resource,-1)) then raise_application_error(-20886,'CASE_CARRIER_NEEDS_EXPLICIT_TRANSFER');end if;
  j.put('resource_id',v_resource);j.put('resource_session_id',v_session);j.put('equipment_id',v_equipment);j.put('assigned_to',target);
  return j.to_clob;
 exception when no_data_found then raise_application_error(-20886,'CASE_RESOURCE_IDENTITY_MISSING');
 end;
end;
/
