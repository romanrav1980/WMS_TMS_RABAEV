create or replace package body RRL_ST_DEFER_WAIT_CORE as
 procedure check_target(p_cell varchar2,p_ware number)is n number;
 begin
  select count(*)into n from RRL_CELLS c where c.CELL=p_cell and c.WARE_ID=p_ware
   and nvl(c.OTBOR,0)=0 and nvl(c.IS_SYSTEM,0)=0 and c.EXPEDITION_GROUP is null
   and nvl(c.BLOCKED_FOR_ACCEPT,0)=0 and nvl(c.BLOCKED_FOR_REMAINS,0)=0 and nvl(c.BLOCKED_FOR_POPOLNENIE,0)=0
   and not exists(select 1 from RRL_TOPOLOGY_CELL tc where tc.WARE_ID=c.WARE_ID and tc.LEGACY_CELL_CODE=c.CELL
    and tc.ACTIVE=1 and tc.CELL_KIND in('TRANSPORT_STAGING','GATE','FILM_WRAP')
    and tc.TOPOLOGY_ID=(select max(TOPOLOGY_ID)from RRL_WAREHOUSE_TOPOLOGY where WARE_ID=c.WARE_ID and STATUS='PUBLISHED'));
  if n!=1 then raise_application_error(-20886,'DEFER_WAIT_CELL_SAME_WARE_OPEN_STORAGE_OUTSIDE_SHIPPING_REQUIRED');end if;
 end;
 function members(p_snapshot clob,p_uid varchar2)return clob is
  s json_object_t:=json_object_t.parse(p_snapshot);a json_array_t;out_a json_array_t:=json_array_t();v json_object_t;
 begin
  if s.get_string('state')!='PREPARED_WHOLE_STOCK' then raise_application_error(-20886,'DEFER_WAIT_PREPARED_SOURCE_REQUIRED');end if;
  a:=s.get_array('members');
  for i in 0..a.get_size-1 loop
   v:=treat(a.get(i)as json_object_t);
   if v.get_string('pallet_identifier')=p_uid then out_a.append(v);end if;
  end loop;
  if out_a.get_size=0 then raise_application_error(-20886,'DEFER_WAIT_PALLET_NOT_IN_SOURCE');end if;
  return out_a.to_clob;
 end;
 procedure describe_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_current out json_object_t)is
  plan RRL_ST_DEFER_WAIT_PLAN%rowtype;run RRL_ST_DEFER_WAIT_RUN%rowtype;decision RRL_ST_DEFER_DECISION%rowtype;
  n number;target varchar2(50);source clob;current_members clob;first_member json_object_t;arr json_array_t;
 begin
  select *into plan from RRL_ST_DEFER_WAIT_PLAN where TASK_ID=p_task.TASK_ID;
  select *into run from RRL_ST_DEFER_WAIT_RUN where OPERATION_ID=plan.PLAN_OPERATION_ID;
  select *into decision from RRL_ST_DEFER_DECISION where OPERATION_ID=run.DECISION_OPERATION_ID;
  select count(*)into n from RUSERS u where u.ID=p_actor and nvl(u.DELETED,0)=0
   and RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')=1
   and(u.WARE_ID=decision.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
  if n!=1 then raise_application_error(-20882,'DEFER_WAIT_CURRENT_WAREHOUSE_EXECUTOR_REQUIRED');end if;
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
  if target is null or target!=plan.TARGET_CELL then raise_application_error(-20886,'DEFER_WAIT_TARGET_CONFIGURATION_CHANGED');end if;
  check_target(target,decision.WARE_ID);
  select count(*)into n from RRL_CELLS where CELL=target and(nvl(LIMIT_HEIGHT,0)>0 or nvl(LIMIT_WEIGHT,0)>0);
  if n!=0 then raise_application_error(-20886,'DEFER_WAIT_MEASURED_CAPACITY_PLAN_REQUIRED');end if;
  select count(*)into n from RRL_TOPOLOGY_CELL tc join RRL_WAREHOUSE_TOPOLOGY tp on tp.TOPOLOGY_ID=tc.TOPOLOGY_ID
   join RRL_TOPOLOGY_CELL_SLOT sl on sl.TOPOLOGY_CELL_ID=tc.TOPOLOGY_CELL_ID
   where tc.LEGACY_CELL_CODE=target and tc.WARE_ID=decision.WARE_ID and tc.ACTIVE=1 and sl.ACTIVE=1 and tp.STATUS='PUBLISHED';
  if n!=0 then raise_application_error(-20886,'DEFER_WAIT_PHYSICAL_SLOT_PLAN_REQUIRED');end if;
  source:=RRL_ST_DEFER_PHYSICAL.snapshot(decision.ST_NUMBER,decision.WARE_ID,run.OPERATION_ID);
  current_members:=members(source,plan.UID_PALLET);
  if dbms_lob.compare(current_members,plan.SOURCE_MEMBERS_JSON)!=0 then raise_application_error(-20886,'DEFER_WAIT_PREPARED_SOURCE_CHANGED');end if;
  arr:=json_array_t.parse(current_members);first_member:=treat(arr.get(0)as json_object_t);
  if nvl(p_task.TASK_SOURCE,'~')!='MANUAL' or nvl(p_task.SOURCE_DOC_TYPE,'~')!='ST_DEFER' or nvl(p_task.TASK_TYPE,'~')!='PUTAWAY'
   or nvl(p_task.SOURCE_DOC_ID,-1)!=decision.VERSION_NO or nvl(p_task.SOURCE_TASK_ID,-1)!=p_task.TASK_ID
   or nvl(p_task.UID_PALLET,'~')!=plan.UID_PALLET or nvl(p_task.FROM_CELL,'~')!=plan.FROM_CELL or nvl(p_task.TO_CELL,'~')!=plan.TARGET_CELL
   or nvl(p_task.FROM_WARE_ID,-1)!=decision.WARE_ID or nvl(p_task.TO_WARE_ID,-1)!=decision.WARE_ID
   or nvl(p_task.QTY,-1)!=plan.BASE_QTY or nvl(p_task.UNIT_CODE,'~')!=plan.BASE_UOM or nvl(p_task.QTY_MODE,'~')!='PALLET'
   or p_task.FROM_CELL_SLOT_ID is not null or p_task.TO_CELL_SLOT_ID is not null
   then raise_application_error(-20886,'DEFER_WAIT_REGISTERED_TASK_REQUIRED');end if;
  if first_member.get_string('cell')!=plan.FROM_CELL or first_member.get_number('stock_version')!=plan.STOCK_VERSION
   or RRL_STOCK_MATH.quantity(first_member.get_string('pallet_quantity'))!=plan.BASE_QTY
   or first_member.get_string('base_uom')!=plan.BASE_UOM then raise_application_error(-20886,'DEFER_WAIT_ORIGINAL_WHOLE_PALLET_REQUIRED');end if;
  p_current:=json_object_t();p_current.put('decision',decision.OPERATION_ID);p_current.put('plan',run.OPERATION_ID);
  p_current.put('st_number',decision.ST_NUMBER);p_current.put('warehouse',decision.WARE_ID);
  p_current.put('target_trip',decision.TARGET_TT_ID);p_current.put('members',arr);p_current.put('target',target);
 exception when no_data_found then raise_application_error(-20886,'DEFER_WAIT_REGISTERED_SOURCE_REQUIRED');
 end;
 procedure plan_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t)is
  v json_object_t;v_st varchar2(100);
 begin
  describe_task(p_task,p_actor,v);
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_ST_DEFER_WAIT_PLAN',RRL_STOCK_PLAN_HELPER.decimal_text(p_task.TASK_ID));
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_ST_DEFER_WAIT_RUN',v.get_string('plan'));
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_ST_DEFER_DECISION',v.get_string('decision'));
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_RECEIPT_WARE_SETTINGS',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('warehouse')));
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_TRANSPORT_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('target_trip')));
  v_st:=v.get_string('st_number');
  for x in(select p.ID,f.FULFILLMENT_ID,f.PICKED_WAREHOUSE_TASK_ID from RRL_SBORKA_PALLETS p
   join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.LEGACY_SBORKA_PALLET_ID=p.ID where p.ST_NUMBER=v_st)loop
   RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(x.ID));
   RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(x.FULFILLMENT_ID));
   RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(x.PICKED_WAREHOUSE_TASK_ID));
  end loop;
  p_domain.put('deferred_waiting',v);
 end;
 procedure validate_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_frozen json_object_t)is v json_object_t;
 begin
  describe_task(p_task,p_actor,v);
  if p_frozen is null or dbms_lob.compare(v.to_clob,p_frozen.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: deferred waiting source');end if;
 end;
 procedure complete_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_quantity number,p_target_uid varchar2,p_actor varchar2)is
  n number;version_no number;plan RRL_ST_DEFER_WAIT_PLAN%rowtype;st varchar2(100);q number;h number;unit varchar2(20);
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is null then raise_application_error(-20886,'DEFER_WAIT_ROOT_POSTING_REQUIRED');end if;
  select *into plan from RRL_ST_DEFER_WAIT_PLAN where TASK_ID=p_task.TASK_ID;
  select d.ST_NUMBER into st from RRL_ST_DEFER_WAIT_RUN r join RRL_ST_DEFER_DECISION d on d.OPERATION_ID=r.DECISION_OPERATION_ID where r.OPERATION_ID=plan.PLAN_OPERATION_ID;
  if p_quantity!=plan.BASE_QTY or p_target_uid!=plan.UID_PALLET then raise_application_error(-20886,'DEFER_WAIT_WHOLE_PALLET_REQUIRED');end if;
  select count(*)into n from RRL_WAREHOUSE_TASK where TASK_ID=p_task.TASK_ID and STATUS='DONE'and FACT_QTY=plan.BASE_QTY;
  if n!=1 then raise_application_error(-20886,'DEFER_WAIT_DONE_TASK_REQUIRED');end if;
  select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION,BASE_UOM into q,h,version_no,unit from RRL_REMAINS where UID_POLETA=p_target_uid and CELL=plan.TARGET_CELL;
  if q!=plan.BASE_QTY or h!=q or unit!=plan.BASE_UOM then raise_application_error(-20886,'DEFER_WAIT_MOVED_RESERVE_PROOF_REQUIRED');end if;
  for x in(select f.FULFILLMENT_ID from RRL_CUSTOMER_ORDER_FULFILLMENT f join RRL_SBORKA_PALLETS p on p.ID=f.LEGACY_SBORKA_PALLET_ID
   where p.ST_NUMBER=st and f.PICKED_PALLET_UID=p_target_uid and f.STATUS='PICKED')loop
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(x.FULFILLMENT_ID)));
  end loop;
  update RRL_CUSTOMER_ORDER_FULFILLMENT f set PICKED_STOCK_VERSION=version_no,UPDATED_AT=sysdate,UPDATED_BY=p_actor
   where f.PICKED_PALLET_UID=p_target_uid and f.STATUS='PICKED'and exists(select 1 from RRL_SBORKA_PALLETS p where p.ID=f.LEGACY_SBORKA_PALLET_ID and p.ST_NUMBER=st);
  if sql%rowcount=0 then raise_application_error(-20886,'DEFER_WAIT_FULFILLMENT_BINDING_REQUIRED');end if;
 end;
end;
/
