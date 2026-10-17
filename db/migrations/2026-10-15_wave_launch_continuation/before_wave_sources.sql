create or replace package body RRL_STOCK_WAVE_CMD as

 function release_amount(p_text varchar2)return number is

 begin

  if p_text='0'then return 0;end if;

  return RRL_STOCK_MATH.quantity(p_text);

 end;

 function signature(p_row RRL_PICK_WAVE_REPLENISH_TASK%rowtype) return varchar2 is v json_object_t:=json_object_t();

 begin

  v.put('id',p_row.PICK_WAVE_REPLENISH_TASK_ID);v.put('wave',p_row.PICK_WAVE_ID);v.put('article',p_row.ARTICUL);

  v.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(p_row.QTY));v.put('target',p_row.TARGET_CELL_CODE);

  v.put('demand',p_row.DEMAND_BASE_QTY);v.put('pick_task',p_row.PICK_TASK_ID);v.put('scope',p_row.REPLENISHMENT_QTY_MODE);v.put('shelf_days',p_row.MIN_SHELF_LIFE_DAYS);v.put('shelf_percent',p_row.MIN_SHELF_LIFE_PERCENT);

  return rawtohex(sys.dbms_crypto.hash(v.to_clob,sys.dbms_crypto.hash_sh256));

 end;

 procedure compile_target_supply(rt RRL_PICK_WAVE_REPLENISH_TASK%rowtype,p_needed number,p_ware number,p_mode varchar2,p_capacity number,

  f in out nocopy json_array_t,r in out nocopy json_array_t,p_used in out nocopy json_object_t,

  p_changes in out nocopy json_object_t,p_decision out json_object_t,p_plan out json_object_t) is

  old_a json_array_t:=json_array_t();new_a json_array_t:=json_array_t();x json_object_t;

  v_total number:=0;v_count number;v_version number;v_id number;v_left number:=p_needed;v_take number;v_key varchar2(2000);v_base varchar2(20);v_taken number;v_release_left number;v_release number;v_source json_object_t;v_source_uid varchar2(200);v_source_cell varchar2(60);v_source_p number;v_source_ver number;v_reason varchar2(4000);v_candidates json_array_t:=json_array_t();v_cand json_object_t;

 begin

  p_plan:=null;p_decision:=json_object_t();p_decision.put('needed',p_needed);

  p_decision.put('mode',p_mode);p_decision.put('capacity',p_capacity);

  if rt.PICK_TASK_ID is null or p_needed is null or p_needed<=0 then return;end if;

  select count(*) into v_count from RRL_WAREHOUSE_TASK wh join RRL_PICK_WAVE_REPLENISH_TASK rr

   on rr.PICK_WAVE_REPLENISH_TASK_ID=wh.SOURCE_TASK_ID and rr.PICK_WAVE_ID=wh.SOURCE_DOC_ID

   where wh.TASK_SOURCE='WAVE' and wh.TASK_TYPE='REPLENISHMENT' and rr.PICK_WAVE_ID=rt.PICK_WAVE_ID

    and rr.PICK_TASK_ID=rt.PICK_TASK_ID and wh.STATUS not in('DONE','CANCELLED');

  if v_count>0 then p_decision.put('reason','PHYSICAL_TASK_ALREADY_PLANNED');return;end if;

  for sr in(select sr.* from RRL_STOCK_RESERVATION sr join RRL_PICK_TASK pt on pt.PICK_TASK_ID=sr.SOURCE_LINE_ID

   join RRL_CELLS c on c.CELL=sr.CELL

   where sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.SOURCE_DOC_ID=rt.PICK_WAVE_ID and sr.SOURCE_LINE_ID=rt.PICK_TASK_ID

    and sr.RESERVATION_DOMAIN='PICKING' and sr.RESERVATION_KIND='HARD' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING')

    and sr.BASE_QTY>0 and sr.CELL!=rt.TARGET_CELL_CODE and sr.ARTICUL=rt.ARTICUL

    and sr.CUSTOMER_ORDER_ID=pt.CUSTOMER_ORDER_ID and c.WARE_ID=p_ware order by sr.RESERVATION_ID fetch first 201 rows only) loop

   if old_a.get_size>=200 then raise_application_error(-20881,'TARGET_SUPPLY_OWNER_BOUND_200');end if;

   if v_base is null then v_base:=sr.BASE_UOM;elsif v_base!=sr.BASE_UOM then raise_application_error(-20868,'TARGET_SUPPLY_BASE_CONFLICT');end if;

   x:=json_object_t();x.put('id',sr.RESERVATION_ID);x.put('version',sr.RESERVATION_VERSION);

   x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(sr.BASE_QTY));x.put('uid',sr.UID_PALLET);x.put('cell',sr.CELL);

   x.put('base_uom',sr.BASE_UOM);old_a.append(x);v_total:=v_total+sr.BASE_QTY;

  end loop;

  p_decision.put('source_binding_count',old_a.get_size);p_decision.put('source_owned_quantity',v_total);

  if v_total!=p_needed or old_a.get_size=0 then p_decision.put('reason','COMPLETE_OWN_SOURCE_BINDING_REQUIRED');return;end if;

  for i in 0..old_a.get_size-1 loop

   x:=treat(old_a.get(i) as json_object_t);v_source_uid:=x.get_string('uid');v_source_cell:=x.get_string('cell');

   select count(*) into v_count from RRL_WAREHOUSE_TASK where UID_PALLET=v_source_uid and FROM_CELL=v_source_cell and STATUS not in('DONE','CANCELLED');

   if v_count>0 then p_decision.put('reason','SOURCE_PALLET_PHYSICAL_TASK_ALREADY_PLANNED');return;end if;

  end loop;

  v_count:=0;

  for st in(select rr.UID_POLETA,rr.CELL,rr.REMAIN,rr.HARD_RESERVED_BASE,rr.STOCK_VERSION,rr.BASE_UOM

   from RRL_REMAINS rr join RRL_PALLETS pp on pp.UID_PALLET=rr.UID_POLETA join RRL_CELLS c on c.CELL=rr.CELL

   where rr.CELL=rt.TARGET_CELL_CODE and c.WARE_ID=p_ware and pp.ARTICUL=rt.ARTICUL and rr.REMAIN>rr.HARD_RESERVED_BASE

   order by pp.EXPIRY_DATE nulls last,pp.PRODUCED_DATE nulls last,rr.UID_POLETA fetch first 201 rows only) loop

   exit when v_left=0;v_count:=v_count+1;if v_count>200 then raise_application_error(-20881,'TARGET_SUPPLY_CANDIDATE_BOUND_200');end if;

   v_key:=RRL_STOCK_LOCK_API.resource_key('STOCK',st.UID_POLETA,st.CELL);

   v_take:=least(v_left,st.REMAIN-st.HARD_RESERVED_BASE-nvl(p_used.get_number(v_key),0));

   v_cand:=json_object_t();v_cand.put('uid',st.UID_POLETA);v_cand.put('free',st.REMAIN-st.HARD_RESERVED_BASE);v_cand.put('planned_used',nvl(p_used.get_number(v_key),0));v_cand.put('take',v_take);

   if v_take<=0 then v_cand.put('reason','NO_UNPLANNED_FREE_QUANTITY');v_candidates.append(v_cand);continue;end if;

   v_reason:=RRL_STOCK_ELIGIBILITY.reason(st.UID_POLETA,st.CELL,p_ware,v_take,rt.MIN_SHELF_LIFE_DAYS,

    rt.MIN_SHELF_LIFE_PERCENT,'ALLOCATE',null,rt.ARTICUL);

   v_cand.put('reason',v_reason);v_candidates.append(v_cand);

   if v_reason is not null then continue;end if;

   if st.BASE_UOM!=v_base then raise_application_error(-20868,'TARGET_SUPPLY_BASE_CONFLICT');end if;

   select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=rt.ARTICUL

    and INPUT_UOM=st.BASE_UOM and BASE_UOM=st.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;

   if v_version is null then raise_application_error(-20868,'TARGET_SUPPLY_BASE_POLICY_REQUIRED');end if;

   select RRL_STOCK_RESERVATION_SQ.nextval into v_id from dual;

   x:=json_object_t();x.put('uid',st.UID_POLETA);x.put('cell',st.CELL);x.put('id',v_id);x.put('base_uom',st.BASE_UOM);

   x.put('stock_version',st.STOCK_VERSION+nvl(p_changes.get_number(v_key),0));x.put('uom_version',v_version);

   x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_take));new_a.append(x);v_left:=v_left-v_take;

  end loop;

  v_taken:=p_needed-v_left;p_decision.put('candidates',v_candidates);p_decision.put('usable_target_quantity',v_taken);

  -- Compute releases without changing global batch accounting until admission succeeds.

  v_release_left:=v_taken;

  for i in 0..old_a.get_size-1 loop

   x:=treat(old_a.get(i)as json_object_t);

   v_release:=least(v_release_left,RRL_STOCK_MATH.quantity(x.get_string('quantity')));

   v_release_left:=v_release_left-v_release;

   x.put('release_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_release));old_a.put(i,x,true);

  end loop;

  if v_left>0 then

   if v_taken<=0 or p_mode!='FULL_PALLET' then p_decision.put('reason','PARTIAL_TARGET_WHOLE_SOURCE_REQUIRED');return;end if;

   -- Retain every untouched own binding. Issue only the first whole source;

   -- the existing REPL_CONTINUATION calculates further own demand after its receipt.

   v_count:=0;

   for i in 0..old_a.get_size-1 loop

    x:=treat(old_a.get(i)as json_object_t);

    if RRL_STOCK_MATH.quantity(x.get_string('quantity'))>release_amount(x.get_string('release_quantity'))then

     v_count:=v_count+1;

     if v_source is null then v_source:=json_object_t.parse(x.to_clob);end if;

    end if;

   end loop;

   if v_source is null then raise_application_error(-20890,'TARGET_SUPPLY_RETAINED_OWNER_REQUIRED');end if;

   p_decision.put('remaining_source_binding_count',v_count);

   v_source_uid:=v_source.get_string('uid');v_source_cell:=v_source.get_string('cell');

   -- Every retained reservation is captured in old_a and verified separately.
   -- One representative binding selects physical stock; original whole arrival
   -- moves all captured owners, including multiple bindings of this same owner.
   select REMAIN,STOCK_VERSION into v_source_p,v_source_ver from RRL_REMAINS where UID_POLETA=v_source_uid and CELL=v_source_cell;

   p_decision.put('whole_source_quantity',v_source_p);

   if p_capacity is not null and v_source_p>p_capacity then p_decision.put('reason','WHOLE_SOURCE_EXCEEDS_REMAINING_TARGET_CAPACITY');return;end if;

   v_release:=release_amount(v_source.get_string('release_quantity'));

   v_source.put('remaining_owner_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(RRL_STOCK_MATH.quantity(v_source.get_string('quantity'))-v_release));

   v_source.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_source_p));

   v_source.put('remaining_total_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_left));

   v_source.put('reservation_version',v_source.get_number('version')+case when v_release>0 then 1 else 0 end);

   v_key:=RRL_STOCK_LOCK_API.resource_key('STOCK',v_source_uid,v_source_cell);

   v_count:=0;

   for i in 0..old_a.get_size-1 loop

    x:=treat(old_a.get(i)as json_object_t);

    if x.get_string('uid')=v_source_uid and x.get_string('cell')=v_source_cell

     and release_amount(x.get_string('release_quantity'))>0 then v_count:=v_count+1;end if;

   end loop;

   v_source.put('stock_version',v_source_ver+nvl(p_changes.get_number(v_key),0)+v_count);

  end if;

  v_release_left:=v_taken;

  for i in 0..old_a.get_size-1 loop

   x:=treat(old_a.get(i) as json_object_t);

   v_release:=least(v_release_left,RRL_STOCK_MATH.quantity(x.get_string('quantity')));v_release_left:=v_release_left-v_release;

   x.put('release_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_release));old_a.put(i,x,true);v_key:=RRL_STOCK_LOCK_API.resource_key('STOCK',x.get_string('uid'),x.get_string('cell'));

   if v_release>0 then p_changes.put(v_key,nvl(p_changes.get_number(v_key),0)+1);end if;

   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,x.get_string('uid'),rt.ARTICUL,x.get_string('cell'),null);

  end loop;

  for i in 0..new_a.get_size-1 loop

   x:=treat(new_a.get(i) as json_object_t);v_key:=RRL_STOCK_LOCK_API.resource_key('STOCK',x.get_string('uid'),x.get_string('cell'));

   p_used.put(v_key,nvl(p_used.get_number(v_key),0)+RRL_STOCK_MATH.quantity(x.get_string('quantity')));

   p_changes.put(v_key,nvl(p_changes.get_number(v_key),0)+1);

   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,x.get_string('uid'),rt.ARTICUL,x.get_string('cell'),null);

   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('id')));

  end loop;

  p_plan:=json_object_t();p_plan.put('old',old_a);p_plan.put('new',new_a);

  p_decision.put('reason',case when v_source is null then 'COMPLETE_TARGET_REPLACEMENT' else 'PARTIAL_TARGET_AND_WHOLE_SOURCE' end);

  p_plan.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_taken));if v_source is not null then p_plan.put('continuation',v_source);end if;

 end;

 procedure execute_target_supply(rt RRL_PICK_WAVE_REPLENISH_TASK%rowtype,p_plan json_object_t,p_ware number,p_actor varchar2) is

  a json_array_t:=p_plan.get_array('old');b json_array_t:=p_plan.get_array('new');x json_object_t;sr RRL_STOCK_RESERVATION%rowtype;

  v_qty number;v_stock number;v_count number;v_units clob;v_uid varchar2(200);v_cell varchar2(60);v_id number;

  v_details json_object_t:=json_object_t();v_rid number;v_version number;v_old_qty number;v_first varchar2(200);v_release_qty number;v_remaining_owner number;v_source_p number;v_source_ver number;v_source_res_ver number;v_next json_object_t;

 begin

  select count(*) into v_count from RRL_WAREHOUSE_TASK wh join RRL_PICK_WAVE_REPLENISH_TASK rr

   on rr.PICK_WAVE_REPLENISH_TASK_ID=wh.SOURCE_TASK_ID and rr.PICK_WAVE_ID=wh.SOURCE_DOC_ID

   where wh.TASK_SOURCE='WAVE' and wh.TASK_TYPE='REPLENISHMENT' and rr.PICK_WAVE_ID=rt.PICK_WAVE_ID

    and rr.PICK_TASK_ID=rt.PICK_TASK_ID and wh.STATUS not in('DONE','CANCELLED');

  if v_count>0 then raise_application_error(-20890,'CLOSURE_CHANGED: target supply physical task issued');end if;

  for pt in(select CUSTOMER_ID,CUSTOMER_ORDER_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID from RRL_PICK_TASK

   where PICK_TASK_ID=rt.PICK_TASK_ID and ARTICUL=rt.ARTICUL and TASK_TYPE='CASE_PICK' and STATUS not in('DONE','CANCELLED','FAILED')) loop

   v_details.put('reservation_scope','QTY');v_details.put('customer_id',pt.CUSTOMER_ID);v_details.put('customer_order_id',pt.CUSTOMER_ORDER_ID);

   v_details.put('pick_plan_id',pt.PICK_PLAN_ID);v_details.put('pick_plan_line_id',pt.PICK_PLAN_LINE_ID);v_details.put('pick_wave_id',rt.PICK_WAVE_ID);

  end loop;

  if not v_details.has('customer_order_id') then raise_application_error(-20887,'TARGET_SUPPLY_CASE_OWNER_REQUIRED');end if;

  for i in 0..a.get_size-1 loop

   x:=treat(a.get(i) as json_object_t);v_uid:=x.get_string('uid');v_cell:=x.get_string('cell');

   select count(*) into v_count from RRL_WAREHOUSE_TASK where UID_PALLET=v_uid and FROM_CELL=v_cell and STATUS not in('DONE','CANCELLED');

   if v_count>0 then raise_application_error(-20890,'CLOSURE_CHANGED: source pallet physical task planned');end if;

   v_rid:=x.get_number('id');

   select * into sr from RRL_STOCK_RESERVATION where RESERVATION_ID=v_rid for update;

   v_old_qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));

   if sr.RESERVATION_VERSION!=x.get_number('version') or sr.BASE_QTY!=v_old_qty

    or sr.UID_PALLET!=x.get_string('uid') or sr.CELL!=x.get_string('cell')

    or sr.SOURCE_DOC_TYPE!='PICK_WAVE' or sr.SOURCE_DOC_ID!=rt.PICK_WAVE_ID or sr.SOURCE_LINE_ID!=rt.PICK_TASK_ID

    or sr.CUSTOMER_ORDER_ID!=v_details.get_number('customer_order_id')

    or sr.RESERVATION_DOMAIN!='PICKING' or sr.RESERVATION_KIND!='HARD'

    or sr.STATUS not in('ACTIVE','ALLOCATED','PICKING') then raise_application_error(-20890,'CLOSURE_CHANGED: target supply owner');end if;

   select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=rt.ARTICUL

    and INPUT_UOM=sr.BASE_UOM and BASE_UOM=sr.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;

   v_release_qty:=release_amount(x.get_string('release_quantity'));

   if v_release_qty>0 then RRL_STOCK_UNIT_CORE.release_units(v_rid,v_release_qty,null,0);

   RRL_STOCK_RESERVE_CORE.release_hard(v_rid,v_release_qty,v_version,'PICK_WAVE',rt.PICK_WAVE_ID,p_actor);end if;

  end loop;

  for i in 0..b.get_size-1 loop

   x:=treat(b.get(i) as json_object_t);v_uid:=x.get_string('uid');v_cell:=x.get_string('cell');v_id:=x.get_number('id');

   v_qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));

   select STOCK_VERSION into v_stock from RRL_REMAINS where UID_POLETA=v_uid and CELL=v_cell;

   if v_stock!=x.get_number('stock_version') then raise_application_error(-20890,'CLOSURE_CHANGED: target supply stock');end if;

   RRL_STOCK_ELIGIBILITY.assert_source(v_uid,v_cell,p_ware,v_qty,rt.MIN_SHELF_LIFE_DAYS,rt.MIN_SHELF_LIFE_PERCENT,'ALLOCATE',null,rt.ARTICUL);

   v_units:=RRL_WEIGHT_CHOICE_UNIT_READ.selected_units(rt.PICK_TASK_ID,v_uid,v_cell,v_qty);

   if v_units is null then v_units:=RRL_STOCK_UNIT_CORE.automatic_units(v_uid,v_cell,v_qty);end if;

   RRL_STOCK_RESERVE_CORE.create_hard(v_id,v_uid,v_cell,v_qty,x.get_string('base_uom'),x.get_number('uom_version'),

    'PICK_WAVE',rt.PICK_WAVE_ID,rt.PICK_TASK_ID,'PICKING',p_actor,v_details.to_clob);

   RRL_STOCK_UNIT_CORE.reserve_units(v_uid,v_cell,v_id,v_qty,v_units);

   if v_first is null then v_first:=v_uid;end if;

  end loop;

  if p_plan.has('continuation') then

   v_next:=p_plan.get_object('continuation');v_uid:=v_next.get_string('uid');v_cell:=v_next.get_string('cell');v_id:=v_next.get_number('id');

   v_qty:=RRL_STOCK_MATH.quantity(v_next.get_string('quantity'));

   v_remaining_owner:=RRL_STOCK_MATH.quantity(v_next.get_string('remaining_owner_quantity'));

   select BASE_QTY,RESERVATION_VERSION into v_old_qty,v_source_res_ver from RRL_STOCK_RESERVATION where RESERVATION_ID=v_id;

   select REMAIN,STOCK_VERSION into v_source_p,v_source_ver from RRL_REMAINS where UID_POLETA=v_uid and CELL=v_cell;

   if v_old_qty!=v_remaining_owner or v_source_res_ver!=v_next.get_number('reservation_version')

    or v_source_p!=v_qty or v_source_ver!=v_next.get_number('stock_version') then raise_application_error(-20890,'CLOSURE_CHANGED: partial target source binding');end if;

   update RRL_PICK_TASK set PALLET_UID=v_uid,SOURCE_CELL_CODE=v_cell where PICK_TASK_ID=rt.PICK_TASK_ID;

   update RRL_PICK_WAVE_TASK set PALLET_UID=v_uid,SOURCE_CELL_CODE=v_cell where PICK_WAVE_ID=rt.PICK_WAVE_ID and PICK_TASK_ID=rt.PICK_TASK_ID;

   update RRL_PICK_WAVE_REPLENISH_TASK set STATUS='RELEASED',SOURCE_RESERVATION_ID=v_id,PALLET_UID=v_uid,SOURCE_CELL_CODE=v_cell,

    DEMAND_BASE_QTY=v_remaining_owner,QTY=v_qty,SOURCE_AVAILABLE_QTY=v_qty,REPLENISHMENT_QTY_MODE='FULL_PALLET',

    WAIT_REASON='Existing target HARD plus remaining own whole-pallet source; physical receipt still required',

    UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_WAVE_REPLENISH_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID;

  else

  update RRL_PICK_TASK set PALLET_UID=v_first,SOURCE_CELL_CODE=rt.TARGET_CELL_CODE where PICK_TASK_ID=rt.PICK_TASK_ID;

  update RRL_PICK_WAVE_TASK set PALLET_UID=v_first,SOURCE_CELL_CODE=rt.TARGET_CELL_CODE where PICK_WAVE_ID=rt.PICK_WAVE_ID and PICK_TASK_ID=rt.PICK_TASK_ID;

  update RRL_PICK_WAVE_REPLENISH_TASK set STATUS='CANCELLED',DEMAND_BASE_QTY=0,WAIT_REASON='Atomic multi-UID target HARD replacement; no physical replenishment',

   UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_WAVE_REPLENISH_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID;

  end if;

 end;

 procedure compile_reserve(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is

  d json_object_t:=json_object_t.parse(p_request);v_wave number;v_ware number;v_id number;v_qty number;v_version number;

  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t:=json_array_t();v json_object_t:=json_object_t();x json_object_t;

  v_uid varchar2(200);v_cell varchar2(60);v_uom varchar2(20);v_free number;v_own_id number;v_own_qty number;v_capacity number;v_wanted number;v_is_short number;v_needed number;v_num number;v_den number;v_scale number;

  v_target_supply json_object_t;v_target_decision json_object_t;v_target_used json_object_t:=json_object_t();v_target_changes json_object_t:=json_object_t();v_target_picks json_object_t:=json_object_t();v_pick_key varchar2(80);v_rebind number:=0;v_requested clob;v_requested_array json_array_t;v_mode varchar2(40);v_kind varchar2(40);

  type quantities is table of number index by varchar2(2000);used quantities;k varchar2(2000);

 begin

  if d.get_object('metadata').get_boolean('allow_unissued_source_rebind') then v_rebind:=1;end if;

  if d.get_object('metadata').has('requested_row_ids') then

   v_requested_array:=d.get_object('metadata').get_array('requested_row_ids');

   if v_requested_array is null or v_requested_array.get_size<1 or v_requested_array.get_size>200 then raise_application_error(-20881,'WAVE_REQUESTED_ROWS_BOUND');end if;

   v_requested:=v_requested_array.to_clob;

  end if;

  v_wave:=d.get_object('source').get_number('wave_id');select WARE_ID,WAVE_KIND into v_ware,v_kind from RRL_PICK_WAVE where PICK_WAVE_ID=v_wave;

  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');

  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);

  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));

  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(v_wave));

  for rt in(select * from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=v_wave

   and STATUS in('RELEASED','QUEUED','WAIT_FREE_CELL','WAIT_MINIMAX') and(SOURCE_RESERVATION_ID is null or v_rebind=1)

   and (v_requested is null or PICK_WAVE_REPLENISH_TASK_ID in(select id from json_table(v_requested,'$[*]' columns(id number path '$' error on error))))

   order by PICK_WAVE_REPLENISH_TASK_ID) loop

   if a.get_size>=200 then raise_application_error(-20881,'WAVE_RESERVATION_BATCH_BOUND');end if;

   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_REPLENISH_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(rt.PICK_WAVE_REPLENISH_TASK_ID));

   RRL_STOCK_PLAN_HELPER.fence(f,'SKU',rt.ARTICUL);

   if rt.PICK_TASK_ID is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(rt.PICK_TASK_ID));end if;

   v_uid:=null;v_qty:=null;v_cell:=null;v_uom:=null;v_version:=null;

   v_own_id:=null;v_own_qty:=null;

   RRL_STOCK_PLAN_HELPER.fence(f,'CELL',rt.TARGET_CELL_CODE,6);

   v_capacity:=RRL_STOCK_REPL_CAPACITY.remaining_base_quantity(rt.TARGET_CELL_CODE,rt.ARTICUL,rt.PICK_WAVE_REPLENISH_TASK_ID);

   select count(*) into v_is_short from RRL_CASE_PICK_SHORT where REPLENISH_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID and RECOVERY_STATE='WAIT_REPLENISHMENT';

   v_mode:=RRL_STOCK_REPL_ADMISSION.mode_for(rt.PICK_WAVE_REPLENISH_TASK_ID);

   v_wanted:=case when v_mode='FILL_TO_VOLUME' and v_is_short=0 and nvl(v_kind,'CUSTOMER_ORDER')!='REPLENISHMENT' and v_capacity is not null then v_capacity

    when v_capacity is not null and v_mode!='FULL_PALLET' then least(rt.QTY,v_capacity) else rt.QTY end;

   v_needed:=null;

   if rt.PICK_TASK_ID is not null then

    v_needed:=RRL_STOCK_REPL_NEED.remaining_for_task(rt.PICK_TASK_ID,rt.TARGET_CELL_CODE);

    if v_needed<=0 then v_wanted:=0;end if;

   end if;

   v_pick_key:=RRL_STOCK_PLAN_HELPER.decimal_text(rt.PICK_TASK_ID);

   if v_pick_key is not null and v_target_picks.has(v_pick_key) then continue;end if;

   compile_target_supply(rt,v_needed,v_ware,v_mode,v_capacity,f,r,v_target_used,v_target_changes,v_target_decision,v_target_supply);

   if v_target_supply is not null then v_target_picks.put(v_pick_key,1);end if;

   if rt.SOURCE_RESERVATION_ID is not null and v_target_supply is null then continue;end if;

   if v_wanted>0 and v_target_supply is null then

   for own in(select sr.RESERVATION_ID,sr.BASE_QTY,sr.UID_PALLET,sr.CELL,sr.BASE_UOM,rr.REMAIN

    from RRL_STOCK_RESERVATION sr join RRL_REMAINS rr on rr.UID_POLETA=sr.UID_PALLET and rr.CELL=sr.CELL

    join RRL_CELLS cc on cc.CELL=sr.CELL

    where sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.SOURCE_DOC_ID=v_wave and sr.SOURCE_LINE_ID=rt.PICK_TASK_ID

     and sr.RESERVATION_DOMAIN='PICKING' and sr.RESERVATION_KIND='HARD' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING') and sr.CELL!=rt.TARGET_CELL_CODE

     and sr.BASE_QTY>0 and cc.WARE_ID=v_ware

     and (v_mode!='FULL_PALLET' or RRL_STOCK_REPL_SHARED.allowed(sr.UID_PALLET,sr.CELL,rt.TARGET_CELL_CODE,v_ware,sr.RESERVATION_ID)=1)

     and RRL_STOCK_REPL_ADMISSION.reason(sr.UID_PALLET,rt.TARGET_CELL_CODE,v_ware,rt.ARTICUL) is null

     and (v_mode!='FULL_PALLET' or v_capacity is null or rr.REMAIN<=v_capacity) and nvl(cc.BLOCKED_FOR_REMAINS,0)=0 and nvl(cc.BLOCKED_FOR_POPOLNENIE,0)=0

    and RRL_STOCK_ELIGIBILITY.reason(sr.UID_PALLET,sr.CELL,v_ware,least(v_wanted,sr.BASE_QTY),rt.MIN_SHELF_LIFE_DAYS,rt.MIN_SHELF_LIFE_PERCENT,'REPLENISH',sr.RESERVATION_ID,rt.ARTICUL) is null

    order by sr.RESERVATION_ID) loop

    v_own_id:=own.RESERVATION_ID;v_own_qty:=own.BASE_QTY;v_uid:=own.UID_PALLET;v_cell:=own.CELL;v_uom:=own.BASE_UOM;

    v_qty:=case when v_mode='FULL_PALLET' then own.REMAIN else least(v_wanted,own.BASE_QTY) end;

    select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=rt.ARTICUL and INPUT_UOM=v_uom and BASE_UOM=v_uom and NUMERATOR=1 and DENOMINATOR=1;

    if v_version is null then raise_application_error(-20868,'WAVE_BASE_POLICY_REQUIRED');end if;

    exit;

   end loop;

   if v_own_id is null then

   for c in(select rr.UID_POLETA,rr.CELL,rr.REMAIN,rr.HARD_RESERVED_BASE,rr.BASE_UOM,pp.EXPIRY_DATE,pp.PRODUCED_DATE

    from RRL_REMAINS rr join RRL_PALLETS pp on pp.UID_PALLET=rr.UID_POLETA join RRL_CELLS cc on cc.CELL=rr.CELL

    where pp.ARTICUL=rt.ARTICUL and rr.REMAIN>rr.HARD_RESERVED_BASE and cc.WARE_ID=v_ware

     and RRL_STOCK_REPL_ADMISSION.reason(rr.UID_POLETA,rt.TARGET_CELL_CODE,v_ware,rt.ARTICUL) is null

     and rr.CELL!=rt.TARGET_CELL_CODE and nvl(cc.BLOCKED_FOR_REMAINS,0)=0 and nvl(cc.BLOCKED_FOR_POPOLNENIE,0)=0

     and (rt.MIN_SHELF_LIFE_DAYS is null or trunc(pp.EXPIRY_DATE)-trunc(sysdate)>=rt.MIN_SHELF_LIFE_DAYS)

     and (rt.MIN_SHELF_LIFE_PERCENT is null or (pp.PRODUCED_DATE is not null and pp.EXPIRY_DATE>pp.PRODUCED_DATE

      and (trunc(pp.EXPIRY_DATE)-trunc(sysdate))*100 >= rt.MIN_SHELF_LIFE_PERCENT*(trunc(pp.EXPIRY_DATE)-trunc(pp.PRODUCED_DATE))))

     and RRL_STOCK_ELIGIBILITY.reason(rr.UID_POLETA,rr.CELL,v_ware,least(v_wanted,rr.REMAIN-rr.HARD_RESERVED_BASE),rt.MIN_SHELF_LIFE_DAYS,rt.MIN_SHELF_LIFE_PERCENT,'REPLENISH',null,rt.ARTICUL) is null

    order by pp.EXPIRY_DATE nulls last,pp.PRODUCED_DATE nulls last,rr.CELL,rr.UID_POLETA

   ) loop

    k:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',c.UID_POLETA,c.CELL));if not used.exists(k) then used(k):=0;end if;

    v_free:=c.REMAIN-c.HARD_RESERVED_BASE-used(k);

    if v_free>0 and (v_mode!='FULL_PALLET' or (c.HARD_RESERVED_BASE+used(k)=0 and (v_capacity is null or c.REMAIN<=v_capacity))) then

     v_uid:=c.UID_POLETA;v_cell:=c.CELL;v_uom:=c.BASE_UOM;

     v_qty:=case when v_mode='FULL_PALLET' then c.REMAIN else least(v_wanted,v_free) end;

     select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=rt.ARTICUL and INPUT_UOM=v_uom and BASE_UOM=v_uom and NUMERATOR=1 and DENOMINATOR=1;

     if v_version is null then raise_application_error(-20868,'WAVE_BASE_POLICY_REQUIRED');end if;

     used(k):=used(k)+v_qty;exit;

    end if;

   end loop;

   end if;

   end if;

   x:=json_object_t();x.put('needed_base',case when v_needed is not null then RRL_STOCK_PLAN_HELPER.decimal_text(v_needed) end);x.put('already_covered',case when v_needed=0 then 1 else 0 end);x.put('resolved_mode',v_mode);x.put('policy_signature',RRL_STOCK_REPL_ADMISSION.policy_signature(rt.PICK_WAVE_REPLENISH_TASK_ID));x.put('capacity_wait',case when v_capacity is not null and v_capacity=0 then 1 else 0 end);x.put('own_reservation_id',v_own_id);x.put('own_qty',case when v_own_qty is not null then RRL_STOCK_PLAN_HELPER.decimal_text(v_own_qty) end);x.put('source_reservation_before',rt.SOURCE_RESERVATION_ID);x.put('task_id',rt.PICK_WAVE_REPLENISH_TASK_ID);x.put('signature',signature(rt));x.put('uid',v_uid);

   if v_target_decision is not null then x.put('target_supply_decision',v_target_decision);end if;

   if v_target_supply is not null then x.put('target_supply',v_target_supply);end if;

   if v_uid is not null then

    if v_own_id is null then select RRL_STOCK_RESERVATION_SQ.nextval into v_id from dual;else v_id:=v_own_id;end if;

    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(v_id));

    RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v_uid,rt.ARTICUL,v_cell,null);

    x.put('reservation_id',v_id);x.put('cell',v_cell);x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));x.put('base_uom',v_uom);x.put('uom_version',v_version);

   end if;

   a.append(x);

  end loop;

  v.put('wave_id',v_wave);v.put('warehouse',v_ware);v.put('tasks',a);p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;

 end;

 procedure execute_reserve(p_request clob,p_actor varchar2,p_result out clob) is

  d json_object_t:=json_object_t.parse(p_request);v json_object_t;x json_object_t;j json_object_t:=json_object_t();

  a json_array_t;v_plan clob;v_status varchar2(40);rt RRL_PICK_WAVE_REPLENISH_TASK%rowtype;

  v_qty number;v_id number;v_units clob;v_count number:=0;v_details json_object_t;v_produced date;v_expiry date;own RRL_STOCK_RESERVATION%rowtype;

 v_recovery_count number;v_mode varchar2(40);v_needed number;

 begin

  if RRL_HAS_WRIGHT(p_actor,'pick_wave_launch')!=1 and RRL_HAS_WRIGHT(p_actor,'pick_wave_release_reserves')!=1 then raise_application_error(-20882,'WAVE_RESERVATION_FORBIDDEN');end if;

  declare

 v_json_sql_1_1 varchar2(32767):=d.get_string('operation_id');

begin

select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=v_json_sql_1_1;

end;

  v:=json_object_t.parse(v_plan).get_object('domain');a:=v.get_array('tasks');

  declare

 v_json_sql_2_1 number:=v.get_number('wave_id');

begin

select STATUS into v_status from RRL_PICK_WAVE where PICK_WAVE_ID=v_json_sql_2_1 for update;

end;

  if v_status in('CANCELLED','DONE','COMPLETED','CLOSED') then raise_application_error(-20886,'WAVE_NOT_OPEN');end if;

  for i in 0..a.get_size-1 loop

   x:=treat(a.get(i) as json_object_t);

   declare

 v_json_sql_3_1 number:=x.get_number('task_id');

begin

select * into rt from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=v_json_sql_3_1 for update;

end;

   if RRL_STOCK_REPL_ADMISSION.policy_signature(rt.PICK_WAVE_REPLENISH_TASK_ID)!=x.get_string('policy_signature') then raise_application_error(-20890,'CLOSURE_CHANGED: replenishment policy');end if;

   v_mode:=x.get_string('resolved_mode');

   if nvl(rt.SOURCE_RESERVATION_ID,-1)!=nvl(x.get_number('source_reservation_before'),-1) or signature(rt)!=x.get_string('signature') or rt.STATUS not in('RELEASED','QUEUED','WAIT_FREE_CELL','WAIT_MINIMAX') then raise_application_error(-20890,'CLOSURE_CHANGED: replenishment row');end if;

   v_needed:=null;

   if rt.PICK_TASK_ID is not null then

    v_needed:=RRL_STOCK_REPL_NEED.remaining_for_task(rt.PICK_TASK_ID,rt.TARGET_CELL_CODE);

    if RRL_STOCK_PLAN_HELPER.decimal_text(v_needed)!=x.get_string('needed_base') then raise_application_error(-20890,'CLOSURE_CHANGED: explicit picking target need');end if;

    update RRL_PICK_WAVE_REPLENISH_TASK set DEMAND_BASE_QTY=v_needed where PICK_WAVE_REPLENISH_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID;

   end if;

   if x.has('target_supply') then

    execute_target_supply(rt,x.get_object('target_supply'),v.get_number('warehouse'),p_actor);v_count:=v_count+1;

   elsif x.get_number('already_covered')=1 then

    update RRL_PICK_WAVE_REPLENISH_TASK set STATUS='CANCELLED',WAIT_REASON='Existing usable own target coverage satisfies this CASE task',

     UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_WAVE_REPLENISH_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID;

   elsif x.get('uid').is_null then

    declare

 v_json_sql_1_1 number:=x.get_number('capacity_wait');

 v_json_sql_1_2 number:=x.get_number('capacity_wait');

begin

update RRL_PICK_WAVE_REPLENISH_TASK set STATUS=case when v_json_sql_1_1=1 then 'WAIT_FREE_CELL' else 'FAILED' end,WAIT_REASON=case when v_json_sql_1_2=1 then 'Waiting for canonical pick-face capacity including open arrivals' else 'No eligible source stock' end,UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_WAVE_REPLENISH_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID;

end;

   else

    v_qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));v_id:=x.get_number('reservation_id');

    RRL_STOCK_REPL_CAPACITY.assert_arrival(rt.PICK_WAVE_REPLENISH_TASK_ID,v_qty);

    RRL_STOCK_REPL_ADMISSION.assert_target(x.get_string('uid'),rt.TARGET_CELL_CODE,v.get_number('warehouse'),rt.ARTICUL);

    if rt.PICK_TASK_ID is not null then

     select count(*) into v_recovery_count from RRL_PICK_TASK pt join RRL_PICK_WAVE_TASK wt on wt.PICK_TASK_ID=pt.PICK_TASK_ID

      where pt.PICK_TASK_ID=rt.PICK_TASK_ID and wt.PICK_WAVE_ID=rt.PICK_WAVE_ID and pt.ARTICUL=rt.ARTICUL and pt.STATUS not in('DONE','CANCELLED','FAILED');

     if v_recovery_count=0 then raise_application_error(-20887,'REPLENISHMENT_PICK_DEMAND_IDENTITY_CONFLICT');end if;

    end if;

    RRL_STOCK_ELIGIBILITY.assert_source(x.get_string('uid'),x.get_string('cell'),v.get_number('warehouse'),case when x.get_number('own_reservation_id') is not null then least(v_qty,RRL_STOCK_MATH.quantity(x.get_string('own_qty'))) else v_qty end,

     rt.MIN_SHELF_LIFE_DAYS,rt.MIN_SHELF_LIFE_PERCENT,'REPLENISH',x.get_number('own_reservation_id'),rt.ARTICUL);

    if x.get('own_reservation_id').is_null then

    v_units:=RRL_WEIGHT_CHOICE_UNIT_READ.selected_units(rt.PICK_TASK_ID,x.get_string('uid'),x.get_string('cell'),v_qty);

    if v_units is null then v_units:=RRL_STOCK_UNIT_CORE.automatic_units(x.get_string('uid'),x.get_string('cell'),v_qty);end if;

    v_details:=json_object_t();v_details.put('pick_wave_id',v.get_number('wave_id'));

    v_details.put('reservation_scope',case when v_mode='FULL_PALLET' then 'PALLET' else 'QTY' end);

    if rt.PICK_TASK_ID is not null then

     for pt in(select CUSTOMER_ID,CUSTOMER_ORDER_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID from RRL_PICK_TASK where PICK_TASK_ID=rt.PICK_TASK_ID) loop

      v_details.put('customer_id',pt.CUSTOMER_ID);v_details.put('customer_order_id',pt.CUSTOMER_ORDER_ID);

      v_details.put('pick_plan_id',pt.PICK_PLAN_ID);v_details.put('pick_plan_line_id',pt.PICK_PLAN_LINE_ID);

     end loop;

    end if;

    select count(*) into v_recovery_count from RRL_CASE_PICK_SHORT sh where sh.REPLENISH_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID and sh.RECOVERY_STATE='WAIT_REPLENISHMENT';

    RRL_STOCK_RESERVE_CORE.create_hard(v_id,x.get_string('uid'),x.get_string('cell'),v_qty,x.get_string('base_uom'),x.get_number('uom_version'),

     'PICK_WAVE',v.get_number('wave_id'),

     case when rt.PICK_TASK_ID is not null then rt.PICK_TASK_ID else rt.PICK_WAVE_REPLENISH_TASK_ID end,

     case when rt.PICK_TASK_ID is not null then 'PICKING' else 'WAVE' end,p_actor,v_details.to_clob);

    RRL_STOCK_UNIT_CORE.reserve_units(x.get_string('uid'),x.get_string('cell'),v_id,v_qty,v_units);

    else

     select * into own from RRL_STOCK_RESERVATION where RESERVATION_ID=v_id for update;

     if own.SOURCE_DOC_TYPE!='PICK_WAVE' or own.SOURCE_DOC_ID!=v.get_number('wave_id') or own.SOURCE_LINE_ID!=rt.PICK_TASK_ID

      or own.RESERVATION_DOMAIN!='PICKING' or own.RESERVATION_KIND!='HARD' or own.STATUS not in('ACTIVE','ALLOCATED','PICKING')

      or own.UID_PALLET!=x.get_string('uid') or own.CELL!=x.get_string('cell') or RRL_STOCK_PLAN_HELPER.decimal_text(own.BASE_QTY)!=x.get_string('own_qty') then

      raise_application_error(-20890,'CLOSURE_CHANGED: own picking reserve');end if;

    end if;

    declare

 v_json_sql_4_1 varchar2(32767):=x.get_string('uid');

begin

select PRODUCED_DATE,EXPIRY_DATE into v_produced,v_expiry from RRL_PALLETS where UID_PALLET=v_json_sql_4_1;

end;

    declare

 v_json_sql_5_1 varchar2(32767):=x.get_string('uid');

 v_json_sql_5_2 varchar2(32767):=x.get_string('cell');

begin

update RRL_PICK_WAVE_REPLENISH_TASK set SOURCE_RESERVATION_ID=v_id,PALLET_UID=v_json_sql_5_1,SOURCE_CELL_CODE=v_json_sql_5_2,

     REPLENISHMENT_QTY_MODE=v_mode,DEMAND_BASE_QTY=case when v_needed is not null then v_needed else nvl(DEMAND_BASE_QTY,QTY) end,SOURCE_AVAILABLE_QTY=v_qty,SOURCE_PRODUCED_DATE=v_produced,SOURCE_EXPIRY_DATE=v_expiry,QTY=v_qty,WAIT_REASON=null,UPDATED_AT=sysdate,UPDATED_BY=p_actor

     where PICK_WAVE_REPLENISH_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID;

end;

    v_count:=v_count+1;

   end if;

  end loop;

  j.put('operation_id',d.get_string('operation_id'));j.put('wave_id',v.get_number('wave_id'));j.put('reserved_count',v_count);p_result:=j.to_clob;

 end;

end;
/
