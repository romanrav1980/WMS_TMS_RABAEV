declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_PLAN_HELPER authid definer as
 procedure fence(p_plan in out nocopy json_array_t,p_kind varchar2,p_id varchar2,p_mode number default 4);
 procedure anchor(p_plan in out nocopy json_array_t,p_rank number,p_kind varchar2,p_a varchar2,p_b varchar2 default null);
 procedure row_key(p_plan in out nocopy json_array_t,p_table varchar2,p_id varchar2);
 procedure stock_closure(p_policies in out nocopy json_array_t,p_resources in out nocopy json_array_t,
  p_uid varchar2,p_article varchar2,p_from varchar2,p_to varchar2);
 function decimal_text(p_value number) return varchar2;
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

create or replace package RRL_STOCK_TASK_PLAN authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE) as
 procedure compile_task(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 function signature(p_task RRL_WAREHOUSE_TASK%rowtype) return varchar2;
end;
/

create or replace package RRL_STOCK_TASK_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure execute_task(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_TASK_DOMAIN authid definer
 accessible by(package RRL_STOCK_TASK_CORE) as
 procedure sync_fact(p_task RRL_WAREHOUSE_TASK%rowtype,p_qty number,p_target_uid varchar2,p_residual number,p_actor varchar2);
end;
/

create or replace package RRL_STOCK_UNIT_CORE authid definer
 accessible by(package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_INVARIANT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_TRANSFER_CORE,
 package RRL_STOCK_EFFECT_CORE,package RRL_STOCK_RECEIPT_CORE) as
 procedure admit_captured(p_uid varchar2,p_cell varchar2);
 procedure assert_composition(p_uid varchar2,p_cell varchar2);
 procedure issue_free_units(p_uid varchar2,p_cell varchar2,p_qty number,p_units clob);
 procedure reserve_units(p_uid varchar2,p_cell varchar2,p_id number,p_qty number,p_units clob);
 procedure release_units(p_id number,p_qty number,p_units clob,p_issue number default 0);
end;
/

create or replace package RRL_STOCK_RECEIPT_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure execute_receipt(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_STOCK_PLAN_HELPER as
 procedure fence(p_plan in out nocopy json_array_t,p_kind varchar2,p_id varchar2,p_mode number default 4) is v json_object_t:=json_object_t();
 begin
  v.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key(p_kind,p_id)));v.put('mode',p_mode);p_plan.append(v);
 end;
 procedure anchor(p_plan in out nocopy json_array_t,p_rank number,p_kind varchar2,p_a varchar2,p_b varchar2 default null) is v json_object_t:=json_object_t();
 begin
  v.put('rank',p_rank);v.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key(p_kind,p_a,p_b)));p_plan.append(v);
 end;
 procedure row_key(p_plan in out nocopy json_array_t,p_table varchar2,p_id varchar2) is
 begin anchor(p_plan,20,'ROW',p_table,p_id);end;
 function decimal_text(p_value number) return varchar2 is
 begin return to_char(p_value,'TM9','NLS_NUMERIC_CHARACTERS=''.,''');end;
 procedure stock_closure(p_policies in out nocopy json_array_t,p_resources in out nocopy json_array_t,
  p_uid varchar2,p_article varchar2,p_from varchar2,p_to varchar2) is
 begin
  fence(p_policies,'CONFIG','WAREHOUSE');fence(p_policies,'SKU',p_article);
  if p_from is not null then fence(p_policies,'CELL',p_from);anchor(p_resources,40,'SLOT','CELL:'||p_from);end if;
  if p_to is not null then fence(p_policies,'CELL',p_to);anchor(p_resources,40,'SLOT','CELL:'||p_to);end if;
  anchor(p_resources,30,'HU',p_uid);anchor(p_resources,50,'STOCK',p_uid);
  for r in(select RESERVATION_ID,CELL_SLOT_ID from RRL_STOCK_RESERVATION
    where UID_PALLET=p_uid and STATUS in('ACTIVE','ALLOCATED','PICKING') and RESERVATION_KIND='HARD') loop
   row_key(p_resources,'RRL_STOCK_RESERVATION',decimal_text(r.RESERVATION_ID));
   if r.CELL_SLOT_ID is not null then anchor(p_resources,40,'SLOT',decimal_text(r.CELL_SLOT_ID));end if;
  end loop;
  for u in(select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and STOCK_STATUS!='ISSUED') loop
   if u.PHYSICAL_UNIT_KEY is null then raise_application_error(-20884,'COMPOSITION_BINDING_REQUIRED');end if;
   anchor(p_resources,60,'UNIT',u.PHYSICAL_UNIT_KEY);
  end loop;
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

create or replace package body RRL_STOCK_TASK_PLAN as
 function signature(p_task RRL_WAREHOUSE_TASK%rowtype) return varchar2 is v json_object_t:=json_object_t();
 begin
  v.put('task_id',p_task.TASK_ID);v.put('source',p_task.TASK_SOURCE);v.put('kind',p_task.TASK_TYPE);
  v.put('uid',p_task.UID_PALLET);v.put('sscc',p_task.SSCC);v.put('from',p_task.FROM_CELL);v.put('to',p_task.TO_CELL);
  v.put('from_ware',p_task.FROM_WARE_ID);v.put('to_ware',p_task.TO_WARE_ID);v.put('slot_from',p_task.FROM_CELL_SLOT_ID);
  v.put('slot_to',p_task.TO_CELL_SLOT_ID);v.put('doc_type',p_task.SOURCE_DOC_TYPE);v.put('doc',p_task.SOURCE_DOC_ID);
  v.put('source_task',p_task.SOURCE_TASK_ID);v.put('movement',p_task.SOURCE_MOVEMENT_ID);
  v.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(p_task.QTY));v.put('unit',p_task.UNIT_CODE);
  v.put('raw_article',p_task.RAW_ARTICUL);v.put('target_article',p_task.TARGET_ARTICUL);
  v.put('mode',p_task.QTY_MODE);v.put('production',p_task.PRODUCTION_ORDER_ID);
  return rawtohex(sys.dbms_crypto.hash(v.to_clob,sys.dbms_crypto.hash_sh256));
 end;
 procedure compile_task(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  v_doc json_object_t:=json_object_t.parse(p_request);v_source json_object_t;v_meta json_object_t;
  v_task RRL_WAREHOUSE_TASK%rowtype;v_uid varchar2(200);v_article varchar2(160);v_target varchar2(200);
  v_p json_array_t:=json_array_t();v_r json_array_t:=json_array_t();v_domain json_object_t:=json_object_t();
  v_task_id number;v_residual number;v_reservation number;v_new_reservation number;v_fact number;v_pick_task number;v_movement_id number;v_sync_id number;v_sync_key varchar2(400);v_from_ware number;v_to_ware number;v_source_p number;v_base varchar2(20);v_input varchar2(20);v_qbase number;v_num number;v_den number;v_scale number;v_uom_version number;v_uom_signature varchar2(64);
 begin
  v_source:=v_doc.get_object('source');v_meta:=v_doc.get_object('metadata');v_source.on_error(1);
  v_task_id:=v_source.get_number('task_id');
  if v_task_id is null or v_task_id<1 or v_task_id!=trunc(v_task_id) then raise_application_error(-20881,'TASK_ID_REQUIRED');end if;
  select * into v_task from RRL_WAREHOUSE_TASK where TASK_ID=v_task_id;
  v_uid:=nvl(v_task.UID_PALLET,v_task.SSCC);
  v_sync_key:='WT:'||RRL_STOCK_PLAN_HELPER.decimal_text(v_task_id)||':'||v_task.TASK_SOURCE||':'||v_task.TASK_TYPE||':'||RRL_STOCK_PLAN_HELPER.decimal_text(v_task.SOURCE_TASK_ID)||':'||RRL_STOCK_PLAN_HELPER.decimal_text(v_task.SOURCE_MOVEMENT_ID);
  begin select SYNC_ID into v_sync_id from RRL_WAREHOUSE_TASK_SYNC where SYNC_KEY=v_sync_key;
  exception when no_data_found then select RRL_WH_TASK_SYNC_SQ.nextval into v_sync_id from dual;end;
  select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=v_uid;
  select WARE_ID into v_from_ware from RRL_CELLS where CELL=v_task.FROM_CELL;
  select WARE_ID into v_to_ware from RRL_CELLS where CELL=v_task.TO_CELL;
  if (v_task.FROM_WARE_ID is not null and v_task.FROM_WARE_ID!=v_from_ware) or
   (v_task.TO_WARE_ID is not null and v_task.TO_WARE_ID!=v_to_ware) then raise_application_error(-20886,'TASK_CELL_WAREHOUSE_CONFLICT');end if;
  v_fact:=v_task.QTY;
  if v_meta.has('fact_qty') and not v_meta.get('fact_qty').is_null then
   v_fact:=RRL_STOCK_MATH.quantity(v_meta.get_string('fact_qty'));
  end if;
  select REMAIN,BASE_UOM into v_source_p,v_base from RRL_REMAINS where UID_POLETA=v_uid and CELL=v_task.FROM_CELL;
  v_input:=nvl(v_task.UNIT_CODE,v_base);
  RRL_STOCK_PALLET_UOM.resolve_quantity(v_uid,v_input,RRL_STOCK_PLAN_HELPER.decimal_text(v_fact),
   v_base,v_qbase,v_uom_version,v_uom_signature);
  v_target:=v_uid;
  if v_fact<v_task.QTY then select RRL_WAREHOUSE_TASK_SQ.nextval into v_residual from dual;end if;
  if v_qbase<v_source_p then
   v_target:='PART:'||substr(rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)),1,64);
   select RRL_STOCK_RESERVATION_SQ.nextval into v_new_reservation from dual;
  end if;
  RRL_STOCK_PLAN_HELPER.fence(v_p,'RELEASE','STOCK');
  RRL_STOCK_PLAN_HELPER.anchor(v_r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(v_r,70,'UNIQUE','STOCK.OUTBOX:'||
   rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.row_key(v_r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_task_id));
  RRL_STOCK_PLAN_HELPER.row_key(v_r,'RRL_WAREHOUSE_TASK_SYNC',RRL_STOCK_PLAN_HELPER.decimal_text(v_sync_id));
  RRL_STOCK_PLAN_HELPER.anchor(v_r,70,'UNIQUE','TASK.SYNC:'||v_sync_key);
  if v_residual is not null then RRL_STOCK_PLAN_HELPER.row_key(v_r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_residual));end if;
  if v_new_reservation is not null then RRL_STOCK_PLAN_HELPER.row_key(v_r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(v_new_reservation));end if;
  if v_task.TASK_SOURCE='WAVE' then
   RRL_STOCK_PLAN_HELPER.row_key(v_r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(v_task.SOURCE_DOC_ID));
   if v_task.TASK_TYPE='REPLENISHMENT' then
    RRL_STOCK_PLAN_HELPER.row_key(v_r,'RRL_PICK_WAVE_REPLENISH_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_task.SOURCE_TASK_ID));
    select SOURCE_RESERVATION_ID into v_reservation from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=v_task.SOURCE_TASK_ID;
   elsif v_task.TASK_TYPE='PICKING_MOVE' then
    RRL_STOCK_PLAN_HELPER.row_key(v_r,'RRL_PICK_WAVE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_task.SOURCE_TASK_ID));
    select PICK_TASK_ID into v_pick_task from RRL_PICK_WAVE_TASK where PICK_WAVE_TASK_ID=v_task.SOURCE_TASK_ID;
    RRL_STOCK_PLAN_HELPER.row_key(v_r,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_pick_task));
   end if;
  elsif v_task.TASK_SOURCE='SAP_RECEIPT' then
   RRL_STOCK_PLAN_HELPER.row_key(v_r,'RRL_PRIHOD_NAKLAD',RRL_STOCK_PLAN_HELPER.decimal_text(v_task.SOURCE_DOC_ID));
   RRL_STOCK_PLAN_HELPER.row_key(v_r,'RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(v_task_id));
  elsif v_task.TASK_SOURCE in('MES_RAW_SUPPLY','MES_COMPLETION') then
   RRL_STOCK_PLAN_HELPER.row_key(v_r,'RRL_PRODUCTION_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(nvl(v_task.PRODUCTION_ORDER_ID,v_task.SOURCE_DOC_ID)));
   if v_task.SOURCE_TASK_ID is not null then
    RRL_STOCK_PLAN_HELPER.row_key(v_r,'RRL_MES_RAW_TRANSFER_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_task.SOURCE_TASK_ID));
   end if;
   if v_task.SOURCE_MOVEMENT_ID is not null then
    RRL_STOCK_PLAN_HELPER.row_key(v_r,'RRL_MES_MOVEMENT',RRL_STOCK_PLAN_HELPER.decimal_text(v_task.SOURCE_MOVEMENT_ID));
   end if;
  end if;
  if v_task.TASK_SOURCE='MES_RAW_SUPPLY' then
   select RESERVATION_ID into v_reservation from RRL_MES_RAW_TRANSFER_TASK where TASK_ID=v_task.SOURCE_TASK_ID;
   select RRL_MES_MOVEMENT_SQ.nextval into v_movement_id from dual;
   RRL_STOCK_PLAN_HELPER.row_key(v_r,'RRL_MES_MOVEMENT',RRL_STOCK_PLAN_HELPER.decimal_text(v_movement_id));
  end if;
  if v_meta.has('resource_session_id') and not v_meta.get('resource_session_id').is_null then
   RRL_STOCK_PLAN_HELPER.row_key(v_r,'RRL_RESOURCE_SESSION',RRL_STOCK_PLAN_HELPER.decimal_text(v_meta.get_number('resource_session_id')));
  end if;
  if v_task.FROM_CELL_SLOT_ID is not null then RRL_STOCK_PLAN_HELPER.anchor(v_r,40,'SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(v_task.FROM_CELL_SLOT_ID));end if;
  if v_task.TO_CELL_SLOT_ID is not null then RRL_STOCK_PLAN_HELPER.anchor(v_r,40,'SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(v_task.TO_CELL_SLOT_ID));end if;
  RRL_STOCK_PLAN_HELPER.stock_closure(v_p,v_r,v_uid,v_article,v_task.FROM_CELL,v_task.TO_CELL);
  if v_target!=v_uid then
   RRL_STOCK_PLAN_HELPER.anchor(v_r,30,'HU',v_target);RRL_STOCK_PLAN_HELPER.anchor(v_r,50,'STOCK',v_target);
   RRL_STOCK_PLAN_HELPER.anchor(v_r,70,'UNIQUE','PALLET:'||v_target);
  end if;
  v_domain.put('uom_signature',v_uom_signature);v_domain.put('source_p',RRL_STOCK_PLAN_HELPER.decimal_text(v_source_p));v_domain.put('uom_version',v_uom_version);v_domain.put('base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qbase));
  v_domain.put('from_ware_id',v_from_ware);v_domain.put('to_ware_id',v_to_ware);
  v_domain.put('sync_id',v_sync_id);v_domain.put('sync_key',v_sync_key);
  v_domain.put('task_signature',signature(v_task));v_domain.put('target_uid',v_target);
  v_domain.put('residual_task_id',v_residual);v_domain.put('source_reservation_id',v_reservation);
  v_domain.put('new_movement_id',v_movement_id);
  v_domain.put('new_reservation_id',v_new_reservation);v_domain.put('pick_task_id',v_pick_task);
  p_policies:=v_p.to_clob;p_resources:=v_r.to_clob;p_domain:=v_domain.to_clob;
 end;
end;
/

create or replace package body RRL_STOCK_TASK_CORE as
 procedure execute_task(p_request clob,p_actor varchar2,p_result out clob) is
  v_doc json_object_t:=json_object_t.parse(p_request);v_meta json_object_t;v_source json_object_t;v_domain json_object_t;
  v_plan clob;v_task RRL_WAREHOUSE_TASK%rowtype;v_residual RRL_WAREHOUSE_TASK%rowtype;v_pallet RRL_PALLETS%rowtype;
  v_task_id number;v_qty number;v_original number;v_qbase number;v_target varchar2(200);v_base varchar2(20);
  v_factor_num number;v_factor_den number;v_scale number;v_version number;v_article varchar2(160);
  v_residual_id number;v_reservation number;v_new_reservation number;v_ware number;v_pick_task number;
  v_signature varchar2(64);v_hash varchar2(64);v_op varchar2(100);v_units clob;v_n number;v_doc_status varchar2(40);
  v_result json_object_t:=json_object_t();v_resource number;v_session number;v_equipment number;v_sync_id number;v_sync_key varchar2(400);v_session_actor varchar2(100);v_input_uom varchar2(20);v_source_p number;v_uom_signature varchar2(64);
 begin
  v_doc.on_error(1);v_source:=v_doc.get_object('source');v_meta:=v_doc.get_object('metadata');v_meta.on_error(1);
  v_op:=v_doc.get_string('operation_id');v_task_id:=v_source.get_number('task_id');
  if RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 then raise_application_error(-20882,'TASK_COMPLETE_FORBIDDEN');end if;
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_task_id)));
  select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
  v_domain:=json_object_t.parse(v_plan).get_object('domain');
  -- Existing assignment/start commands lock the source document before the task.
  -- Read identity without a row lock, validate the planned signature, then use the same order.
  select * into v_task from RRL_WAREHOUSE_TASK where TASK_ID=v_task_id;
  if RRL_STOCK_TASK_PLAN.signature(v_task)!=v_domain.get_string('task_signature') then raise_application_error(-20890,'CLOSURE_CHANGED: task source');end if;
  if v_task.TASK_SOURCE='WAVE' then
   select STATUS into v_doc_status from RRL_PICK_WAVE where PICK_WAVE_ID=v_task.SOURCE_DOC_ID for update;
  elsif v_task.TASK_SOURCE in('MES_RAW_SUPPLY','MES_COMPLETION') then
   select STATUS into v_doc_status from RRL_PRODUCTION_ORDER where PRODUCTION_ORDER_ID=nvl(v_task.PRODUCTION_ORDER_ID,v_task.SOURCE_DOC_ID) for update;
  elsif v_task.TASK_SOURCE='SAP_RECEIPT' then
   select to_char(CONDITION) into v_doc_status from RRL_PRIHOD_NAKLAD where ID=v_task.SOURCE_DOC_ID for update;
  end if;
  select * into v_task from RRL_WAREHOUSE_TASK where TASK_ID=v_task_id for update;
  if RRL_STOCK_TASK_PLAN.signature(v_task)!=v_domain.get_string('task_signature') then
   raise_application_error(-20890,'CLOSURE_CHANGED: task identity');
  end if;
  if v_task.STATUS is null or v_task.STATUS not in('PLANNED','ASSIGNED','IN_PROGRESS') then
   raise_application_error(-20886,'TASK_STATE_CONFLICT');end if;
  v_task.FROM_WARE_ID:=v_domain.get_number('from_ware_id');v_task.TO_WARE_ID:=v_domain.get_number('to_ware_id');
  if v_task.FROM_WARE_ID is null or v_task.TO_WARE_ID is null or v_task.FROM_WARE_ID!=v_task.TO_WARE_ID then
   raise_application_error(-20886,'INTERWAREHOUSE_COMMAND_REQUIRED');end if;
  if upper(trim(v_meta.get_string('scanned_pallet'))) is null or
   trim(v_meta.get_string('scanned_pallet')) not in(nvl(v_task.UID_PALLET,v_task.SSCC),nvl(v_task.SSCC,v_task.UID_PALLET))
   or upper(trim(v_meta.get_string('scanned_from_cell'))) is null or upper(trim(v_meta.get_string('scanned_from_cell')))!=upper(v_task.FROM_CELL)
   or upper(trim(v_meta.get_string('scanned_to_cell'))) is null or upper(trim(v_meta.get_string('scanned_to_cell')))!=upper(v_task.TO_CELL) then
   raise_application_error(-20886,'TASK_SCAN_CONFLICT');end if;
  v_original:=v_task.QTY;v_qty:=v_original;
  if v_meta.has('fact_qty') and not v_meta.get('fact_qty').is_null then v_qty:=RRL_STOCK_MATH.quantity(v_meta.get_string('fact_qty'));end if;
  if v_qty is null or v_qty<=0 or v_qty>v_original or (v_task.QTY_MODE='PALLET' and v_qty!=v_original) then
   raise_application_error(-20886,'TASK_QUANTITY_CONFLICT');end if;
  v_target:=v_domain.get_string('target_uid');v_residual_id:=v_domain.get_number('residual_task_id');
  v_reservation:=v_domain.get_number('source_reservation_id');v_new_reservation:=v_domain.get_number('new_reservation_id');
  v_pick_task:=v_domain.get_number('pick_task_id');
  select * into v_pallet from RRL_PALLETS where UID_PALLET=nvl(v_task.UID_PALLET,v_task.SSCC);
  v_article:=v_pallet.ARTICUL;
  if (v_task.RAW_ARTICUL is not null and v_task.RAW_ARTICUL!=v_article) or (v_task.TARGET_ARTICUL is not null and v_task.TARGET_ARTICUL!=v_article) then raise_application_error(-20887,'TASK_ARTICLE_CONFLICT');end if;
  select BASE_UOM,REMAIN into v_input_uom,v_source_p from RRL_REMAINS where UID_POLETA=v_pallet.UID_PALLET and CELL=v_task.FROM_CELL;
  v_input_uom:=nvl(v_task.UNIT_CODE,v_input_uom);
  RRL_STOCK_PALLET_UOM.resolve_quantity(v_pallet.UID_PALLET,v_input_uom,RRL_STOCK_PLAN_HELPER.decimal_text(v_qty),
   v_base,v_qbase,v_version,v_uom_signature);
  if v_uom_signature!=v_domain.get_string('uom_signature') then raise_application_error(-20890,'CLOSURE_CHANGED: pallet pack');end if;
  if v_version!=v_domain.get_number('uom_version') or RRL_STOCK_PLAN_HELPER.decimal_text(v_qbase)!=v_domain.get_string('base_quantity') or RRL_STOCK_PLAN_HELPER.decimal_text(v_source_p)!=v_domain.get_string('source_p') then raise_application_error(-20890,'CLOSURE_CHANGED: task quantity policy');end if;
  if v_task.QTY_MODE='PALLET' and v_qbase!=v_source_p then raise_application_error(-20886,'WHOLE_PALLET_STOCK_CHANGED');end if;
  if v_task.TASK_SOURCE='WAVE' then
   select STATUS into v_doc_status from RRL_PICK_WAVE where PICK_WAVE_ID=v_task.SOURCE_DOC_ID for update;
   if v_doc_status='CANCELLED' then raise_application_error(-20886,'SOURCE_DOCUMENT_CANCELLED');end if;
  elsif v_task.TASK_SOURCE='SAP_RECEIPT' then
   if v_qty!=v_original then raise_application_error(-20886,'PUTAWAY_MUST_BE_WHOLE');end if;
   select count(*) into v_n from RRL_SAP_PALLET_RECEIPT rec join RRL_SAP_SUPPLY_ORDER so on so.ORDER_ID=rec.ORDER_ID
    where rec.UID_PALLET=v_pallet.UID_PALLET and so.NAKLAD_ID=v_task.SOURCE_DOC_ID and so.RECEIVE_CELL=v_task.FROM_CELL and so.WARE_ID=v_task.FROM_WARE_ID;
   if v_n!=1 then raise_application_error(-20886,'PUTAWAY_RECEIPT_SOURCE_CONFLICT');end if;
   if v_task.TO_CELL_SLOT_ID is not null then
    select count(*) into v_n from RRL_RECEIPT_SLOT_CLAIM cl join RRL_TOPOLOGY_CELL_SLOT sl on sl.CELL_SLOT_ID=cl.CELL_SLOT_ID
     where cl.TASK_ID=v_task_id and cl.STATUS='RESERVED' and sl.ACTIVE=1;
    if v_n!=1 then raise_application_error(-20886,'PUTAWAY_SLOT_CONFLICT');end if;
   end if;
  elsif v_task.TASK_SOURCE in('MES_RAW_SUPPLY','MES_COMPLETION') then
   select STATUS into v_doc_status from RRL_PRODUCTION_ORDER
    where PRODUCTION_ORDER_ID=nvl(v_task.PRODUCTION_ORDER_ID,v_task.SOURCE_DOC_ID) for update;
   if v_doc_status='CANCELLED' then raise_application_error(-20886,'SOURCE_DOCUMENT_CANCELLED');end if;
  else raise_application_error(-20888,'TASK_DOMAIN_HANDLER_REQUIRED');end if;
  if v_target!=v_pallet.UID_PALLET then
   RRL_STOCK_LOCK_API.assert_held(70,RRL_STOCK_LOCK_API.resource_key('UNIQUE','PALLET:'||v_target));
   v_pallet.STOCK_ORIGIN_UID:=nvl(v_pallet.STOCK_ORIGIN_UID,v_pallet.UID_PALLET);v_pallet.CREATED_BY_STOCK_OP:=v_op;
   if v_pallet.WEIGHT_BRUTTO is not null then
    if v_pallet.UNIT_COUNT is null or v_pallet.UNIT_COUNT<=0 then raise_application_error(-20887,'PALLET_BIRTH_QUANTITY_REQUIRED');end if;
    v_pallet.WEIGHT_BRUTTO:=v_pallet.WEIGHT_BRUTTO*v_qbase/v_pallet.UNIT_COUNT;
   end if;
   v_pallet.UID_PALLET:=v_target;v_pallet.SSCC:=null;v_pallet.UNIT_COUNT:=v_qbase;v_pallet.PRINTED:=0;
   insert into RRL_PALLETS values v_pallet;
  end if;
  if v_meta.has('unit_keys') and v_meta.get_array('unit_keys').get_size>0 then v_units:=v_meta.get_array('unit_keys').to_clob;end if;
  RRL_STOCK_TRANSFER_CORE.move(nvl(v_task.UID_PALLET,v_task.SSCC),v_target,v_task.FROM_CELL,v_task.TO_CELL,
   v_qbase,v_base,v_version,v_task.TO_WARE_ID,p_actor,1,v_reservation,v_units,v_new_reservation,v_task.TO_CELL_SLOT_ID,null,case when v_task.TASK_SOURCE='SAP_RECEIPT' then 'PUTAWAY' else 'ORDINARY' end);
  v_resource:=v_meta.get_number('resource_id');v_session:=v_meta.get_number('resource_session_id');v_equipment:=v_meta.get_number('equipment_id');
  if v_session is not null then
   select RESOURCE_ID,EQUIPMENT_ID,OPERATOR_USER_ID into v_resource,v_equipment,v_session_actor from RRL_RESOURCE_SESSION where SESSION_ID=v_session and STATUS='ACTIVE' for update;
   if v_session_actor is null or v_session_actor!=p_actor then raise_application_error(-20882,'TASK_SESSION_OWNER_CONFLICT');end if;
  end if;
  v_hash:=rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256));
  if v_residual_id is not null then
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_residual_id)));
   v_residual:=v_task;v_residual.TASK_ID:=v_residual_id;v_residual.QTY:=v_original-v_qty;
   v_residual.PARENT_TASK_ID:=v_task_id;v_residual.STATUS:='PLANNED';v_residual.FACT_QTY:=null;
   v_residual.CREATED_BY:=p_actor;v_residual.CREATED_AT:=systimestamp;v_residual.COMPLETION_HASH:=null;
   v_residual.COMPLETION_JSON:=null;v_residual.FINISHED_AT:=null;v_residual.ASSIGNED_TO:=null;
   v_residual.STARTED_AT:=null;v_residual.TARGET_UID_PALLET:=null;v_residual.LAST_ERROR:='Residual of task '||v_task_id;
   insert into RRL_WAREHOUSE_TASK values v_residual;
  end if;
  update RRL_WAREHOUSE_TASK set STATUS='DONE',QTY=v_qty,FACT_QTY=v_qty,TARGET_UID_PALLET=v_target,
   FROM_WARE_ID=v_task.FROM_WARE_ID,TO_WARE_ID=v_task.TO_WARE_ID,FINISHED_AT=systimestamp,ASSIGNED_TO=p_actor,RESOURCE_ID=nvl(v_resource,RESOURCE_ID),
   RESOURCE_SESSION_ID=nvl(v_session,RESOURCE_SESSION_ID),EQUIPMENT_ID=nvl(v_equipment,EQUIPMENT_ID),
   COMPLETION_HASH=v_hash,COMPLETION_JSON=p_request,LAST_ERROR=null where TASK_ID=v_task_id;
  insert into RRL_WAREHOUSE_TASK_STOCK_MOVE(STOCK_MOVE_ID,TASK_ID,TASK_SOURCE,TASK_TYPE,SOURCE_DOC_TYPE,SOURCE_DOC_ID,
   SOURCE_TASK_ID,UID_PALLET,TARGET_UID_PALLET,FROM_CELL,TO_CELL,QTY,BASE_QTY,BASE_UOM,OPERATION_ID,CREATED_AT,CREATED_BY)
   values(RRL_WH_TASK_STOCK_MOVE_SQ.nextval,v_task_id,v_task.TASK_SOURCE,v_task.TASK_TYPE,v_task.SOURCE_DOC_TYPE,v_task.SOURCE_DOC_ID,
    v_task.SOURCE_TASK_ID,nvl(v_task.UID_PALLET,v_task.SSCC),v_target,v_task.FROM_CELL,v_task.TO_CELL,v_qty,v_qbase,v_base,v_op,systimestamp,p_actor);
  if v_resource is not null or v_session is not null or v_equipment is not null then
   insert into RRL_RESOURCE_FACT_EVENT(EVENT_ID,TASK_ID,SESSION_ID,RESOURCE_ID,EVENT_TYPE,EVENT_AT,EVENT_BY,PAYLOAD_JSON)
    values(RRL_RESOURCE_FACT_EVENT_SQ.nextval,v_task_id,v_session,v_resource,'COMPLETED',systimestamp,p_actor,p_request);
  end if;
  RRL_STOCK_TASK_DOMAIN.sync_fact(v_task,v_qty,v_target,v_residual_id,p_actor);
  v_sync_id:=v_domain.get_number('sync_id');v_sync_key:=v_domain.get_string('sync_key');
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK_SYNC',RRL_STOCK_PLAN_HELPER.decimal_text(v_sync_id)));
  merge into RRL_WAREHOUSE_TASK_SYNC d using(select v_sync_key SYNC_KEY from dual)s on(d.SYNC_KEY=s.SYNC_KEY)
   when matched then update set d.SYNC_STATUS='SYNCED',d.SYNCED_AT=systimestamp,d.UPDATED_AT=systimestamp,d.UPDATED_BY=p_actor,d.LAST_ERROR=null
   when not matched then insert(SYNC_ID,TASK_ID,TASK_SOURCE,TASK_TYPE,SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_TASK_ID,SOURCE_MOVEMENT_ID,SYNC_KEY,SYNC_STATUS,SYNC_ATTEMPT,CREATED_AT,UPDATED_AT,SYNCED_AT,UPDATED_BY)
    values(v_sync_id,v_task_id,v_task.TASK_SOURCE,v_task.TASK_TYPE,v_task.SOURCE_DOC_TYPE,v_task.SOURCE_DOC_ID,v_task.SOURCE_TASK_ID,v_task.SOURCE_MOVEMENT_ID,v_sync_key,'SYNCED',1,systimestamp,systimestamp,systimestamp,p_actor);
  v_result.put('operation_id',v_op);v_result.put('task_id',v_task_id);v_result.put('status','DONE');
  v_result.put('pallet_identifier',v_target);v_result.put('source_pallet_identifier',nvl(v_task.UID_PALLET,v_task.SSCC));
  v_result.put('cell',v_task.TO_CELL);v_result.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));
  v_result.put('base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qbase));v_result.put('base_uom',v_base);
  v_result.put('residual_task_id',v_residual_id);p_result:=v_result.to_clob;
 end;
end;
/

create or replace package body RRL_STOCK_TASK_DOMAIN as
 procedure sync_fact(p_task RRL_WAREHOUSE_TASK%rowtype,p_qty number,p_target_uid varchar2,p_residual number,p_actor varchar2) is
  v_n number;v_status varchar2(40);v_pick number;
 begin
  if p_task.TASK_SOURCE='WAVE' then
   select count(*) into v_n from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE' and TASK_TYPE=p_task.TASK_TYPE
    and SOURCE_TASK_ID=p_task.SOURCE_TASK_ID and STATUS not in('DONE','CANCELLED');
   v_status:=case when v_n=0 then 'DONE' else 'IN_PROGRESS' end;
   if p_task.TASK_TYPE='REPLENISHMENT' then
    update RRL_PICK_WAVE_REPLENISH_TASK set STATUS=v_status,UPDATED_AT=sysdate,UPDATED_BY=p_actor
     where PICK_WAVE_REPLENISH_TASK_ID=p_task.SOURCE_TASK_ID;
    -- HARD coverage is now at the target. Do not mark it CONSUMED by placement.
   elsif p_task.TASK_TYPE='PICKING_MOVE' then
    select PICK_TASK_ID into v_pick from RRL_PICK_WAVE_TASK where PICK_WAVE_TASK_ID=p_task.SOURCE_TASK_ID;
    update RRL_PICK_WAVE_TASK set STATUS=v_status,FACT_QTY=p_qty,
     DONE_AT=case when v_status='DONE' then sysdate else DONE_AT end,
     DONE_BY=case when v_status='DONE' then p_actor else DONE_BY end,
     TARGET_CELL_CODE=p_task.TO_CELL,UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_WAVE_TASK_ID=p_task.SOURCE_TASK_ID;
    update RRL_PICK_TASK set STATUS=v_status,FACT_QTY=p_qty,
     DONE_AT=case when v_status='DONE' then sysdate else DONE_AT end,
     DONE_BY=case when v_status='DONE' then p_actor else DONE_BY end,
     TARGET_CELL_CODE=p_task.TO_CELL,UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_TASK_ID=v_pick;
    -- Physical relocation preserves HARD until ISSUE/SHIP, even if the picking task is DONE.
   else raise_application_error(-20888,'WAVE_TASK_HANDLER_REQUIRED');end if;
  elsif p_task.TASK_SOURCE='SAP_RECEIPT' then
   update RRL_RECEIPT_SLOT_CLAIM set STATUS='OCCUPIED' where TASK_ID=p_task.TASK_ID and STATUS='RESERVED';
  elsif p_task.TASK_SOURCE in('MES_RAW_SUPPLY','MES_COMPLETION') then
   RRL_STOCK_MES_CORE.sync_warehouse_fact(p_task,p_qty,p_target_uid,p_residual,p_actor);
  else raise_application_error(-20888,'TASK_DOMAIN_HANDLER_REQUIRED');end if;
 end;
end;
/

create or replace package body RRL_STOCK_UNIT_CORE as
 procedure require_context is
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null or
   sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or
   sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then
   raise_application_error(-20863,'UNIT_WRITE_FORBIDDEN');end if;
 end;
 procedure own_unit(p_key varchar2) is
 begin
  if p_key is null then raise_application_error(-20884,'UNIT_BINDING_REQUIRED');end if;
  begin RRL_STOCK_LOCK_API.assert_held(60,RRL_STOCK_LOCK_API.resource_key('UNIT',p_key));
  exception when others then if sqlcode=-20850 then raise_application_error(-20890,'CLOSURE_CHANGED: units');else raise;end if;end;
 end;
 procedure assert_composition(p_uid varchar2,p_cell varchar2) is
  v_p number;v_base varchar2(20);v_total number;v_count number;v_bad number;v_article varchar2(160);v_marked number;
 begin
  select REMAIN,BASE_UOM into v_p,v_base from RRL_REMAINS where UID_POLETA=p_uid and CELL=p_cell;
  select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=p_uid;
  select greatest(nvl((select MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY where ARTICUL=v_article),0),
   nvl((select CRPT_REQUIRED from RRL_FINISHED_GOODS_SKU where ARTICUL=v_article),0),
   case when exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=v_article) then 1 else 0 end) into v_marked from dual;
  select count(*),nvl(sum(BASE_QTY),0),nvl(sum(case when PHYSICAL_UNIT_KEY is null or STOCK_STATUS is null or BASE_QTY<=0 or BASE_UOM is null or BASE_UOM!=v_base then 1 else 0 end),0)
   into v_count,v_total,v_bad from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and (STOCK_STATUS is null or STOCK_STATUS!='ISSUED');
  if v_bad>0 or (v_count>0 and v_total!=v_p) or (v_marked=1 and v_p>0 and v_count=0) then
   raise_application_error(-20884,'PHYSICAL_COMPOSITION_CONFLICT');end if;
 end;
 procedure admit_captured(p_uid varchar2,p_cell varchar2) is
 begin
  require_context;assert_composition(p_uid,p_cell);
  for u in(select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS='CAPTURED') loop own_unit(u.PHYSICAL_UNIT_KEY);end loop;
  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_cell);
  update RRL_WMS_RECEIPT_UNIT set STOCK_STATUS='AVAILABLE',UNIT_VERSION=UNIT_VERSION+1
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS='CAPTURED';
  RRL_STOCK_CTX_API.end_effect;
 end;
 procedure issue_free_units(p_uid varchar2,p_cell varchar2,p_qty number,p_units clob) is v_total number;v_count number;v_qty number;v_expected number;v_distinct number;
 begin
  require_context;assert_composition(p_uid,p_cell);
  select count(*) into v_total from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED';
  if v_total=0 then return;end if;
  select count(*),nvl(sum(BASE_QTY),0) into v_count,v_qty from RRL_WMS_RECEIPT_UNIT u
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  if v_qty!=p_qty then raise_application_error(-20884,'ISSUE_UNIT_QUANTITY_CONFLICT');end if;
  if p_units is not null then
   select count(*),count(distinct K) into v_expected,v_distinct from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'));
   if v_count!=v_expected or v_expected!=v_distinct then raise_application_error(-20884,'UNIT_SELECTION_CONFLICT');end if;
  end if;
  for r in(select PHYSICAL_UNIT_KEY,STOCK_STATUS,HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT u
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY))) loop
   own_unit(r.PHYSICAL_UNIT_KEY);
   if r.HARD_RESERVATION_ID is not null then raise_application_error(-20869,'UNIT_RESERVED_BY_OTHER_OWNER');end if;
   if r.STOCK_STATUS!='AVAILABLE' then raise_application_error(-20884,'UNIT_NOT_ADMITTED');end if;
  end loop;
  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_cell);
  update RRL_WMS_RECEIPT_UNIT u set STOCK_STATUS='ISSUED',UNIT_VERSION=UNIT_VERSION+1
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  RRL_STOCK_CTX_API.end_effect;
 end;
 procedure reserve_units(p_uid varchar2,p_cell varchar2,p_id number,p_qty number,p_units clob) is
  v_count number;v_total number;v_chosen number;v_qty number;v_expected number;
 begin
  require_context;assert_composition(p_uid,p_cell);
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  select count(*),nvl(sum(BASE_QTY),0) into v_count,v_total from RRL_WMS_RECEIPT_UNIT
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED';
  if v_count=0 then return;end if;
  select count(*),nvl(sum(BASE_QTY),0) into v_chosen,v_qty from RRL_WMS_RECEIPT_UNIT u
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  if v_qty!=p_qty then raise_application_error(-20884,'RESERVATION_UNIT_QUANTITY_CONFLICT');end if;
  if p_units is not null then
   select count(*),count(distinct K) into v_expected,v_count from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'));
   if v_expected!=v_count or v_expected!=v_chosen then raise_application_error(-20884,'UNIT_SELECTION_CONFLICT');end if;
  end if;
  for r in(select PHYSICAL_UNIT_KEY,HARD_RESERVATION_ID,STOCK_STATUS from RRL_WMS_RECEIPT_UNIT u
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY))) loop
   own_unit(r.PHYSICAL_UNIT_KEY);
   if r.HARD_RESERVATION_ID is not null then raise_application_error(-20869,'UNIT_ALREADY_RESERVED');end if;
   if r.STOCK_STATUS!='AVAILABLE' then raise_application_error(-20884,'UNIT_NOT_ADMITTED');end if;
  end loop;
  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_cell);
  update RRL_WMS_RECEIPT_UNIT u set HARD_RESERVATION_ID=p_id,UNIT_VERSION=UNIT_VERSION+1
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  RRL_STOCK_CTX_API.end_effect;
 end;
 procedure release_units(p_id number,p_qty number,p_units clob,p_issue number default 0) is
  v_qty number;v_count number;v_expected number;v_distinct number;v_uid varchar2(200);v_cell varchar2(60);
 begin
  require_context;
  select UID_PALLET,CELL into v_uid,v_cell from RRL_STOCK_RESERVATION where RESERVATION_ID=p_id;
  assert_composition(v_uid,v_cell);
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',v_uid));
  select count(*),nvl(sum(BASE_QTY),0) into v_count,v_qty from RRL_WMS_RECEIPT_UNIT u
   where HARD_RESERVATION_ID=p_id and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  if v_count=0 then
   select count(*) into v_expected from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=v_uid and CURRENT_CELL=v_cell and STOCK_STATUS!='ISSUED';
   if v_expected>0 then raise_application_error(-20869,'RESERVATION_UNIT_BINDING_REQUIRED');end if;
   return;end if;
  if v_qty!=p_qty then raise_application_error(-20884,'RESERVATION_UNIT_QUANTITY_CONFLICT');end if;
  if p_units is not null then
   select count(*),count(distinct K) into v_expected,v_distinct from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'));
   if v_count!=v_expected or v_expected!=v_distinct then raise_application_error(-20884,'UNIT_SELECTION_CONFLICT');end if;
  end if;
  for r in(select PHYSICAL_UNIT_KEY,STOCK_STATUS from RRL_WMS_RECEIPT_UNIT u
   where HARD_RESERVATION_ID=p_id and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY))) loop
   own_unit(r.PHYSICAL_UNIT_KEY);
   if p_issue=1 and r.STOCK_STATUS!='AVAILABLE' then raise_application_error(-20884,'UNIT_NOT_ADMITTED');end if;
  end loop;
  RRL_STOCK_CTX_API.begin_effect('UNIT',v_uid,v_cell);
  update RRL_WMS_RECEIPT_UNIT u set HARD_RESERVATION_ID=null,UNIT_VERSION=UNIT_VERSION+1,
   STOCK_STATUS=case when p_issue=1 then 'ISSUED' else STOCK_STATUS end
   where HARD_RESERVATION_ID=p_id and STOCK_STATUS!='ISSUED'
    and (p_units is null or exists(select 1 from json_table(p_units,'$[*]' columns(K varchar2(64) path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));
  RRL_STOCK_CTX_API.end_effect;
 end;
end;
/

create or replace package body RRL_STOCK_RECEIPT_CORE as
 procedure execute_receipt(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);h json_object_t;m json_object_t;o RRL_SAP_SUPPLY_ORDER%rowtype;
  v_plan clob;v_result clob;v_response json_object_t;v_policy number;v_qty number;v_planned number;v_done number;v_n number;
  v_base varchar2(20);v_unit varchar2(20);v_article varchar2(160);v_uom_version number;v_num number;v_den number;v_scale number;
  v_uid varchar2(200);v_cell varchar2(60);v_event number;v_task number;v_expiry date;v_header number;
 begin
  if RRL_HAS_WRIGHT(p_actor,'warehouse_receipt_confirm')!=1 then raise_application_error(-20882,'RECEIPT_FORBIDDEN');end if;
  select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=d.get_string('operation_id');
  h:=json_object_t.parse(v_plan).get_object('domain');m:=d.get_object('metadata');
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),4);
  select * into o from RRL_SAP_SUPPLY_ORDER where ORDER_ID=h.get_string('source_order_id') for update;
  if o.REVISION!=h.get_number('order_revision') or o.NAKLAD_ID!=h.get_number('naklad_id')
   or o.WARE_ID!=h.get_number('warehouse_id') or o.RECEIVE_CELL!=h.get_string('receive_cell') then
   raise_application_error(-20890,'CLOSURE_CHANGED: SAP receipt order');end if;
  select CONDITION into v_header from RRL_PRIHOD_NAKLAD where ID=o.NAKLAD_ID for update;
  if nvl(v_header,0)!=0 then raise_application_error(-20886,'RECEIPT_DOCUMENT_CLOSED');end if;
  select ARTICUL,PLANNED_QTY,BASE_UOM into v_article,v_planned,v_unit from RRL_SAP_SUPPLY_LINE
   where ORDER_ID=o.ORDER_ID and LINE_NUMBER=h.get_string('line_number');
  if v_article!=h.get_string('article') or v_unit!=h.get_string('input_uom') then raise_application_error(-20890,'CLOSURE_CHANGED: SAP receipt line');end if;
  select max(POLICY_VERSION) into v_uom_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_unit;
  select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into v_base,v_num,v_den,v_scale
   from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_unit and POLICY_VERSION=v_uom_version;
  v_qty:=RRL_STOCK_MATH.convert_exact(m.get_string('quantity'),v_num,v_den,v_scale);
  v_planned:=RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(v_planned),v_num,v_den,v_scale);
  if h.get_number('uom_version')!=v_uom_version or h.get_string('base_uom')!=v_base or
   RRL_STOCK_MATH.quantity(h.get_string('base_quantity'))!=v_qty then raise_application_error(-20890,'CLOSURE_CHANGED: receipt UOM');end if;
  select count(*) into v_n from RRL_SAP_PALLET_RECEIPT where ORDER_ID=o.ORDER_ID and LINE_NUMBER=h.get_string('line_number')
   and (POSTED_BASE_QTY is null or STOCK_BASE_UOM is null or STOCK_BASE_UOM!=v_base);
  if v_n>0 then raise_application_error(-20884,'LEGACY_RECEIPT_BASELINE_REQUIRED');end if;
  select nvl(sum(POSTED_BASE_QTY),0) into v_done from RRL_SAP_PALLET_RECEIPT where ORDER_ID=o.ORDER_ID and LINE_NUMBER=h.get_string('line_number');
  if v_done+v_qty>v_planned then raise_application_error(-20886,'RECEIPT_OVER_SUPPLY');end if;
  select POLICY_VERSION into v_policy from RRL_SKU_RECEIPT_POLICY where ARTICUL=v_article;
  if v_policy!=h.get_number('marking_policy_version') then raise_application_error(-20890,'CLOSURE_CHANGED: marking policy');end if;
  v_uid:=h.get_string('uid');v_cell:=o.RECEIVE_CELL;v_task:=h.get_number('task_id');
  select count(*) into v_n from RRL_PALLETS where UID_PALLET=v_uid and ARTICUL=v_article and PRIHOD_NAKLAD_ID=o.NAKLAD_ID
   and UNIT_COUNT=v_qty and EXPIRY_DATE=to_date(m.get_string('expiry_date'),'YYYY-MM-DD');
  if v_n!=1 then raise_application_error(-20884,'RECEIPT_STAGING_PALLET_CONFLICT');end if;
  select count(*) into v_n from RRL_WAREHOUSE_TASK where TASK_ID=v_task and UID_PALLET=v_uid and STATUS='PLANNED'
   and FROM_CELL=v_cell and TO_CELL=h.get_object('placement').get_string('cell');
  if v_n!=1 then raise_application_error(-20884,'RECEIPT_STAGING_TASK_CONFLICT');end if;
  select count(*) into v_n from RRL_REMAINS where UID_POLETA=v_uid;
  if v_n>0 then raise_application_error(-20886,'RECEIPT_STOCK_ALREADY_EXISTS');end if;
  RRL_STOCK_LOCATION_CORE.assert_receiving(v_cell,o.WARE_ID);
  select count(*) into v_n from RRL_CELLS where CELL=v_cell and WARE_ID=o.WARE_ID and nvl(BLOCKED_FOR_ACCEPT,0)=0;
  if v_n!=1 then raise_application_error(-20886,'RECEIVING_CELL_BLOCKED');end if;
  RRL_STOCK_BALANCE_CORE.apply_delta(v_uid,v_cell,v_qty,0,v_base,v_uom_version);
  RRL_STOCK_UNIT_CORE.assert_composition(v_uid,v_cell);
  RRL_STOCK_UNIT_CORE.admit_captured(v_uid,v_cell);
  update RRL_PALLETS set STOCK_ORIGIN_UID=v_uid,CREATED_BY_STOCK_OP=d.get_string('operation_id') where UID_PALLET=v_uid;
  RRL_STOCK_BALANCE_CORE.write_leg(v_uid,null,v_cell,v_qty,v_base,v_uom_version,1,1,1,p_actor,v_event);
  v_response:=h.get_object('result');v_response.put('task_id',v_task);p_result:=v_response.to_clob;
  insert into RRL_SAP_PALLET_RECEIPT(OPERATION_ID,ORDER_ID,LINE_NUMBER,UID_PALLET,SUPPLIER_BATCH,PAYLOAD_HASH,RESULT_JSON,
   RECEIVED_BY,POSTED_BASE_QTY,STOCK_BASE_UOM,STOCK_OPERATION_ID)
   values(d.get_string('operation_id'),o.ORDER_ID,h.get_string('line_number'),v_uid,m.get_string('supplier_batch'),
    rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256)),p_result,p_actor,v_qty,v_base,d.get_string('operation_id'));
  insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)
   values(d.get_string('operation_id'),'PALLET_RECEIVED',p_result);
 end;
end;
/
