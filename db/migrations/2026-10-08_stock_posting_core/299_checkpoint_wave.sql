create or replace package RRL_STOCK_WAVE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_reserve(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_reserve(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_STOCK_WAVE_CMD as
 function signature(p_row RRL_PICK_WAVE_REPLENISH_TASK%rowtype) return varchar2 is v json_object_t:=json_object_t();
 begin
  v.put('id',p_row.PICK_WAVE_REPLENISH_TASK_ID);v.put('wave',p_row.PICK_WAVE_ID);v.put('article',p_row.ARTICUL);
  v.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(p_row.QTY));v.put('target',p_row.TARGET_CELL_CODE);
  v.put('demand',p_row.DEMAND_BASE_QTY);v.put('pick_task',p_row.PICK_TASK_ID);v.put('scope',p_row.REPLENISHMENT_QTY_MODE);v.put('shelf_days',p_row.MIN_SHELF_LIFE_DAYS);v.put('shelf_percent',p_row.MIN_SHELF_LIFE_PERCENT);
  return rawtohex(sys.dbms_crypto.hash(v.to_clob,sys.dbms_crypto.hash_sh256));
 end;
 procedure compile_reserve(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);v_wave number;v_ware number;v_id number;v_qty number;v_version number;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t:=json_array_t();v json_object_t:=json_object_t();x json_object_t;
  v_uid varchar2(200);v_cell varchar2(60);v_uom varchar2(20);v_free number;v_own_id number;v_own_qty number;v_capacity number;v_wanted number;v_is_short number;v_needed number;v_num number;v_den number;v_scale number;
  v_requested clob;v_requested_array json_array_t;v_mode varchar2(40);v_kind varchar2(40);
  type quantities is table of number index by varchar2(2000);used quantities;k varchar2(2000);
 begin
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
   and STATUS in('RELEASED','QUEUED','WAIT_FREE_CELL','WAIT_MINIMAX') and SOURCE_RESERVATION_ID is null
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
   if v_wanted>0 then
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
   x:=json_object_t();x.put('needed_base',case when v_needed is not null then RRL_STOCK_PLAN_HELPER.decimal_text(v_needed) end);x.put('already_covered',case when v_needed=0 then 1 else 0 end);x.put('resolved_mode',v_mode);x.put('policy_signature',RRL_STOCK_REPL_ADMISSION.policy_signature(rt.PICK_WAVE_REPLENISH_TASK_ID));x.put('capacity_wait',case when v_capacity is not null and v_capacity=0 then 1 else 0 end);x.put('own_reservation_id',v_own_id);x.put('own_qty',case when v_own_qty is not null then RRL_STOCK_PLAN_HELPER.decimal_text(v_own_qty) end);x.put('task_id',rt.PICK_WAVE_REPLENISH_TASK_ID);x.put('signature',signature(rt));x.put('uid',v_uid);
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
   if rt.SOURCE_RESERVATION_ID is not null or signature(rt)!=x.get_string('signature') or rt.STATUS not in('RELEASED','QUEUED','WAIT_FREE_CELL','WAIT_MINIMAX') then raise_application_error(-20890,'CLOSURE_CHANGED: replenishment row');end if;
   v_needed:=null;
   if rt.PICK_TASK_ID is not null then
    v_needed:=RRL_STOCK_REPL_NEED.remaining_for_task(rt.PICK_TASK_ID,rt.TARGET_CELL_CODE);
    if RRL_STOCK_PLAN_HELPER.decimal_text(v_needed)!=x.get_string('needed_base') then raise_application_error(-20890,'CLOSURE_CHANGED: explicit picking target need');end if;
    update RRL_PICK_WAVE_REPLENISH_TASK set DEMAND_BASE_QTY=v_needed where PICK_WAVE_REPLENISH_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID;
   end if;
   if x.get_number('already_covered')=1 then
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
    v_units:=RRL_STOCK_UNIT_CORE.automatic_units(x.get_string('uid'),x.get_string('cell'),v_qty);
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
