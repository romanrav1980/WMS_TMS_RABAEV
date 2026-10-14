create or replace package RRL_ST_DEFER_HU_WAIT authid definer
 accessible by(package RRL_ST_DEFER_PHYSICAL,package RRL_ST_DEFER_WAIT_API,package RRL_STOCK_HU_TASK)as
 function snapshot(p_st varchar2,p_ware number,p_ignore_plan varchar2 default null)return clob;
 procedure request_plan(p_operation varchar2,p_decision varchar2,p_actor varchar2,p_request out clob);
 procedure declare_plan(p_request clob,p_task number,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure validate_plan(p_request clob,p_actor varchar2,p_frozen json_object_t,p_task number default null);
end;
/
create or replace package body RRL_ST_DEFER_HU_WAIT as
 function snapshot(p_st varchar2,p_ware number,p_ignore_plan varchar2 default null)return clob is
  n number;root_uid varchar2(200);next_uid varchar2(200);counted number;steps number:=0;case_count number:=0;members number;
  ignore_task number;tree json_object_t;nodes json_array_t;node json_object_t;child json_object_t;cases json_array_t:=json_array_t();
  stocks json_array_t;lot json_object_t;wait_cell varchar2(50);outcome json_object_t:=json_object_t();total_lots number:=0;
  type lot_map is table of clob index by varchar2(200);expected lot_map;seen lot_map;lot_uid varchar2(200);
 begin
  select count(*),min(h.PARENT_UID)into n,root_uid from RRL_WMS_HU_LINK h
   join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=h.CHILD_CASE_TASK_ID
   join RRL_SBORKA_PALLETS st on st.ID=ct.LEGACY_SBORKA_PALLET_ID where st.ST_NUMBER=p_st and h.ACTIVE_FLAG=1;
  if n=0 then return null;end if;
  loop
   steps:=steps+1;if steps>200 then raise_application_error(-20886,'DEFER_HU_PARENT_CHAIN_BOUND_200');end if;
   select count(*),min(PARENT_UID)into counted,next_uid from RRL_WMS_HU_LINK where CHILD_PALLET_UID=root_uid and ACTIVE_FLAG=1;
   exit when counted=0;
   if counted!=1 then raise_application_error(-20886,'DEFER_HU_ONE_TOP_PARENT_REQUIRED');end if;root_uid:=next_uid;
  end loop;
  if p_ignore_plan is not null then
   select count(*),min(TASK_ID)into counted,ignore_task from RRL_ST_DEFER_WAIT_PLAN
    where PLAN_OPERATION_ID=p_ignore_plan and UID_PALLET=root_uid and BASE_UOM='HU';
   if counted>1 then raise_application_error(-20886,'DEFER_HU_ONE_WAIT_TASK_REQUIRED');end if;
  end if;
  tree:=json_object_t.parse(RRL_STOCK_HU_READ.snapshot_json(root_uid,ignore_task));nodes:=tree.get_array('nodes');
  if tree.get_number('warehouse')!=p_ware or nodes is null or nodes.get_size<2 or nodes.get_size>200
   or tree.get_array('ancestors').get_size!=0 or treat(nodes.get(0)as json_object_t).get_string('kind')!='CONTAINER'
   then raise_application_error(-20886,'DEFER_HU_REGISTERED_OWN_TOP_TREE_REQUIRED');end if;
  select count(*)into members from RRL_SBORKA_PALLETS where ST_NUMBER=p_st;
  if members<1 or members>200 then raise_application_error(-20881,'DEFER_HU_ST_MEMBER_BOUND_200');end if;
  for i in 0..nodes.get_size-1 loop
   node:=treat(nodes.get(i)as json_object_t);
   if nvl(node.get_number('open_task_count'),0)>0 then raise_application_error(-20886,'DEFER_HU_OTHER_PHYSICAL_TASK_OPEN');end if;
   if node.get_string('kind')='CASE'then
    child:=json_object_t.parse(RRL_ST_DEFER_CASE_WAIT.snapshot(p_st,p_ware,p_ignore_plan,node.get_number('case_task_id'),root_uid));
    case_count:=case_count+1;cases.append(child);stocks:=child.get_array('stocks');
    for j in 0..stocks.get_size-1 loop
     lot:=treat(stocks.get(j)as json_object_t);lot_uid:=lot.get_string('uid');
     if expected.exists(lot_uid)then raise_application_error(-20886,'DEFER_HU_DISTINCT_CASE_LOTS_REQUIRED');end if;
     expected(lot_uid):=lot.to_clob;total_lots:=total_lots+1;
     if total_lots>200 then raise_application_error(-20881,'DEFER_HU_TOTAL_LOT_BOUND_200');end if;
    end loop;
   elsif node.get_string('kind')not in('CONTAINER','STOCK')then raise_application_error(-20886,'DEFER_HU_CASE_TREE_ONLY');end if;
  end loop;
  if case_count!=members then raise_application_error(-20886,'DEFER_HU_EXACT_ALL_ST_MEMBERS_IN_TOP_REQUIRED');end if;
  for i in 0..nodes.get_size-1 loop
   node:=treat(nodes.get(i)as json_object_t);
   if node.get_string('kind')='STOCK'then
    lot_uid:=node.get_string('uid');
    if not expected.exists(lot_uid)or seen.exists(lot_uid)then raise_application_error(-20886,'DEFER_HU_EXACT_OWN_CASE_LEAVES_REQUIRED');end if;
    lot:=json_object_t.parse(expected(lot_uid));seen(lot_uid):=lot.to_clob;
    if node.get_string('cell')!=lot.get_string('cell')or node.get_string('quantity')!=lot.get_string('quantity')
     or node.get_string('hard_quantity')!=lot.get_string('quantity')or node.get_string('base_uom')!=lot.get_string('base')
     or node.get_number('stock_version')!=lot.get_number('version')then raise_application_error(-20886,'DEFER_HU_EXACT_RESERVED_LEAF_REQUIRED');end if;
   end if;
  end loop;
  if seen.count!=total_lots or total_lots<1 then raise_application_error(-20886,'DEFER_HU_COMPLETE_CASE_STOCK_REQUIRED');end if;
  select DEFER_WAIT_CELL into wait_cell from RRL_RECEIPT_WARE_SETTINGS where WARE_ID=p_ware;
  outcome.put('state','PREPARED_HU');outcome.put('root',root_uid);outcome.put('cell',tree.get_string('cell'));
  outcome.put('content_version',treat(nodes.get(0)as json_object_t).get_number('version'));
  outcome.put('tree',tree);outcome.put('cases',cases);outcome.put('case_count',case_count);outcome.put('lot_count',total_lots);
  outcome.put('physical_move_required',wait_cell is null or wait_cell!=tree.get_string('cell'));outcome.put('stock_changed',false);
  return outcome.to_clob;
 end;

 procedure describe(p_decision varchar2,p_actor varchar2,p_task number,p_value out json_object_t)is
  dec RRL_ST_DEFER_DECISION%rowtype;target varchar2(50);n number;source clob;plan RRL_ST_DEFER_WAIT_PLAN%rowtype;
  ignore_plan varchar2(100);own number;admin_flag number;
 begin
  select *into dec from RRL_ST_DEFER_DECISION where OPERATION_ID=p_decision;
  begin select WARE_ID,case when upper(trim(USER_GROUP))='GLOBAL_ADMIN'then 1 else 0 end into own,admin_flag
   from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'warehouse_task_execute')=1;
  exception when no_data_found then raise_application_error(-20882,'DEFER_HU_CURRENT_WARE_ACTOR_REQUIRED');end;
  if RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 or(admin_flag=0 and(own is null or own!=dec.WARE_ID))
   then raise_application_error(-20882,'DEFER_HU_CURRENT_WARE_ACTOR_REQUIRED');end if;
  select count(*)into n from RRL_ST_DEFER_DECISION where ST_NUMBER=dec.ST_NUMBER and VERSION_NO>dec.VERSION_NO;
  if n!=0 then raise_application_error(-20886,'DEFER_WAIT_DECISION_SUPERSEDED');end if;
  select count(*)into n from RRL_SBORKA_PALLETS st where st.ST_NUMBER=dec.ST_NUMBER and(nvl(st.TRANSTASK_ID,-1)!=dec.TARGET_TT_ID or nvl(st.CONDITION,0)=2
   or exists(select 1 from RRL_TT_HU_LOAD_ST ls join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=ls.LOAD_OPERATION_ID where ls.SBORKA_PALLET_ID=st.ID and ls.ACTIVE_FLAG=1 and l.STATUS in('LOADED','DEPARTED')));
  if n!=0 then raise_application_error(-20886,'DEFER_HU_ST_ASSIGNMENT_OR_LOAD_CHANGED');end if;
  select count(*)into n from RRL_TRANSPORT_TASK where ID=dec.TARGET_TT_ID and CONDITION='Спланирован'and nvl(DELETED,0)=0 and nvl(PAY_ORDER_ID,0)=0;
  if n!=1 then raise_application_error(-20886,'DEFER_WAIT_PLANNED_TARGET_TRIP_REQUIRED');end if;
  select DEFER_WAIT_CELL into target from RRL_RECEIPT_WARE_SETTINGS where WARE_ID=dec.WARE_ID;
  RRL_ST_DEFER_WAIT_CORE.check_target(target,dec.WARE_ID);
  select count(*)into n from RRL_CELLS where CELL=target and(nvl(LIMIT_HEIGHT,0)>0 or nvl(LIMIT_WEIGHT,0)>0);
  if n!=0 then raise_application_error(-20886,'DEFER_WAIT_MEASURED_CAPACITY_PLAN_REQUIRED');end if;
  select count(*)into n from RRL_TOPOLOGY_CELL tc join RRL_WAREHOUSE_TOPOLOGY tp on tp.TOPOLOGY_ID=tc.TOPOLOGY_ID
   join RRL_TOPOLOGY_CELL_SLOT sl on sl.TOPOLOGY_CELL_ID=tc.TOPOLOGY_CELL_ID
   where tc.LEGACY_CELL_CODE=target and tc.WARE_ID=dec.WARE_ID and tc.ACTIVE=1 and sl.ACTIVE=1 and tp.STATUS='PUBLISHED';
  if n!=0 then raise_application_error(-20886,'DEFER_WAIT_PHYSICAL_SLOT_PLAN_REQUIRED');end if;
  if p_task is not null then
   select *into plan from RRL_ST_DEFER_WAIT_PLAN where TASK_ID=p_task;
   if plan.BASE_UOM!='HU'or plan.CASE_TASK_ID is not null then raise_application_error(-20886,'DEFER_HU_WAIT_PLAN_REQUIRED');end if;
   ignore_plan:=plan.PLAN_OPERATION_ID;
  end if;
  source:=snapshot(dec.ST_NUMBER,dec.WARE_ID,ignore_plan);
  if source is null then raise_application_error(-20886,'DEFER_HU_WHOLE_TREE_REQUIRED');end if;
  if p_task is not null and(dbms_lob.compare(source,plan.SOURCE_MEMBERS_JSON)!=0 or target!=plan.TARGET_CELL)
   then raise_application_error(-20890,'CLOSURE_CHANGED: deferred HU source');end if;
  p_value:=json_object_t.parse(source);p_value.put('decision_operation_id',dec.OPERATION_ID);p_value.put('st_number',dec.ST_NUMBER);
  p_value.put('warehouse',dec.WARE_ID);p_value.put('decision_version',dec.VERSION_NO);p_value.put('target_trip',dec.TARGET_TT_ID);p_value.put('target_cell',target);
 end;

 procedure request_plan(p_operation varchar2,p_decision varchar2,p_actor varchar2,p_request out clob)is
  dec RRL_ST_DEFER_DECISION%rowtype;value json_object_t;wire json_object_t:=json_object_t();src json_object_t:=json_object_t();meta json_object_t:=json_object_t();raw_source clob;
 begin
  p_request:=null;select *into dec from RRL_ST_DEFER_DECISION where OPERATION_ID=p_decision;
  raw_source:=snapshot(dec.ST_NUMBER,dec.WARE_ID);if raw_source is null then return;end if;
  describe(p_decision,p_actor,null,value);
  if value.get_string('cell')=value.get_string('target_cell')then raise_application_error(-20886,'DEFER_HU_ALREADY_WAITING_NO_MOVE_REQUIRED');end if;
  wire.put('operation_id',p_operation);wire.put('command_type','HU_PLAN_MOVE');wire.put('actor',p_actor);
  src.put('uid',value.get_string('root'));wire.put('source',src);wire.put('lines',json_array_t());wire.put('units',json_array_t());
  meta.put('expected_version',value.get_number('content_version'));meta.put('target_cell',value.get_string('target_cell'));
  meta.put('defer_decision_operation_id',p_decision);wire.put('metadata',meta);p_request:=wire.to_clob;
 end;

 procedure declare_plan(p_request clob,p_task number,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t)is
  d json_object_t:=json_object_t.parse(p_request);meta json_object_t:=d.get_object('metadata');value json_object_t;plan RRL_ST_DEFER_WAIT_PLAN%rowtype;
  decision varchar2(100):=meta.get_string('defer_decision_operation_id');planning boolean:=d.get_string('command_type')='HU_PLAN_MOVE';task_id number;
 begin
  if planning then
   if decision is null then return;end if;
   describe(decision,d.get_string('actor'),null,value);
   RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_ST_DEFER_WAIT_RUN',d.get_string('operation_id'));
   RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_ST_DEFER_WAIT_PLAN',RRL_STOCK_PLAN_HELPER.decimal_text(p_task));
  else
   select count(*)into task_id from RRL_ST_DEFER_WAIT_PLAN where TASK_ID=p_task and BASE_UOM='HU';
   if task_id=0 then return;end if;
   select *into plan from RRL_ST_DEFER_WAIT_PLAN where TASK_ID=p_task;
   select r.DECISION_OPERATION_ID into decision from RRL_ST_DEFER_WAIT_RUN r where r.OPERATION_ID=plan.PLAN_OPERATION_ID;
   describe(decision,d.get_string('actor'),p_task,value);
   RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_ST_DEFER_WAIT_PLAN',RRL_STOCK_PLAN_HELPER.decimal_text(p_task));
   RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_ST_DEFER_WAIT_RUN',plan.PLAN_OPERATION_ID);
  end if;
  if value.get_string('root')!=p_domain.get_string('uid')or value.get_string('target_cell')!=p_domain.get_string('target')
   then raise_application_error(-20886,'DEFER_HU_ROOT_TARGET_REQUIRED');end if;
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_ST_DEFER_DECISION',decision);
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_TRANSPORT_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(value.get_number('target_trip')));
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_RECEIPT_WARE_SETTINGS',RRL_STOCK_PLAN_HELPER.decimal_text(value.get_number('warehouse')));
  declare cases json_array_t:=value.get_array('cases');item json_object_t;begin
   for i in 0..cases.get_size-1 loop
    item:=treat(cases.get(i)as json_object_t);
    RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(item.get_number('st_member_id')));
    RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(item.get_number('fulfillment_id')));
   end loop;
  end;
  p_domain.put('defer_wait_hu',value);
 end;

 procedure validate_plan(p_request clob,p_actor varchar2,p_frozen json_object_t,p_task number default null)is
  current_value json_object_t;d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');
  cases json_array_t;item json_object_t;trip number;st number;st_number varchar2(100);
 begin
  if p_frozen is null then return;end if;
  trip:=p_frozen.get_number('target_trip');
  select ID into trip from RRL_TRANSPORT_TASK where ID=trip for update;
  cases:=p_frozen.get_array('cases');st_number:=p_frozen.get_string('st_number');
  for x in(select s.ID from RRL_SBORKA_PALLETS s where s.ST_NUMBER=st_number order by s.ID)loop
   select ID into st from RRL_SBORKA_PALLETS where ID=x.ID for update;
  end loop;
  describe(p_frozen.get_string('decision_operation_id'),p_actor,p_task,current_value);
  if dbms_lob.compare(current_value.to_clob,p_frozen.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: deferred HU decision/source');end if;
  if d.get_string('command_type')!='HU_PLAN_MOVE'then
   if m.get_string('scanned_from_cell')is null or m.get_string('scanned_from_cell')!=current_value.get_string('cell')
    or m.get_string('scanned_to_cell')is null or m.get_string('scanned_to_cell')!=current_value.get_string('target_cell')
    or m.get_string('fact_qty')is null or RRL_STOCK_MATH.quantity(m.get_string('fact_qty'))!=1
    then raise_application_error(-20886,'DEFER_HU_WHOLE_TOP_SOURCE_TARGET_SCANS_REQUIRED');end if;
   if m.has('unit_keys')then declare keys json_array_t:=m.get_array('unit_keys');begin
    if keys is not null and keys.get_size>0 then raise_application_error(-20886,'DEFER_HU_NO_PARTIAL_UNIT_SELECTION');end if;
   end;end if;
  end if;
 end;
end;
/
