declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_WAVE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_reserve(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_reserve(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_TRANSFER_CORE authid definer
 accessible by(package RRL_STOCK_INTERNAL_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE,
 package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_MOVE_CORE,package RRL_STOCK_MES_CORE) as
 procedure move(p_uid varchar2,p_target_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,
  p_uom varchar2,p_uom_version number,p_warehouse number,p_actor varchar2,p_line number,
  p_reservation number default null,p_units clob default null,p_new_reservation number default null,p_target_slot number default null,p_source_warehouse number default null,p_location_mode varchar2 default 'ORDINARY');
end;
/

create or replace package body RRL_STOCK_WAVE_CMD as
 function signature(p_row RRL_PICK_WAVE_REPLENISH_TASK%rowtype) return varchar2 is v json_object_t:=json_object_t();
 begin
  v.put('id',p_row.PICK_WAVE_REPLENISH_TASK_ID);v.put('wave',p_row.PICK_WAVE_ID);v.put('article',p_row.ARTICUL);
  v.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(p_row.QTY));v.put('target',p_row.TARGET_CELL_CODE);
  v.put('scope',p_row.REPLENISHMENT_QTY_MODE);v.put('shelf_days',p_row.MIN_SHELF_LIFE_DAYS);v.put('shelf_percent',p_row.MIN_SHELF_LIFE_PERCENT);
  return rawtohex(sys.dbms_crypto.hash(v.to_clob,sys.dbms_crypto.hash_sh256));
 end;
 procedure compile_reserve(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);v_wave number;v_ware number;v_id number;v_qty number;v_version number;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t:=json_array_t();v json_object_t:=json_object_t();x json_object_t;
  v_uid varchar2(200);v_cell varchar2(60);v_uom varchar2(20);v_free number;v_num number;v_den number;v_scale number;
  type quantities is table of number index by varchar2(2000);used quantities;k varchar2(2000);
 begin
  v_wave:=d.get_object('source').get_number('wave_id');select WARE_ID into v_ware from RRL_PICK_WAVE where PICK_WAVE_ID=v_wave;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(v_wave));
  for rt in(select * from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=v_wave
   and STATUS in('RELEASED','QUEUED','WAIT_FREE_CELL','WAIT_MINIMAX') and SOURCE_RESERVATION_ID is null order by PICK_WAVE_REPLENISH_TASK_ID) loop
   if a.get_size>=200 then raise_application_error(-20881,'WAVE_RESERVATION_BATCH_BOUND');end if;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_REPLENISH_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(rt.PICK_WAVE_REPLENISH_TASK_ID));
   RRL_STOCK_PLAN_HELPER.fence(f,'SKU',rt.ARTICUL);
   v_uid:=null;v_qty:=null;v_cell:=null;v_uom:=null;v_version:=null;
   for c in(select rr.UID_POLETA,rr.CELL,rr.REMAIN,rr.HARD_RESERVED_BASE,rr.BASE_UOM,pp.EXPIRY_DATE,pp.PRODUCED_DATE
    from RRL_REMAINS rr join RRL_PALLETS pp on pp.UID_PALLET=rr.UID_POLETA join RRL_CELLS cc on cc.CELL=rr.CELL
    where pp.ARTICUL=rt.ARTICUL and rr.REMAIN>rr.HARD_RESERVED_BASE and cc.WARE_ID=v_ware
     and rr.CELL!=rt.TARGET_CELL_CODE and nvl(cc.BLOCKED_FOR_REMAINS,0)=0 and nvl(cc.BLOCKED_FOR_POPOLNENIE,0)=0
     and (rt.MIN_SHELF_LIFE_DAYS is null or trunc(pp.EXPIRY_DATE)-trunc(sysdate)>=rt.MIN_SHELF_LIFE_DAYS)
     and (rt.MIN_SHELF_LIFE_PERCENT is null or (pp.PRODUCED_DATE is not null and pp.EXPIRY_DATE>pp.PRODUCED_DATE
      and (trunc(pp.EXPIRY_DATE)-trunc(sysdate))*100 >= rt.MIN_SHELF_LIFE_PERCENT*(trunc(pp.EXPIRY_DATE)-trunc(pp.PRODUCED_DATE))))
    order by pp.EXPIRY_DATE nulls last,pp.PRODUCED_DATE nulls last,rr.CELL,rr.UID_POLETA
   ) loop
    k:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',c.UID_POLETA,c.CELL));if not used.exists(k) then used(k):=0;end if;
    v_free:=c.REMAIN-c.HARD_RESERVED_BASE-used(k);
    if v_free>=rt.QTY and (nvl(rt.REPLENISHMENT_QTY_MODE,'PARTIAL')!='FULL_PALLET' or c.HARD_RESERVED_BASE+used(k)=0) then
     v_uid:=c.UID_POLETA;v_cell:=c.CELL;v_uom:=c.BASE_UOM;
     v_qty:=case when rt.REPLENISHMENT_QTY_MODE='FULL_PALLET' then c.REMAIN else rt.QTY end;
     select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=rt.ARTICUL and INPUT_UOM=v_uom and BASE_UOM=v_uom and NUMERATOR=1 and DENOMINATOR=1;
     if v_version is null then raise_application_error(-20868,'WAVE_BASE_POLICY_REQUIRED');end if;
     used(k):=used(k)+v_qty;exit;
    end if;
   end loop;
   x:=json_object_t();x.put('task_id',rt.PICK_WAVE_REPLENISH_TASK_ID);x.put('signature',signature(rt));x.put('uid',v_uid);
   if v_uid is not null then
    select RRL_STOCK_RESERVATION_SQ.nextval into v_id from dual;
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
  v_qty number;v_id number;v_units clob;v_count number:=0;v_details json_object_t;v_produced date;v_expiry date;
 begin
  if RRL_HAS_WRIGHT(p_actor,'pick_wave_launch')!=1 and RRL_HAS_WRIGHT(p_actor,'pick_wave_release_reserves')!=1 then raise_application_error(-20882,'WAVE_RESERVATION_FORBIDDEN');end if;
  select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=d.get_string('operation_id');
  v:=json_object_t.parse(v_plan).get_object('domain');a:=v.get_array('tasks');
  select STATUS into v_status from RRL_PICK_WAVE where PICK_WAVE_ID=v.get_number('wave_id') for update;
  if v_status in('CANCELLED','COMPLETED','CLOSED') then raise_application_error(-20886,'WAVE_NOT_OPEN');end if;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   select * into rt from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=x.get_number('task_id') for update;
   if rt.SOURCE_RESERVATION_ID is not null or signature(rt)!=x.get_string('signature') or rt.STATUS not in('RELEASED','QUEUED','WAIT_FREE_CELL','WAIT_MINIMAX') then raise_application_error(-20890,'CLOSURE_CHANGED: replenishment row');end if;
   if x.get('uid').is_null then
    update RRL_PICK_WAVE_REPLENISH_TASK set STATUS='FAILED',WAIT_REASON='No eligible source stock',UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_WAVE_REPLENISH_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID;
   else
    v_qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));v_id:=x.get_number('reservation_id');
    v_units:=RRL_STOCK_UNIT_CORE.automatic_units(x.get_string('uid'),x.get_string('cell'),v_qty);
    v_details:=json_object_t();v_details.put('pick_wave_id',v.get_number('wave_id'));
    v_details.put('reservation_scope',case when rt.REPLENISHMENT_QTY_MODE='FULL_PALLET' then 'PALLET' else 'QTY' end);
    RRL_STOCK_RESERVE_CORE.create_hard(v_id,x.get_string('uid'),x.get_string('cell'),v_qty,x.get_string('base_uom'),x.get_number('uom_version'),
     'PICK_WAVE',v.get_number('wave_id'),rt.PICK_WAVE_REPLENISH_TASK_ID,'WAVE',p_actor,v_details.to_clob);
    RRL_STOCK_UNIT_CORE.reserve_units(x.get_string('uid'),x.get_string('cell'),v_id,v_qty,v_units);
    select PRODUCED_DATE,EXPIRY_DATE into v_produced,v_expiry from RRL_PALLETS where UID_PALLET=x.get_string('uid');
    update RRL_PICK_WAVE_REPLENISH_TASK set SOURCE_RESERVATION_ID=v_id,PALLET_UID=x.get_string('uid'),SOURCE_CELL_CODE=x.get_string('cell'),
     SOURCE_AVAILABLE_QTY=v_qty,SOURCE_PRODUCED_DATE=v_produced,SOURCE_EXPIRY_DATE=v_expiry,QTY=v_qty,WAIT_REASON=null,UPDATED_AT=sysdate,UPDATED_BY=p_actor
     where PICK_WAVE_REPLENISH_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID;
    v_count:=v_count+1;
   end if;
  end loop;
  j.put('operation_id',d.get_string('operation_id'));j.put('wave_id',v.get_number('wave_id'));j.put('reserved_count',v_count);p_result:=j.to_clob;
 end;
end;
/

create or replace package body RRL_STOCK_TRANSFER_CORE as
 procedure require_row(p_id number) is
 begin
  begin RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STOCK_RESERVATION',
   RRL_STOCK_PLAN_HELPER.decimal_text(p_id)));
  exception when others then
   if sqlcode=-20850 then raise_application_error(-20890,'CLOSURE_CHANGED: reservation set');else raise;end if;
  end;
 end;
 procedure move(p_uid varchar2,p_target_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,
  p_uom varchar2,p_uom_version number,p_warehouse number,p_actor varchar2,p_line number,
  p_reservation number default null,p_units clob default null,p_new_reservation number default null,p_target_slot number default null,p_source_warehouse number default null,p_location_mode varchar2 default 'ORDINARY') is
  v_p number;v_h number;v_ver number;v_uom varchar2(20);v_article varchar2(160);v_sum number;
  v_hmove number:=0;v_event number;v_units number;v_unit_qty number;v_selected number;v_expected number;
  v_r RRL_STOCK_RESERVATION%rowtype;v_result_reservation number;
 begin
  if p_uid is null or p_target_uid is null or p_from is null or p_to is null or p_from=p_to
   or p_qty is null or p_qty<=0 then raise_application_error(-20886,'TRANSFER_CONTRACT_INVALID');end if;
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',p_uid));
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',p_target_uid));
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_target_uid));
  if p_location_mode='PUTAWAY' then
   RRL_STOCK_LOCATION_CORE.assert_receiving(p_from,nvl(p_source_warehouse,p_warehouse));
   RRL_STOCK_LOCATION_CORE.assert_ordinary(p_to,p_warehouse,'TARGET');
  elsif p_location_mode='QUARANTINE' then
   if RRL_HAS_WRIGHT(p_actor,'QUARANTINE_MOVE')!=1 then raise_application_error(-20882,'QUARANTINE_MOVE_FORBIDDEN');end if;
   RRL_STOCK_LOCATION_CORE.assert_quarantine(p_from,nvl(p_source_warehouse,p_warehouse));
   RRL_STOCK_LOCATION_CORE.assert_quarantine(p_to,p_warehouse);
  elsif p_location_mode='ORDINARY' then
   RRL_STOCK_LOCATION_CORE.assert_ordinary(p_from,nvl(p_source_warehouse,p_warehouse),'SOURCE');
   RRL_STOCK_LOCATION_CORE.assert_ordinary(p_to,p_warehouse,'TARGET');
  else raise_application_error(-20878,'TRANSFER_LOCATION_MODE_INVALID');end if;
  select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION,BASE_UOM into v_p,v_h,v_ver,v_uom
   from RRL_REMAINS where UID_POLETA=p_uid and CELL=p_from;
  if v_uom is null or v_uom!=p_uom or p_qty>v_p then raise_application_error(-20868,'TRANSFER_STOCK_CONFLICT');end if;
  select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=p_uid;
  select count(*) into v_sum from RRL_STOCK_RESERVATION where UID_PALLET=p_uid and CELL=p_from and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING') and (BASE_QTY is null or BASE_QTY<=0 or BASE_UOM is null or BASE_UOM!=p_uom);
  if v_sum>0 then raise_application_error(-20869,'HARD_BASE_IDENTITY_CONFLICT');end if;
  select nvl(sum(BASE_QTY),0) into v_sum from RRL_STOCK_RESERVATION where UID_PALLET=p_uid
   and CELL=p_from and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING');
  if v_sum!=v_h then raise_application_error(-20869,'HARD_MATERIALIZATION_CONFLICT');end if;
  for r in(select RESERVATION_ID from RRL_STOCK_RESERVATION where UID_PALLET=p_uid and CELL=p_from
   and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING')) loop require_row(r.RESERVATION_ID);end loop;
  if p_qty=v_p and p_target_uid=p_uid then
   v_hmove:=v_h;
  elsif p_reservation is not null then
   require_row(p_reservation);
   select * into v_r from RRL_STOCK_RESERVATION where RESERVATION_ID=p_reservation;
   if v_r.UID_PALLET is null or v_r.UID_PALLET!=p_uid or v_r.CELL is null or v_r.CELL!=p_from
    or v_r.RESERVATION_KIND!='HARD' or v_r.STATUS not in('ACTIVE','ALLOCATED','PICKING')
    or v_r.BASE_QTY is null or v_r.BASE_QTY<p_qty then raise_application_error(-20869,'TRANSFER_RESERVATION_CONFLICT');end if;
   v_hmove:=p_qty;
  elsif p_qty>v_p-v_h then raise_application_error(-20869,'TRANSFER_UNRESERVED_INSUFFICIENT');end if;
  if p_target_uid!=p_uid then
   declare t RRL_PALLETS%rowtype;s RRL_PALLETS%rowtype;
   begin
    select * into s from RRL_PALLETS where UID_PALLET=p_uid;
    select * into t from RRL_PALLETS where UID_PALLET=p_target_uid;
    if t.ARTICUL!=s.ARTICUL or t.PRIHOD_NAKLAD_ID!=s.PRIHOD_NAKLAD_ID
     or (t.EXPIRY_DATE!=s.EXPIRY_DATE or (t.EXPIRY_DATE is null and s.EXPIRY_DATE is not null) or (t.EXPIRY_DATE is not null and s.EXPIRY_DATE is null)) or (t.PRODUCED_DATE!=s.PRODUCED_DATE or (t.PRODUCED_DATE is null and s.PRODUCED_DATE is not null) or (t.PRODUCED_DATE is not null and s.PRODUCED_DATE is null))
     or (t.PROD_BATCH_ID!=s.PROD_BATCH_ID or (t.PROD_BATCH_ID is null and s.PROD_BATCH_ID is not null) or (t.PROD_BATCH_ID is not null and s.PROD_BATCH_ID is null)) then raise_application_error(-20887,'TRANSFER_LOT_IDENTITY_CONFLICT');end if;
   end;
  end if;
  select count(*),nvl(sum(BASE_QTY),0) into v_units,v_unit_qty from RRL_WMS_RECEIPT_UNIT
   where CURRENT_UID=p_uid and CURRENT_CELL=p_from and STOCK_STATUS!='ISSUED';
  if v_units>0 then
   if p_target_uid!=p_uid then raise_application_error(-20888,'HU_REBIND_HANDLER_REQUIRED');end if;
   if v_unit_qty!=v_p then raise_application_error(-20884,'COMPOSITION_STOCK_CONFLICT');end if;
   if p_qty!=v_p and p_units is null then raise_application_error(-20884,'PARTIAL_UNIT_SELECTION_REQUIRED');end if;
   select count(*),nvl(sum(u.BASE_QTY),0) into v_selected,v_unit_qty from RRL_WMS_RECEIPT_UNIT u
    where u.CURRENT_UID=p_uid and u.CURRENT_CELL=p_from and u.STOCK_STATUS!='ISSUED' and
     (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
   if v_unit_qty!=p_qty then raise_application_error(-20884,'SELECTED_UNIT_QUANTITY_CONFLICT');end if;
   if p_units is not null then
    select count(distinct K) into v_expected from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'));
    if v_expected!=v_selected then raise_application_error(-20884,'SELECTED_UNIT_IDENTITY_CONFLICT');end if;
   end if;
   if p_qty!=v_p and p_reservation is not null then
    select nvl(sum(u.BASE_QTY),0) into v_unit_qty from RRL_WMS_RECEIPT_UNIT u
     where u.CURRENT_UID=p_uid and u.CURRENT_CELL=p_from and u.HARD_RESERVATION_ID=p_reservation and
      (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
    if v_unit_qty!=v_hmove then raise_application_error(-20869,'RESERVED_UNIT_SELECTION_CONFLICT');end if;
   end if;
   for u in(select PHYSICAL_UNIT_KEY,HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT
    where CURRENT_UID=p_uid and CURRENT_CELL=p_from and STOCK_STATUS!='ISSUED' and
     (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=PHYSICAL_UNIT_KEY))) loop
    begin RRL_STOCK_LOCK_API.assert_held(60,RRL_STOCK_LOCK_API.resource_key('UNIT',u.PHYSICAL_UNIT_KEY));
    exception when others then if sqlcode=-20850 then raise_application_error(-20890,'CLOSURE_CHANGED: unit set');else raise;end if;end;
    if u.HARD_RESERVATION_ID is not null and p_qty!=v_p and
      (p_reservation is null or u.HARD_RESERVATION_ID!=p_reservation) then raise_application_error(-20869,'UNIT_RESERVED_BY_OTHER_OWNER');end if;
   end loop;
  else
   select nvl(max(MARKING_REQUIRED),0) into v_expected from RRL_SKU_RECEIPT_POLICY where ARTICUL=v_article;
   if v_expected=1 then raise_application_error(-20884,'MARKED_BINDING_REQUIRED');end if;
  end if;
  RRL_STOCK_BALANCE_CORE.apply_delta(p_uid,p_from,-p_qty,-v_hmove,p_uom,p_uom_version,v_ver);
  RRL_STOCK_BALANCE_CORE.apply_delta(p_target_uid,p_to,p_qty,v_hmove,p_uom,p_uom_version);
  if p_qty=v_p then
   for c in(select TASK_ID from RRL_RECEIPT_SLOT_CLAIM where UID_PALLET=p_uid and CELL=p_from and STATUS='OCCUPIED') loop
    RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(c.TASK_ID)));
    delete from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=c.TASK_ID and STATUS='OCCUPIED';
   end loop;
  end if;
  if v_hmove>0 then
   for r in(select RESERVATION_ID,BASE_QTY from RRL_STOCK_RESERVATION
    where UID_PALLET=p_uid and CELL=p_from and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING')
     and (p_qty=v_p or RESERVATION_ID=p_reservation)) loop
    RRL_STOCK_RESERVE_CORE.move_coverage(r.RESERVATION_ID,p_new_reservation,p_target_uid,p_to,p_warehouse,
     case when p_qty=v_p then r.BASE_QTY else p_qty end,p_target_slot,p_actor,v_result_reservation);
    RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_from);
    update RRL_WMS_RECEIPT_UNIT set HARD_RESERVATION_ID=v_result_reservation,UNIT_VERSION=UNIT_VERSION+1
     where CURRENT_UID=p_uid and CURRENT_CELL=p_from and HARD_RESERVATION_ID=r.RESERVATION_ID and
      (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=PHYSICAL_UNIT_KEY));
    RRL_STOCK_CTX_API.end_effect;
   end loop;
  end if;
  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_from);
  update RRL_WMS_RECEIPT_UNIT set CURRENT_UID=p_target_uid,CURRENT_CELL=p_to,UNIT_VERSION=UNIT_VERSION+1
   where CURRENT_UID=p_uid and CURRENT_CELL=p_from and STOCK_STATUS!='ISSUED' and
    (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=PHYSICAL_UNIT_KEY));
  RRL_STOCK_CTX_API.end_effect;
  if p_target_uid=p_uid then
   RRL_STOCK_BALANCE_CORE.write_move(p_uid,p_from,p_to,p_qty,p_uom,p_uom_version,p_line,p_actor,v_event);
  else
  RRL_STOCK_BALANCE_CORE.write_leg(p_uid,p_from,null,-p_qty,p_uom,p_uom_version,p_line,1,2,p_actor,v_event);
  RRL_STOCK_BALANCE_CORE.write_leg(p_target_uid,null,p_to,p_qty,p_uom,p_uom_version,p_line,2,2,p_actor,v_event);
  end if;
 end;
end;
/
