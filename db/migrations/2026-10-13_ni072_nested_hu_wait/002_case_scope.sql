create or replace package body RRL_ST_DEFER_CASE_WAIT as

 function task_signature(t RRL_WAREHOUSE_TASK%rowtype)return varchar2 is v json_object_t:=json_object_t();begin

  v.put('status',t.STATUS);v.put('assigned',t.ASSIGNED_TO);v.put('resource',t.RESOURCE_ID);v.put('session',t.RESOURCE_SESSION_ID);v.put('equipment',t.EQUIPMENT_ID);

  v.put('started',to_char(t.STARTED_AT_INSTANT,'YYYY-MM-DD HH24:MI:SS.FF6TZH:TZM'));

  return lower(rawtohex(sys.dbms_crypto.hash(v.to_clob,sys.dbms_crypto.hash_sh256)));

 end;

 function single_snapshot(p_st varchar2,p_ware number,p_ignore_plan varchar2,p_case_id number,p_nested_root varchar2 default null)return clob is

  ct RRL_CASE_PICK_TASK%rowtype;ff RRL_CUSTOMER_ORDER_FULFILLMENT%rowtype;

  n number;h number;own_qty number;items json_array_t:=json_array_t();x json_object_t;r json_object_t:=json_object_t();wait_cell varchar2(50);

 begin

  select count(*)into n from RRL_SBORKA_PALLETS where ST_NUMBER=p_st and ID=(select LEGACY_SBORKA_PALLET_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_case_id);

  if n!=1 then raise_application_error(-20886,'DEFER_CASE_SINGLE_ST_PLACE_REQUIRED');end if;

  select c.*into ct from RRL_CASE_PICK_TASK c join RRL_SBORKA_PALLETS p on p.ID=c.LEGACY_SBORKA_PALLET_ID where p.ST_NUMBER=p_st and c.CASE_PICK_TASK_ID=p_case_id;

  if ct.WARE_ID is null or ct.WARE_ID!=p_ware or ct.CURRENT_CELL is null or ct.SSCC is null

   or ct.STATUS not in('WAIT_CONTROL','CONTROLLED','READY_TO_SHIP')then raise_application_error(-20886,'DEFER_CASE_COMPLETED_OWN_CARRIER_REQUIRED');end if;

  select count(*)into n from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=ct.LEGACY_SBORKA_PALLET_ID;

  if n!=1 then raise_application_error(-20886,'DEFER_CASE_SINGLE_FULFILLMENT_REQUIRED');end if;

  select *into ff from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=ct.LEGACY_SBORKA_PALLET_ID;

  if ff.STATUS!='PICKED'or ff.PICKED_CASE_TASK_ID is null or ff.PICKED_CASE_TASK_ID!=ct.CASE_PICK_TASK_ID

   or ff.CUSTOMER_ORDER_ID!=ct.CUSTOMER_ORDER_ID or ff.PICKED_CONTENT_VERSION is null or ff.PICKED_CONTENT_VERSION!=ct.CONTENT_VERSION

   then raise_application_error(-20886,'DEFER_CASE_CURRENT_PHYSICAL_FULFILLMENT_REQUIRED');end if;

  select count(*)into n from RRL_WMS_HU_LINK where CHILD_CASE_TASK_ID=ct.CASE_PICK_TASK_ID and ACTIVE_FLAG=1;

  if n!=0 then
   if p_nested_root is null then raise_application_error(-20886,'DEFER_CASE_NESTED_SOURCE_REQUIRES_HU_PLAN');end if;
   declare parent_uid varchar2(200);next_uid varchar2(200);counted number;steps number:=0;begin
    select count(*),min(PARENT_UID)into counted,parent_uid from RRL_WMS_HU_LINK where CHILD_CASE_TASK_ID=ct.CASE_PICK_TASK_ID and ACTIVE_FLAG=1;
    if counted!=1 then raise_application_error(-20886,'DEFER_CASE_ONE_REGISTERED_PARENT_REQUIRED');end if;
    loop
     steps:=steps+1;if steps>200 then raise_application_error(-20886,'DEFER_CASE_PARENT_CHAIN_BOUND_200');end if;
     select count(*),min(PARENT_UID)into counted,next_uid from RRL_WMS_HU_LINK where CHILD_PALLET_UID=parent_uid and ACTIVE_FLAG=1;
     exit when counted=0;
     if counted!=1 then raise_application_error(-20886,'DEFER_CASE_ONE_REGISTERED_PARENT_REQUIRED');end if;
     parent_uid:=next_uid;
    end loop;
    if parent_uid!=p_nested_root then raise_application_error(-20886,'DEFER_CASE_EXACT_TOP_ROOT_REQUIRED');end if;
   end;
  elsif p_nested_root is not null then raise_application_error(-20886,'DEFER_CASE_NESTED_MEMBER_REQUIRED');end if;

  select count(*)into n from RRL_WAREHOUSE_TASK w where w.STATUS not in('DONE','CANCELLED')

   and(w.UID_PALLET=ct.SSCC or(w.SOURCE_DOC_TYPE='ST_DEFER_CASE'and exists(select 1 from RRL_ST_DEFER_WAIT_PLAN cp where cp.TASK_ID=w.TASK_ID and cp.CASE_TASK_ID=ct.CASE_PICK_TASK_ID)))

   and(p_ignore_plan is null or not exists(select 1 from RRL_ST_DEFER_WAIT_PLAN p where p.TASK_ID=w.TASK_ID and p.PLAN_OPERATION_ID=p_ignore_plan));

  if n!=0 then raise_application_error(-20886,'DEFER_CASE_PHYSICAL_TASK_ALREADY_OPEN');end if;

  for l in(select h.LOT_UID,s.CELL,s.REMAIN,s.HARD_RESERVED_BASE,s.STOCK_VERSION,s.BASE_UOM,p.ARTICUL,h.CASE_PICK_LINE_ID

   from RRL_CASE_CARRIER_LOT h join RRL_REMAINS s on s.UID_POLETA=h.LOT_UID join RRL_PALLETS p on p.UID_PALLET=h.LOT_UID

   where h.CASE_PICK_TASK_ID=ct.CASE_PICK_TASK_ID and(s.REMAIN>0 or s.HARD_RESERVED_BASE>0)order by h.LOT_UID,s.CELL fetch first 201 rows only)loop

   if items.get_size>=200 then raise_application_error(-20881,'DEFER_CASE_LOT_BOUND_200');end if;

   if l.CELL!=ct.CURRENT_CELL or l.REMAIN<=0 or l.HARD_RESERVED_BASE!=l.REMAIN then raise_application_error(-20886,'DEFER_CASE_WHOLE_RESERVED_STOCK_REQUIRED');end if;

   select nvl(sum(BASE_QTY),0)into own_qty from RRL_STOCK_RESERVATION where UID_PALLET=l.LOT_UID and CELL=l.CELL

    and CUSTOMER_ORDER_ID=ct.CUSTOMER_ORDER_ID and RESERVATION_KIND='HARD'and STATUS in('ACTIVE','ALLOCATED','PICKING');

   if own_qty!=l.REMAIN then raise_application_error(-20886,'DEFER_CASE_EXACT_OWN_HARD_REQUIRED');end if;

   x:=json_object_t();x.put('uid',l.LOT_UID);x.put('cell',l.CELL);x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(l.REMAIN));

   x.put('version',l.STOCK_VERSION);x.put('base',l.BASE_UOM);x.put('article',l.ARTICUL);x.put('case_line',l.CASE_PICK_LINE_ID);items.append(x);

  end loop;

  if items.get_size=0 then raise_application_error(-20886,'DEFER_CASE_HAS_NO_PHYSICAL_STOCK');end if;

  select count(*)into n from RRL_CELLS where CELL=ct.CURRENT_CELL and WARE_ID=p_ware;

  if n!=1 then raise_application_error(-20886,'DEFER_CASE_SOURCE_WAREHOUSE_REQUIRED');end if;

  select max(DEFER_WAIT_CELL)into wait_cell from RRL_RECEIPT_WARE_SETTINGS where WARE_ID=p_ware;

  r.put('state','PREPARED_CASE');r.put('case_task_id',ct.CASE_PICK_TASK_ID);r.put('st_member_id',ct.LEGACY_SBORKA_PALLET_ID);

  r.put('fulfillment_id',ff.FULFILLMENT_ID);r.put('pallet_identifier',ct.SSCC);r.put('cell',ct.CURRENT_CELL);

  r.put('content_version',ct.CONTENT_VERSION);r.put('stocks',items);r.put('physical_move_required',wait_cell is null or wait_cell!=ct.CURRENT_CELL);

  r.put('stock_changed',false);return r.to_clob;

 exception when no_data_found or too_many_rows then raise_application_error(-20886,'DEFER_CASE_SINGLE_REGISTERED_SOURCE_REQUIRED');

 end;

 function snapshot(p_st varchar2,p_ware number,p_ignore_plan varchar2 default null,p_case_id number default null,p_nested_root varchar2 default null)return clob is

  n number;case_id number;case_count number;total_lots number:=0;need_move boolean:=false;

  cases json_array_t:=json_array_t();child json_object_t;result json_object_t:=json_object_t();uid varchar2(200);

  type identifiers is table of pls_integer index by varchar2(200);seen identifiers;

 begin

  if p_case_id is not null then return single_snapshot(p_st,p_ware,p_ignore_plan,p_case_id,p_nested_root);end if;

  if p_nested_root is not null then raise_application_error(-20886,'DEFER_CASE_EXPLICIT_NESTED_MEMBER_REQUIRED');end if;
  select count(*)into n from RRL_SBORKA_PALLETS where ST_NUMBER=p_st;

  if n<1 or n>200 then raise_application_error(-20881,'DEFER_CASE_ST_MEMBER_BOUND_200');end if;

  for member in(select ID from RRL_SBORKA_PALLETS where ST_NUMBER=p_st order by ID)loop

   select count(*),min(CASE_PICK_TASK_ID)into case_count,case_id from RRL_CASE_PICK_TASK where LEGACY_SBORKA_PALLET_ID=member.ID;

   if case_count!=1 then raise_application_error(-20886,'DEFER_CASE_ALL_ST_MEMBERS_SINGLE_CASE_REQUIRED');end if;

   child:=json_object_t.parse(single_snapshot(p_st,p_ware,p_ignore_plan,case_id));

   total_lots:=total_lots+child.get_array('stocks').get_size;

   if total_lots>200 then raise_application_error(-20881,'DEFER_CASE_ST_TOTAL_LOT_BOUND_200');end if;

   uid:=child.get_string('pallet_identifier');if seen.exists(uid)then raise_application_error(-20886,'DEFER_CASE_DISTINCT_CARRIER_IDENTIFIERS_REQUIRED');end if;seen(uid):=1;

   if child.get_boolean('physical_move_required')then need_move:=true;end if;cases.append(child);

  end loop;

  if cases.get_size=1 then return treat(cases.get(0)as json_object_t).to_clob;end if;

  result.put('state','PREPARED_CASES');result.put('cases',cases);result.put('case_count',cases.get_size);result.put('lot_count',total_lots);

  result.put('physical_move_required',need_move);result.put('stock_changed',false);return result.to_clob;

 end;

 procedure assert_command(p_request clob,p_actor varchar2)is

  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');tid number;

  t RRL_WAREHOUSE_TASK%rowtype;p RRL_ST_DEFER_WAIT_PLAN%rowtype;

 begin

  tid:=m.get_number('physical_task_id');if tid is null then return;end if;

  select *into t from RRL_WAREHOUSE_TASK where TASK_ID=tid;

  select *into p from RRL_ST_DEFER_WAIT_PLAN where TASK_ID=tid;

  RRL_WAREHOUSE_TASK_ACCESS.assert_scope(tid,p_actor);

  if RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 then raise_application_error(-20882,'DEFER_CASE_CURRENT_EXECUTOR_REQUIRED');end if;

  if p.CASE_TASK_ID is null or p.CASE_TASK_ID!=d.get_object('source').get_number('case_task_id')

   or t.SOURCE_DOC_TYPE!='ST_DEFER_CASE'or t.TASK_TYPE!='PUTAWAY'or t.TASK_SOURCE!='MANUAL'

   or(t.SOURCE_TASK_ID is null or(t.SOURCE_TASK_ID!=p.CASE_TASK_ID and t.SOURCE_TASK_ID!=t.TASK_ID))or t.UID_PALLET!=p.UID_PALLET or t.FROM_CELL!=p.FROM_CELL or t.TO_CELL!=p.TARGET_CELL

   or t.QTY!=1 or t.UNIT_CODE!='CASE'or t.QTY_MODE!='PALLET'

   then raise_application_error(-20886,'DEFER_CASE_REGISTERED_WAITING_TASK_REQUIRED');end if;

  if t.ASSIGNED_TO is not null and t.ASSIGNED_TO!=p_actor then raise_application_error(-20882,'DEFER_CASE_ASSIGNED_EXECUTOR_REQUIRED');end if;

 end;

 procedure describe(p_request clob,p_actor varchar2,p_current out json_object_t)is

  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');tid number:=m.get_number('physical_task_id');

  p RRL_ST_DEFER_WAIT_PLAN%rowtype;t RRL_WAREHOUSE_TASK%rowtype;dec RRL_ST_DEFER_DECISION%rowtype;

  src clob;n number;target varchar2(50);

 begin

  assert_command(p_request,p_actor);

  if m.get_string('scanned_pallet')is null or m.get_string('scanned_pallet')!=m.get_string('scan_container')

   or m.get_string('scanned_from_cell')is null or m.get_string('fact_qty')is null or RRL_STOCK_MATH.quantity(m.get_string('fact_qty'))!=1

   or m.get_number('resource_id')is not null or m.get_number('resource_session_id')is not null or m.get_number('equipment_id')is not null

   or m.get_string('scan_draft_id')is not null or m.get_string('scanned_to_slot_code')is not null

   then raise_application_error(-20886,'DEFER_CASE_WHOLE_PLACE_SCANS_REQUIRED');end if;

  if m.has('unit_keys')then declare keys json_array_t:=m.get_array('unit_keys');begin

   if keys is not null and keys.get_size>0 then raise_application_error(-20886,'DEFER_CASE_WHOLE_CARRIER_NO_PARTIAL_UNIT_SELECTION');end if;

  end;end if;

  select *into p from RRL_ST_DEFER_WAIT_PLAN where TASK_ID=tid;

  select *into t from RRL_WAREHOUSE_TASK where TASK_ID=tid;

  if m.get_string('scanned_from_cell')!=p.FROM_CELL then raise_application_error(-20886,'DEFER_CASE_ORIGINAL_SOURCE_SCAN_REQUIRED');end if;

  select d.*into dec from RRL_ST_DEFER_WAIT_RUN r join RRL_ST_DEFER_DECISION d on d.OPERATION_ID=r.DECISION_OPERATION_ID where r.OPERATION_ID=p.PLAN_OPERATION_ID;

  if t.STATUS not in('PLANNED','ASSIGNED','IN_PROGRESS')then raise_application_error(-20886,'DEFER_CASE_WAITING_TASK_OPEN_REQUIRED');end if;

  if t.FROM_WARE_ID!=dec.WARE_ID or t.TO_WARE_ID!=dec.WARE_ID or t.SOURCE_DOC_ID!=dec.VERSION_NO

   or t.FROM_CELL_SLOT_ID is not null or t.TO_CELL_SLOT_ID is not null or t.RESOURCE_ID is not null or t.RESOURCE_SESSION_ID is not null or t.EQUIPMENT_ID is not null

   then raise_application_error(-20886,'DEFER_CASE_ORDINARY_WAITING_TASK_REQUIRED');end if;

  select count(*)into n from RRL_ST_DEFER_DECISION where ST_NUMBER=dec.ST_NUMBER and VERSION_NO>dec.VERSION_NO;

  if n!=0 then raise_application_error(-20886,'DEFER_WAIT_DECISION_SUPERSEDED');end if;

  select count(*)into n from RRL_SBORKA_PALLETS s where s.ST_NUMBER=dec.ST_NUMBER and(nvl(s.TRANSTASK_ID,-1)!=dec.TARGET_TT_ID or nvl(s.CONDITION,0)=2

   or exists(select 1 from RRL_TT_HU_LOAD_ST ls join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=ls.LOAD_OPERATION_ID

    where ls.SBORKA_PALLET_ID=s.ID and ls.ACTIVE_FLAG=1 and l.STATUS in('LOADED','DEPARTED')));

  if n!=0 then raise_application_error(-20886,'DEFER_CASE_ST_ASSIGNMENT_OR_LOAD_CHANGED');end if;

  select count(*)into n from RRL_TRANSPORT_TASK where ID=dec.TARGET_TT_ID and CONDITION='Спланирован'and nvl(DELETED,0)=0 and nvl(PAY_ORDER_ID,0)=0;

  if n!=1 then raise_application_error(-20886,'DEFER_WAIT_PLANNED_TARGET_TRIP_REQUIRED');end if;

  select DEFER_WAIT_CELL into target from RRL_RECEIPT_WARE_SETTINGS where WARE_ID=dec.WARE_ID;

  if target is null or target!=p.TARGET_CELL or target!=m.get_string('target_cell')then raise_application_error(-20886,'DEFER_WAIT_TARGET_CONFIGURATION_CHANGED');end if;

  RRL_ST_DEFER_WAIT_CORE.check_target(target,dec.WARE_ID);

  select count(*)into n from RRL_CELLS where CELL=target and(nvl(LIMIT_HEIGHT,0)>0 or nvl(LIMIT_WEIGHT,0)>0);

  if n!=0 then raise_application_error(-20886,'DEFER_WAIT_MEASURED_CAPACITY_PLAN_REQUIRED');end if;

  select count(*)into n from RRL_TOPOLOGY_CELL tc join RRL_WAREHOUSE_TOPOLOGY tp on tp.TOPOLOGY_ID=tc.TOPOLOGY_ID join RRL_TOPOLOGY_CELL_SLOT sl on sl.TOPOLOGY_CELL_ID=tc.TOPOLOGY_CELL_ID

   where tc.LEGACY_CELL_CODE=target and tc.WARE_ID=dec.WARE_ID and tc.ACTIVE=1 and sl.ACTIVE=1 and tp.STATUS='PUBLISHED';

  if n!=0 then raise_application_error(-20886,'DEFER_WAIT_PHYSICAL_SLOT_PLAN_REQUIRED');end if;

  src:=snapshot(dec.ST_NUMBER,dec.WARE_ID,p.PLAN_OPERATION_ID,p.CASE_TASK_ID);

  if dbms_lob.compare(src,p.SOURCE_MEMBERS_JSON)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: deferred CASE source');end if;

  p_current:=json_object_t.parse(src);p_current.put('decision',dec.OPERATION_ID);p_current.put('plan',p.PLAN_OPERATION_ID);

  p_current.put('target_trip',dec.TARGET_TT_ID);p_current.put('warehouse',dec.WARE_ID);p_current.put('task_signature',task_signature(t));

 end;

 procedure validate_move(p_request clob,p_actor varchar2,p_frozen json_object_t)is current_src json_object_t;copy_src json_object_t;begin

  describe(p_request,p_actor,current_src);

  if p_frozen is null then raise_application_error(-20886,'DEFER_CASE_ROOT_PLAN_REQUIRED');end if;

  copy_src:=json_object_t.parse(p_frozen.to_clob);copy_src.remove('sync_id');copy_src.remove('sync_key');

  if dbms_lob.compare(current_src.to_clob,copy_src.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: deferred CASE waiting source');end if;

 end;

 procedure plan_move(p_request clob,p_actor varchar2,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t)is

  d json_object_t:=json_object_t.parse(p_request);tid number:=d.get_object('metadata').get_number('physical_task_id');v json_object_t;v_sync_id number;v_sync_key varchar2(400);

 begin

  if tid is null then return;end if;describe(p_request,p_actor,v);

  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_ST_DEFER_WAIT_PLAN',RRL_STOCK_PLAN_HELPER.decimal_text(tid));

  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(tid));

  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_ST_DEFER_WAIT_RUN',v.get_string('plan'));

  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_ST_DEFER_DECISION',v.get_string('decision'));

  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_RECEIPT_WARE_SETTINGS',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('warehouse')));

  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_TRANSPORT_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('target_trip')));

  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('st_member_id')));

  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('fulfillment_id')));

  v_sync_key:='DEFER.CASE.WT:'||RRL_STOCK_PLAN_HELPER.decimal_text(tid);

  begin select SYNC_ID into v_sync_id from RRL_WAREHOUSE_TASK_SYNC where SYNC_KEY=v_sync_key;

  exception when no_data_found then select RRL_WH_TASK_SYNC_SQ.nextval into v_sync_id from dual;end;

  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_WAREHOUSE_TASK_SYNC',RRL_STOCK_PLAN_HELPER.decimal_text(v_sync_id));

  RRL_STOCK_PLAN_HELPER.anchor(p_resources,70,'UNIQUE','TASK.SYNC:'||v_sync_key);

  v.put('sync_id',v_sync_id);v.put('sync_key',v_sync_key);p_domain.put('deferred_case_waiting',v);

 end;

 procedure finish_move(p_request clob,p_actor varchar2,p_result in out clob)is

  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');tid number:=m.get_number('physical_task_id');

  frozen json_object_t;current_src json_object_t;wire clob;t RRL_WAREHOUSE_TASK%rowtype;j json_object_t:=json_object_t.parse(p_result);

  v_sync_id number;v_sync_key varchar2(400);op varchar2(100):=d.get_string('operation_id');new_version number;ff_id number;case_id number;lots json_array_t;lot json_object_t;lot_uid varchar2(200);lot_qty number;lot_base varchar2(20);

 begin

  if tid is null then return;end if;

  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')!=op or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is null

   or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20886,'DEFER_CASE_ROOT_POSTING_REQUIRED');end if;

  select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=op;

  frozen:=json_object_t.parse(wire).get_object('domain').get_object('deferred_case_waiting');

  if frozen is null then raise_application_error(-20886,'DEFER_CASE_ROOT_PLAN_REQUIRED');end if;

  select *into t from RRL_WAREHOUSE_TASK where TASK_ID=tid;

  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(tid)));

  if task_signature(t)!=frozen.get_string('task_signature')then raise_application_error(-20890,'CLOSURE_CHANGED: deferred CASE task');end if;

  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(frozen.get_number('fulfillment_id'))));

  new_version:=j.get_number('content_version');ff_id:=frozen.get_number('fulfillment_id');case_id:=j.get_number('case_pick_task_id');

  select count(*)into v_sync_id from RRL_CUSTOMER_ORDER_FULFILLMENT

   where FULFILLMENT_ID=ff_id and STATUS='PICKED'and PICKED_CASE_TASK_ID=case_id and PICKED_CONTENT_VERSION=new_version;

  if v_sync_id!=1 then raise_application_error(-20886,'DEFER_CASE_FULFILLMENT_BINDING_CHANGED');end if;

  update RRL_WAREHOUSE_TASK set STATUS='DONE',FACT_QTY=1,TARGET_UID_PALLET=UID_PALLET,FINISHED_AT=systimestamp,ASSIGNED_TO=p_actor,

   COMPLETION_HASH=lower(rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256))),COMPLETION_JSON=p_request,LAST_ERROR=null where TASK_ID=tid;

  lots:=j.get_array('lots');

  for i in 0..lots.get_size-1 loop

   lot:=treat(lots.get(i)as json_object_t);lot_uid:=lot.get_string('uid');lot_qty:=RRL_STOCK_MATH.quantity(lot.get_string('quantity'));lot_base:=lot.get_string('base');

   insert into RRL_WAREHOUSE_TASK_STOCK_MOVE(STOCK_MOVE_ID,TASK_ID,TASK_SOURCE,TASK_TYPE,SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_TASK_ID,

    UID_PALLET,TARGET_UID_PALLET,FROM_CELL,TO_CELL,QTY,BASE_QTY,BASE_UOM,OPERATION_ID,CREATED_AT,CREATED_BY)

    values(RRL_WH_TASK_STOCK_MOVE_SQ.nextval,tid,t.TASK_SOURCE,t.TASK_TYPE,t.SOURCE_DOC_TYPE,t.SOURCE_DOC_ID,t.SOURCE_TASK_ID,

     lot_uid,lot_uid,t.FROM_CELL,t.TO_CELL,lot_qty,lot_qty,lot_base,op,systimestamp,p_actor);

  end loop;

  v_sync_id:=frozen.get_number('sync_id');v_sync_key:=frozen.get_string('sync_key');

  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK_SYNC',RRL_STOCK_PLAN_HELPER.decimal_text(v_sync_id)));

  insert into RRL_WAREHOUSE_TASK_SYNC(SYNC_ID,TASK_ID,TASK_SOURCE,TASK_TYPE,SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_TASK_ID,SYNC_KEY,SYNC_STATUS,SYNC_ATTEMPT,CREATED_AT,UPDATED_AT,SYNCED_AT,UPDATED_BY)

   values(v_sync_id,tid,t.TASK_SOURCE,t.TASK_TYPE,t.SOURCE_DOC_TYPE,t.SOURCE_DOC_ID,t.SOURCE_TASK_ID,v_sync_key,'SYNCED',1,systimestamp,systimestamp,systimestamp,p_actor);

  j.put('task_id',tid);j.put('status','DONE');j.put('quantity','1');j.put('base_uom','CASE');j.put('pallet_identifier',t.UID_PALLET);j.put('remaining_quantity','0');

  p_result:=j.to_clob;

 end;

end;


/
