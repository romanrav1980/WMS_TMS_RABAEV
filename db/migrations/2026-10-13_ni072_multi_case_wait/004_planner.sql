create or replace package body RRL_ST_DEFER_WAIT_API as
 g_tx varchar2(100);
 function write_allowed return number is
 begin return case when g_tx is not null and g_tx=dbms_transaction.local_transaction_id(false)then 1 else 0 end;end;
 procedure plan_waiting(p_operation varchar2,p_decision varchar2,p_actor varchar2,p_result out clob)is
  decision RRL_ST_DEFER_DECISION%rowtype;existing RRL_ST_DEFER_WAIT_RUN%rowtype;request json_object_t:=json_object_t();
  request_body clob;source clob;arr json_array_t;selected json_array_t;first_member json_object_t;v json_object_t;
  targets json_array_t:=json_array_t();skips json_array_t:=json_array_t();result json_object_t:=json_object_t();
  target varchar2(50);uid varchar2(50 char);task_id number;n number;qty number;unit varchar2(20);from_cell varchar2(50);
  type seen_set is table of pls_integer index by varchar2(200);seen seen_set;
  meta_started boolean:=false;saved boolean:=false;
 begin
  if p_operation is null or lengthb(p_operation)>100 or not regexp_like(p_operation,'^[A-Za-z0-9_.:-]+$')
   or p_decision is null or lengthb(p_decision)>100 then raise_application_error(-20881,'DEFER_WAIT_OPERATION_DECISION_REQUIRED');end if;
  select *into decision from RRL_ST_DEFER_DECISION where OPERATION_ID=p_decision;
  select count(*)into n from RUSERS u where u.ID=p_actor and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(p_actor,'warehouse_task_edit')=1
   and(u.WARE_ID=decision.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
  if n!=1 then raise_application_error(-20882,'DEFER_WAIT_CURRENT_WAREHOUSE_PLANNER_REQUIRED');end if;
  request.put('decision_operation_id',p_decision);request.put('actor',p_actor);request_body:=request.to_clob;
  RRL_STOCK_METADATA_TX.begin_change(p_actor,'warehouse_task_edit');meta_started:=true;savepoint RRL_DWAIT772;saved:=true;
  select count(*)into n from RUSERS u where u.ID=p_actor and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(p_actor,'warehouse_task_edit')=1
   and(u.WARE_ID=decision.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
  if n!=1 then raise_application_error(-20882,'DEFER_WAIT_CURRENT_WAREHOUSE_PLANNER_REQUIRED');end if;
  begin
   select *into existing from RRL_ST_DEFER_WAIT_RUN where OPERATION_ID=p_operation;
   if existing.ACTOR!=p_actor or dbms_lob.compare(existing.REQUEST_JSON,request_body)!=0 then raise_application_error(-20886,'DEFER_WAIT_OPERATION_PAYLOAD_CONFLICT');end if;
   p_result:=existing.RESULT_JSON;RRL_STOCK_METADATA_TX.end_change;return;
  exception when no_data_found then null;end;
  select count(*)into n from RRL_ST_DEFER_DECISION where ST_NUMBER=decision.ST_NUMBER and VERSION_NO>decision.VERSION_NO;
  if n!=0 then raise_application_error(-20886,'DEFER_WAIT_DECISION_SUPERSEDED');end if;
  select count(*)into n from RRL_SBORKA_PALLETS p where p.ST_NUMBER=decision.ST_NUMBER and(
   nvl(p.TRANSTASK_ID,-1)!=decision.TARGET_TT_ID or nvl(p.CONDITION,0)=2
   or exists(select 1 from RRL_TT_HU_LOAD_ST ls join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=ls.LOAD_OPERATION_ID
    where ls.SBORKA_PALLET_ID=p.ID and ls.ACTIVE_FLAG=1 and l.STATUS in('LOADED','DEPARTED')));
  if n!=0 then raise_application_error(-20886,'DEFER_WAIT_ST_ASSIGNMENT_OR_LOAD_CHANGED');end if;
  select count(*)into n from RRL_TRANSPORT_TASK where ID=decision.TARGET_TT_ID and CONDITION='Спланирован'and nvl(DELETED,0)=0 and nvl(PAY_ORDER_ID,0)=0;
  if n!=1 then raise_application_error(-20886,'DEFER_WAIT_PLANNED_TARGET_TRIP_REQUIRED');end if;
  select DEFER_WAIT_CELL into target from RRL_RECEIPT_WARE_SETTINGS where WARE_ID=decision.WARE_ID;
  if target is null then raise_application_error(-20886,'DEFER_WAIT_TARGET_CONFIGURATION_REQUIRED');end if;
  RRL_ST_DEFER_WAIT_CORE.check_target(target,decision.WARE_ID);
  select count(*)into n from RRL_CELLS where CELL=target and(nvl(LIMIT_HEIGHT,0)>0 or nvl(LIMIT_WEIGHT,0)>0);
  if n!=0 then raise_application_error(-20886,'DEFER_WAIT_MEASURED_CAPACITY_PLAN_REQUIRED');end if;
  select count(*)into n from RRL_TOPOLOGY_CELL tc join RRL_WAREHOUSE_TOPOLOGY tp on tp.TOPOLOGY_ID=tc.TOPOLOGY_ID
   join RRL_TOPOLOGY_CELL_SLOT sl on sl.TOPOLOGY_CELL_ID=tc.TOPOLOGY_CELL_ID
   where tc.LEGACY_CELL_CODE=target and tc.WARE_ID=decision.WARE_ID and tc.ACTIVE=1 and sl.ACTIVE=1 and tp.STATUS='PUBLISHED';
  if n!=0 then raise_application_error(-20886,'DEFER_WAIT_PHYSICAL_SLOT_PLAN_REQUIRED');end if;
  source:=RRL_ST_DEFER_PHYSICAL.snapshot(decision.ST_NUMBER,decision.WARE_ID);
  declare prep json_object_t:=json_object_t.parse(source);src_case number;case_uid varchar2(200);case_version number;
   cases json_array_t:=json_array_t();child json_object_t;case_body clob;
   type origin_map is table of clob index by varchar2(100);origins origin_map;origin_key varchar2(100);
  begin
   if prep.get_string('state')in('PREPARED_CASE','PREPARED_CASES')then
    if prep.get_string('state')='PREPARED_CASE'then cases.append(prep);else cases:=prep.get_array('cases');end if;
    if cases is null or cases.get_size<1 or cases.get_size>200 then raise_application_error(-20881,'DEFER_WAIT_CASE_MEMBER_BOUND_200');end if;
    for i in 0..cases.get_size-1 loop
     child:=treat(cases.get(i)as json_object_t);src_case:=child.get_number('case_task_id');from_cell:=child.get_string('cell');case_uid:=child.get_string('pallet_identifier');
     origin_key:=RRL_STOCK_PLAN_HELPER.decimal_text(src_case);origins(origin_key):=child.to_clob;
     if from_cell=target then skips.append(case_uid);
     else
      select RRL_WAREHOUSE_TASK_SQ.nextval into task_id from dual;
      v:=json_object_t();v.put('task_id',task_id);v.put('pallet_identifier',case_uid);v.put('case_pick_task_id',src_case);targets.append(v);
     end if;
    end loop;
    result.put('operation_id',p_operation);result.put('decision_operation_id',p_decision);result.put('st_number',decision.ST_NUMBER);
    result.put('warehouse_id',decision.WARE_ID);result.put('waiting_cell',target);result.put('tasks',targets);result.put('already_waiting',skips);
    result.put('stock_changed',false);result.put('physical_move_completed',false);p_result:=result.to_clob;
    g_tx:=dbms_transaction.local_transaction_id(true);
    insert into RRL_ST_DEFER_WAIT_RUN(OPERATION_ID,DECISION_OPERATION_ID,ACTOR,REQUEST_JSON,RESULT_JSON)values(p_operation,p_decision,p_actor,request_body,p_result);
    for i in 0..targets.get_size-1 loop
     v:=treat(targets.get(i)as json_object_t);task_id:=v.get_number('task_id');src_case:=v.get_number('case_pick_task_id');
     child:=json_object_t.parse(origins(RRL_STOCK_PLAN_HELPER.decimal_text(src_case)));
     from_cell:=child.get_string('cell');case_uid:=child.get_string('pallet_identifier');case_version:=child.get_number('content_version');case_body:=child.to_clob;
     insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,
      FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,CREATED_BY)
      values(task_id,'PUTAWAY','MANUAL',task_id,'ST_DEFER_CASE',decision.VERSION_NO,case_uid,from_cell,target,decision.WARE_ID,decision.WARE_ID,1,'CASE','PALLET','PLANNED',p_actor);
     insert into RRL_ST_DEFER_WAIT_PLAN(TASK_ID,PLAN_OPERATION_ID,UID_PALLET,FROM_CELL,TARGET_CELL,BASE_QTY,BASE_UOM,STOCK_VERSION,SOURCE_MEMBERS_JSON,CASE_TASK_ID)
      values(task_id,p_operation,case_uid,from_cell,target,1,'CASE',case_version,case_body,src_case);
    end loop;
    g_tx:=null;RRL_STOCK_METADATA_TX.end_change;return;
   end if;
  end;
  arr:=json_object_t.parse(source).get_array('members');
  if arr is null or arr.get_size=0 or arr.get_size>200 then raise_application_error(-20886,'DEFER_WAIT_PREPARED_SOURCE_REQUIRED');end if;
  g_tx:=dbms_transaction.local_transaction_id(true);
  -- The run row is inserted before FK-bound plans; the result is built from all original members.
  for i in 0..arr.get_size-1 loop
   v:=treat(arr.get(i)as json_object_t);uid:=v.get_string('pallet_identifier');
   if not seen.exists(uid)then
    seen(uid):=1;selected:=json_array_t.parse(RRL_ST_DEFER_WAIT_CORE.members(source,uid));
    first_member:=treat(selected.get(0)as json_object_t);from_cell:=first_member.get_string('cell');
    if from_cell=target then skips.append(uid);
    else select RRL_WAREHOUSE_TASK_SQ.nextval into task_id from dual;
     v:=json_object_t();v.put('task_id',task_id);v.put('pallet_identifier',uid);targets.append(v);
    end if;
   end if;
  end loop;
  result.put('operation_id',p_operation);result.put('decision_operation_id',p_decision);result.put('st_number',decision.ST_NUMBER);
  result.put('warehouse_id',decision.WARE_ID);result.put('waiting_cell',target);result.put('tasks',targets);result.put('already_waiting',skips);
  result.put('stock_changed',false);result.put('physical_move_completed',false);p_result:=result.to_clob;
  insert into RRL_ST_DEFER_WAIT_RUN(OPERATION_ID,DECISION_OPERATION_ID,ACTOR,REQUEST_JSON,RESULT_JSON)values(p_operation,p_decision,p_actor,request_body,p_result);
  for i in 0..targets.get_size-1 loop
   v:=treat(targets.get(i)as json_object_t);uid:=v.get_string('pallet_identifier');task_id:=v.get_number('task_id');
   selected:=json_array_t.parse(RRL_ST_DEFER_WAIT_CORE.members(source,uid));first_member:=treat(selected.get(0)as json_object_t);
   qty:=RRL_STOCK_MATH.quantity(first_member.get_string('pallet_quantity'));unit:=first_member.get_string('base_uom');from_cell:=first_member.get_string('cell');
   insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,
    FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,CREATED_BY)
    values(task_id,'PUTAWAY','MANUAL',task_id,'ST_DEFER',decision.VERSION_NO,uid,from_cell,target,decision.WARE_ID,decision.WARE_ID,qty,unit,'PALLET','PLANNED',p_actor);
   declare members_body clob:=selected.to_clob;version_no number:=first_member.get_number('stock_version');
   begin insert into RRL_ST_DEFER_WAIT_PLAN(TASK_ID,PLAN_OPERATION_ID,UID_PALLET,FROM_CELL,TARGET_CELL,BASE_QTY,BASE_UOM,STOCK_VERSION,SOURCE_MEMBERS_JSON)
    values(task_id,p_operation,uid,from_cell,target,qty,unit,version_no,members_body);end;
  end loop;
  g_tx:=null;RRL_STOCK_METADATA_TX.end_change;
 exception when others then
  g_tx:=null;if saved then rollback to RRL_DWAIT772;end if;
  if meta_started then RRL_STOCK_METADATA_TX.end_change;end if;raise;
 end;
end;
/
