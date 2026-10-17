declare a clob;e clob;n number;begin
 dbms_lob.createtemporary(a,true);dbms_lob.createtemporary(e,true);
 for s in(select TEXT from USER_SOURCE where NAME='RRL_WAREHOUSE_TASK_ACCESS'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 dbms_lob.append(e,'package RRL_WAREHOUSE_TASK_ACCESS authid definer as
 function scoped_stock_executor(p_task number,p_actor varchar2) return number;
 function task_signature(p_task number) return varchar2;
 procedure assert_scope(p_task number,p_actor varchar2,p_assignee varchar2 default null);
 procedure assert_completion(p_request clob,p_actor varchar2);
end;
');
 e:=replace(e,chr(13),'');if dbms_lob.compare(a,e)!=0 then raise_application_error(-20886,'WTASK_BASELINE_CHANGED_RRL_WAREHOUSE_TASK_ACCESS');end if;
 dbms_lob.freetemporary(a);dbms_lob.freetemporary(e);
 dbms_lob.createtemporary(a,true);dbms_lob.createtemporary(e,true);
 for s in(select TEXT from USER_SOURCE where NAME='RRL_WAREHOUSE_TASK_ACCESS'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 dbms_lob.append(e,'package body RRL_WAREHOUSE_TASK_ACCESS as

 function scoped_stock_executor(p_task number,p_actor varchar2) return number is
  t RRL_WAREHOUSE_TASK%rowtype;v_from number;v_to number;n number;v_kind varchar2(40);
 begin
  select * into t from RRL_WAREHOUSE_TASK where TASK_ID=p_task;
  if p_actor is null or t.ASSIGNED_TO is null or t.ASSIGNED_TO!=p_actor or t.HU_CONTENT_VERSION is not null then return 0;end if;
  select count(*) into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  if n!=1 then return 0;end if;
  select HU_KIND into v_kind from RRL_PALLETS where UID_PALLET=nvl(t.UID_PALLET,t.SSCC);
  if v_kind is null or v_kind!=''STOCK'' then return 0;end if;
  select count(*)into n from RRL_ST_DEFER_WAIT_PLAN where TASK_ID=p_task and CASE_TASK_ID is not null;
  if n!=0 then return 0;end if;
  select WARE_ID into v_from from RRL_CELLS where CELL=t.FROM_CELL;
  select WARE_ID into v_to from RRL_CELLS where CELL=t.TO_CELL;
  if v_from is null or v_to is null or(t.FROM_WARE_ID is not null and t.FROM_WARE_ID!=v_from)
   or(t.TO_WARE_ID is not null and t.TO_WARE_ID!=v_to)then return 0;end if;
  if RRL_ACCESS_API.allowed(p_actor,''warehouse_task_execute'',''WAREHOUSE'',to_char(v_from),t.ASSIGNED_TO)!=1
   or RRL_ACCESS_API.allowed(p_actor,''warehouse_task_execute'',''WAREHOUSE'',to_char(v_to),t.ASSIGNED_TO)!=1 then return 0;end if;
  return 1;
 exception when no_data_found then return 0;
 end;
 function task_signature(p_task number) return varchar2 is t RRL_WAREHOUSE_TASK%rowtype;
 begin select * into t from RRL_WAREHOUSE_TASK where TASK_ID=p_task;return RRL_STOCK_TASK_PLAN.signature(t);end;
 procedure assert_scope(p_task number,p_actor varchar2,p_assignee varchar2 default null) is
 ');
 dbms_lob.append(e,' v_from number;v_to number;v_ware number;v_group varchar2(100);
  procedure check_user(p_user varchar2) is
  begin
   if trim(p_user) is null then raise_application_error(-20882,''TASK_ACTIVE_USER_REQUIRED'');end if;
   begin
    select WARE_ID,USER_GROUP into v_ware,v_group from RUSERS
     where ID=p_user and nvl(DELETED,0)=0;
   exception when no_data_found then raise_application_error(-20882,''TASK_ACTIVE_USER_REQUIRED'');end;
   if upper(trim(v_group))=''GLOBAL_ADMIN'' then return;end if;
   if v_ware is null or (nvl(v_from,-1)!=v_ware and nvl(v_to,-1)!=v_ware) then
    raise_application_error(-20882,''TASK_USER_WAREHOUSE_FORBIDDEN'');end if;
  end;
 begin
  select FROM_WARE_ID,TO_WARE_ID into v_from,v_to from RRL_WAREHOUSE_TASK where TASK_ID=p_task;
  check_user(p_actor);
  if p_assignee is not null and p_assignee!=p_actor then check_user(p_assignee);end if;
 end;
 procedure assert_completion(p_request clob,p_actor varchar2) is
  v_doc json_object_t:=json_object_t.parse(p_request);v_source json_object_t;v_meta json_object_t;
  v_task number;v_permission varchar2(100):=''warehouse_task_execute'';v_task_source varchar2(40);
 begin
  v_source:=v_doc.get_object(''source'');v_task:=v_source.get_number(''task_id'');
  v_meta:=v_doc.get_object(''metadata'');
  if v_doc.get_string(''command_type'')=''TASK_COMPLETE'' and nvl(v_meta.get_number(''document_confirmation''),0)!=1
   and scoped_stock_executor(v_task,p_actor)=1 then return;end if;
  assert_scope(v_task,p_actor);
  v_meta:=v_doc.get_object(''metadata'');
  if v_meta.get_number(''document_confirmation'')=1 then
   select TASK_SOURCE into v_task_source from RRL_WAREHOUSE_TASK where TASK_ID=v_task;
   if v_task_source!=''MES_RAW_SUPPLY'' or v_tas');
 dbms_lob.append(e,'k_source is null then
    raise_application_error(-20882,''MES_DOCUMENT_CONFIRM_FORBIDDEN'');end if;
   v_permission:=''mes_raw_transfer_confirm'';
  end if;
  if RRL_HAS_WRIGHT(p_actor,v_permission)!=1 then
   raise_application_error(-20882,''TASK_CURRENT_EXECUTE_FORBIDDEN'');end if;
 end;
end;
');
 e:=replace(e,chr(13),'');if dbms_lob.compare(a,e)!=0 then raise_application_error(-20886,'WTASK_BASELINE_CHANGED_RRL_WAREHOUSE_TASK_ACCESS');end if;
 dbms_lob.freetemporary(a);dbms_lob.freetemporary(e);
 dbms_lob.createtemporary(a,true);dbms_lob.createtemporary(e,true);
 for s in(select TEXT from USER_SOURCE where NAME='RRL_TASK_RESOURCE_POLICY'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 dbms_lob.append(e,'package body RRL_TASK_RESOURCE_POLICY as
 function context_json(p_task number,p_action varchar2,p_actor varchar2,p_assignee varchar2,
  p_resource number default null,p_session number default null,p_equipment number default null) return clob is
  t RRL_WAREHOUSE_TASK%rowtype;s RRL_RESOURCE_SESSION%rowtype;r RRL_RESOURCE%rowtype;e RRL_RESOURCE_EQUIPMENT%rowtype;
  sh RRL_RESOURCE_SHIFT%rowtype;v_other_status varchar2(40);j json_object_t:=json_object_t();v_resource number:=p_resource;v_session number:=p_session;v_equipment number:=p_equipment;
  v_started_begin timestamp with time zone;v_started_end timestamp with time zone;v_current_begin timestamp with time zone;v_current_end timestamp with time zone;
  v_finishing_step boolean:=false;v_target varchar2(100):=trim(p_assignee);v_n number;v_actor varchar2(100):=trim(p_actor);v_types varchar2(1000);
 begin
  if p_action is null or p_action not in(''ASSIGN'',''START'',''COMPLETE'',''COMPLETE_DOCUMENT'') or v_actor is null or v_target is null then
   raise_application_error(-20881,''TASK_ASSIGNMENT_INPUT_REQUIRED'');end if;
  select * into t from RRL_WAREHOUSE_TASK where TASK_ID=p_task;
  if not (p_action=''COMPLETE'' and v_target=v_actor and RRL_WAREHOUSE_TASK_ACCESS.scoped_stock_executor(p_task,v_actor)=1) then RRL_WAREHOUSE_TASK_ACCESS.assert_scope(p_task,v_actor,v_target);end if;
  if t.TASK_SOURCE=''WAVE'' and t.TASK_TYPE=''PICKING_MOVE'' and p_action in(''START'',''COMPLETE'') then RRL_STOCK_WAVE_READY.assert_released(t.SOURCE_DOC_ID);end if;
  if p_action=''COMPLETE_DOCUMENT'' then
   if t.TASK_SOURCE!=''MES_RAW_SUPPLY'' or RRL_HAS_WRIGHT(v_actor,''mes_raw_transfer_confirm'')!=1 then
    raise_application_error(-20882,''MES_DOCUMENT_CONFIRM_FORBID');
 dbms_lob.append(e,'DEN'');end if;
   if p_resource is not null or p_session is not null or p_equipment is not null then
    raise_application_error(-20881,''DOCUMENT_CONFIRM_HAS_NO_RESOURCE_SESSION'');end if;
   j.put_null(''resource_id'');j.put_null(''resource_session_id'');j.put_null(''equipment_id'');return j.to_clob;
  end if;
  if RRL_HAS_WRIGHT(v_actor,''warehouse_task_execute'')!=1 and not (p_action=''COMPLETE'' and v_target=v_actor and RRL_WAREHOUSE_TASK_ACCESS.scoped_stock_executor(p_task,v_actor)=1) then raise_application_error(-20882,''TASK_EXECUTE_FORBIDDEN'');end if;
  select count(*) into v_n from RUSERS where ID=v_target and nvl(DELETED,0)=0;
  if v_n!=1 or(RRL_HAS_WRIGHT(v_target,''warehouse_task_execute'')!=1 and not (p_action=''COMPLETE'' and v_target=v_actor and RRL_WAREHOUSE_TASK_ACCESS.scoped_stock_executor(p_task,v_actor)=1))then
   raise_application_error(-20882,''TASK_ASSIGNEE_NOT_EXECUTOR'');end if;
  if p_action=''ASSIGN'' and t.STATUS not in(''PLANNED'',''ASSIGNED'') then
   raise_application_error(-20886,''TASK_ASSIGN_STATE_CONFLICT'');end if;
  if p_action=''START'' and t.STATUS not in(''PLANNED'',''ASSIGNED'',''IN_PROGRESS'') then
   raise_application_error(-20886,''TASK_START_STATE_CONFLICT'');end if;
  if p_action=''COMPLETE'' and t.STATUS not in(''PLANNED'',''ASSIGNED'',''IN_PROGRESS'') then
   raise_application_error(-20886,''TASK_COMPLETE_STATE_CONFLICT'');end if;
  if v_target!=v_actor then
   if p_action!=''ASSIGN'' or RRL_HAS_WRIGHT(v_actor,''resource_dispatch_manage'')!=1 then
    raise_application_error(-20882,''TASK_DISPATCH_PERMISSION_REQUIRED'');end if;
  end if;
  if t.ASSIGNED_TO is not null and t.ASSIGNED_TO!=v_target then
   if t.STATUS=''IN_PROGRESS'' and p_action!=''COMPLETE'' then
    raise_applicat');
 dbms_lob.append(e,'ion_error(-20886,''FINISH_CURRENT_PHYSICAL_STEP_BEFORE_REASSIGN'');end if;
   if RRL_HAS_WRIGHT(v_actor,''warehouse_task_force_assign'')!=1 then
    raise_application_error(-20882,''TASK_FORCE_ASSIGN_PERMISSION_REQUIRED'');end if;
  end if;
  if t.ASSIGNED_TO=v_target then
   v_resource:=nvl(v_resource,t.RESOURCE_ID);v_session:=nvl(v_session,t.RESOURCE_SESSION_ID);v_equipment:=nvl(v_equipment,t.EQUIPMENT_ID);
  end if;
  if p_action!=''ASSIGN'' and v_session is null and (v_resource is not null or v_equipment is not null) then raise_application_error(-20882,''TASK_RESOURCE_SESSION_REQUIRED'');end if;
  if p_action!=''ASSIGN'' and v_session is null and t.TASK_TYPE in(''PUTAWAY'',''REPLENISHMENT'',''PICKING_MOVE'',''FG_TO_STORAGE'',''RAW_TO_PRODUCTION'')
   and RRL_HAS_WRIGHT(v_actor,''warehouse_task_force_assign'')!=1 then raise_application_error(-20882,''TASK_MACHINE_SESSION_REQUIRED'');end if;
  if p_action!=''ASSIGN'' then
   select count(*) into v_n from RRL_WAREHOUSE_TASK where ASSIGNED_TO=v_target and STATUS=''IN_PROGRESS'' and TASK_ID!=p_task;
   if v_n>0 then raise_application_error(-20886,''FINISH_OTHER_OPERATOR_PHYSICAL_STEP_FIRST'');end if;
   select count(*) into v_n from RRL_CASE_PICK_TASK where ASSIGNED_TO=v_target and PICKED_QTY>0 and STATUS in(''IN_PROGRESS'',''PARTIAL'',''WAIT_REPLENISHMENT'');
   if v_n>0 then raise_application_error(-20886,''FINISH_OPERATOR_CASE_CARRIER_FIRST'');end if;
  end if;
  if v_session is not null then
   select * into s from RRL_RESOURCE_SESSION where SESSION_ID=v_session;
   if s.OPERATOR_USER_ID is null or s.OPERATOR_USER_ID!=v_target then
    raise_application_error(-20882,''TASK_SESSION_OWNER_CONFLICT'');end if;
   if s.STATUS is null or (p_action=''ASSIGN'' and s.STA');
 dbms_lob.append(e,'TUS not in(''ACTIVE'',''PAUSED''))
     or (p_action!=''ASSIGN'' and s.STATUS!=''ACTIVE'') then raise_application_error(-20886,''TASK_SESSION_NOT_ACTIVE'');end if;
   if (v_resource is not null and v_resource!=s.RESOURCE_ID) or
      (v_equipment is not null and (s.EQUIPMENT_ID is null or v_equipment!=s.EQUIPMENT_ID)) then
    raise_application_error(-20886,''TASK_SESSION_RESOURCE_IDENTITY_CONFLICT'');end if;
   select * into sh from RRL_RESOURCE_SHIFT where SHIFT_ID=s.SHIFT_ID;
   select from_tz(cast(sh.START_AT as timestamp),nvl(t.STARTED_SHIFT_TIME_ZONE,sessiontimezone)),
          from_tz(cast(sh.FINISH_AT as timestamp),nvl(t.STARTED_SHIFT_TIME_ZONE,sessiontimezone)),
          from_tz(cast(sh.START_AT as timestamp),sessiontimezone),from_tz(cast(sh.FINISH_AT as timestamp),sessiontimezone)
    into v_started_begin,v_started_end,v_current_begin,v_current_end from dual;
   v_finishing_step:=p_action in(''COMPLETE'',''COMPLETE_DOCUMENT'') and t.STATUS=''IN_PROGRESS''
    and t.RESOURCE_SESSION_ID=s.SESSION_ID and t.ASSIGNED_TO=v_target
    and t.STARTED_AT is not null and sh.START_AT is not null and sh.FINISH_AT is not null
    and ((t.STARTED_AT_INSTANT is not null and t.STARTED_SHIFT_TIME_ZONE is not null
     and t.STARTED_AT_INSTANT between v_started_begin and v_started_end)
     or (t.STARTED_AT_INSTANT is null and t.STARTED_AT between sh.START_AT and sh.FINISH_AT));
   if sh.STATUS is null or sh.STATUS not in(''PLANNED'',''OPEN'') or
     (p_action!=''ASSIGN'' and (sh.STATUS!=''OPEN'' or sh.START_AT is null or sh.FINISH_AT is null or (not v_finishing_step and (systimestamp<v_current_begin or systimestamp>v_current_end)))) then
    raise_application_error(-20886,''TASK_SHIFT_UNAVAILABLE'');end ');
 dbms_lob.append(e,'if;
   if p_action!=''ASSIGN'' and s.CURRENT_TASK_ID is not null and s.CURRENT_TASK_ID!=p_task then
    begin select STATUS into v_other_status from RRL_WAREHOUSE_TASK where TASK_ID=s.CURRENT_TASK_ID;
    exception when no_data_found then v_other_status:=''UNKNOWN'';end;
    if v_other_status not in(''DONE'',''CANCELLED'') then raise_application_error(-20886,''FINISH_CURRENT_PHYSICAL_STEP_FIRST'');end if;
   end if;
   if s.CURRENT_INVENTORY_TASK_ID is not null then
    select STATUS into v_other_status from RRL_INVENTORY_TASK where INVENTORY_TASK_ID=s.CURRENT_INVENTORY_TASK_ID;
    if v_other_status not in(''DONE'',''CANCELLED'') then raise_application_error(-20886,''FINISH_CURRENT_INVENTORY_STEP_FIRST'');end if;
   end if;
   v_resource:=s.RESOURCE_ID;v_equipment:=s.EQUIPMENT_ID;
  end if;
  if v_resource is not null then
   select * into r from RRL_RESOURCE where RESOURCE_ID=v_resource;
   if nvl(r.ACTIVE,0)!=1 or r.STATUS is null or r.STATUS not in(''AVAILABLE'',''IN_WORK'',''IDLE'')
      or (r.USER_ID is not null and r.USER_ID!=v_target) then raise_application_error(-20886,''TASK_RESOURCE_UNAVAILABLE'');end if;
   select DEFAULT_TASK_TYPES into v_types from RRL_RESOURCE_TYPE where RESOURCE_TYPE=r.RESOURCE_TYPE and ACTIVE=1;
   if v_types is null or instr('',''||replace(v_types,'' '','''')||'','','',''||t.TASK_TYPE||'','')=0 then
    raise_application_error(-20886,''TASK_RESOURCE_TYPE_UNSUITABLE'');end if;
   select count(*) into v_n from RRL_RESOURCE_TASK_QUAL where RESOURCE_ID=v_resource and TASK_TYPE=t.TASK_TYPE
    and ACTIVE=1 and VALID_FROM<=systimestamp and (VALID_UNTIL is null or VALID_UNTIL>systimestamp);
   if v_n!=1 then raise_application_error(-20886,''TASK_RESOURCE_QUALIFICATION_REQUIRED'');en');
 dbms_lob.append(e,'d if;
   if v_equipment is null and r.EQUIPMENT_ID is not null then raise_application_error(-20886,''TASK_RESOURCE_EQUIPMENT_REQUIRED'');end if;
   if r.EQUIPMENT_ID is not null and r.EQUIPMENT_ID!=v_equipment then raise_application_error(-20886,''TASK_RESOURCE_EQUIPMENT_BINDING_CONFLICT'');end if;
   if r.WARE_ID is not null and r.WARE_ID not in(nvl(t.FROM_WARE_ID,r.WARE_ID),nvl(t.TO_WARE_ID,r.WARE_ID)) then
    raise_application_error(-20886,''TASK_RESOURCE_WAREHOUSE_CONFLICT'');end if;
  end if;
  if v_equipment is not null then
   select * into e from RRL_RESOURCE_EQUIPMENT where EQUIPMENT_ID=v_equipment;
   if nvl(e.ACTIVE,0)!=1 or e.SERVICE_STATUS is null or e.SERVICE_STATUS!=''ACTIVE'' then
    raise_application_error(-20886,''TASK_EQUIPMENT_UNAVAILABLE'');end if;
   if e.WARE_ID is not null and e.WARE_ID not in(nvl(t.FROM_WARE_ID,e.WARE_ID),nvl(t.TO_WARE_ID,e.WARE_ID)) then
    raise_application_error(-20886,''TASK_EQUIPMENT_WAREHOUSE_CONFLICT'');end if;
  end if;
  if p_action=''START'' and t.STATUS=''IN_PROGRESS'' and
   (nvl(t.ASSIGNED_TO,chr(0))!=v_target or nvl(t.RESOURCE_SESSION_ID,-1)!=nvl(v_session,-1)
    or nvl(t.RESOURCE_ID,-1)!=nvl(v_resource,-1) or nvl(t.EQUIPMENT_ID,-1)!=nvl(v_equipment,-1)) then
   raise_application_error(-20886,''TASK_START_ALREADY_IN_PROGRESS'');end if;
  j.put(''resource_id'',v_resource);j.put(''resource_session_id'',v_session);j.put(''equipment_id'',v_equipment);
  j.put(''finishing_started_step'',case when v_finishing_step then 1 else 0 end);
  return j.to_clob;
 exception when no_data_found then raise_application_error(-20886,''TASK_RESOURCE_IDENTITY_NOT_FOUND'');
 end;
end;
');
 e:=replace(e,chr(13),'');if dbms_lob.compare(a,e)!=0 then raise_application_error(-20886,'WTASK_BASELINE_CHANGED_RRL_TASK_RESOURCE_POLICY');end if;
 dbms_lob.freetemporary(a);dbms_lob.freetemporary(e);
 dbms_lob.createtemporary(a,true);dbms_lob.createtemporary(e,true);
 for s in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_TASK_PLAN'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 dbms_lob.append(e,'package body RRL_STOCK_TASK_PLAN as 
 function signature(p_task RRL_WAREHOUSE_TASK%rowtype) return varchar2 is v json_object_t:=json_object_t(); 
 begin 
  v.put(''task_id'',p_task.TASK_ID);v.put(''source'',p_task.TASK_SOURCE);v.put(''kind'',p_task.TASK_TYPE); 
  v.put(''uid'',p_task.UID_PALLET);v.put(''sscc'',p_task.SSCC);v.put(''from'',p_task.FROM_CELL);v.put(''to'',p_task.TO_CELL); 
  v.put(''from_ware'',p_task.FROM_WARE_ID);v.put(''to_ware'',p_task.TO_WARE_ID);v.put(''slot_from'',p_task.FROM_CELL_SLOT_ID); 
  v.put(''slot_to'',p_task.TO_CELL_SLOT_ID);v.put(''doc_type'',p_task.SOURCE_DOC_TYPE);v.put(''doc'',p_task.SOURCE_DOC_ID); 
  v.put(''source_task'',p_task.SOURCE_TASK_ID);v.put(''movement'',p_task.SOURCE_MOVEMENT_ID); 
  v.put(''quantity'',RRL_STOCK_PLAN_HELPER.decimal_text(p_task.QTY));v.put(''unit'',p_task.UNIT_CODE); 
  v.put(''raw_article'',p_task.RAW_ARTICUL);v.put(''target_article'',p_task.TARGET_ARTICUL); 
  v.put(''status'',p_task.STATUS);v.put(''assigned_to'',p_task.ASSIGNED_TO);v.put(''resource_id'',p_task.RESOURCE_ID); 
  v.put(''resource_session_id'',p_task.RESOURCE_SESSION_ID);v.put(''equipment_id'',p_task.EQUIPMENT_ID); 
  v.put(''started_instant'',to_char(p_task.STARTED_AT_INSTANT,''YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM''));v.put(''started_zone'',p_task.STARTED_SHIFT_TIME_ZONE); 
  v.put(''mode'',p_task.QTY_MODE);v.put(''production'',p_task.PRODUCTION_ORDER_ID); 
  return rawtohex(sys.dbms_crypto.hash(v.to_clob,sys.dbms_crypto.hash_sh256)); 
 end; 
 procedure compile_task(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is 
  v_doc json_object_t:=json_object_t.parse(p_request);v_source json_object_t;v_meta json_object_t; 
  v_bind json_object_t;v_context json_obj');
 dbms_lob.append(e,'ect_t;v_task RRL_WAREHOUSE_TASK%rowtype;v_uid varchar2(200);v_article varchar2(160);v_target varchar2(200); 
  v_p json_array_t:=json_array_t();v_r json_array_t:=json_array_t();v_domain json_object_t:=json_object_t(); 
  v_task_id number;v_residual number;v_reservation number;v_new_reservation number;v_fact number;v_pick_task number;v_movement_id number;v_sync_id number;v_sync_key varchar2(400);v_from_ware number;v_to_ware number;v_source_p number;v_base varchar2(20);v_input varchar2(20);v_sap_order varchar2(100);v_sap_line varchar2(40);v_qbase number;v_num number;v_den number;v_scale number;v_uom_version number;v_uom_signature varchar2(64); 
 begin 
  v_source:=v_doc.get_object(''source'');v_meta:=v_doc.get_object(''metadata'');v_source.on_error(1); 
  v_task_id:=v_source.get_number(''task_id''); 
  if v_task_id is null or v_task_id<1 or v_task_id!=trunc(v_task_id) then raise_application_error(-20881,''TASK_ID_REQUIRED'');end if; 
  select * into v_task from RRL_WAREHOUSE_TASK where TASK_ID=v_task_id;
  if RRL_HAS_WRIGHT(v_doc.get_string(''actor''),''warehouse_task_execute'')!=1 and
   RRL_WAREHOUSE_TASK_ACCESS.scoped_stock_executor(v_task_id,v_doc.get_string(''actor''))=1 and
   (not v_meta.has(''expected_task_signature'') or v_meta.get_string(''expected_task_signature'')is null)then
    raise_application_error(-20886,''TASK_EXPECTED_SIGNATURE_REQUIRED'');end if;
  if v_meta.has(''expected_task_signature'')and v_meta.get_string(''expected_task_signature'')is not null and
   v_meta.get_string(''expected_task_signature'')!=signature(v_task)then raise_application_error(-20890,''TASK_EXPECTED_SIGNATURE_CHANGED'');end if;
 
  v_uid:=nvl(v_task.UID_PALLET,v_task.SSCC); 
  RRL_STOCK_TASK_SCAN.assert_draf');
 dbms_lob.append(e,'t(p_request,v_task_id,v_uid,v_task.FROM_CELL,v_doc.get_string(''actor'')); 
  v_meta.on_error(0); 
  if v_meta.has(''scan_draft_id'') and not v_meta.get(''scan_draft_id'').is_null then 
   RRL_STOCK_PLAN_HELPER.row_key(v_r,''RRL_TASK_SCAN_DRAFT'',v_meta.get_string(''scan_draft_id''));end if; 
  v_sync_key:=''WT:''||RRL_STOCK_PLAN_HELPER.decimal_text(v_task_id)||'':''||v_task.TASK_SOURCE||'':''||v_task.TASK_TYPE||'':''||RRL_STOCK_PLAN_HELPER.decimal_text(v_task.SOURCE_TASK_ID)||'':''||RRL_STOCK_PLAN_HELPER.decimal_text(v_task.SOURCE_MOVEMENT_ID); 
  begin select SYNC_ID into v_sync_id from RRL_WAREHOUSE_TASK_SYNC where SYNC_KEY=v_sync_key; 
  exception when no_data_found then select RRL_WH_TASK_SYNC_SQ.nextval into v_sync_id from dual;end; 
  select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=v_uid; 
  select WARE_ID into v_from_ware from RRL_CELLS where CELL=v_task.FROM_CELL; 
  select WARE_ID into v_to_ware from RRL_CELLS where CELL=v_task.TO_CELL; 
  if (v_task.FROM_WARE_ID is not null and v_task.FROM_WARE_ID!=v_from_ware) or 
   (v_task.TO_WARE_ID is not null and v_task.TO_WARE_ID!=v_to_ware) then raise_application_error(-20886,''TASK_CELL_WAREHOUSE_CONFLICT'');end if; 
  v_fact:=v_task.QTY; 
  if v_meta.has(''fact_qty'') and not v_meta.get(''fact_qty'').is_null then 
   v_fact:=RRL_STOCK_MATH.quantity(v_meta.get_string(''fact_qty'')); 
  end if; 
  select REMAIN,BASE_UOM into v_source_p,v_base from RRL_REMAINS where UID_POLETA=v_uid and CELL=v_task.FROM_CELL; 
  v_input:=nvl(v_task.UNIT_CODE,v_base); 
  RRL_STOCK_PALLET_UOM.resolve_quantity(v_uid,v_input,RRL_STOCK_PLAN_HELPER.decimal_text(v_fact), 
   v_base,v_qbase,v_uom_version,v_uom_signature); 
  v_target:=v_uid; 
  if v_fact<v_');
 dbms_lob.append(e,'task.QTY then select RRL_WAREHOUSE_TASK_SQ.nextval into v_residual from dual;end if; 
  if v_qbase<v_source_p then 
   v_target:=''PART:''||substr(rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,''AL32UTF8''),sys.dbms_crypto.hash_sh256)),1,45); -- PART prefix + 45 hex characters fits legacy UID_PALLET(50 CHAR). 
   select RRL_STOCK_RESERVATION_SQ.nextval into v_new_reservation from dual; 
  end if; 
  RRL_STOCK_PLAN_HELPER.fence(v_p,''RELEASE'',''STOCK''); 
  RRL_STOCK_PLAN_HELPER.anchor(v_r,10,''OP'',p_operation); 
  RRL_STOCK_PLAN_HELPER.anchor(v_r,70,''UNIQUE'',''STOCK.OUTBOX:''|| 
   rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,''AL32UTF8''),sys.dbms_crypto.hash_sh256))); 
  RRL_STOCK_PLAN_HELPER.row_key(v_r,''RRL_WAREHOUSE_TASK'',RRL_STOCK_PLAN_HELPER.decimal_text(v_task_id)); 
  RRL_STOCK_PLAN_HELPER.row_key(v_r,''RRL_WAREHOUSE_TASK_SYNC'',RRL_STOCK_PLAN_HELPER.decimal_text(v_sync_id)); 
  RRL_STOCK_PLAN_HELPER.anchor(v_r,70,''UNIQUE'',''TASK.SYNC:''||v_sync_key); 
  if v_residual is not null then RRL_STOCK_PLAN_HELPER.row_key(v_r,''RRL_WAREHOUSE_TASK'',RRL_STOCK_PLAN_HELPER.decimal_text(v_residual));end if; 
  if v_new_reservation is not null then RRL_STOCK_PLAN_HELPER.row_key(v_r,''RRL_STOCK_RESERVATION'',RRL_STOCK_PLAN_HELPER.decimal_text(v_new_reservation));end if; 
  if v_task.TASK_SOURCE=''WAVE'' then 
   RRL_STOCK_PLAN_HELPER.row_key(v_r,''RRL_PICK_WAVE'',RRL_STOCK_PLAN_HELPER.decimal_text(v_task.SOURCE_DOC_ID)); 
   if v_task.TASK_TYPE=''REPLENISHMENT'' then 
    RRL_STOCK_PLAN_HELPER.row_key(v_r,''RRL_PICK_WAVE_REPLENISH_TASK'',RRL_STOCK_PLAN_HELPER.decimal_text(v_task.SOURCE_TASK_ID)); 
    RRL_STOCK_SHORT_RECOVERY.plan_replenishment(v_task.SOURCE_TASK_ID');
 dbms_lob.append(e,',v_r); 
    select SOURCE_RESERVATION_ID into v_reservation from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=v_task.SOURCE_TASK_ID; 
   elsif v_task.TASK_TYPE=''PICKING_MOVE'' then 
    RRL_STOCK_PLAN_HELPER.row_key(v_r,''RRL_PICK_WAVE_TASK'',RRL_STOCK_PLAN_HELPER.decimal_text(v_task.SOURCE_TASK_ID)); 
    select PICK_TASK_ID into v_pick_task from RRL_PICK_WAVE_TASK where PICK_WAVE_TASK_ID=v_task.SOURCE_TASK_ID; 
    RRL_STOCK_PLAN_HELPER.row_key(v_r,''RRL_PICK_TASK'',RRL_STOCK_PLAN_HELPER.decimal_text(v_pick_task)); 
    begin 
     select RESERVATION_ID into v_reservation from ( 
      select RESERVATION_ID from RRL_STOCK_RESERVATION where UID_PALLET=v_uid and CELL=v_task.FROM_CELL 
       and SOURCE_DOC_TYPE=''PICK_WAVE'' and SOURCE_DOC_ID=v_task.SOURCE_DOC_ID and SOURCE_LINE_ID=v_pick_task 
       and RESERVATION_DOMAIN=''PICKING'' and RESERVATION_KIND=''HARD'' and STATUS in(''ACTIVE'',''ALLOCATED'',''PICKING'') 
       and BASE_QTY>0 order by BASE_QTY desc,RESERVATION_ID) where rownum=1; 
    exception when no_data_found then raise_application_error(-20869,''FULLPAL_OWN_SOURCE_RESERVATION_REQUIRED'');end; 
   end if; 
  elsif v_task.TASK_SOURCE=''SAP_RECEIPT'' then 
   select ORDER_ID,LINE_NUMBER into v_sap_order,v_sap_line from RRL_SAP_PALLET_RECEIPT where UID_PALLET=v_uid; 
   RRL_STOCK_PLAN_HELPER.row_key(v_r,''RRL_SAP_SUPPLY_ORDER'',v_sap_order); 
   v_domain.put(''sap_order_id'',v_sap_order);v_domain.put(''sap_line_number'',v_sap_line); 
   RRL_STOCK_PLAN_HELPER.anchor(v_r,70,''UNIQUE'',''SAP.OUTBOX:PUTAWAY:''||RRL_STOCK_PLAN_HELPER.decimal_text(v_task_id)); 
   RRL_STOCK_PLAN_HELPER.row_key(v_r,''RRL_PRIHOD_NAKLAD'',RRL_STOCK_PLAN_HELPER.decimal_text(v_task.SOURCE_DOC_ID)); 
');
 dbms_lob.append(e,'   RRL_STOCK_PLAN_HELPER.row_key(v_r,''RRL_RECEIPT_SLOT_CLAIM'',RRL_STOCK_PLAN_HELPER.decimal_text(v_task_id)); 
  elsif v_task.TASK_SOURCE in(''MES_RAW_SUPPLY'',''MES_COMPLETION'') then 
   RRL_STOCK_PLAN_HELPER.row_key(v_r,''RRL_PRODUCTION_ORDER'',RRL_STOCK_PLAN_HELPER.decimal_text(nvl(v_task.PRODUCTION_ORDER_ID,v_task.SOURCE_DOC_ID))); 
   if v_task.SOURCE_TASK_ID is not null then 
    RRL_STOCK_PLAN_HELPER.row_key(v_r,''RRL_MES_RAW_TRANSFER_TASK'',RRL_STOCK_PLAN_HELPER.decimal_text(v_task.SOURCE_TASK_ID)); 
   end if; 
   if v_task.SOURCE_MOVEMENT_ID is not null then 
    RRL_STOCK_PLAN_HELPER.row_key(v_r,''RRL_MES_MOVEMENT'',RRL_STOCK_PLAN_HELPER.decimal_text(v_task.SOURCE_MOVEMENT_ID)); 
   end if; 
  end if; 
  if v_task.TASK_SOURCE=''MES_RAW_SUPPLY'' then 
   select RESERVATION_ID into v_reservation from RRL_MES_RAW_TRANSFER_TASK where TASK_ID=v_task.SOURCE_TASK_ID; 
   select RRL_MES_MOVEMENT_SQ.nextval into v_movement_id from dual; 
   RRL_STOCK_PLAN_HELPER.row_key(v_r,''RRL_MES_MOVEMENT'',RRL_STOCK_PLAN_HELPER.decimal_text(v_movement_id)); 
  end if; 
  v_context:=json_object_t.parse(RRL_TASK_RESOURCE_POLICY.context_json(v_task_id,case when v_meta.get_number(''document_confirmation'')=1 then ''COMPLETE_DOCUMENT'' else ''COMPLETE'' end,v_doc.get_string(''actor''),v_doc.get_string(''actor''), 
   v_meta.get_number(''resource_id''),v_meta.get_number(''resource_session_id''),v_meta.get_number(''equipment_id''))); 
  if not v_context.get(''resource_session_id'').is_null then 
   RRL_STOCK_PLAN_HELPER.row_key(v_r,''RRL_RESOURCE_SESSION'',RRL_STOCK_PLAN_HELPER.decimal_text(v_context.get_number(''resource_session_id''))); 
   RRL_STOCK_PLAN_HELPER.row_key(v_r,''RUSERS'',v_doc.get_string(''actor'')); 
  end if;');
 dbms_lob.append(e,' 
  if v_task.RESOURCE_SESSION_ID is not null then 
   RRL_STOCK_PLAN_HELPER.row_key(v_r,''RRL_RESOURCE_SESSION'',RRL_STOCK_PLAN_HELPER.decimal_text(v_task.RESOURCE_SESSION_ID)); 
  end if; 
  v_domain.put(''resource_context'',v_context); 
  if v_task.FROM_CELL_SLOT_ID is not null then RRL_STOCK_PLAN_HELPER.anchor(v_r,40,''SLOT'',RRL_STOCK_PLAN_HELPER.decimal_text(v_task.FROM_CELL_SLOT_ID));end if; 
  if v_task.TO_CELL_SLOT_ID is not null then RRL_STOCK_PLAN_HELPER.anchor(v_r,40,''SLOT'',RRL_STOCK_PLAN_HELPER.decimal_text(v_task.TO_CELL_SLOT_ID));end if; 
  RRL_STOCK_PLAN_HELPER.stock_closure(v_p,v_r,v_uid,v_article,v_task.FROM_CELL,v_task.TO_CELL); 
  if v_task.TASK_SOURCE=''WAVE'' and v_task.TASK_TYPE=''REPLENISHMENT'' then 
   RRL_STOCK_PLAN_HELPER.fence(v_p,''CELL'',v_task.TO_CELL,6); 
  end if; 
  if v_target!=v_uid then 
   RRL_STOCK_PLAN_HELPER.anchor(v_r,30,''HU'',v_target);RRL_STOCK_PLAN_HELPER.anchor(v_r,50,''STOCK'',v_target); 
   RRL_STOCK_PLAN_HELPER.anchor(v_r,70,''UNIQUE'',''PALLET:''||v_target); 
  end if; 
  v_domain.put(''uom_signature'',v_uom_signature);v_domain.put(''source_p'',RRL_STOCK_PLAN_HELPER.decimal_text(v_source_p));v_domain.put(''uom_version'',v_uom_version);v_domain.put(''base_quantity'',RRL_STOCK_PLAN_HELPER.decimal_text(v_qbase)); 
  v_domain.put(''from_ware_id'',v_from_ware);v_domain.put(''to_ware_id'',v_to_ware); 
  v_domain.put(''sync_id'',v_sync_id);v_domain.put(''sync_key'',v_sync_key); 
  v_domain.put(''task_signature'',signature(v_task));v_domain.put(''target_uid'',v_target); 
  v_domain.put(''residual_task_id'',v_residual);v_domain.put(''source_reservation_id'',v_reservation); 
  v_domain.put(''new_movement_id'',v_movement_id); 
  v_domain.put(''new_reservation_id'',v_new_reservat');
 dbms_lob.append(e,'ion);v_domain.put(''pick_task_id'',v_pick_task); 
  RRL_STOCK_REPL_CONTINUATION.plan_next(v_task,v_qbase,v_residual,v_r,v_domain); 
  RRL_STOCK_REPL_BIND.plan_bind(v_task,v_qbase,v_r,v_bind);v_domain.put(''consumer_bindings'',v_bind); 
  if v_task.TASK_SOURCE=''MANUAL''and v_task.SOURCE_DOC_TYPE=''RECOVERY''then RRL_STOCK_IW_RECOVERY_PUT.plan_task(v_task,v_doc.get_string(''actor''),v_r,v_domain);end if;
  if v_task.TASK_SOURCE=''MANUAL'' and v_task.SOURCE_DOC_TYPE=''INTERWARE'' then RRL_STOCK_INTERWARE_PUT.plan_task(v_task,v_doc.get_string(''actor''),v_r,v_domain);end if; 
  if v_task.TASK_SOURCE=''MANUAL'' and v_task.SOURCE_DOC_TYPE=''STORE_RETURN'' then RRL_STOCK_STORE_RETURN_PUT.plan_task(v_task,v_doc.get_string(''actor''),v_r,v_domain);end if; 
  if v_task.TASK_SOURCE=''MANUAL''and v_task.SOURCE_DOC_TYPE=''ST_DEFER''then
   RRL_STOCK_PLAN_HELPER.fence(v_p,''CONFIG'',''WAREHOUSE'');
   RRL_ST_DEFER_WAIT_CORE.plan_task(v_task,v_doc.get_string(''actor''),v_r,v_domain);
  end if;
  p_policies:=v_p.to_clob;p_resources:=v_r.to_clob;p_domain:=v_domain.to_clob; 
 end; 
end;
');
 e:=replace(e,chr(13),'');if dbms_lob.compare(a,e)!=0 then raise_application_error(-20886,'WTASK_BASELINE_CHANGED_RRL_STOCK_TASK_PLAN');end if;
 dbms_lob.freetemporary(a);dbms_lob.freetemporary(e);
 dbms_lob.createtemporary(a,true);dbms_lob.createtemporary(e,true);
 for s in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_TASK_CORE'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 dbms_lob.append(e,'package body RRL_STOCK_TASK_CORE as 
 procedure validate_metadata(p_meta json_object_t) is 
  v_keys json_key_list:=p_meta.get_keys;v_value json_element_t;v_key varchar2(4000); 
 begin 
  for i in 1..v_keys.count loop 
   v_key:=v_keys(i);v_value:=p_meta.get(v_key); 
   if not v_value.is_null then 
    if v_key in(''resource_id'',''resource_session_id'',''equipment_id'',''document_confirmation'') then 
     if not v_value.is_number then raise_application_error(-20881,''TASK_METADATA_NUMBER_REQUIRED:''||v_key);end if; 
     if v_key!=''document_confirmation'' and (p_meta.get_number(v_key)<=0 or p_meta.get_number(v_key)!=trunc(p_meta.get_number(v_key))) then 
      raise_application_error(-20881,''TASK_RESOURCE_ID_INVALID:''||v_key);end if; 
    elsif v_key in(''scan_draft_id'',''scanned_pallet'',''scanned_from_cell'',''scanned_to_cell'') then 
     if not v_value.is_string then raise_application_error(-20881,''TASK_METADATA_STRING_REQUIRED:''||v_key);end if; 
    elsif v_key=''fact_qty'' then 
     if not v_value.is_string and not v_value.is_number then raise_application_error(-20881,''TASK_FACT_QUANTITY_TYPE'');end if; 
    elsif v_key=''unit_keys'' then 
     if not v_value.is_array then raise_application_error(-20881,''TASK_UNIT_KEYS_ARRAY_REQUIRED'');end if; 
    end if; 
   end if; 
  end loop; 
 end; 
 procedure execute_task(p_request clob,p_actor varchar2,p_result out clob) is 
  v_doc json_object_t:=json_object_t.parse(p_request);v_meta json_object_t;v_source json_object_t;v_domain json_object_t;v_context json_object_t; 
  v_plan clob;v_task RRL_WAREHOUSE_TASK%rowtype;v_residual RRL_WAREHOUSE_TASK%rowtype;v_pallet RRL_PALLETS%rowtype; 
  v_task_id number;v_qty number;v_original number;v_qbase num');
 dbms_lob.append(e,'ber;v_target varchar2(200);v_base varchar2(20); 
  v_factor_num number;v_factor_den number;v_scale number;v_version number;v_article varchar2(160); 
  v_delivered_reservation number;v_residual_id number;v_reservation number;v_new_reservation number;v_ware number;v_pick_task number; 
  v_signature varchar2(64);v_hash varchar2(64);v_op varchar2(100);v_units clob;v_n number;v_doc_status varchar2(40); 
  v_result json_object_t:=json_object_t();v_resource number;v_session number;v_equipment number;v_sync_id number;v_sync_key varchar2(400);v_session_actor varchar2(100);v_input_uom varchar2(20);v_source_p number;v_uom_signature varchar2(64);v_sap_header number;v_sap_cell varchar2(60);v_sap_ware number;v_document_confirmation number:=0; 
 begin 
  v_doc.on_error(1);v_source:=v_doc.get_object(''source'');v_meta:=v_doc.get_object(''metadata'');v_meta.on_error(0); -- Oracle 19c HAS raises for missing keys with nonzero error modes. 
  validate_metadata(v_meta); 
  if v_meta.has(''document_confirmation'') then v_document_confirmation:=nvl(v_meta.get_number(''document_confirmation''),0);end if; 
  v_op:=v_doc.get_string(''operation_id'');v_task_id:=v_source.get_number(''task_id''); 
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key(''ROW'',''RRL_WAREHOUSE_TASK'',RRL_STOCK_PLAN_HELPER.decimal_text(v_task_id))); 
  select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=v_op; 
  v_domain:=json_object_t.parse(v_plan).get_object(''domain''); 
  -- Existing assignment/start commands lock the source document before the task. 
  -- Read identity without a row lock, validate the planned signature, then use the same order. 
  select * into v_task from RRL_WAREHOUSE_TAS');
 dbms_lob.append(e,'K where TASK_ID=v_task_id; 
  if v_document_confirmation=1 then 
   if v_task.TASK_SOURCE!=''MES_RAW_SUPPLY'' or RRL_HAS_WRIGHT(p_actor,''mes_raw_transfer_confirm'')!=1 then raise_application_error(-20882,''MES_DOCUMENT_CONFIRM_FORBIDDEN'');end if; 
  elsif RRL_HAS_WRIGHT(p_actor,''warehouse_task_execute'')!=1 and RRL_WAREHOUSE_TASK_ACCESS.scoped_stock_executor(v_task_id,p_actor)!=1 then raise_application_error(-20882,''TASK_COMPLETE_FORBIDDEN'');end if; 
  if RRL_STOCK_TASK_PLAN.signature(v_task)!=v_domain.get_string(''task_signature'') then raise_application_error(-20890,''CLOSURE_CHANGED: task source'');end if; 
  if v_task.TASK_SOURCE=''WAVE'' then 
   select STATUS into v_doc_status from RRL_PICK_WAVE where PICK_WAVE_ID=v_task.SOURCE_DOC_ID for update; 
   if v_doc_status is null or v_doc_status!=''LAUNCHED'' then raise_application_error(-20886,''WAVE_PHYSICAL_EXECUTION_REQUIRES_LAUNCHED'');end if; 
  elsif v_task.TASK_SOURCE in(''MES_RAW_SUPPLY'',''MES_COMPLETION'') then 
   select STATUS into v_doc_status from RRL_PRODUCTION_ORDER where PRODUCTION_ORDER_ID=nvl(v_task.PRODUCTION_ORDER_ID,v_task.SOURCE_DOC_ID) for update; 
  elsif v_task.TASK_SOURCE=''SAP_RECEIPT'' then 
   declare 
 v_json_sql_1_1 varchar2(32767):=v_domain.get_string(''sap_order_id''); 
begin 
select NAKLAD_ID,RECEIVE_CELL,WARE_ID into v_sap_header,v_sap_cell,v_sap_ware from RRL_SAP_SUPPLY_ORDER where ORDER_ID=v_json_sql_1_1 for update; 
end; 
   if v_sap_header!=v_task.SOURCE_DOC_ID or v_sap_cell!=v_task.FROM_CELL or v_sap_ware!=v_domain.get_number(''from_ware_id'') then raise_application_error(-20890,''CLOSURE_CHANGED: putaway source order'');end if; 
   select to_char(CONDITION) into v_doc_status from RRL_PRIHOD_NAKLAD where ID');
 dbms_lob.append(e,'=v_task.SOURCE_DOC_ID for update; 
  end if; 
  select * into v_task from RRL_WAREHOUSE_TASK where TASK_ID=v_task_id for update; 
  if RRL_STOCK_TASK_PLAN.signature(v_task)!=v_domain.get_string(''task_signature'') then 
   raise_application_error(-20890,''CLOSURE_CHANGED: task identity''); 
  end if; 
  if v_task.STATUS is null or v_task.STATUS not in(''PLANNED'',''ASSIGNED'',''IN_PROGRESS'') then 
   raise_application_error(-20886,''TASK_STATE_CONFLICT'');end if; 
  v_task.FROM_WARE_ID:=v_domain.get_number(''from_ware_id'');v_task.TO_WARE_ID:=v_domain.get_number(''to_ware_id''); 
  if v_task.FROM_WARE_ID is null or v_task.TO_WARE_ID is null or (v_task.FROM_WARE_ID!=v_task.TO_WARE_ID and v_task.TASK_SOURCE not in(''MES_RAW_SUPPLY'',''MES_COMPLETION'')) then 
   raise_application_error(-20886,''INTERWAREHOUSE_COMMAND_REQUIRED'');end if; 
  if v_document_confirmation!=1 and (upper(trim(v_meta.get_string(''scanned_pallet''))) is null or 
   trim(v_meta.get_string(''scanned_pallet'')) not in(nvl(v_task.UID_PALLET,v_task.SSCC),nvl(v_task.SSCC,v_task.UID_PALLET)) 
   or upper(trim(v_meta.get_string(''scanned_from_cell''))) is null or upper(trim(v_meta.get_string(''scanned_from_cell'')))!=upper(v_task.FROM_CELL) 
   or upper(trim(v_meta.get_string(''scanned_to_cell''))) is null or upper(trim(v_meta.get_string(''scanned_to_cell'')))!=upper(v_task.TO_CELL)) then 
   raise_application_error(-20886,''TASK_SCAN_CONFLICT'');end if; 
  if v_task.TASK_SOURCE=''MANUAL''and v_task.SOURCE_DOC_TYPE=''RECOVERY''then RRL_STOCK_IW_RECOVERY_PUT.validate_task(v_task,p_actor,v_domain.get_object(''recovery_placement''));end if;
  if v_task.TASK_SOURCE=''MANUAL'' and v_task.SOURCE_DOC_TYPE=''INTERWARE'' then RRL_STOCK_INTERWARE_PUT.validate_ta');
 dbms_lob.append(e,'sk(v_task,p_actor,v_domain.get_object(''interwarehouse_placement''));end if; 
  if v_task.TASK_SOURCE=''MANUAL'' and v_task.SOURCE_DOC_TYPE=''STORE_RETURN'' then RRL_STOCK_STORE_RETURN_PUT.validate_task(v_task,p_actor,v_domain.get_object(''store_return_placement''));end if; 
  v_original:=v_task.QTY;v_qty:=v_original; 
  if v_meta.has(''fact_qty'') and not v_meta.get(''fact_qty'').is_null then v_qty:=RRL_STOCK_MATH.quantity(v_meta.get_string(''fact_qty''));end if; 
  if v_qty is null or v_qty<=0 or v_qty>v_original or (v_task.QTY_MODE=''PALLET'' and v_qty!=v_original) then 
   raise_application_error(-20886,''TASK_QUANTITY_CONFLICT'');end if; 
  if v_task.TASK_SOURCE=''MANUAL''and v_task.SOURCE_DOC_TYPE=''ST_DEFER''then RRL_ST_DEFER_WAIT_CORE.validate_task(v_task,p_actor,v_domain.get_object(''deferred_waiting''));end if;
  v_target:=v_domain.get_string(''target_uid'');v_residual_id:=v_domain.get_number(''residual_task_id''); 
  v_reservation:=v_domain.get_number(''source_reservation_id'');v_new_reservation:=v_domain.get_number(''new_reservation_id''); 
  v_pick_task:=v_domain.get_number(''pick_task_id''); 
  select * into v_pallet from RRL_PALLETS where UID_PALLET=nvl(v_task.UID_PALLET,v_task.SSCC); 
  v_article:=v_pallet.ARTICUL; 
  if (v_task.RAW_ARTICUL is not null and v_task.RAW_ARTICUL!=v_article) or (v_task.TARGET_ARTICUL is not null and v_task.TARGET_ARTICUL!=v_article) then raise_application_error(-20887,''TASK_ARTICLE_CONFLICT'');end if; 
  select BASE_UOM,REMAIN into v_input_uom,v_source_p from RRL_REMAINS where UID_POLETA=v_pallet.UID_PALLET and CELL=v_task.FROM_CELL; 
  v_input_uom:=nvl(v_task.UNIT_CODE,v_input_uom); 
  RRL_STOCK_PALLET_UOM.resolve_quantity(v_pallet.UID_PALLET,v_input_uom,RRL_ST');
 dbms_lob.append(e,'OCK_PLAN_HELPER.decimal_text(v_qty), 
   v_base,v_qbase,v_version,v_uom_signature); 
  if v_uom_signature!=v_domain.get_string(''uom_signature'') then raise_application_error(-20890,''CLOSURE_CHANGED: pallet pack'');end if; 
  if v_version!=v_domain.get_number(''uom_version'') or RRL_STOCK_PLAN_HELPER.decimal_text(v_qbase)!=v_domain.get_string(''base_quantity'') or RRL_STOCK_PLAN_HELPER.decimal_text(v_source_p)!=v_domain.get_string(''source_p'') then raise_application_error(-20890,''CLOSURE_CHANGED: task quantity policy'');end if; 
  if v_task.QTY_MODE=''PALLET'' and v_qbase!=v_source_p then raise_application_error(-20886,''WHOLE_PALLET_STOCK_CHANGED'');end if; 
  if v_task.TASK_SOURCE=''WAVE'' and v_task.TASK_TYPE=''PICKING_MOVE'' and v_task.QTY_MODE=''PALLET'' then 
   select count(*) into v_n from RRL_STOCK_RESERVATION where UID_PALLET=v_pallet.UID_PALLET and CELL=v_task.FROM_CELL 
    and RESERVATION_KIND=''HARD'' and STATUS in(''ACTIVE'',''ALLOCATED'',''PICKING'') and 
      (SOURCE_DOC_TYPE is null or SOURCE_DOC_TYPE!=''PICK_WAVE'' or SOURCE_DOC_ID is null or SOURCE_DOC_ID!=v_task.SOURCE_DOC_ID 
       or SOURCE_LINE_ID is null or SOURCE_LINE_ID!=v_pick_task or RESERVATION_DOMAIN is null or RESERVATION_DOMAIN!=''PICKING''); 
   if v_n>0 then raise_application_error(-20869,''FULLPAL_OTHER_OWNER_RESERVATION'');end if; 
   select nvl(sum(BASE_QTY),0) into v_n from RRL_STOCK_RESERVATION where UID_PALLET=v_pallet.UID_PALLET and CELL=v_task.FROM_CELL 
    and SOURCE_DOC_TYPE=''PICK_WAVE'' and SOURCE_DOC_ID=v_task.SOURCE_DOC_ID and SOURCE_LINE_ID=v_pick_task 
    and RESERVATION_DOMAIN=''PICKING'' and RESERVATION_KIND=''HARD'' and STATUS in(''ACTIVE'',''ALLOCATED'',''PICKING''); 
   if v_n!=v_qbase then raise_applicatio');
 dbms_lob.append(e,'n_error(-20869,''FULLPAL_WHOLE_OWNED_RESERVATION_REQUIRED'');end if; 
  end if; 
  if v_task.TASK_SOURCE=''WAVE'' then 
   RRL_STOCK_ELIGIBILITY.assert_source(v_pallet.UID_PALLET,v_task.FROM_CELL,v_task.FROM_WARE_ID,case when v_task.QTY_MODE=''PALLET'' and v_task.TASK_TYPE in(''REPLENISHMENT'',''PICKING_MOVE'') and v_reservation is not null then 0 else v_qbase end,null,null, 
    case when v_task.TASK_TYPE=''REPLENISHMENT'' then ''REPLENISH'' else ''ALLOCATE'' end,v_reservation,v_article); 
  end if; 
  if v_task.TASK_SOURCE=''WAVE'' then 
   select STATUS into v_doc_status from RRL_PICK_WAVE where PICK_WAVE_ID=v_task.SOURCE_DOC_ID for update; 
   if v_doc_status is null or v_doc_status!=''LAUNCHED'' then raise_application_error(-20886,''WAVE_PHYSICAL_EXECUTION_REQUIRES_LAUNCHED'');end if; 
   if v_doc_status=''CANCELLED'' then raise_application_error(-20886,''SOURCE_DOCUMENT_CANCELLED'');end if; 
  elsif v_task.TASK_SOURCE=''SAP_RECEIPT'' then 
   if v_qty!=v_original then raise_application_error(-20886,''PUTAWAY_MUST_BE_WHOLE'');end if; 
   select count(*) into v_n from RRL_SAP_PALLET_RECEIPT rec join RRL_SAP_SUPPLY_ORDER so on so.ORDER_ID=rec.ORDER_ID 
    where rec.UID_PALLET=v_pallet.UID_PALLET and so.NAKLAD_ID=v_task.SOURCE_DOC_ID and so.RECEIVE_CELL=v_task.FROM_CELL and so.WARE_ID=v_task.FROM_WARE_ID; 
   if v_n!=1 then raise_application_error(-20886,''PUTAWAY_RECEIPT_SOURCE_CONFLICT'');end if; 
   if v_task.TO_CELL_SLOT_ID is not null then 
    select count(*) into v_n from RRL_RECEIPT_SLOT_CLAIM cl join RRL_TOPOLOGY_CELL_SLOT sl on sl.CELL_SLOT_ID=cl.CELL_SLOT_ID 
     where cl.TASK_ID=v_task_id and cl.STATUS=''RESERVED'' and sl.ACTIVE=1; 
    if v_n!=1 then raise_application_error(-20886,''PUTAWA');
 dbms_lob.append(e,'Y_SLOT_CONFLICT'');end if; 
   end if; 
  elsif v_task.TASK_SOURCE in(''MES_RAW_SUPPLY'',''MES_COMPLETION'') then 
   select STATUS into v_doc_status from RRL_PRODUCTION_ORDER 
    where PRODUCTION_ORDER_ID=nvl(v_task.PRODUCTION_ORDER_ID,v_task.SOURCE_DOC_ID) for update; 
   if v_doc_status=''CANCELLED'' then raise_application_error(-20886,''SOURCE_DOCUMENT_CANCELLED'');end if; 
  elsif v_task.TASK_SOURCE=''MANUAL''and v_task.SOURCE_DOC_TYPE=''RECOVERY''then
   if v_qty!=v_original or v_target!=v_pallet.UID_PALLET then raise_application_error(-20886,''RECOVERY_WHOLE_PLACEMENT_REQUIRED'');end if;
  elsif v_task.TASK_SOURCE=''MANUAL'' and v_task.SOURCE_DOC_TYPE=''INTERWARE'' then 
   if v_qty!=v_original or v_target!=v_pallet.UID_PALLET then raise_application_error(-20886,''INTERWARE_WHOLE_PLACEMENT_REQUIRED'');end if; 
  elsif v_task.TASK_SOURCE=''MANUAL'' and v_task.SOURCE_DOC_TYPE=''STORE_RETURN'' then 
   if v_qty!=v_original or v_target!=v_pallet.UID_PALLET then raise_application_error(-20886,''STORE_RETURN_WHOLE_PLACEMENT_REQUIRED'');end if; 
   select to_char(CONDITION) into v_doc_status from RRL_PRIHOD_NAKLAD where ID=v_task.SOURCE_DOC_ID and DOCUMENT_KIND=''STORE_RETURN'' for update; 
   if v_doc_status!=''1'' then raise_application_error(-20886,''STORE_RETURN_DOCUMENT_PLACEMENT_STATE_CONFLICT'');end if; 
  elsif v_task.TASK_SOURCE=''MANUAL''and v_task.SOURCE_DOC_TYPE=''ST_DEFER''then
   if v_qty!=v_original or v_target!=v_pallet.UID_PALLET then raise_application_error(-20886,''DEFER_WAIT_WHOLE_PALLET_REQUIRED'');end if;
  else raise_application_error(-20888,''TASK_DOMAIN_HANDLER_REQUIRED'');end if; 
  if v_target!=v_pallet.UID_PALLET then 
   RRL_STOCK_LOCK_API.assert_held(70,RRL_STOCK_LOCK_API.resource_');
 dbms_lob.append(e,'key(''UNIQUE'',''PALLET:''||v_target)); 
   v_pallet.STOCK_ORIGIN_UID:=nvl(v_pallet.STOCK_ORIGIN_UID,v_pallet.UID_PALLET);v_pallet.CREATED_BY_STOCK_OP:=v_op; 
   if v_pallet.WEIGHT_BRUTTO is not null then 
    if v_pallet.UNIT_COUNT is null or v_pallet.UNIT_COUNT<=0 then raise_application_error(-20887,''PALLET_BIRTH_QUANTITY_REQUIRED'');end if; 
    v_pallet.WEIGHT_BRUTTO:=v_pallet.WEIGHT_BRUTTO*v_qbase/v_pallet.UNIT_COUNT; 
   end if; 
   v_pallet.UID_PALLET:=v_target;v_pallet.SSCC:=null;v_pallet.UNIT_COUNT:=v_qbase;v_pallet.PRINTED:=0; 
   v_pallet.STOCK_COMPOSITION_VERSION:=0;insert into RRL_PALLETS values v_pallet; 
  end if; 
  RRL_STOCK_TASK_SCAN.assert_draft(p_request,v_task_id,nvl(v_task.UID_PALLET,v_task.SSCC),v_task.FROM_CELL,p_actor); 
  if v_meta.has(''unit_keys'') and not v_meta.get(''unit_keys'').is_null and v_meta.get_array(''unit_keys'').get_size>0 then v_units:=v_meta.get_array(''unit_keys'').to_clob;end if; 
  if v_task.TASK_SOURCE=''WAVE'' and v_task.TASK_TYPE=''REPLENISHMENT'' then 
   if v_task.QTY_MODE=''PALLET'' then 
    select count(*) into v_n from RRL_STOCK_RESERVATION where UID_PALLET=nvl(v_task.UID_PALLET,v_task.SSCC) and CELL=v_task.FROM_CELL 
     and RESERVATION_KIND=''HARD'' and STATUS in(''ACTIVE'',''ALLOCATED'',''PICKING'') and BASE_QTY>0 and RESERVATION_ID!=v_reservation; 
    if v_n>0 and RRL_STOCK_REPL_SHARED.allowed(nvl(v_task.UID_PALLET,v_task.SSCC),v_task.FROM_CELL,v_task.TO_CELL,v_task.FROM_WARE_ID,v_reservation)!=1 then 
     raise_application_error(-20886,''WHOLE_REPLENISHMENT_OTHER_DESTINATION_OR_OWNER'');end if; 
   end if; 
   RRL_STOCK_REPL_CAPACITY.assert_arrival(v_task.SOURCE_TASK_ID,v_qbase); 
   RRL_STOCK_REPL_ADMISSION.assert_target(nvl(v_task.UID_P');
 dbms_lob.append(e,'ALLET,v_task.SSCC),v_task.TO_CELL,v_task.TO_WARE_ID,v_article); 
  end if; 
  RRL_STOCK_TRANSFER_CORE.move(nvl(v_task.UID_PALLET,v_task.SSCC),v_target,v_task.FROM_CELL,v_task.TO_CELL, 
   v_qbase,v_base,v_version,v_task.TO_WARE_ID,p_actor,1,v_reservation,v_units,v_new_reservation,v_task.TO_CELL_SLOT_ID,v_task.FROM_WARE_ID,case when v_task.TASK_SOURCE=''MANUAL'' and v_task.SOURCE_DOC_TYPE in(''INTERWARE'',''RECOVERY'') then ''PUTAWAY'' when v_task.TASK_SOURCE=''SAP_RECEIPT'' then ''PUTAWAY'' when v_task.TASK_SOURCE=''MANUAL'' and v_task.SOURCE_DOC_TYPE=''STORE_RETURN'' then ''QUARANTINE'' else ''ORDINARY'' end); 
  if v_task.TASK_SOURCE=''WAVE'' and v_task.TASK_TYPE=''REPLENISHMENT'' then 
   select case when UID_PALLET=v_target and CELL=v_task.TO_CELL then RESERVATION_ID else v_new_reservation end 
    into v_delivered_reservation from RRL_STOCK_RESERVATION where RESERVATION_ID=v_reservation; 
   RRL_STOCK_REPL_BIND.execute_bind(v_task,v_target,v_delivered_reservation,v_domain.get_object(''consumer_bindings''),p_actor); 
  end if; 
  v_resource:=v_meta.get_number(''resource_id'');v_session:=v_meta.get_number(''resource_session_id'');v_equipment:=v_meta.get_number(''equipment_id''); 
  if v_document_confirmation!=1 and v_session is null and v_task.ASSIGNED_TO=p_actor then v_session:=v_task.RESOURCE_SESSION_ID;end if; 
  for ses in(select SESSION_ID from RRL_RESOURCE_SESSION where SESSION_ID in(v_session,v_task.RESOURCE_SESSION_ID) order by SESSION_ID for update) loop 
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key(''ROW'',''RRL_RESOURCE_SESSION'',RRL_STOCK_PLAN_HELPER.decimal_text(ses.SESSION_ID))); 
  end loop; 
  v_context:=json_object_t.parse(RRL_TASK_RESOURCE_POLICY.context_json(v_t');
 dbms_lob.append(e,'ask_id,case when v_document_confirmation=1 then ''COMPLETE_DOCUMENT'' else ''COMPLETE'' end,p_actor,p_actor, 
   v_meta.get_number(''resource_id''),v_meta.get_number(''resource_session_id''),v_meta.get_number(''equipment_id''))); 
  if dbms_lob.compare(v_context.to_clob,v_domain.get_object(''resource_context'').to_clob)!=0 then 
   raise_application_error(-20890,''CLOSURE_CHANGED: task resource context'');end if; 
  v_resource:=v_context.get_number(''resource_id'');v_session:=v_context.get_number(''resource_session_id'');v_equipment:=v_context.get_number(''equipment_id''); 
  v_hash:=rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256)); 
  if v_residual_id is not null then 
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key(''ROW'',''RRL_WAREHOUSE_TASK'',RRL_STOCK_PLAN_HELPER.decimal_text(v_residual_id))); 
   v_residual:=v_task;v_residual.TASK_ID:=v_residual_id;v_residual.QTY:=v_original-v_qty; 
   v_residual.PARENT_TASK_ID:=v_task_id;v_residual.STATUS:=''PLANNED'';v_residual.FACT_QTY:=null; 
   v_residual.CREATED_BY:=p_actor;v_residual.CREATED_AT:=systimestamp;v_residual.COMPLETION_HASH:=null; 
   v_residual.COMPLETION_JSON:=null;v_residual.FINISHED_AT:=null;v_residual.ASSIGNED_TO:=null; 
   v_residual.STARTED_AT:=null;v_residual.STARTED_AT_INSTANT:=null;v_residual.STARTED_SHIFT_TIME_ZONE:=null;v_residual.TARGET_UID_PALLET:=null; 
   v_residual.RESOURCE_ID:=null;v_residual.RESOURCE_SESSION_ID:=null;v_residual.EQUIPMENT_ID:=null; 
   v_residual.PLANNED_START_AT:=null;v_residual.PLANNED_FINISH_AT:=case when v_task.PRIORITY=0 then v_task.PLANNED_FINISH_AT else null end;v_residual.LAST_ERROR:=''Residual of task ''||v_task_id; 
   insert into RRL_WAREHOUSE_TASK values ');
 dbms_lob.append(e,'v_residual; 
  end if; 
  update RRL_WAREHOUSE_TASK set STATUS=''DONE'',QTY=v_qty,FACT_QTY=v_qty,TARGET_UID_PALLET=v_target, 
   FROM_WARE_ID=v_task.FROM_WARE_ID,TO_WARE_ID=v_task.TO_WARE_ID,FINISHED_AT=systimestamp,ASSIGNED_TO=p_actor,RESOURCE_ID=v_resource, 
   RESOURCE_SESSION_ID=v_session,EQUIPMENT_ID=v_equipment, 
   COMPLETION_HASH=v_hash,COMPLETION_JSON=p_request,LAST_ERROR=null where TASK_ID=v_task_id; 
  insert into RRL_WAREHOUSE_TASK_STOCK_MOVE(STOCK_MOVE_ID,TASK_ID,TASK_SOURCE,TASK_TYPE,SOURCE_DOC_TYPE,SOURCE_DOC_ID, 
   SOURCE_TASK_ID,UID_PALLET,TARGET_UID_PALLET,FROM_CELL,TO_CELL,QTY,BASE_QTY,BASE_UOM,OPERATION_ID,CREATED_AT,CREATED_BY) 
   values(RRL_WH_TASK_STOCK_MOVE_SQ.nextval,v_task_id,v_task.TASK_SOURCE,v_task.TASK_TYPE,v_task.SOURCE_DOC_TYPE,v_task.SOURCE_DOC_ID, 
    v_task.SOURCE_TASK_ID,nvl(v_task.UID_PALLET,v_task.SSCC),v_target,v_task.FROM_CELL,v_task.TO_CELL,v_qty,v_qbase,v_base,v_op,systimestamp,p_actor); 
  if v_resource is not null or v_session is not null or v_equipment is not null then 
   insert into RRL_RESOURCE_FACT_EVENT(EVENT_ID,TASK_ID,SESSION_ID,RESOURCE_ID,EVENT_TYPE,EVENT_AT,EVENT_BY,PAYLOAD_JSON) 
    values(RRL_RESOURCE_FACT_EVENT_SQ.nextval,v_task_id,v_session,v_resource,''COMPLETED'',systimestamp,p_actor,p_request); 
  end if; 
  update RRL_RESOURCE_SESSION set CURRENT_TASK_ID=null 
   where SESSION_ID in(v_session,v_task.RESOURCE_SESSION_ID) and CURRENT_TASK_ID=v_task_id; 
  if v_session is not null then 
   update RRL_RESOURCE_SESSION set LAST_CELL=v_task.TO_CELL,LAST_POSITION_AT=systimestamp, 
    LAST_HEARTBEAT_AT=systimestamp where SESSION_ID=v_session and OPERATOR_USER_ID=p_actor; 
  end if; 
  RRL_STOCK_TASK_DOMAIN.sync_fact(');
 dbms_lob.append(e,'v_task,v_qty,v_target,v_residual_id,p_actor); 
  RRL_STOCK_REPL_CONTINUATION.create_next(v_task,v_domain,p_actor); 
  v_sync_id:=v_domain.get_number(''sync_id'');v_sync_key:=v_domain.get_string(''sync_key''); 
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key(''ROW'',''RRL_WAREHOUSE_TASK_SYNC'',RRL_STOCK_PLAN_HELPER.decimal_text(v_sync_id))); 
  merge into RRL_WAREHOUSE_TASK_SYNC d using(select v_sync_key SYNC_KEY from dual)s on(d.SYNC_KEY=s.SYNC_KEY) 
   when matched then update set d.SYNC_STATUS=''SYNCED'',d.SYNCED_AT=systimestamp,d.UPDATED_AT=systimestamp,d.UPDATED_BY=p_actor,d.LAST_ERROR=null 
   when not matched then insert(SYNC_ID,TASK_ID,TASK_SOURCE,TASK_TYPE,SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_TASK_ID,SOURCE_MOVEMENT_ID,SYNC_KEY,SYNC_STATUS,SYNC_ATTEMPT,CREATED_AT,UPDATED_AT,SYNCED_AT,UPDATED_BY) 
    values(v_sync_id,v_task_id,v_task.TASK_SOURCE,v_task.TASK_TYPE,v_task.SOURCE_DOC_TYPE,v_task.SOURCE_DOC_ID,v_task.SOURCE_TASK_ID,v_task.SOURCE_MOVEMENT_ID,v_sync_key,''SYNCED'',1,systimestamp,systimestamp,systimestamp,p_actor); 
  v_result.put(''operation_id'',v_op);v_result.put(''task_id'',v_task_id);v_result.put(''status'',''DONE''); 
  v_result.put(''pallet_identifier'',v_target);v_result.put(''source_pallet_identifier'',nvl(v_task.UID_PALLET,v_task.SSCC)); 
  v_result.put(''cell'',v_task.TO_CELL);v_result.put(''quantity'',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty)); 
  v_result.put(''base_quantity'',RRL_STOCK_PLAN_HELPER.decimal_text(v_qbase));v_result.put(''base_uom'',v_base); 
  v_result.put(''remaining_quantity'',RRL_STOCK_PLAN_HELPER.decimal_text(v_original-v_qty)); 
  v_result.put(''residual_task_id'',v_residual_id);v_result.put(''movement_id'',v_domain.get_number(''new_movement');
 dbms_lob.append(e,'_id''));p_result:=v_result.to_clob; 
  if v_task.TASK_SOURCE=''SAP_RECEIPT'' then 
   v_result.put(''order_id'',v_domain.get_string(''sap_order_id''));v_result.put(''line_number'',v_domain.get_string(''sap_line_number'')); 
   v_result.put(''article'',v_article);p_result:=v_result.to_clob; 
   insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON) 
    values(''PUTAWAY:''||RRL_STOCK_PLAN_HELPER.decimal_text(v_task_id),''PALLET_PUTAWAY'',p_result); 
  end if; 
 end; 
end;
');
 e:=replace(e,chr(13),'');if dbms_lob.compare(a,e)!=0 then raise_application_error(-20886,'WTASK_BASELINE_CHANGED_RRL_STOCK_TASK_CORE');end if;
 dbms_lob.freetemporary(a);dbms_lob.freetemporary(e);
 dbms_lob.createtemporary(a,true);dbms_lob.createtemporary(e,true);
 for s in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_POSTING_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 dbms_lob.append(e,'package body RRL_STOCK_POSTING_API as  
 g_request clob;g_resolution clob;g_change_before clob;g_actor varchar2(50);g_operation varchar2(100);g_kind varchar2(80);g_tx varchar2(100);g_prepared boolean:=false;  
 procedure assert_actor_active(p_actor varchar2) is v_n number;  
 begin  
  select count(*)into v_n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;  
  if v_n!=1 then raise_application_error(-20882,''STOCK_CURRENT_ACTOR_REQUIRED'');end if;  
 end;  
 procedure assert_case_slot_actor(p_request clob,p_actor varchar2)is d json_object_t:=json_object_t.parse(p_request);m json_object_t;v_case number;begin  
  if d.get_string(''command_type'')not in(''HU_RELOCATE_SLOT'',''HU_ATTACH'',''HU_DETACH'',''HU_UNPACK'',''HU_REPACK_SLOT'')then return;end if;  
  m:=d.get_object(''metadata'');  
  if d.get_string(''command_type'')=''HU_RELOCATE_SLOT''then v_case:=m.get_number(''case_task_id'');  
  else v_case:=m.get_number(''child_case_task_id'');end if;  
  if substr(d.get_object(''source'').get_string(''uid''),1,5)=''CASE:''and v_case is null then raise_application_error(-20886,''CASE_SLOT_TASK_ID_REQUIRED'');end if;  
  if v_case is null then return;end if;  
  if RRL_HAS_WRIGHT(p_actor,''warehouse_task_execute'')!=1 then raise_application_error(-20882,''CASE_SLOT_EXECUTION_FORBIDDEN'');end if;  
  RRL_CASE_TASK_ACCESS.assert_scope(v_case,p_actor,''case_move'');  
 end;  
 procedure assert_repack_actor(p_request clob,p_actor varchar2)is  
  d json_object_t:=json_object_t.parse(p_request);uid varchar2(200);ware number;user_ware number;grp varchar2(100);  
 begin  
  if d.get_string(''command_type'')!=''HU_REPACK_SLOT''then return;end if;uid:=d.get_object(''source'').get_string(''uid'');  
  select c.WARE_ID into ware fro');
 dbms_lob.append(e,'m RRL_PALLETS p join RRL_CELLS c on c.CELL=p.HU_CURRENT_CELL where p.UID_PALLET=uid;  
  select WARE_ID,USER_GROUP into user_ware,grp from RUSERS where ID=p_actor and nvl(DELETED,0)=0;  
  if ware is null or ware<1 then raise_application_error(-20886,''HU_REPACK_WARE_REQUIRED'');end if;  
  if RRL_HAS_WRIGHT(p_actor,''warehouse_task_execute'')!=1 or(nvl(upper(trim(grp)),''-'')!=''GLOBAL_ADMIN''and(user_ware is null or user_ware!=ware))then raise_application_error(-20882,''HU_REPACK_CURRENT_WARE_EXECUTOR_REQUIRED'');end if;  
 exception when no_data_found then raise_application_error(-20886,''HU_REPACK_CURRENT_SOURCE_REQUIRED'');end;  
 procedure reset_connection is  
 begin  
  RRL_STOCK_CTX_API.clear_operation;RRL_STOCK_LOCK_API.clear_plan;  
  g_request:=null;g_resolution:=null;g_change_before:=null;g_actor:=null;g_operation:=null;g_kind:=null;g_tx:=null;g_prepared:=false;  
 end;  
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null) is  
  v_doc json_object_t;v_policies clob;v_resources clob;v_exists number;v_release varchar2(20);v_domain clob;v_resolution json_object_t:=json_object_t();  
  v_plan json_array_t:=json_array_t();v_entry json_object_t:=json_object_t();v_resources_json json_array_t:=json_array_t();  
 begin  
  p_replay:=null;  
  if g_prepared or sys_context(''RRL_STOCK_WRITE_CTX'',''OPERATION_ID'') is not null then  
   raise_application_error(-20862,''POSTING_ALREADY_ENTERED'');  
  end if;  
  if p_request is null or dbms_lob.getlength(p_request)>4194304 then raise_application_error(-20871,''OPERATION_CONTRACT_INVALID''); end if;  
  v_doc:=json_object_t.parse(p_request);v_doc.on_error(1);  
  g_operation:=v_doc.get_stri');
 dbms_lob.append(e,'ng(''operation_id'');g_kind:=v_doc.get_string(''command_type'');  
  if v_doc.get_number(''contract_version'') is null or v_doc.get_number(''contract_version'')!=2 or v_doc.get_string(''actor'') is null  
   or v_doc.get_string(''actor'')!=p_actor or p_actor is null or length(p_actor)>50  
   or g_operation is null or length(g_operation)>100 or g_kind is null then  
   raise_application_error(-20871,''OPERATION_CONTRACT_INVALID'');  
  end if;  
  assert_actor_active(p_actor);
  if g_kind=''STORE_RECEIPT''then RRL_STOCK_STORE_RECEIPT_READ.require_receiver(p_actor,v_doc.get_object(''source'').get_string(''store_address''));end if;  
  if g_kind=''STORE_RETURN_DISPOSE''then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_RETURN_DISPOSE.assert_scope(doc.get_object(''source'').get_string(''request_operation_id''),p_actor);end;end if;  
  if g_kind=''STORE_RETURN_PUTAWAY_PLAN''then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_STORE_RETURN_PUT.assert_scope(doc.get_object(''source'').get_string(''receipt_operation_id''),p_actor);end;end if;  
  if g_kind=''STORE_RETURN_RECEIVE''then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_STORE_RETURN_REC_CMD.assert_scope(doc.get_object(''source'').get_string(''pickup_operation_id''),p_actor);end;end if;  
  if g_kind in(''STORE_RETURN_HANDOVER'',''STORE_RETURN_PICKUP'')then RRL_STOCK_STORE_RETURN_CUST_CMD.assert_scope(p_request,p_actor);end if;  
  if g_kind=''STORE_CUSTODY_RELEASE''then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_STORE_CUSTODY_CMD.assert_scope(doc.get_object(''source'').get_string(''receipt_operation_id''),p_actor);end;end if;  
  if g_kind=''STORE_RETURN_AP');
 dbms_lob.append(e,'PROVE''then RRL_STOCK_STORE_RETURN_CMD.assert_actor(p_actor);end if;  
  if g_kind=''STORE_RECEIPT''then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_STORE_RECEIPT_READ.require_receiver(p_actor,doc.get_object(''source'').get_string(''store_address''));end;end if;  
  if g_kind=''INTERWARE_RECOVERY_CANCEL''then declare req json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_IW_RECOVERY_CANCEL.assert_scope(req.get_object(''source'').get_string(''request_operation_id''),p_actor);end;end if;
  if g_kind=''INTERWARE_RECOVERY_PUTAWAY_PLAN''then declare req json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_IW_RECOVERY_PUT.assert_scope(req.get_object(''source'').get_string(''recovery_operation_id''),p_actor);end;end if;
  if g_kind=''INTERWARE_SHORTAGE_RECOVER''then declare req json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_IW_RECOVERY_REC.assert_scope(req.get_object(''source'').get_string(''approval_operation_id''),p_actor);end;end if;
  if g_kind in(''INTERWARE_RECOVERY_REPORT'',''INTERWARE_RECOVERY_APPROVE'')then RRL_STOCK_IW_RECOVERY_PLAN.assert_scope(p_request,p_actor);end if;
  if g_kind in(''INTERWARE_SHORTAGE_REPORT'',''INTERWARE_SHORTAGE_CONFIRM'')then RRL_STOCK_INTERWARE_SHORT_CMD.assert_scope(p_request,p_actor);end if; 
  if g_kind=''INTERWARE_CUSTODY_RELEASE''then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_INTERWARE_CUSTODY.assert_scope(doc.get_object(''source'').get_string(''receipt_operation_id''),p_actor);end;end if;  
  if g_kind=''INTERWARE_PUTAWAY_PLAN''then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_INTERWARE_PUT.assert_scope(doc.get_object(''source'').get_string(''receipt_opera');
 dbms_lob.append(e,'tion_id''),p_actor,doc.get_object(''metadata'').get_number(''superseded_task_id''));end;end if;  
  if g_kind in(''INTERWARE_UNLOAD'',''INTERWARE_RECEIVE'')then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_INTERWARE_REC.assert_scope(doc.get_object(''source'').get_string(''plan_operation_id''),p_actor);end;end if;  
  if g_kind=''LOAD_SHIPMENT''then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_LOADING_READ.assert_scope(doc.get_object(''source'').get_string(''pallet_identifier''),p_actor);end;end if;  
  if g_kind=''TARE_OFFER_CANCEL''then RRL_STOCK_TARE_CANCEL_CMD.assert_scope(p_request,p_actor);end if;  
  if g_kind=''TARE_BOOK''then RRL_TARE_LOAD_RECOVERY_API.assert_scope(p_request,p_actor);end if;assert_case_slot_actor(p_request,p_actor);assert_repack_actor(p_request,p_actor);  
  if g_kind=''UNLOAD_SHIPMENT''then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_UNLOAD_CMD.assert_scope(doc.get_object(''source'').get_string(''load_operation_id''),p_actor);end;end if;  
  if g_kind in(''TASK_COMPLETE'',''HU_TASK_COMPLETE'',''PICK_PALLET_BIND_SHIPMENT'') then RRL_WAREHOUSE_TASK_ACCESS.assert_completion(p_request,p_actor);end if;  
  if g_kind=''OUTGOING_PALLET_CHECK''then RRL_OUTGOING_QC_ACCESS.assert_identifier(json_object_t.parse(p_request).get_object(''source'').get_string(''pallet_identifier''),p_actor);end if;  
  if g_kind in(''CASE_PICK_CONFIRM'',''CASE_CARRIER_MOVE'',''CASE_CARRIER_RETURN'',''CASE_SHORT_APPROVE'')then RRL_CASE_TASK_ACCESS.assert_command(p_request,p_actor);end if;
  if g_kind=''CASE_CARRIER_MOVE''then RRL_ST_DEFER_CASE_WAIT.assert_command(p_request,p_actor);end if;  
  if g_kind in(''WAVE_LAUNCH'',''WAVE_RESERVE_SOURCES''');
 dbms_lob.append(e,',''WAVE_EXECUTION_FINISH'',''WAVE_PICK_RELEASE'')then RRL_WAVE_EXEC_ACCESS.assert_command(p_request,p_actor);end if;  
  if g_kind=''CASE_PALLET_TYPE_CHANGE''then RRL_CASE_TASK_ACCESS.assert_scope(v_doc.get_object(''source'').get_number(''case_task_id''),p_actor,''case_pick_execute'');end if;
  if g_kind=''PALLET_FLOOR_TYPE_CONFIRM''then declare doc json_object_t:=json_object_t.parse(p_request);ware_no number;begin ware_no:=RRL_PALLET_FLOOR_READ.scope_warehouse(doc.get_object(''source'').get_string(''uid''),p_actor);end;end if;
  if g_kind=''ST_PREPARED_ROW_MOVE''then declare doc json_object_t:=json_object_t.parse(p_request);w number;begin w:=RRL_ST_LAYOUT_READ.scope_order(doc.get_object(''source'').get_number(''order_id''),p_actor,''outgoing_pallet_edit'');end;end if;
  -- Immutable committed replay is considered before any mutable article/cell/UOM validation.  
  select count(*) into v_exists from RRL_STOCK_OPERATION where OPERATION_ID=g_operation;  
  if v_exists!=0 then  
   v_entry.put(''key_hex'',rawtohex(RRL_STOCK_LOCK_API.resource_key(''RELEASE'',''STOCK'')));v_entry.put(''mode'',4);v_plan.append(v_entry);  
   v_entry:=json_object_t();v_entry.put(''rank'',10);  
   v_entry.put(''key_hex'',rawtohex(RRL_STOCK_LOCK_API.resource_key(''OP'',g_operation)));v_resources_json.append(v_entry);  
   v_policies:=v_plan.to_clob;v_resources:=v_resources_json.to_clob;  
  else  
   begin  
   if g_kind=''ST_PREPARED_ROW_MOVE''then RRL_STOCK_ST_ROW_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind=''CASE_PALLET_TYPE_CHANGE''then RRL_STOCK_CASE_TYPE_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind=''PALLET_FLOOR_TYPE_CONFIRM''then RRL_STOCK_');
 dbms_lob.append(e,'PALLET_TYPE_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind=''INTERWARE_RECOVERY_CANCEL''then RRL_STOCK_IW_RECOVERY_CANCEL.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind=''INTERWARE_RECOVERY_PUTAWAY_PLAN''then RRL_STOCK_IW_RECOVERY_PUT.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind=''INTERWARE_SHORTAGE_RECOVER''then RRL_STOCK_IW_RECOVERY_REC.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in(''INTERWARE_RECOVERY_REPORT'',''INTERWARE_RECOVERY_APPROVE'')then RRL_STOCK_IW_RECOVERY_PLAN.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in(''INTERWARE_SHORTAGE_REPORT'',''INTERWARE_SHORTAGE_CONFIRM'')then RRL_STOCK_INTERWARE_SHORT_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain); 
   elsif g_kind in(''INTERWARE_UNLOAD'',''INTERWARE_RECEIVE'') then RRL_STOCK_INTERWARE_REC.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind in(''MANUAL_MOVE'',''COMPAT_MANUAL_MOVE'') then RRL_STOCK_COMMAND_PLAN.compile_move(p_request,g_operation,v_policies,v_resources);  
   elsif g_kind =''INTERWARE_PUTAWAY_PLAN'' then RRL_STOCK_INTERWARE_PUT.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind =''INTERWARE_CUSTODY_RELEASE'' then RRL_STOCK_INTERWARE_CUSTODY.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind=''STORE_RETURN_DISPOSE'' then RRL_STOCK_RETURN_DISPOSE.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind=''STORE_CUSTODY_RELEASE''then RRL_STOCK');
 dbms_lob.append(e,'_STORE_CUSTODY_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind=''RESERVATION_ALLOCATE_POOL'' then RRL_STOCK_POOL_CMD.compile_command(p_request,g_operation,p_hints,v_policies,v_resources,v_domain);  
   elsif g_kind=''PICK_PALLET_BIND_SHIPMENT'' then RRL_STOCK_FULLPAL_BIND_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind in(''HU_PLAN_MOVE'',''HU_TASK_COMPLETE'') then RRL_STOCK_HU_TASK.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind=''HU_RELOCATE_SLOT'' then RRL_STOCK_HU_SLOT_MOVE_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind=''HU_REPACK_SLOT''then RRL_STOCK_HU_REPACK_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind=''HU_UNPACK'' then RRL_STOCK_HU_UNPACK_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind in(''TARE_LOSS_REPORT'',''TARE_LOSS_DECIDE'') then RRL_STOCK_TARE_LOSS.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind in(''TARE_BOOK'',''TARE_BOOK_CANCEL'') then RRL_STOCK_TARE_BOOK_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind in(''TARE_DAMAGE'',''TARE_WRITE_OFF'') then RRL_STOCK_TARE_RESOLVE.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind=''TARE_OFFER_CANCEL''then RRL_STOCK_TARE_CANCEL_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind in(''TARE_COUNT'',''TARE_OFFER'',''TARE_ACCEPT'') then RRL_STOCK_TARE_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain)');
 dbms_lob.append(e,';  
  elsif g_kind=''STORE_RETURN_PUTAWAY_PLAN'' then RRL_STOCK_STORE_RETURN_PUT.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind=''STORE_RETURN_RECEIVE'' then RRL_STOCK_STORE_RETURN_REC_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind in(''STORE_RETURN_HANDOVER'',''STORE_RETURN_PICKUP'') then RRL_STOCK_STORE_RETURN_CUST_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind=''STORE_RETURN_TRANSPORT_PLAN'' then RRL_STOCK_STORE_RETURN_TR_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind=''STORE_RETURN_SAP_BIND'' then RRL_STOCK_STORE_RETURN_SAP_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind=''STORE_RETURN_APPROVE'' then RRL_STOCK_STORE_RETURN_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind=''STORE_CASE_WORK'' then RRL_STOCK_STORE_CASE_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind=''STORE_RECEIPT'' then RRL_STOCK_STORE_RECEIPT_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind=''RECONCILE_HU_LOAD'' then RRL_STOCK_LOAD_RECONCILE_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind=''UNLOAD_SHIPMENT'' then RRL_STOCK_UNLOAD_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind=''LOAD_SHIPMENT'' then RRL_STOCK_SINGLE_LOAD_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind=''TRIP_DEPART'' then RRL_STOCK_TRIP_DEPART_CMD.compile_command(p_request,g_o');
 dbms_lob.append(e,'peration,v_policies,v_resources,v_domain);  
  elsif g_kind=''HU_SHIP'' then RRL_STOCK_HU_SHIP_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind in(''HU_CREATE'',''HU_ATTACH'',''HU_DETACH'',''HU_MOVE'') then RRL_STOCK_HU_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind=''WAVE_EXECUTION_FINISH'' then RRL_STOCK_WAVE_FINISH_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
  elsif g_kind=''WAVE_PICK_RELEASE'' then RRL_STOCK_WAVE_PICK_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind=''WAVE_LAUNCH'' then RRL_STOCK_WAVE_LAUNCH_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind=''OUTGOING_PALLET_CHECK'' then RRL_STOCK_PALLET_QC_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind=''CASE_SHORT_APPROVE'' then RRL_STOCK_CASE_SHORT_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind=''CASE_CARRIER_RETURN'' then RRL_STOCK_CASE_RETURN_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind=''CASE_CARRIER_MOVE'' then RRL_STOCK_CASE_MOVE_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind=''CASE_PICK_CONFIRM'' then RRL_STOCK_CASE_PICK_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind=''RECEIPT_REVERSE'' then RRL_STOCK_RECEIPT_REVERSE.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind=''INVENTORY_REGISTER_LOT'' then RRL_STOCK_INVENTORY_BIRTH.compile_command(p_request,g_operati');
 dbms_lob.append(e,'on,v_policies,v_resources,v_domain);  
   elsif g_kind=''INVENTORY_COUNT'' then RRL_STOCK_INVENTORY_CMD.compile_count(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind=''MES_RAW_TASK_CANCEL'' then RRL_STOCK_MES_CANCEL_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind in(''MES_RELEASE_TO_PRODUCTION'',''MES_CALCULATE_SUPPLY'') then RRL_STOCK_MES_SUPPLY_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind in(''DOCUMENT_RELEASE_RESERVATIONS'',''WAVE_CANCEL'',''WAVE_RELEASE'',''PICK_PLAN_CANCEL'') then RRL_STOCK_DOC_RESERVE_CMD.compile_release(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind=''WAVE_RESERVE_SOURCES'' then RRL_STOCK_WAVE_CMD.compile_reserve(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind in(''SHIP_DOCUMENT'',''SHIP_PALLET'') then RRL_STOCK_SHIPPING_CORE.compile_shipment(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind in(''INTERNAL_MOVE'',''MOVE_QUARANTINE'') then RRL_STOCK_INTERNAL_CMD.compile_move(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind=''MES_MOVEMENTS'' then RRL_STOCK_MES_MOVEMENT_PLAN.compile_movements(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind=''SAP_RECEIPT'' then RRL_STOCK_RECEIPT_PLAN.compile_receipt(p_request,g_operation,p_hints,v_policies,v_resources,v_domain);  
   elsif g_kind=''TASK_COMPLETE'' then RRL_STOCK_TASK_PLAN.compile_task(p_request,g_operation,v_policies,v_resources,v_domain);  
   elsif g_kind in(''RESERVATION_CREATE'',''RESERVATION_PROMOTE'',''RESERVATION_RELEASE'',''RESERVATION_CANCEL'',''RESERVATION_CONSUME'') then RRL_STOCK_RESERVAT');
 dbms_lob.append(e,'ION_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);  
   else raise_application_error(-20888,''COMMAND_HANDLER_NOT_INSTALLED'');end if;  
   exception when others then  
    -- A concurrent identical command may have committed while this planner read mutable stock.  
    -- Rebuild only the existing replay lock plan; never take OP before the full resource plan.  
    select count(*) into v_exists from RRL_STOCK_OPERATION where OPERATION_ID=g_operation;  
    if v_exists=0 then raise;end if;  
    v_domain:=null;v_plan:=json_array_t();v_resources_json:=json_array_t();  
    v_entry:=json_object_t();v_entry.put(''key_hex'',rawtohex(RRL_STOCK_LOCK_API.resource_key(''RELEASE'',''STOCK'')));v_entry.put(''mode'',4);v_plan.append(v_entry);  
    v_entry:=json_object_t();v_entry.put(''rank'',10);v_entry.put(''key_hex'',rawtohex(RRL_STOCK_LOCK_API.resource_key(''OP'',g_operation)));v_resources_json.append(v_entry);  
    v_policies:=v_plan.to_clob;v_resources:=v_resources_json.to_clob;  
   end;  
  end if;  
  if v_domain is not null and p_hints is not null and g_kind in(''INVENTORY_REGISTER_LOT'',''MES_MOVEMENTS'') then  
   declare h json_object_t:=json_object_t.parse(p_hints);a json_array_t;b json_object_t;u json_object_t;  
    rr json_array_t:=json_array_t.parse(v_resources);dom json_object_t:=json_object_t.parse(v_domain);  
    uid varchar2(150);qty varchar2(30);base varchar2(20);cell varchar2(60);expected_article varchar2(160);found boolean;total number;  
   begin  
    a:=h.get_array(''births'');if a.get_size>200 then raise_application_error(-20881,''BIRTH_CAPTURE_BOUND'');end if;  
    for i in 0..a.get_size-1 loop  
     b:=treat(a.get(i) as json_object_t);uid:=b.');
 dbms_lob.append(e,'get_string(''uid'');found:=false;  
     if g_kind=''INVENTORY_REGISTER_LOT'' and dom.get_string(''uid'')=uid then  
      found:=true;qty:=dom.get_string(''quantity'');base:=dom.get_string(''base'');cell:=dom.get_string(''cell'');expected_article:=dom.get_string(''article'');  
     elsif g_kind=''MES_MOVEMENTS'' then  
      for z in 0..dom.get_array(''movements'').get_size-1 loop  
       u:=treat(dom.get_array(''movements'').get(z) as json_object_t);  
       if u.get_string(''physical_uid'')=uid and u.get_number(''movement_id'')=b.get_number(''movement_id'') then  
        declare m RRL_MES_MOVEMENT%rowtype;mid number:=u.get_number(''movement_id'');begin  
         select * into m from RRL_MES_MOVEMENT where MOVEMENT_ID=mid;  
         if m.MOVEMENT_TYPE!=''FG_PALLET_RELEASE'' then raise_application_error(-20884,''NOT_A_BIRTH_MOVEMENT'');end if;  
         found:=true;qty:=u.get_string(''base_quantity'');base:=u.get_string(''base_uom'');cell:=m.TARGET_LOCATION;expected_article:=u.get_string(''article'');  
        end;  
       end if;  
      end loop;  
     end if;  
     if not found or RRL_STOCK_MATH.quantity(b.get_string(''quantity''))!=RRL_STOCK_MATH.quantity(qty) or b.get_string(''article'')!=expected_article or b.get_string(''base'')!=base or b.get_string(''cell'')!=cell  
      then raise_application_error(-20890,''CLOSURE_CHANGED: birth capture'');end if;  
     total:=0;  
     if b.get_array(''unit_bindings'').get_size<1 or b.get_array(''unit_bindings'').get_size>10000 then raise_application_error(-20881,''BIRTH_UNIT_BOUND'');end if;  
     for z in 0..b.get_array(''unit_bindings'').get_size-1 loop  
      u:=treat(b.get_array(''unit_bindings'').get(z) as json_object_t);  
      total:=total+RRL_STOCK_MATH.quan');
 dbms_lob.append(e,'tity(u.get_string(''quantity''));  
      RRL_STOCK_PLAN_HELPER.anchor(rr,60,''UNIT'',u.get_string(''key''));  
     end loop;  
     if total!=RRL_STOCK_MATH.quantity(qty) then raise_application_error(-20884,''BIRTH_UNIT_QUANTITY_CONFLICT'');end if;  
     for z in 0..b.get_array(''aliases'').get_size-1 loop  
      u:=treat(b.get_array(''aliases'').get(z) as json_object_t);  
      RRL_STOCK_PLAN_HELPER.anchor(rr,70,''UNIQUE'',''MARK:''||u.get_string(''system'')||'':''||u.get_string(''hash''));  
     end loop;  
    end loop;  
    v_resources:=rr.to_clob;v_resolution.put(''births'',a);  
   end;  
  end if;  
  -- A composition update is a predeclared part of the same command, never a late lock.  
  declare rr json_array_t:=json_array_t.parse(v_resources);uid_value varchar2(200);raw_resources clob:=v_resources;begin  
   for k in(select distinct KEY_HEX from json_table(raw_resources,''$[*]'' columns(RANK_NO number path ''$.rank'',KEY_HEX varchar2(2000) path ''$.key_hex'')) where RANK_NO=50) loop  
    uid_value:=RRL_STOCK_INVARIANT_CORE.stock_uid(hextoraw(k.KEY_HEX));  
    RRL_STOCK_PLAN_HELPER.row_key(rr,''RRL_PALLETS'',uid_value);  
    for ct in(select CASE_PICK_TASK_ID,LEGACY_SBORKA_PALLET_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID in(select CASE_PICK_TASK_ID from RRL_CASE_CARRIER_LOT where LOT_UID=uid_value)) loop  
     RRL_STOCK_PLAN_HELPER.row_key(rr,''RRL_CASE_PICK_TASK'',RRL_STOCK_PLAN_HELPER.decimal_text(ct.CASE_PICK_TASK_ID));  
     if ct.LEGACY_SBORKA_PALLET_ID is not null then RRL_STOCK_PLAN_HELPER.row_key(rr,''RRL_SBORKA_PALLETS'',RRL_STOCK_PLAN_HELPER.decimal_text(ct.LEGACY_SBORKA_PALLET_ID));end if;  
    end loop;  
    for st in(select distinct LEGACY_SBORKA_PALLET_ID from R');
 dbms_lob.append(e,'RL_CUSTOMER_ORDER_FULFILLMENT where PICKED_PALLET_UID=uid_value and LEGACY_SBORKA_PALLET_ID is not null) loop  
     RRL_STOCK_PLAN_HELPER.row_key(rr,''RRL_SBORKA_PALLETS'',RRL_STOCK_PLAN_HELPER.decimal_text(st.LEGACY_SBORKA_PALLET_ID));  
    end loop;  
   end loop;v_resources:=rr.to_clob;  
  end;  
  RRL_STOCK_LOCK_API.begin_plan;
  if g_kind in(''WAVE_LAUNCH'',''WAVE_RESERVE_SOURCES'',''STORE_RECEIPT'',''TASK_COMPLETE'',''CASE_PICK_CONFIRM'')then lock table RRL_ACCESS_REV in share mode wait 5;end if;  
  RRL_STOCK_LOCK_API.acquire_policies(v_policies);  
  RRL_STOCK_LOCK_API.acquire_resources(v_resources);  
  assert_actor_active(p_actor);
  if g_kind=''STORE_RECEIPT''then RRL_STOCK_STORE_RECEIPT_READ.require_receiver(p_actor,v_doc.get_object(''source'').get_string(''store_address''));end if;  
  if g_kind=''STORE_RETURN_DISPOSE''then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_RETURN_DISPOSE.assert_scope(doc.get_object(''source'').get_string(''request_operation_id''),p_actor);end;end if;  
  if g_kind=''STORE_RETURN_PUTAWAY_PLAN''then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_STORE_RETURN_PUT.assert_scope(doc.get_object(''source'').get_string(''receipt_operation_id''),p_actor);end;end if;  
  if g_kind=''STORE_RETURN_RECEIVE''then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_STORE_RETURN_REC_CMD.assert_scope(doc.get_object(''source'').get_string(''pickup_operation_id''),p_actor);end;end if;  
  if g_kind in(''STORE_RETURN_HANDOVER'',''STORE_RETURN_PICKUP'')then RRL_STOCK_STORE_RETURN_CUST_CMD.assert_scope(p_request,p_actor);end if;  
  if g_kind=''STORE_CUSTODY_RELEASE''then declare doc json_object_t:=json_object_t.pa');
 dbms_lob.append(e,'rse(p_request);begin RRL_STOCK_STORE_CUSTODY_CMD.assert_scope(doc.get_object(''source'').get_string(''receipt_operation_id''),p_actor);end;end if;  
  if g_kind=''STORE_RETURN_APPROVE''then RRL_STOCK_STORE_RETURN_CMD.assert_actor(p_actor);end if;  
  if g_kind=''STORE_RECEIPT''then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_STORE_RECEIPT_READ.require_receiver(p_actor,doc.get_object(''source'').get_string(''store_address''));end;end if;  
  if g_kind=''INTERWARE_RECOVERY_CANCEL''then declare req json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_IW_RECOVERY_CANCEL.assert_scope(req.get_object(''source'').get_string(''request_operation_id''),p_actor);end;end if;
  if g_kind=''INTERWARE_RECOVERY_PUTAWAY_PLAN''then declare req json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_IW_RECOVERY_PUT.assert_scope(req.get_object(''source'').get_string(''recovery_operation_id''),p_actor);end;end if;
  if g_kind=''INTERWARE_SHORTAGE_RECOVER''then declare req json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_IW_RECOVERY_REC.assert_scope(req.get_object(''source'').get_string(''approval_operation_id''),p_actor);end;end if;
  if g_kind in(''INTERWARE_RECOVERY_REPORT'',''INTERWARE_RECOVERY_APPROVE'')then RRL_STOCK_IW_RECOVERY_PLAN.assert_scope(p_request,p_actor);end if;
  if g_kind in(''INTERWARE_SHORTAGE_REPORT'',''INTERWARE_SHORTAGE_CONFIRM'')then RRL_STOCK_INTERWARE_SHORT_CMD.assert_scope(p_request,p_actor);end if; 
  if g_kind=''INTERWARE_CUSTODY_RELEASE''then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_INTERWARE_CUSTODY.assert_scope(doc.get_object(''source'').get_string(''receipt_operation_id''),p_actor);end;end if;  
  if g_kind=''INTERW');
 dbms_lob.append(e,'ARE_PUTAWAY_PLAN''then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_INTERWARE_PUT.assert_scope(doc.get_object(''source'').get_string(''receipt_operation_id''),p_actor,doc.get_object(''metadata'').get_number(''superseded_task_id''));end;end if;  
  if g_kind in(''INTERWARE_UNLOAD'',''INTERWARE_RECEIVE'')then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_INTERWARE_REC.assert_scope(doc.get_object(''source'').get_string(''plan_operation_id''),p_actor);end;end if;  
  if g_kind=''LOAD_SHIPMENT''then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_LOADING_READ.assert_scope(doc.get_object(''source'').get_string(''pallet_identifier''),p_actor);end;end if;  
  if g_kind=''TARE_OFFER_CANCEL''then RRL_STOCK_TARE_CANCEL_CMD.assert_scope(p_request,p_actor);end if;  
  if g_kind=''TARE_BOOK''then RRL_TARE_LOAD_RECOVERY_API.assert_scope(p_request,p_actor);end if;assert_case_slot_actor(p_request,p_actor);assert_repack_actor(p_request,p_actor);  
  if g_kind=''UNLOAD_SHIPMENT''then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_UNLOAD_CMD.assert_scope(doc.get_object(''source'').get_string(''load_operation_id''),p_actor);end;end if;  
  select STATE into v_release from RRL_STOCK_RELEASE where RELEASE_ID=1;  
  if v_release!=''ACTIVE'' then raise_application_error(-20860,''STOCK_RELEASE_NOT_ACTIVE''); end if;  
  if v_domain is not null then v_resolution.put(''domain'',json_object_t.parse(v_domain));end if;  
  v_resolution.put(''stock_before'',json_array_t.parse(RRL_STOCK_INVARIANT_CORE.snapshot_stock(v_resources)));  
  v_resolution.put(''physical_before'',json_array_t.parse(RRL_STOCK_COMPOSITION_CORE.snapshot_before(v_res');
 dbms_lob.append(e,'ources)));  
  v_resolution.put(''resources'',json_array_t.parse(v_resources));  
  v_resolution.put(''policies'',json_array_t.parse(v_policies));  
  if g_kind in(''TASK_COMPLETE'',''HU_TASK_COMPLETE'',''PICK_PALLET_BIND_SHIPMENT'') then RRL_WAREHOUSE_TASK_ACCESS.assert_completion(p_request,p_actor);end if;  
  if g_kind=''OUTGOING_PALLET_CHECK''then RRL_OUTGOING_QC_ACCESS.assert_identifier(json_object_t.parse(p_request).get_object(''source'').get_string(''pallet_identifier''),p_actor);end if;  
  if g_kind in(''CASE_PICK_CONFIRM'',''CASE_CARRIER_MOVE'',''CASE_CARRIER_RETURN'',''CASE_SHORT_APPROVE'')then RRL_CASE_TASK_ACCESS.assert_command(p_request,p_actor);end if;
  if g_kind=''CASE_CARRIER_MOVE''then RRL_ST_DEFER_CASE_WAIT.assert_command(p_request,p_actor);end if;  
  if g_kind in(''WAVE_LAUNCH'',''WAVE_RESERVE_SOURCES'',''WAVE_EXECUTION_FINISH'',''WAVE_PICK_RELEASE'')then RRL_WAVE_EXEC_ACCESS.assert_command(p_request,p_actor);end if;  
  RRL_STOCK_OPERATION_CORE.begin_operation(p_request,p_actor,g_operation,g_kind,p_replay,v_resolution.to_clob);  
  if p_replay is not null then return; end if;  
  g_change_before:=RRL_STOCK_CHANGE_AUDIT.snapshot(v_resources);  
  g_request:=p_request;g_resolution:=v_resolution.to_clob;g_actor:=p_actor;g_tx:=dbms_transaction.local_transaction_id(false);g_prepared:=true;  
  if g_kind=''SAP_RECEIPT'' then RRL_STOCK_CTX_API.begin_staging(v_resolution.get_object(''domain'').get_string(''uid''),v_resolution.get_object(''domain'').get_string(''receive_cell''));end if;  
 end;  
 procedure stage_birth(p_uid varchar2) is  
  d json_object_t:=json_object_t.parse(g_resolution);b json_object_t;v json_object_t;a json_array_t;  
  n number;policy number;capture_required number;found boolea');
 dbms_lob.append(e,'n:=false;uid varchar2(150);article varchar2(160);cell varchar2(60);qty number;  
  doc number;expiry date;price number;mid number;m RRL_MES_MOVEMENT%rowtype;  
 begin  
  if not g_prepared or g_tx is null or g_tx!=dbms_transaction.local_transaction_id(false)  
   or g_kind not in(''INVENTORY_REGISTER_LOT'',''MES_MOVEMENTS'') then raise_application_error(-20850,''WRITE_PLAN_VIOLATION'');end if;  
  if RRL_HAS_WRIGHT(g_actor,case when g_kind=''INVENTORY_REGISTER_LOT'' then ''stock_inventory_count'' else ''mes_wms_bridge_apply'' end)!=1  
   then raise_application_error(-20882,''BIRTH_CAPTURE_FORBIDDEN'');end if;  
  a:=d.get_array(''births'');  
  for i in 0..a.get_size-1 loop  
   b:=treat(a.get(i) as json_object_t);  
   if b.get_string(''uid'')=p_uid then found:=true;exit;end if;  
  end loop;  
  if not found then raise_application_error(-20884,''BIRTH_CAPTURE_NOT_PLANNED'');end if;  
  uid:=b.get_string(''uid'');article:=b.get_string(''article'');cell:=b.get_string(''cell'');qty:=RRL_STOCK_MATH.quantity(b.get_string(''quantity''));  
  select POLICY_VERSION,greatest(MARKING_REQUIRED,SERIALIZED_WEIGHT_BOXES)into policy,capture_required from RRL_SKU_RECEIPT_POLICY where ARTICUL=article;  
  if capture_required!=1 or policy!=b.get_number(''policy_version'') then raise_application_error(-20890,''CLOSURE_CHANGED: birth marking policy'');end if;  
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key(''HU'',uid));  
  select count(*) into n from RRL_REMAINS where UID_POLETA=uid and REMAIN>0;  
  if n>0 then raise_application_error(-20886,''BIRTH_STOCK_ALREADY_EXISTS'');end if;  
  select count(*) into n from RRL_PALLETS where UID_PALLET=uid;  
  if n=0 then  
   if g_kind=''INVENTORY_REGISTER_LOT''');
 dbms_lob.append(e,' then  
    v:=d.get_object(''domain'');doc:=v.get_number(''document'');expiry:=to_date(v.get_string(''expiry_date''),''FXYYYY-MM-DD'');price:=v.get_number(''price'');  
    insert into RRL_PALLETS(UID_PALLET,ARTICUL,CREATION_DATE,EXPIRY_DATE,UNIT_COUNT,PRICE,PRIHOD_NAKLAD_ID,STOCK_ORIGIN_UID,CREATED_BY_STOCK_OP)  
     values(uid,article,systimestamp,expiry,qty,price,-doc,uid,g_operation);  
   else  
    mid:=b.get_number(''movement_id'');select * into m from RRL_MES_MOVEMENT where MOVEMENT_ID=mid;  
    insert into RRL_PALLETS(UID_PALLET,ARTICUL,UNIT_COUNT,PRIHOD_NAKLAD_ID,PROD_BATCH_ID,SSCC,QUALITY_STATUS,CREATED_BY_STOCK_OP)  
     values(uid,article,qty,0,m.PROD_BATCH_ID,m.SSCC,''RELEASED'',g_operation);  
   end if;  
  end if;  
  RRL_STOCK_CTX_API.begin_staging(uid,cell);  
 end;  
 procedure finish_birth_capture is  
 begin  
  if not g_prepared or g_tx!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20850,''WRITE_PLAN_VIOLATION'');end if;  
  RRL_STOCK_CTX_API.end_effect;  
 end;  
 procedure execute_prepared(p_result out clob) is  
  v_outbox number;v_existing number;v_key varchar2(100);v_json json_object_t;v_resolved json_object_t;v_event json_object_t;v_changes clob;v_resources clob;v_after clob;v_composition json_object_t;v_unit_changes json_array_t;v_unit_change json_object_t;v_old_unit json_object_t;v_new_unit json_object_t;v_repacking boolean:=false;  
 begin  
  if not g_prepared or g_tx is null or dbms_transaction.local_transaction_id(false) is null  
   or g_tx!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20850,''WRITE_PLAN_VIOLATION''); end if;  
  if g_kind=''SAP_RECEIPT'' then RRL_STOCK_CTX_API.end_effect;end ');
 dbms_lob.append(e,'if;  
  if g_kind=''ST_PREPARED_ROW_MOVE''then RRL_STOCK_ST_ROW_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind=''CASE_PALLET_TYPE_CHANGE''then RRL_STOCK_CASE_TYPE_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind=''PALLET_FLOOR_TYPE_CONFIRM''then RRL_STOCK_PALLET_TYPE_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind in(''MANUAL_MOVE'',''COMPAT_MANUAL_MOVE'') then RRL_STOCK_MOVE_CORE.manual_whole(g_request,g_actor,p_result);  
  elsif g_kind=''PICK_PALLET_BIND_SHIPMENT'' then RRL_STOCK_FULLPAL_BIND_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind in(''HU_PLAN_MOVE'',''HU_TASK_COMPLETE'') then RRL_STOCK_HU_TASK.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''HU_RELOCATE_SLOT'' then RRL_STOCK_HU_SLOT_MOVE_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''HU_REPACK_SLOT''then RRL_STOCK_HU_REPACK_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''HU_UNPACK'' then RRL_STOCK_HU_UNPACK_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind in(''TARE_LOSS_REPORT'',''TARE_LOSS_DECIDE'') then RRL_STOCK_TARE_LOSS.execute_command(g_request,g_actor,p_result);  
  elsif g_kind in(''TARE_BOOK'',''TARE_BOOK_CANCEL'') then RRL_STOCK_TARE_BOOK_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind in(''TARE_DAMAGE'',''TARE_WRITE_OFF'') then RRL_STOCK_TARE_RESOLVE.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''TARE_OFFER_CANCEL''then RRL_STOCK_TARE_CANCEL_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind in(''TARE_COUNT'',''TARE_OFFER'',''TARE_ACCEPT'') then RRL_STOCK_TARE_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''STORE_RETURN_PUTAWAY_PLAN'' t');
 dbms_lob.append(e,'hen RRL_STOCK_STORE_RETURN_PUT.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''STORE_RETURN_RECEIVE'' then RRL_STOCK_STORE_RETURN_REC_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind in(''STORE_RETURN_HANDOVER'',''STORE_RETURN_PICKUP'') then RRL_STOCK_STORE_RETURN_CUST_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''STORE_RETURN_TRANSPORT_PLAN'' then RRL_STOCK_STORE_RETURN_TR_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''STORE_RETURN_SAP_BIND'' then RRL_STOCK_STORE_RETURN_SAP_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''STORE_RETURN_APPROVE'' then RRL_STOCK_STORE_RETURN_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''STORE_CASE_WORK'' then RRL_STOCK_STORE_CASE_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''STORE_RECEIPT'' then RRL_STOCK_STORE_RECEIPT_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''RECONCILE_HU_LOAD'' then RRL_STOCK_LOAD_RECONCILE_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''UNLOAD_SHIPMENT'' then RRL_STOCK_UNLOAD_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''INTERWARE_RECOVERY_CANCEL''then RRL_STOCK_IW_RECOVERY_CANCEL.execute_command(g_request,g_actor,p_result);
  elsif g_kind=''INTERWARE_RECOVERY_PUTAWAY_PLAN''then RRL_STOCK_IW_RECOVERY_PUT.execute_command(g_request,g_actor,p_result);
  elsif g_kind=''INTERWARE_SHORTAGE_RECOVER''then RRL_STOCK_IW_RECOVERY_REC.execute_command(g_request,g_actor,p_result);
  elsif g_kind in(''INTERWARE_RECOVERY_REPORT'',''INTERWARE_RECOVERY_APPROVE'')then RRL_STOCK_IW_RECOVERY_PLAN.execute_command(g_request,g_actor,p_result);
  elsif g_kind in(''INTERWAR');
 dbms_lob.append(e,'E_SHORTAGE_REPORT'',''INTERWARE_SHORTAGE_CONFIRM'')then RRL_STOCK_INTERWARE_SHORT_CMD.execute_command(g_request,g_actor,p_result); 
  elsif g_kind in(''INTERWARE_UNLOAD'',''INTERWARE_RECEIVE'') then RRL_STOCK_INTERWARE_REC.execute_command(g_request,g_actor,p_result);  
  elsif g_kind =''INTERWARE_PUTAWAY_PLAN'' then RRL_STOCK_INTERWARE_PUT.execute_command(g_request,g_actor,p_result);  
  elsif g_kind =''INTERWARE_CUSTODY_RELEASE'' then RRL_STOCK_INTERWARE_CUSTODY.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''STORE_RETURN_DISPOSE'' then RRL_STOCK_RETURN_DISPOSE.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''STORE_CUSTODY_RELEASE''then RRL_STOCK_STORE_CUSTODY_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''LOAD_SHIPMENT'' then RRL_STOCK_SINGLE_LOAD_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''TRIP_DEPART'' then RRL_STOCK_TRIP_DEPART_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''HU_SHIP'' then RRL_STOCK_HU_SHIP_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind in(''HU_CREATE'',''HU_ATTACH'',''HU_DETACH'',''HU_MOVE'') then RRL_STOCK_HU_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''WAVE_EXECUTION_FINISH'' then RRL_STOCK_WAVE_FINISH_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''WAVE_PICK_RELEASE'' then RRL_STOCK_WAVE_PICK_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''WAVE_LAUNCH'' then RRL_STOCK_WAVE_LAUNCH_CMD.execute_command(g_request,g_actor,p_result);  
   elsif g_kind=''OUTGOING_PALLET_CHECK'' then RRL_STOCK_PALLET_QC_CMD.execute_command(g_request,g_actor,p_result);  
   elsif g_kind=''CASE_SHORT_APPROVE'' then RRL_STOCK_CASE_SHORT_');
 dbms_lob.append(e,'CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''CASE_CARRIER_RETURN'' then RRL_STOCK_CASE_RETURN_CMD.execute_command(g_request,g_actor,p_result);  
   elsif g_kind=''CASE_CARRIER_MOVE'' then RRL_STOCK_CASE_MOVE_CMD.execute_command(g_request,g_actor,p_result);  
   elsif g_kind=''CASE_PICK_CONFIRM'' then RRL_STOCK_CASE_PICK_CMD.execute_command(g_request,g_actor,p_result);  
   elsif g_kind=''RECEIPT_REVERSE'' then RRL_STOCK_RECEIPT_REVERSE.execute_command(g_request,g_actor,p_result);  
   elsif g_kind=''INVENTORY_REGISTER_LOT'' then RRL_STOCK_INVENTORY_BIRTH.execute_command(g_request,g_actor,p_result);  
   elsif g_kind=''INVENTORY_COUNT'' then RRL_STOCK_INVENTORY_CMD.execute_count(g_request,g_actor,p_result);  
   elsif g_kind=''MES_RAW_TASK_CANCEL'' then RRL_STOCK_MES_CANCEL_CMD.execute_command(g_request,g_actor,p_result);  
   elsif g_kind in(''MES_RELEASE_TO_PRODUCTION'',''MES_CALCULATE_SUPPLY'') then RRL_STOCK_MES_SUPPLY_CMD.execute_command(g_request,g_actor,p_result);  
   elsif g_kind in(''DOCUMENT_RELEASE_RESERVATIONS'',''WAVE_CANCEL'',''WAVE_RELEASE'',''PICK_PLAN_CANCEL'') then RRL_STOCK_DOC_RESERVE_CMD.execute_release(g_request,g_actor,p_result);  
  elsif g_kind=''RESERVATION_ALLOCATE_POOL'' then RRL_STOCK_POOL_CMD.execute_command(g_request,g_actor,p_result);  
  elsif g_kind=''WAVE_RESERVE_SOURCES'' then RRL_STOCK_WAVE_CMD.execute_reserve(g_request,g_actor,p_result);  
  elsif g_kind in(''SHIP_DOCUMENT'',''SHIP_PALLET'') then RRL_STOCK_SHIPPING_CORE.execute_shipment(g_request,g_actor,p_result);  
  elsif g_kind in(''INTERNAL_MOVE'',''MOVE_QUARANTINE'') then RRL_STOCK_INTERNAL_CMD.execute_move(g_request,g_actor,p_result);  
  elsif g_kind=''MES_MOVEMENTS'' then RRL_STOCK_MES_MOVEME');
 dbms_lob.append(e,'NT_CORE.execute_movements(g_request,g_actor,p_result);  
  elsif g_kind=''SAP_RECEIPT'' then RRL_STOCK_RECEIPT_CORE.execute_receipt(g_request,g_actor,p_result);  
  elsif g_kind=''TASK_COMPLETE'' then RRL_STOCK_TASK_CORE.execute_task(g_request,g_actor,p_result);  
  elsif g_kind in(''RESERVATION_CREATE'',''RESERVATION_PROMOTE'',''RESERVATION_RELEASE'',''RESERVATION_CANCEL'',''RESERVATION_CONSUME'') then RRL_STOCK_RESERVATION_CMD.execute_command(g_request,g_actor,p_result);  
  else raise_application_error(-20888,''COMMAND_HANDLER_NOT_INSTALLED''); end if;  
  v_resolved:=json_object_t.parse(g_resolution);  
  RRL_STOCK_COMPOSITION_CORE.finish_changes(v_resolved.get_array(''physical_before'').to_clob);  
  RRL_STOCK_INVARIANT_CORE.verify_posting(v_resolved.get_array(''resources'').to_clob,v_resolved.get_array(''stock_before'').to_clob,g_operation);  
  v_key:=''STOCK:''||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(g_operation,''AL32UTF8''),sys.dbms_crypto.hash_sh256));  
  RRL_STOCK_LOCK_API.assert_held(70,RRL_STOCK_LOCK_API.resource_key(''UNIQUE'',''STOCK.OUTBOX:''||substr(v_key,7)));  
  select count(*) into v_existing from RRL_EVENT_OUTBOX where IDEMPOTENCY_KEY=v_key;  
  if v_existing!=0 then raise_application_error(-20889,''OUTBOX_IDENTITY_CONFLICT''); end if;  
  v_resources:=v_resolved.get_array(''resources'').to_clob;  
  v_after:=RRL_STOCK_CHANGE_AUDIT.snapshot(v_resources);v_changes:=RRL_STOCK_CHANGE_AUDIT.differences(g_change_before,v_after);  
  v_event:=json_object_t();v_event.put(''contract_version'',3);v_event.put(''operation_id'',g_operation);v_event.put(''command_type'',g_kind);  
  v_event.put(''source'',json_object_t.parse(g_request).get_object(''source''));v_event.put(''result'',json_objec');
 dbms_lob.append(e,'t_t.parse(p_result));  
  v_event.put(''stock_before'',v_resolved.get_array(''stock_before''));  
  v_event.put(''stock_after'',json_array_t.parse(RRL_STOCK_INVARIANT_CORE.snapshot_stock(v_resources)));  
  v_composition:=json_object_t.parse(v_changes);v_unit_changes:=v_composition.get_array(''units'');  
  for i in 0..v_unit_changes.get_size-1 loop  
   v_unit_change:=treat(v_unit_changes.get(i) as json_object_t);  
   if not v_unit_change.get(''before'').is_null and not v_unit_change.get(''after'').is_null then  
    v_old_unit:=v_unit_change.get_object(''before'');v_new_unit:=v_unit_change.get_object(''after'');  
    if v_old_unit.get_string(''uid'')!=v_new_unit.get_string(''uid'') then v_repacking:=true;end if;  
   end if;  
  end loop;  
  v_event.put(''composition_changes'',v_composition);  
  if v_repacking then  
   v_event.put(''regulatory_composition_status'',''PENDING'');  
   v_event.put(''regulatory_action'',''PHYSICAL_REPACK_PROPOSED'');  
  end if;  
  v_event.put(''immutable_request_reference'',g_operation);  
  v_outbox:=RRL_TRACEABILITY_API.enqueue_event(''STOCK_POSTED'',''STOCK_OPERATION'',g_operation,v_key,v_event.to_clob,''WMS'',g_operation);  
  v_json:=json_object_t.parse(p_result);v_json.put(''outbox_id'',v_outbox);  
  if v_repacking then v_json.put(''regulatory_composition_status'',''PENDING'');end if;  
  p_result:=v_json.to_clob;  
  RRL_STOCK_OPERATION_CORE.finish_operation(g_operation,p_result);  
  g_prepared:=false;  
 end;  
end;
');
 e:=replace(e,chr(13),'');if dbms_lob.compare(a,e)!=0 then raise_application_error(-20886,'WTASK_BASELINE_CHANGED_RRL_STOCK_POSTING_API');end if;
 dbms_lob.freetemporary(a);dbms_lob.freetemporary(e);
 dbms_lob.createtemporary(a,true);dbms_lob.createtemporary(e,true);
 for s in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_HU_TASK'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 dbms_lob.append(e,'package body RRL_STOCK_HU_TASK as

 function proxy_request(p_request clob,t RRL_WAREHOUSE_TASK%rowtype) return clob is

  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object(''metadata'');src json_object_t:=json_object_t();

 begin

  if d.get_string(''command_type'')=''HU_PLAN_MOVE'' then

   d.put(''command_type'',''HU_MOVE'');return d.to_clob;

  end if;

  declare v_group_receipt varchar2(100);begin

   select max(RECEIPT_OPERATION_ID)into v_group_receipt from RRL_IW_GROUP_PUT_PLAN where TASK_ID=t.TASK_ID;

   if v_group_receipt is not null then m.put(''group_receipt_operation_id'',v_group_receipt);

   else m.remove(''group_receipt_operation_id'');end if;

  end;

  src.put(''uid'',t.UID_PALLET);d.put(''source'',src);d.put(''command_type'',''HU_TASK_COMPLETE'');

  m.put(''expected_version'',t.HU_CONTENT_VERSION);m.put(''target_cell'',t.TO_CELL);m.put(''physical_task_id'',t.TASK_ID);

  m.put(''target_slot_id'',t.TO_CELL_SLOT_ID);

  if t.HU_MEASUREMENTS_JSON is not null then m.put(''measurements'',json_object_t.parse(t.HU_MEASUREMENTS_JSON));end if;

  m.put(''scan_container'',m.get_string(''scanned_pallet''));d.put(''metadata'',m);return d.to_clob;

 end;

 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is

  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object(''metadata'');v json_object_t;ctx json_object_t;

  t RRL_WAREHOUSE_TASK%rowtype;pr clob;f json_array_t;r json_array_t;v_id number;v_sync number;v_key varchar2(400);iw_count number;

 begin

  if d.get_string(''command_type'')=''HU_PLAN_MOVE'' then

   select RRL_WAREHOUSE_TASK_SQ.nextval into v_id from dual;

   m.put(''planned');
 dbms_lob.append(e,'_physical_task_id'',v_id);d.put(''metadata'',m);pr:=proxy_request(d.to_clob,t);

   RRL_STOCK_HU_CMD.compile_command(pr,p_operation,p_policies,p_resources,p_domain,p_defer_wait_planning=>true);

   v:=json_object_t.parse(p_domain);r:=json_array_t.parse(p_resources);

   RRL_STOCK_PLAN_HELPER.row_key(r,''RRL_WAREHOUSE_TASK'',RRL_STOCK_PLAN_HELPER.decimal_text(v_id));

   if m.get_string(''group_receipt_operation_id'')is not null then

    declare group_value json_object_t;begin

     RRL_IW_GROUP_PUT.describe_receipt(m.get_string(''group_receipt_operation_id''),v.get_string(''target''),d.get_string(''actor''),null,group_value);

     if group_value.get_string(''uid'')!=v.get_string(''uid'')then raise_application_error(-20886,''INTERWARE_GROUP_PLACEMENT_ROOT_REQUIRED'');end if;

     RRL_IW_GROUP_PUT.declare_rows(group_value,p_operation,r);v.put(''group_placement'',group_value);

    end;

   end if;

   RRL_ST_DEFER_HU_WAIT.declare_plan(p_request,v_id,r,v);
   v.put(''task_id'',v_id);v.put(''planning'',1);p_domain:=v.to_clob;p_resources:=r.to_clob;

  else

   v_id:=d.get_object(''source'').get_number(''task_id'');

   select * into t from RRL_WAREHOUSE_TASK where TASK_ID=v_id;

   if t.HU_CONTENT_VERSION is null or t.TASK_SOURCE!=''MANUAL'' or t.SOURCE_DOC_TYPE!=''WAREHOUSE_HU''

    or t.TASK_TYPE!=''PUTAWAY'' or t.UNIT_CODE!=''HU'' or t.QTY_MODE!=''PALLET'' or t.QTY!=1

    or t.STATUS not in(''PLANNED'',''ASSIGNED'',''IN_PROGRESS'') then raise_application_error(-20886,''HU_TASK_CONTRACT_OR_STATE_INVALID'');end if;

   if m.has(''fact_qty'') and not m.get(''fact_qty'').is_null and RRL_STOCK_MATH.quantity(m.get_string(''fact_qty''))!=1 then

    raise_application_error(-20886,''HU_TASK_ONE_WHOLE_PLACE_REQUIRED'');end if;

  ');
 dbms_lob.append(e,' if m.get_number(''scan_draft_id'') is not null then raise_application_error(-20886,''HU_TASK_SEALED_TOP_SCAN_REQUIRED'');end if;

   pr:=proxy_request(p_request,t);

   RRL_STOCK_HU_CMD.compile_command(pr,p_operation,p_policies,p_resources,p_domain);

   v:=json_object_t.parse(p_domain);r:=json_array_t.parse(p_resources);

   if v.get_object(''parent_snapshot'').get_string(''cell'')!=t.FROM_CELL

    or v.get_number(''warehouse'')!=t.FROM_WARE_ID or t.FROM_WARE_ID!=t.TO_WARE_ID then raise_application_error(-20886,''HU_TASK_SOURCE_LOCATION_CONFLICT'');end if;

   ctx:=json_object_t.parse(RRL_TASK_RESOURCE_POLICY.context_json(v_id,''COMPLETE'',d.get_string(''actor''),d.get_string(''actor''),

    m.get_number(''resource_id''),m.get_number(''resource_session_id''),m.get_number(''equipment_id'')));

   if ctx.get_number(''resource_session_id'') is not null then

    RRL_STOCK_PLAN_HELPER.row_key(r,''RRL_RESOURCE_SESSION'',RRL_STOCK_PLAN_HELPER.decimal_text(ctx.get_number(''resource_session_id'')));

    RRL_STOCK_PLAN_HELPER.row_key(r,''RUSERS'',d.get_string(''actor''));

   end if;

   if t.RESOURCE_SESSION_ID is not null then RRL_STOCK_PLAN_HELPER.row_key(r,''RRL_RESOURCE_SESSION'',RRL_STOCK_PLAN_HELPER.decimal_text(t.RESOURCE_SESSION_ID));end if;

   RRL_STOCK_PLAN_HELPER.row_key(r,''RRL_WAREHOUSE_TASK'',RRL_STOCK_PLAN_HELPER.decimal_text(v_id));

   v_key:=''WT:''||RRL_STOCK_PLAN_HELPER.decimal_text(v_id)||'':MANUAL:PUTAWAY:''||RRL_STOCK_PLAN_HELPER.decimal_text(v_id)||'':'';

   begin select SYNC_ID into v_sync from RRL_WAREHOUSE_TASK_SYNC where SYNC_KEY=v_key;

   exception when no_data_found then select RRL_WH_TASK_SYNC_SQ.nextval into v_sync from dual;end;

   RRL_STOCK_PLAN_HELPER.row_key(r,''RRL_WAREHOUSE_TAS');
 dbms_lob.append(e,'K_SYNC'',RRL_STOCK_PLAN_HELPER.decimal_text(v_sync));

   RRL_STOCK_PLAN_HELPER.anchor(r,70,''UNIQUE'',''TASK.SYNC:''||v_key);

   v.put(''task_signature'',RRL_STOCK_TASK_PLAN.signature(t));v.put(''hu_version'',t.HU_CONTENT_VERSION);

   select count(*)into iw_count from RRL_INTERWARE_PUT_PLAN where TASK_ID=v_id;

   if iw_count=1 then RRL_STOCK_INTERWARE_PUT.plan_task(t,d.get_string(''actor''),r,v);end if;

   declare group_receipt varchar2(100);group_value json_object_t;begin

    select max(RECEIPT_OPERATION_ID)into group_receipt from RRL_IW_GROUP_PUT_PLAN where TASK_ID=v_id;

    if group_receipt is not null then

     RRL_IW_GROUP_PUT.describe_receipt(group_receipt,t.TO_CELL,d.get_string(''actor''),v_id,group_value);

     RRL_IW_GROUP_PUT.declare_rows(group_value,p_operation,r);v.put(''group_placement'',group_value);

    end if;

   end;

   RRL_ST_DEFER_HU_WAIT.declare_plan(p_request,v_id,r,v);
   v.put(''resource_context'',ctx);v.put(''task_id'',v_id);v.put(''sync_id'',v_sync);v.put(''sync_key'',v_key);v.put(''planning'',0);

   p_domain:=v.to_clob;p_resources:=r.to_clob;

  end if;

 end;

 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is

  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object(''metadata'');v json_object_t;j json_object_t:=json_object_t();ctx json_object_t;x json_object_t;

  t RRL_WAREHOUSE_TASK%rowtype;plan clob;s clob;pr clob;a json_array_t;v_op varchar2(100):=d.get_string(''operation_id'');v_id number;

  v_uid varchar2(200);v_from varchar2(60);v_to varchar2(60);v_ware number;v_version number;v_resource number;v_session number;v_equipment number;v_sync number;v_key varchar2(400);

  v_leaf_uid varchar2(200);v_qty n');
 dbms_lob.append(e,'umber;v_base varchar2(20);v_sscc varchar2(32);v_slot number;v_measures clob;

 begin

  if RRL_HAS_WRIGHT(p_actor,''warehouse_task_execute'')!=1 then raise_application_error(-20882,''HU_TASK_EXECUTION_FORBIDDEN'');end if;

  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=v_op;

  v:=json_object_t.parse(plan).get_object(''domain'');v_id:=v.get_number(''task_id'');v_uid:=v.get_string(''uid'');

  v_from:=v.get_object(''parent_snapshot'').get_string(''cell'');v_to:=v.get_string(''target'');v_ware:=v.get_number(''warehouse'');

  if v.has(''defer_wait_hu'')then
   RRL_ST_DEFER_HU_WAIT.validate_plan(p_request,p_actor,v.get_object(''defer_wait_hu''),case when v.get_number(''planning'')=1 then null else v_id end);
  end if;
  if v.has(''group_placement'')then RRL_IW_GROUP_PUT.validate_receipt(v.get_object(''group_placement''),p_actor,case when v.get_number(''planning'')=1 then null else v_id end);end if;

  if v.get_number(''planning'')=1 then

   s:=RRL_STOCK_HU_READ.snapshot_json(v_uid);

   if rawtohex(sys.dbms_crypto.hash(s,sys.dbms_crypto.hash_sh256))!=v.get_string(''parent_signature'') then raise_application_error(-20890,''CLOSURE_CHANGED: HU task planning'');end if;

   select SSCC into v_sscc from RRL_PALLETS where UID_PALLET=v_uid;

   if not v.has(''defer_wait_hu'')and(m.get_string(''scan_container'') is null or(m.get_string(''scan_container'')!=v_uid and(v_sscc is null or m.get_string(''scan_container'')!=v_sscc))) then raise_application_error(-20886,''HU_TASK_PLAN_TOP_SCAN_REQUIRED'');end if;

   v_version:=treat(v.get_object(''parent_snapshot'').get_array(''nodes'').get(0) as json_object_t).get_number(''version'');

   v_slot:=v.get_object(''placement'').get_number(''slot_id'');

   if v.');
 dbms_lob.append(e,'get_object(''placement'').has(''measurements'') then v_measures:=v.get_object(''placement'').get_object(''measurements'').to_clob;end if;

   insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,UID_PALLET,

    FROM_WARE_ID,FROM_CELL,TO_WARE_ID,TO_CELL,QTY,UNIT_CODE,QTY_MODE,STATUS,CREATED_BY,HU_CONTENT_VERSION,TO_CELL_SLOT_ID,HU_MEASUREMENTS_JSON)

    values(v_id,''PUTAWAY'',''MANUAL'',v_id,''WAREHOUSE_HU'',v_uid,v_ware,v_from,v_ware,v_to,1,''HU'',''PALLET'',''PLANNED'',p_actor,v_version,v_slot,v_measures);

   if v.has(''group_placement'')then RRL_IW_GROUP_PUT.record_plan(v_op,v_id,v.get_object(''group_placement''),p_actor);end if;

   j.put(''operation_id'',v_op);j.put(''task_id'',v_id);j.put(''pallet_identifier'',v_uid);j.put(''from_cell'',v_from);j.put(''cell'',v_to);

   j.put(''target_slot_id'',v_slot);j.put(''placement'',v.get_object(''placement''));j.put(''status'',''PLANNED'');j.put(''quantity'',''1'');j.put(''unit_code'',''HU'');j.put(''content_version'',v_version);p_result:=j.to_clob;
   if v.has(''defer_wait_hu'')then RRL_ST_DEFER_WAIT_API.record_hu_plan(p_request,v_id,v.get_object(''defer_wait_hu''),p_result);end if;

  else

   select * into t from RRL_WAREHOUSE_TASK where TASK_ID=v_id for update;

   if t.HU_CONTENT_VERSION!=v.get_number(''hu_version'') or RRL_STOCK_TASK_PLAN.signature(t)!=v.get_string(''task_signature'') then raise_application_error(-20890,''CLOSURE_CHANGED: HU physical task'');end if;

   if v.has(''interwarehouse_placement'')then RRL_STOCK_INTERWARE_PUT.validate_task(t,p_actor,v.get_object(''interwarehouse_placement''));end if;

   ctx:=json_object_t.parse(RRL_TASK_RESOURCE_POLICY.context_json(v_id,''COMPLETE'',p_actor,p_actor,

    m.get_number(''resource_id''),m.ge');
 dbms_lob.append(e,'t_number(''resource_session_id''),m.get_number(''equipment_id'')));

   if dbms_lob.compare(ctx.to_clob,v.get_object(''resource_context'').to_clob)!=0 then raise_application_error(-20890,''CLOSURE_CHANGED: HU task resource context'');end if;

   pr:=proxy_request(p_request,t);RRL_STOCK_HU_CMD.execute_command(pr,p_actor,s);

   v_resource:=ctx.get_number(''resource_id'');v_session:=ctx.get_number(''resource_session_id'');v_equipment:=ctx.get_number(''equipment_id'');

   update RRL_WAREHOUSE_TASK set STATUS=''DONE'',FACT_QTY=1,TARGET_UID_PALLET=v_uid,FINISHED_AT=systimestamp,

    ASSIGNED_TO=p_actor,RESOURCE_ID=v_resource,RESOURCE_SESSION_ID=v_session,EQUIPMENT_ID=v_equipment,

    COMPLETION_HASH=rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256)),COMPLETION_JSON=p_request,LAST_ERROR=null where TASK_ID=v_id;

   a:=v.get_object(''parent_snapshot'').get_array(''nodes'');

   for i in 0..a.get_size-1 loop x:=treat(a.get(i) as json_object_t);

    if x.get_string(''kind'')=''STOCK'' then

     v_leaf_uid:=x.get_string(''uid'');v_qty:=RRL_STOCK_MATH.quantity(x.get_string(''quantity''));v_base:=x.get_string(''base_uom'');

     insert into RRL_WAREHOUSE_TASK_STOCK_MOVE(STOCK_MOVE_ID,TASK_ID,TASK_SOURCE,TASK_TYPE,SOURCE_DOC_TYPE,SOURCE_TASK_ID,

      UID_PALLET,TARGET_UID_PALLET,FROM_CELL,TO_CELL,QTY,BASE_QTY,BASE_UOM,OPERATION_ID,CREATED_AT,CREATED_BY)

      values(RRL_WH_TASK_STOCK_MOVE_SQ.nextval,v_id,''MANUAL'',''PUTAWAY'',''WAREHOUSE_HU'',v_id,v_leaf_uid,v_leaf_uid,

       v_from,v_to,v_qty,v_qty,v_base,v_op,systimestamp,p_actor);

    end if;

   end loop;

   if v_resource is not null or v_session is not null or v_equipment is not null then

    insert into RRL_RESOURCE_FACT_EVENT(EVEN');
 dbms_lob.append(e,'T_ID,TASK_ID,SESSION_ID,RESOURCE_ID,EVENT_TYPE,EVENT_AT,EVENT_BY,PAYLOAD_JSON)

     values(RRL_RESOURCE_FACT_EVENT_SQ.nextval,v_id,v_session,v_resource,''COMPLETED'',systimestamp,p_actor,p_request);

   end if;

   update RRL_RESOURCE_SESSION set CURRENT_TASK_ID=null where SESSION_ID in(v_session,t.RESOURCE_SESSION_ID) and CURRENT_TASK_ID=v_id;

   if v_session is not null then update RRL_RESOURCE_SESSION set LAST_CELL=v_to,LAST_POSITION_AT=systimestamp,LAST_HEARTBEAT_AT=systimestamp

    where SESSION_ID=v_session and OPERATOR_USER_ID=p_actor;end if;

   v_sync:=v.get_number(''sync_id'');v_key:=v.get_string(''sync_key'');

   merge into RRL_WAREHOUSE_TASK_SYNC dst using(select v_key SYNC_KEY from dual)src on(dst.SYNC_KEY=src.SYNC_KEY)

    when matched then update set dst.SYNC_STATUS=''SYNCED'',dst.SYNCED_AT=systimestamp,dst.UPDATED_AT=systimestamp,dst.UPDATED_BY=p_actor,dst.LAST_ERROR=null

    when not matched then insert(SYNC_ID,TASK_ID,TASK_SOURCE,TASK_TYPE,SOURCE_DOC_TYPE,SOURCE_TASK_ID,SYNC_KEY,SYNC_STATUS,SYNC_ATTEMPT,CREATED_AT,UPDATED_AT,SYNCED_AT,UPDATED_BY)

     values(v_sync,v_id,''MANUAL'',''PUTAWAY'',''WAREHOUSE_HU'',v_id,v_key,''SYNCED'',1,systimestamp,systimestamp,systimestamp,p_actor);

   if v.has(''interwarehouse_placement'')then

    x:=v.get_object(''interwarehouse_placement'');

    RRL_STOCK_INTERWARE_PUT.complete_task(t,RRL_STOCK_MATH.quantity(x.get_string(''quantity'')),x.get_string(''uid''),p_actor);

   end if;

   if v.has(''group_placement'')then RRL_IW_GROUP_PUT.record_complete(v_op,v_id,v.get_object(''group_placement''),p_actor);end if;

   j:=json_object_t.parse(RRL_STOCK_HU_READ.snapshot_json(v_uid));j.put(''operation_id'',v_op);j.put(''task_id'',v_id);j.put(''status'',');
 dbms_lob.append(e,'''DONE'');

   j.put(''pallet_identifier'',v_uid);j.put(''source_pallet_identifier'',v_uid);j.put(''quantity'',''1'');j.put(''unit_code'',''HU'');j.put(''remaining_quantity'',''0'');j.put_null(''residual_task_id'');

   p_result:=j.to_clob;

  end if;

 end;

end;





');
 e:=replace(e,chr(13),'');if dbms_lob.compare(a,e)!=0 then raise_application_error(-20886,'WTASK_BASELINE_CHANGED_RRL_STOCK_HU_TASK');end if;
 dbms_lob.freetemporary(a);dbms_lob.freetemporary(e);
 dbms_lob.createtemporary(a,true);dbms_lob.createtemporary(e,true);
 for s in(select TEXT from USER_SOURCE where NAME='RRL_ST_DEFER_CASE_WAIT'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 dbms_lob.append(e,'package body RRL_ST_DEFER_CASE_WAIT as

 function task_signature(t RRL_WAREHOUSE_TASK%rowtype)return varchar2 is v json_object_t:=json_object_t();begin

  v.put(''status'',t.STATUS);v.put(''assigned'',t.ASSIGNED_TO);v.put(''resource'',t.RESOURCE_ID);v.put(''session'',t.RESOURCE_SESSION_ID);v.put(''equipment'',t.EQUIPMENT_ID);

  v.put(''started'',to_char(t.STARTED_AT_INSTANT,''YYYY-MM-DD HH24:MI:SS.FF6TZH:TZM''));

  return lower(rawtohex(sys.dbms_crypto.hash(v.to_clob,sys.dbms_crypto.hash_sh256)));

 end;

 function single_snapshot(p_st varchar2,p_ware number,p_ignore_plan varchar2,p_case_id number,p_nested_root varchar2 default null)return clob is

  ct RRL_CASE_PICK_TASK%rowtype;ff RRL_CUSTOMER_ORDER_FULFILLMENT%rowtype;

  n number;h number;own_qty number;items json_array_t:=json_array_t();x json_object_t;r json_object_t:=json_object_t();wait_cell varchar2(50);

 begin

  select count(*)into n from RRL_SBORKA_PALLETS where ST_NUMBER=p_st and ID=(select LEGACY_SBORKA_PALLET_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_case_id);

  if n!=1 then raise_application_error(-20886,''DEFER_CASE_SINGLE_ST_PLACE_REQUIRED'');end if;

  select c.*into ct from RRL_CASE_PICK_TASK c join RRL_SBORKA_PALLETS p on p.ID=c.LEGACY_SBORKA_PALLET_ID where p.ST_NUMBER=p_st and c.CASE_PICK_TASK_ID=p_case_id;

  if ct.WARE_ID is null or ct.WARE_ID!=p_ware or ct.CURRENT_CELL is null or ct.SSCC is null

   or ct.STATUS not in(''WAIT_CONTROL'',''CONTROLLED'',''READY_TO_SHIP'')then raise_application_error(-20886,''DEFER_CASE_COMPLETED_OWN_CARRIER_REQUIRED'');end if;

  select count(*)into n from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=ct.LEGACY_SBORKA_PALLET_ID;

  if n!=1 then raise_applicati');
 dbms_lob.append(e,'on_error(-20886,''DEFER_CASE_SINGLE_FULFILLMENT_REQUIRED'');end if;

  select *into ff from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=ct.LEGACY_SBORKA_PALLET_ID;

  if ff.STATUS!=''PICKED''or ff.PICKED_CASE_TASK_ID is null or ff.PICKED_CASE_TASK_ID!=ct.CASE_PICK_TASK_ID

   or ff.CUSTOMER_ORDER_ID!=ct.CUSTOMER_ORDER_ID or ff.PICKED_CONTENT_VERSION is null or ff.PICKED_CONTENT_VERSION!=ct.CONTENT_VERSION

   then raise_application_error(-20886,''DEFER_CASE_CURRENT_PHYSICAL_FULFILLMENT_REQUIRED'');end if;

  select count(*)into n from RRL_WMS_HU_LINK where CHILD_CASE_TASK_ID=ct.CASE_PICK_TASK_ID and ACTIVE_FLAG=1;

  if n!=0 then
   if p_nested_root is null then raise_application_error(-20886,''DEFER_CASE_NESTED_SOURCE_REQUIRES_HU_PLAN'');end if;
   declare v_parent_uid varchar2(200);next_uid varchar2(200);counted number;steps number:=0;begin
    select count(*),min(PARENT_UID)into counted,v_parent_uid from RRL_WMS_HU_LINK where CHILD_CASE_TASK_ID=ct.CASE_PICK_TASK_ID and ACTIVE_FLAG=1;
    if counted!=1 then raise_application_error(-20886,''DEFER_CASE_ONE_REGISTERED_PARENT_REQUIRED'');end if;
    loop
     steps:=steps+1;if steps>200 then raise_application_error(-20886,''DEFER_CASE_PARENT_CHAIN_BOUND_200'');end if;
     select count(*),min(PARENT_UID)into counted,next_uid from RRL_WMS_HU_LINK where CHILD_PALLET_UID=v_parent_uid and ACTIVE_FLAG=1;
     exit when counted=0;
     if counted!=1 then raise_application_error(-20886,''DEFER_CASE_ONE_REGISTERED_PARENT_REQUIRED'');end if;
     v_parent_uid:=next_uid;
    end loop;
    if v_parent_uid!=p_nested_root then raise_application_error(-20886,''DEFER_CASE_EXACT_TOP_ROOT_REQUIRED'');end if;
   end;
  elsif p_nested_root i');
 dbms_lob.append(e,'s not null then raise_application_error(-20886,''DEFER_CASE_NESTED_MEMBER_REQUIRED'');end if;

  select count(*)into n from RRL_WAREHOUSE_TASK w where w.STATUS not in(''DONE'',''CANCELLED'')

   and(w.UID_PALLET=ct.SSCC or(w.SOURCE_DOC_TYPE=''ST_DEFER_CASE''and exists(select 1 from RRL_ST_DEFER_WAIT_PLAN cp where cp.TASK_ID=w.TASK_ID and cp.CASE_TASK_ID=ct.CASE_PICK_TASK_ID)))

   and(p_ignore_plan is null or not exists(select 1 from RRL_ST_DEFER_WAIT_PLAN p where p.TASK_ID=w.TASK_ID and p.PLAN_OPERATION_ID=p_ignore_plan));

  if n!=0 then raise_application_error(-20886,''DEFER_CASE_PHYSICAL_TASK_ALREADY_OPEN'');end if;

  for l in(select h.LOT_UID,s.CELL,s.REMAIN,s.HARD_RESERVED_BASE,s.STOCK_VERSION,s.BASE_UOM,p.ARTICUL,h.CASE_PICK_LINE_ID

   from RRL_CASE_CARRIER_LOT h join RRL_REMAINS s on s.UID_POLETA=h.LOT_UID join RRL_PALLETS p on p.UID_PALLET=h.LOT_UID

   where h.CASE_PICK_TASK_ID=ct.CASE_PICK_TASK_ID and(s.REMAIN>0 or s.HARD_RESERVED_BASE>0)order by h.LOT_UID,s.CELL fetch first 201 rows only)loop

   if items.get_size>=200 then raise_application_error(-20881,''DEFER_CASE_LOT_BOUND_200'');end if;

   if l.CELL!=ct.CURRENT_CELL or l.REMAIN<=0 or l.HARD_RESERVED_BASE!=l.REMAIN then raise_application_error(-20886,''DEFER_CASE_WHOLE_RESERVED_STOCK_REQUIRED'');end if;

   select nvl(sum(BASE_QTY),0)into own_qty from RRL_STOCK_RESERVATION where UID_PALLET=l.LOT_UID and CELL=l.CELL

    and CUSTOMER_ORDER_ID=ct.CUSTOMER_ORDER_ID and RESERVATION_KIND=''HARD''and STATUS in(''ACTIVE'',''ALLOCATED'',''PICKING'');

   if own_qty!=l.REMAIN then raise_application_error(-20886,''DEFER_CASE_EXACT_OWN_HARD_REQUIRED'');end if;

   x:=json_object_t();x.put(''uid'',l.LOT_UID);x.put(''cell'',l.CELL);x.put(''quan');
 dbms_lob.append(e,'tity'',RRL_STOCK_PLAN_HELPER.decimal_text(l.REMAIN));

   x.put(''version'',l.STOCK_VERSION);x.put(''base'',l.BASE_UOM);x.put(''article'',l.ARTICUL);x.put(''case_line'',l.CASE_PICK_LINE_ID);items.append(x);

  end loop;

  if items.get_size=0 then raise_application_error(-20886,''DEFER_CASE_HAS_NO_PHYSICAL_STOCK'');end if;

  select count(*)into n from RRL_CELLS where CELL=ct.CURRENT_CELL and WARE_ID=p_ware;

  if n!=1 then raise_application_error(-20886,''DEFER_CASE_SOURCE_WAREHOUSE_REQUIRED'');end if;

  select max(DEFER_WAIT_CELL)into wait_cell from RRL_RECEIPT_WARE_SETTINGS where WARE_ID=p_ware;

  r.put(''state'',''PREPARED_CASE'');r.put(''case_task_id'',ct.CASE_PICK_TASK_ID);r.put(''st_member_id'',ct.LEGACY_SBORKA_PALLET_ID);

  r.put(''fulfillment_id'',ff.FULFILLMENT_ID);r.put(''pallet_identifier'',ct.SSCC);r.put(''cell'',ct.CURRENT_CELL);

  r.put(''content_version'',ct.CONTENT_VERSION);r.put(''stocks'',items);r.put(''physical_move_required'',wait_cell is null or wait_cell!=ct.CURRENT_CELL);

  r.put(''stock_changed'',false);return r.to_clob;

 exception when no_data_found or too_many_rows then raise_application_error(-20886,''DEFER_CASE_SINGLE_REGISTERED_SOURCE_REQUIRED'');

 end;

 function snapshot(p_st varchar2,p_ware number,p_ignore_plan varchar2 default null,p_case_id number default null,p_nested_root varchar2 default null)return clob is

  n number;case_id number;case_count number;total_lots number:=0;need_move boolean:=false;

  cases json_array_t:=json_array_t();child json_object_t;result json_object_t:=json_object_t();uid varchar2(200);

  type identifiers is table of pls_integer index by varchar2(200);seen identifiers;

 begin

  if p_case_id is not null then return single_snapshot(p_st,p_');
 dbms_lob.append(e,'ware,p_ignore_plan,p_case_id,p_nested_root);end if;

  if p_nested_root is not null then raise_application_error(-20886,''DEFER_CASE_EXPLICIT_NESTED_MEMBER_REQUIRED'');end if;
  select count(*)into n from RRL_SBORKA_PALLETS where ST_NUMBER=p_st;

  if n<1 or n>200 then raise_application_error(-20881,''DEFER_CASE_ST_MEMBER_BOUND_200'');end if;

  for member in(select ID from RRL_SBORKA_PALLETS where ST_NUMBER=p_st order by ID)loop

   select count(*),min(CASE_PICK_TASK_ID)into case_count,case_id from RRL_CASE_PICK_TASK where LEGACY_SBORKA_PALLET_ID=member.ID;

   if case_count!=1 then raise_application_error(-20886,''DEFER_CASE_ALL_ST_MEMBERS_SINGLE_CASE_REQUIRED'');end if;

   child:=json_object_t.parse(single_snapshot(p_st,p_ware,p_ignore_plan,case_id));

   total_lots:=total_lots+child.get_array(''stocks'').get_size;

   if total_lots>200 then raise_application_error(-20881,''DEFER_CASE_ST_TOTAL_LOT_BOUND_200'');end if;

   uid:=child.get_string(''pallet_identifier'');if seen.exists(uid)then raise_application_error(-20886,''DEFER_CASE_DISTINCT_CARRIER_IDENTIFIERS_REQUIRED'');end if;seen(uid):=1;

   if child.get_boolean(''physical_move_required'')then need_move:=true;end if;cases.append(child);

  end loop;

  if cases.get_size=1 then return treat(cases.get(0)as json_object_t).to_clob;end if;

  result.put(''state'',''PREPARED_CASES'');result.put(''cases'',cases);result.put(''case_count'',cases.get_size);result.put(''lot_count'',total_lots);

  result.put(''physical_move_required'',need_move);result.put(''stock_changed'',false);return result.to_clob;

 end;

 procedure assert_command(p_request clob,p_actor varchar2)is

  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object(''');
 dbms_lob.append(e,'metadata'');tid number;

  t RRL_WAREHOUSE_TASK%rowtype;p RRL_ST_DEFER_WAIT_PLAN%rowtype;

 begin

  tid:=m.get_number(''physical_task_id'');if tid is null then return;end if;

  select *into t from RRL_WAREHOUSE_TASK where TASK_ID=tid;

  select *into p from RRL_ST_DEFER_WAIT_PLAN where TASK_ID=tid;

  RRL_WAREHOUSE_TASK_ACCESS.assert_scope(tid,p_actor);

  if RRL_HAS_WRIGHT(p_actor,''warehouse_task_execute'')!=1 then raise_application_error(-20882,''DEFER_CASE_CURRENT_EXECUTOR_REQUIRED'');end if;

  if p.CASE_TASK_ID is null or p.CASE_TASK_ID!=d.get_object(''source'').get_number(''case_task_id'')

   or t.SOURCE_DOC_TYPE!=''ST_DEFER_CASE''or t.TASK_TYPE!=''PUTAWAY''or t.TASK_SOURCE!=''MANUAL''

   or(t.SOURCE_TASK_ID is null or(t.SOURCE_TASK_ID!=p.CASE_TASK_ID and t.SOURCE_TASK_ID!=t.TASK_ID))or t.UID_PALLET!=p.UID_PALLET or t.FROM_CELL!=p.FROM_CELL or t.TO_CELL!=p.TARGET_CELL

   or t.QTY!=1 or t.UNIT_CODE!=''CASE''or t.QTY_MODE!=''PALLET''

   then raise_application_error(-20886,''DEFER_CASE_REGISTERED_WAITING_TASK_REQUIRED'');end if;

  if t.ASSIGNED_TO is not null and t.ASSIGNED_TO!=p_actor then raise_application_error(-20882,''DEFER_CASE_ASSIGNED_EXECUTOR_REQUIRED'');end if;

 end;

 procedure describe(p_request clob,p_actor varchar2,p_current out json_object_t)is

  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object(''metadata'');tid number:=m.get_number(''physical_task_id'');

  p RRL_ST_DEFER_WAIT_PLAN%rowtype;t RRL_WAREHOUSE_TASK%rowtype;dec RRL_ST_DEFER_DECISION%rowtype;

  src clob;n number;target varchar2(50);stored json_object_t;stored_wire clob;frozen_members json_array_t;current_members json_array_t;

 begin

  assert_command(p_request,p_actor);

  if m.get');
 dbms_lob.append(e,'_string(''scanned_pallet'')is null or m.get_string(''scanned_pallet'')!=m.get_string(''scan_container'')

   or m.get_string(''scanned_from_cell'')is null or m.get_string(''fact_qty'')is null or RRL_STOCK_MATH.quantity(m.get_string(''fact_qty''))!=1

   or m.get_number(''resource_id'')is not null or m.get_number(''resource_session_id'')is not null or m.get_number(''equipment_id'')is not null

   or m.get_string(''scan_draft_id'')is not null or m.get_string(''scanned_to_slot_code'')is not null

   then raise_application_error(-20886,''DEFER_CASE_WHOLE_PLACE_SCANS_REQUIRED'');end if;

  if m.has(''unit_keys'')then declare keys json_array_t:=m.get_array(''unit_keys'');begin

   if keys is not null and keys.get_size>0 then raise_application_error(-20886,''DEFER_CASE_WHOLE_CARRIER_NO_PARTIAL_UNIT_SELECTION'');end if;

  end;end if;

  select *into p from RRL_ST_DEFER_WAIT_PLAN where TASK_ID=tid;

  select *into t from RRL_WAREHOUSE_TASK where TASK_ID=tid;

  if m.get_string(''scanned_from_cell'')!=p.FROM_CELL then raise_application_error(-20886,''DEFER_CASE_ORIGINAL_SOURCE_SCAN_REQUIRED'');end if;

  select d.*into dec from RRL_ST_DEFER_WAIT_RUN r join RRL_ST_DEFER_DECISION d on d.OPERATION_ID=r.DECISION_OPERATION_ID where r.OPERATION_ID=p.PLAN_OPERATION_ID;

  if t.STATUS not in(''PLANNED'',''ASSIGNED'',''IN_PROGRESS'')then raise_application_error(-20886,''DEFER_CASE_WAITING_TASK_OPEN_REQUIRED'');end if;

  if t.FROM_WARE_ID!=dec.WARE_ID or t.TO_WARE_ID!=dec.WARE_ID or t.SOURCE_DOC_ID!=dec.VERSION_NO

   or t.FROM_CELL_SLOT_ID is not null or t.TO_CELL_SLOT_ID is not null or t.RESOURCE_ID is not null or t.RESOURCE_SESSION_ID is not null or t.EQUIPMENT_ID is not null

   then raise_application_error(-20886,''DEFER_CASE_');
 dbms_lob.append(e,'ORDINARY_WAITING_TASK_REQUIRED'');end if;

  select count(*)into n from RRL_ST_DEFER_DECISION where ST_NUMBER=dec.ST_NUMBER and VERSION_NO>dec.VERSION_NO;

  if n!=0 then raise_application_error(-20886,''DEFER_WAIT_DECISION_SUPERSEDED'');end if;

  select count(*)into n from RRL_SBORKA_PALLETS s where s.ST_NUMBER=dec.ST_NUMBER and(nvl(s.TRANSTASK_ID,-1)!=dec.TARGET_TT_ID or nvl(s.CONDITION,0)=2

   or exists(select 1 from RRL_TT_HU_LOAD_ST ls join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=ls.LOAD_OPERATION_ID

    where ls.SBORKA_PALLET_ID=s.ID and ls.ACTIVE_FLAG=1 and l.STATUS in(''LOADED'',''DEPARTED'')));

  if n!=0 then raise_application_error(-20886,''DEFER_CASE_ST_ASSIGNMENT_OR_LOAD_CHANGED'');end if;

  select count(*)into n from RRL_TRANSPORT_TASK where ID=dec.TARGET_TT_ID and CONDITION=''Спланирован''and nvl(DELETED,0)=0 and nvl(PAY_ORDER_ID,0)=0;

  if n!=1 then raise_application_error(-20886,''DEFER_WAIT_PLANNED_TARGET_TRIP_REQUIRED'');end if;

  select DEFER_WAIT_CELL into target from RRL_RECEIPT_WARE_SETTINGS where WARE_ID=dec.WARE_ID;

  if target is null or target!=p.TARGET_CELL or target!=m.get_string(''target_cell'')then raise_application_error(-20886,''DEFER_WAIT_TARGET_CONFIGURATION_CHANGED'');end if;

  RRL_ST_DEFER_WAIT_CORE.check_target(target,dec.WARE_ID);

  select count(*)into n from RRL_CELLS where CELL=target and(nvl(LIMIT_HEIGHT,0)>0 or nvl(LIMIT_WEIGHT,0)>0);

  if n!=0 then raise_application_error(-20886,''DEFER_WAIT_MEASURED_CAPACITY_PLAN_REQUIRED'');end if;

  select count(*)into n from RRL_TOPOLOGY_CELL tc join RRL_WAREHOUSE_TOPOLOGY tp on tp.TOPOLOGY_ID=tc.TOPOLOGY_ID join RRL_TOPOLOGY_CELL_SLOT sl on sl.TOPOLOGY_CELL_ID=tc.TOPOLOGY_CELL_ID

   where tc.');
 dbms_lob.append(e,'LEGACY_CELL_CODE=target and tc.WARE_ID=dec.WARE_ID and tc.ACTIVE=1 and sl.ACTIVE=1 and tp.STATUS=''PUBLISHED'';

  if n!=0 then raise_application_error(-20886,''DEFER_WAIT_PHYSICAL_SLOT_PLAN_REQUIRED'');end if;

  src:=snapshot(dec.ST_NUMBER,dec.WARE_ID,p.PLAN_OPERATION_ID,p.CASE_TASK_ID);

  stored:=json_object_t.parse(p.SOURCE_MEMBERS_JSON);
  if stored.has(''cohort_manifest'')then
   frozen_members:=stored.get_array(''cohort_manifest'');stored.remove(''cohort_manifest'');
   current_members:=RRL_ST_DEFER_PLACE_READ.manifest(dec.ST_NUMBER);
   if dbms_lob.compare(frozen_members.to_clob,current_members.to_clob)!=0 then raise_application_error(-20890,''CLOSURE_CHANGED: deferred ST membership/cargo'');end if;
  end if;
  stored_wire:=stored.to_clob;
  if dbms_lob.compare(src,stored_wire)!=0 then raise_application_error(-20890,''CLOSURE_CHANGED: deferred CASE source'');end if;

  p_current:=json_object_t.parse(src);if frozen_members is not null then p_current.put(''cohort_manifest'',current_members);end if;p_current.put(''decision'',dec.OPERATION_ID);p_current.put(''plan'',p.PLAN_OPERATION_ID);

  p_current.put(''target_trip'',dec.TARGET_TT_ID);p_current.put(''warehouse'',dec.WARE_ID);p_current.put(''task_signature'',task_signature(t));

 end;

 procedure validate_move(p_request clob,p_actor varchar2,p_frozen json_object_t)is current_src json_object_t;copy_src json_object_t;begin

  describe(p_request,p_actor,current_src);

  if p_frozen is null then raise_application_error(-20886,''DEFER_CASE_ROOT_PLAN_REQUIRED'');end if;

  copy_src:=json_object_t.parse(p_frozen.to_clob);copy_src.remove(''sync_id'');copy_src.remove(''sync_key'');

  if dbms_lob.compare(current_src.to_clob,copy_src.to_clob)!=0 then raise');
 dbms_lob.append(e,'_application_error(-20890,''CLOSURE_CHANGED: deferred CASE waiting source'');end if;

 end;

 procedure plan_move(p_request clob,p_actor varchar2,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t)is

  d json_object_t:=json_object_t.parse(p_request);tid number:=d.get_object(''metadata'').get_number(''physical_task_id'');v json_object_t;v_sync_id number;v_sync_key varchar2(400);

 begin

  if tid is null then return;end if;describe(p_request,p_actor,v);

  RRL_STOCK_PLAN_HELPER.row_key(p_resources,''RRL_ST_DEFER_WAIT_PLAN'',RRL_STOCK_PLAN_HELPER.decimal_text(tid));

  RRL_STOCK_PLAN_HELPER.row_key(p_resources,''RRL_WAREHOUSE_TASK'',RRL_STOCK_PLAN_HELPER.decimal_text(tid));

  RRL_STOCK_PLAN_HELPER.row_key(p_resources,''RRL_ST_DEFER_WAIT_RUN'',v.get_string(''plan''));

  RRL_STOCK_PLAN_HELPER.row_key(p_resources,''RRL_ST_DEFER_DECISION'',v.get_string(''decision''));

  RRL_STOCK_PLAN_HELPER.row_key(p_resources,''RRL_RECEIPT_WARE_SETTINGS'',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number(''warehouse'')));

  RRL_STOCK_PLAN_HELPER.row_key(p_resources,''RRL_TRANSPORT_TASK'',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number(''target_trip'')));

  RRL_STOCK_PLAN_HELPER.row_key(p_resources,''RRL_SBORKA_PALLETS'',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number(''st_member_id'')));

  RRL_STOCK_PLAN_HELPER.row_key(p_resources,''RRL_CUSTOMER_ORDER_FULFILLMENT'',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number(''fulfillment_id'')));

  v_sync_key:=''DEFER.CASE.WT:''||RRL_STOCK_PLAN_HELPER.decimal_text(tid);

  begin select SYNC_ID into v_sync_id from RRL_WAREHOUSE_TASK_SYNC where SYNC_KEY=v_sync_key;

  exception when no_data_found then select RRL_WH_TASK_SYNC_SQ.nextval into v_sync_id from dual;');
 dbms_lob.append(e,'end;

  RRL_STOCK_PLAN_HELPER.row_key(p_resources,''RRL_WAREHOUSE_TASK_SYNC'',RRL_STOCK_PLAN_HELPER.decimal_text(v_sync_id));

  RRL_STOCK_PLAN_HELPER.anchor(p_resources,70,''UNIQUE'',''TASK.SYNC:''||v_sync_key);

  v.put(''sync_id'',v_sync_id);v.put(''sync_key'',v_sync_key);p_domain.put(''deferred_case_waiting'',v);

 end;

 procedure finish_move(p_request clob,p_actor varchar2,p_result in out clob)is

  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object(''metadata'');tid number:=m.get_number(''physical_task_id'');

  frozen json_object_t;current_src json_object_t;wire clob;t RRL_WAREHOUSE_TASK%rowtype;j json_object_t:=json_object_t.parse(p_result);

  v_sync_id number;v_sync_key varchar2(400);op varchar2(100):=d.get_string(''operation_id'');new_version number;ff_id number;case_id number;lots json_array_t;lot json_object_t;lot_uid varchar2(200);lot_qty number;lot_base varchar2(20);

 begin

  if tid is null then return;end if;

  if sys_context(''RRL_STOCK_WRITE_CTX'',''OPERATION_ID'')!=op or sys_context(''RRL_STOCK_WRITE_CTX'',''OPERATION_ID'')is null

   or sys_context(''RRL_STOCK_WRITE_CTX'',''TX_ID'')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20886,''DEFER_CASE_ROOT_POSTING_REQUIRED'');end if;

  select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=op;

  frozen:=json_object_t.parse(wire).get_object(''domain'').get_object(''deferred_case_waiting'');

  if frozen is null then raise_application_error(-20886,''DEFER_CASE_ROOT_PLAN_REQUIRED'');end if;

  select *into t from RRL_WAREHOUSE_TASK where TASK_ID=tid;

  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key(''ROW'',''RRL_WAREHOUSE_TASK'',RRL_STOCK_PLAN_HE');
 dbms_lob.append(e,'LPER.decimal_text(tid)));

  if task_signature(t)!=frozen.get_string(''task_signature'')then raise_application_error(-20890,''CLOSURE_CHANGED: deferred CASE task'');end if;

  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key(''ROW'',''RRL_CUSTOMER_ORDER_FULFILLMENT'',RRL_STOCK_PLAN_HELPER.decimal_text(frozen.get_number(''fulfillment_id''))));

  new_version:=j.get_number(''content_version'');ff_id:=frozen.get_number(''fulfillment_id'');case_id:=j.get_number(''case_pick_task_id'');

  select count(*)into v_sync_id from RRL_CUSTOMER_ORDER_FULFILLMENT

   where FULFILLMENT_ID=ff_id and STATUS=''PICKED''and PICKED_CASE_TASK_ID=case_id and PICKED_CONTENT_VERSION=new_version;

  if v_sync_id!=1 then raise_application_error(-20886,''DEFER_CASE_FULFILLMENT_BINDING_CHANGED'');end if;

  update RRL_WAREHOUSE_TASK set STATUS=''DONE'',FACT_QTY=1,TARGET_UID_PALLET=UID_PALLET,FINISHED_AT=systimestamp,ASSIGNED_TO=p_actor,

   COMPLETION_HASH=lower(rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256))),COMPLETION_JSON=p_request,LAST_ERROR=null where TASK_ID=tid;

  lots:=j.get_array(''lots'');

  for i in 0..lots.get_size-1 loop

   lot:=treat(lots.get(i)as json_object_t);lot_uid:=lot.get_string(''uid'');lot_qty:=RRL_STOCK_MATH.quantity(lot.get_string(''quantity''));lot_base:=lot.get_string(''base'');

   insert into RRL_WAREHOUSE_TASK_STOCK_MOVE(STOCK_MOVE_ID,TASK_ID,TASK_SOURCE,TASK_TYPE,SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_TASK_ID,

    UID_PALLET,TARGET_UID_PALLET,FROM_CELL,TO_CELL,QTY,BASE_QTY,BASE_UOM,OPERATION_ID,CREATED_AT,CREATED_BY)

    values(RRL_WH_TASK_STOCK_MOVE_SQ.nextval,tid,t.TASK_SOURCE,t.TASK_TYPE,t.SOURCE_DOC_TYPE,t.SOURCE_DOC_ID,t.SOURCE_TASK_ID,

     lot_uid,lot');
 dbms_lob.append(e,'_uid,t.FROM_CELL,t.TO_CELL,lot_qty,lot_qty,lot_base,op,systimestamp,p_actor);

  end loop;

  v_sync_id:=frozen.get_number(''sync_id'');v_sync_key:=frozen.get_string(''sync_key'');

  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key(''ROW'',''RRL_WAREHOUSE_TASK_SYNC'',RRL_STOCK_PLAN_HELPER.decimal_text(v_sync_id)));

  insert into RRL_WAREHOUSE_TASK_SYNC(SYNC_ID,TASK_ID,TASK_SOURCE,TASK_TYPE,SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_TASK_ID,SYNC_KEY,SYNC_STATUS,SYNC_ATTEMPT,CREATED_AT,UPDATED_AT,SYNCED_AT,UPDATED_BY)

   values(v_sync_id,tid,t.TASK_SOURCE,t.TASK_TYPE,t.SOURCE_DOC_TYPE,t.SOURCE_DOC_ID,t.SOURCE_TASK_ID,v_sync_key,''SYNCED'',1,systimestamp,systimestamp,systimestamp,p_actor);

  j.put(''task_id'',tid);j.put(''status'',''DONE'');j.put(''quantity'',''1'');j.put(''base_uom'',''CASE'');j.put(''pallet_identifier'',t.UID_PALLET);j.put(''remaining_quantity'',''0'');

  p_result:=j.to_clob;

 end;

end;



');
 e:=replace(e,chr(13),'');if dbms_lob.compare(a,e)!=0 then raise_application_error(-20886,'WTASK_BASELINE_CHANGED_RRL_ST_DEFER_CASE_WAIT');end if;
 dbms_lob.freetemporary(a);dbms_lob.freetemporary(e);
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_WTASK_ASSIGN_VERSION','RRL_WTASK_RESOURCE_COMMAND','RRL_WTASK_VERSION_API','RRL_WTASK_VERSION_GUARD','RRL_WTASK_ASSIGN_DERIVE','RRL_WTASK_ASSIGN_API','RRL_WTASK_COMMAND_GUARD','RRL_WTASK_IDENTITY_GUARD');if n!=0 then raise_application_error(-20886,'WTASK_NAMESPACE_EXISTS');end if;
 select count(*)into n from ALL_CONTEXT where NAMESPACE='RRL_WTASK_ASSIGN_CTX';if n!=0 then raise_application_error(-20886,'WTASK_CONTEXT_EXISTS');end if;
 select count(*)into n from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-warehouse-task-scoped-assignment'and STATUS!='ROLLED_BACK';if n!=0 then raise_application_error(-20886,'WTASK_LEDGER_NOT_EMPTY');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'WTASK_BASELINE_INVALID');end if;
end;
/
