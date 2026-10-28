-- Projection onto the existing CASE lifecycle; no stock quantities or composition version are changed.
create or replace package RRL_STOCK_QC_CASE authid definer accessible by(package RRL_STOCK_PALLET_QC_CMD) as
 procedure project(p_domain clob,p_ready number,p_failed number,p_is_plan number,p_actor varchar2,p_operation varchar2,p_reason varchar2);
 function nested(p_domain clob) return number;
end;
/
create or replace package body RRL_STOCK_QC_CASE as
 function nested(p_domain clob) return number is
  d json_object_t:=json_object_t.parse(p_domain);v_case number:=d.get_number('case_task');a json_array_t:=d.get_array('legs');l json_object_t;n number;v_uid varchar2(150);
 begin
  if v_case is not null then select count(*) into n from RRL_WMS_HU_LINK where CHILD_CASE_TASK_ID=v_case and ACTIVE_FLAG=1;if n>0 then return 1;end if;end if;
  for i in 0..a.get_size-1 loop l:=treat(a.get(i) as json_object_t);v_uid:=l.get_string('uid');
   select count(*) into n from RRL_WMS_HU_LINK where CHILD_PALLET_UID=v_uid and ACTIVE_FLAG=1;if n>0 then return 1;end if;
  end loop;return 0;
 end;
 procedure project(p_domain clob,p_ready number,p_failed number,p_is_plan number,p_actor varchar2,p_operation varchar2,p_reason varchar2) is
  d json_object_t:=json_object_t.parse(p_domain);v_case number:=d.get_number('case_task');ct RRL_CASE_PICK_TASK%rowtype;
  v_payload clob;v_status varchar2(40);v_event varchar2(40);j json_object_t:=json_object_t();
 begin
  if v_case is null then return;end if;
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_case)));
  select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=v_case for update;
  if ct.LEGACY_SBORKA_PALLET_ID!=d.get_number('document_id') or ct.WARE_ID!=d.get_number('warehouse')
   or ct.CONTENT_VERSION!=d.get_number('case_version') or ct.STATUS not in('WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP') then
   raise_application_error(-20890,'CLOSURE_CHANGED: CASE control');end if;
  if p_ready=1 then
   if p_is_plan=1 then v_status:=case when ct.STATUS in('CONTROLLED','READY_TO_SHIP') then ct.STATUS else 'READY_TO_SHIP' end;v_event:='CONTROL_PLAN_READY';
   else v_status:='CONTROLLED';v_event:='CONTROL_PASSED';end if;
  elsif p_failed=1 then v_status:='WAIT_CONTROL';v_event:='CONTROL_FAILED';
  else v_status:='CONTROL_IN_PROGRESS';v_event:=case when p_is_plan=1 then 'CONTROL_PLAN_ASSIGNED' else 'CONTROL_PENDING' end;end if;
  update RRL_CASE_PICK_TASK set STATUS=v_status,UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_TASK_ID=v_case;
  j.put('operation_id',p_operation);j.put('previous_status',ct.STATUS);j.put('status',v_status);j.put('ready',p_ready=1);j.put('failure_reason',p_reason);
  v_payload:=j.to_clob;
  insert into RRL_CASE_PICK_EVENT(CASE_PICK_EVENT_ID,CASE_PICK_TASK_ID,EVENT_TYPE,PAYLOAD_JSON,CREATED_BY)
   values(RRL_CASE_PICK_EVENT_SQ.nextval,v_case,v_event,v_payload,p_actor);
 end;
end;
/