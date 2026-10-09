declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_LOCATION_CORE authid definer
 accessible by(package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,
  package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_EFFECT_CORE) as
 procedure assert_ordinary(p_cell varchar2,p_expected_warehouse number,p_role varchar2);
end;
/

create or replace package RRL_STOCK_TRANSFER_CORE authid definer
 accessible by(package RRL_STOCK_INTERNAL_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE,
 package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_MOVE_CORE,package RRL_STOCK_MES_CORE) as
 procedure move(p_uid varchar2,p_target_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,
  p_uom varchar2,p_uom_version number,p_warehouse number,p_actor varchar2,p_line number,
  p_reservation number default null,p_units clob default null,p_new_reservation number default null,p_target_slot number default null,p_source_warehouse number default null);
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

create or replace package RRL_STOCK_MES_MOVEMENT_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure execute_movements(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_INTERNAL_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_move(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_move(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_UNIT_CORE authid definer
 accessible by(package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_INVARIANT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_TRANSFER_CORE,
 package RRL_STOCK_EFFECT_CORE,package RRL_STOCK_RECEIPT_CORE) as
 procedure assert_composition(p_uid varchar2,p_cell varchar2);
 procedure issue_free_units(p_uid varchar2,p_cell varchar2,p_qty number,p_units clob);
 procedure reserve_units(p_uid varchar2,p_cell varchar2,p_id number,p_qty number,p_units clob);
 procedure release_units(p_id number,p_qty number,p_units clob,p_issue number default 0);
end;
/

create or replace package RRL_STOCK_RECEIPT_PLAN authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_RECEIPT_CORE) as
 procedure compile_receipt(p_request clob,p_operation varchar2,p_hints clob,p_policies out clob,p_resources out clob,p_domain out clob);
end;
/

create or replace package RRL_STOCK_RECEIPT_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure execute_receipt(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_CONFIG_API authid definer as
 procedure begin_change(p_actor varchar2,p_permission varchar2);
 procedure end_change;
end;
/

create or replace package RRL_STOCK_PALLET_UOM authid definer
 accessible by(package RRL_STOCK_INTERNAL_CMD,package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE) as
 procedure resolve_quantity(p_uid varchar2,p_input varchar2,p_quantity varchar2,
  p_base out varchar2,p_quantity_base out number,p_version out number,p_signature out varchar2);
end;
/

create or replace package RRL_STOCK_POSTING_API authid definer as
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null);
 procedure execute_prepared(p_result out clob);
 procedure reset_connection;
end;
/

create or replace package body RRL_STOCK_LOCATION_CORE as
 procedure assert_ordinary(p_cell varchar2,p_expected_warehouse number,p_role varchar2) is
  v_ware number;v_remain number;v_replenish number;v_accept number;
 begin
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CELL',p_cell),4);
  select WARE_ID,nvl(BLOCKED_FOR_REMAINS,0),nvl(BLOCKED_FOR_POPOLNENIE,0),nvl(BLOCKED_FOR_ACCEPT,0)
   into v_ware,v_remain,v_replenish,v_accept from RRL_CELLS where CELL=p_cell;
  if p_expected_warehouse is null or v_ware is null or v_ware!=p_expected_warehouse then
   raise_application_error(-20877,'WAREHOUSE_LOCATION_CONFLICT');
  end if;
  if p_role not in('SOURCE','TARGET','RECEIVE') or p_role is null then raise_application_error(-20878,'LOCATION_ROLE_INVALID'); end if;
  if v_remain!=0 or v_replenish!=0 or(p_role in('TARGET','RECEIVE') and v_accept!=0) then
   raise_application_error(-20879,'LOCATION_BLOCKED: quarantine/unavailable cell excluded');
  end if;
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
  p_reservation number default null,p_units clob default null,p_new_reservation number default null,p_target_slot number default null,p_source_warehouse number default null) is
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
  RRL_STOCK_LOCATION_CORE.assert_ordinary(p_from,nvl(p_source_warehouse,p_warehouse),'SOURCE');
  RRL_STOCK_LOCATION_CORE.assert_ordinary(p_to,p_warehouse,'TARGET');
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
   v_pallet.UID_PALLET:=v_target;v_pallet.SSCC:=null;v_pallet.UNIT_COUNT:=v_qbase;v_pallet.PRINTED:=0;
   if v_pallet.WEIGHT_BRUTTO is not null then v_pallet.WEIGHT_BRUTTO:=v_pallet.WEIGHT_BRUTTO*v_qbase/v_source_p;end if;
   insert into RRL_PALLETS values v_pallet;
  end if;
  if v_meta.has('unit_keys') and v_meta.get_array('unit_keys').get_size>0 then v_units:=v_meta.get_array('unit_keys').to_clob;end if;
  RRL_STOCK_TRANSFER_CORE.move(nvl(v_task.UID_PALLET,v_task.SSCC),v_target,v_task.FROM_CELL,v_task.TO_CELL,
   v_qbase,v_base,v_version,v_task.TO_WARE_ID,p_actor,1,v_reservation,v_units,v_new_reservation,v_task.TO_CELL_SLOT_ID);
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

create or replace package body RRL_STOCK_MES_MOVEMENT_CORE as
 procedure execute_movements(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);h json_object_t;v json_object_t;items json_array_t;m RRL_MES_MOVEMENT%rowtype;
  o RRL_PRODUCTION_ORDER%rowtype;p RRL_PALLETS%rowtype;v_plan clob;v_uid varchar2(200);v_target varchar2(200);
  v_qty number;v_base varchar2(20);v_version number;v_source_ware number;v_target_ware number;v_event number;
  v_reservation number;v_new_reservation number;v_p number;v_article varchar2(160);v_units clob;
  result json_object_t:=json_object_t();facts json_array_t:=json_array_t();fact json_object_t;v_n number;
 begin
  if RRL_HAS_WRIGHT(p_actor,'mes_wms_bridge_apply')!=1 then raise_application_error(-20882,'MES_WMS_APPLY_FORBIDDEN');end if;
  select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=d.get_string('operation_id');
  h:=json_object_t.parse(v_plan).get_object('domain');items:=h.get_array('movements');
  select * into o from RRL_PRODUCTION_ORDER where PRODUCTION_ORDER_ID=h.get_number('production_order_id') for update;
  if o.STATUS='CANCELLED' then raise_application_error(-20886,'MES_ORDER_CANCELLED');end if;
  for i in 0..items.get_size-1 loop
   v:=treat(items.get(i) as json_object_t);
   select * into m from RRL_MES_MOVEMENT where MOVEMENT_ID=v.get_number('movement_id') for update;
   if RRL_STOCK_MES_MOVEMENT_PLAN.signature(m)!=v.get_string('signature') then raise_application_error(-20890,'CLOSURE_CHANGED: MES movement');end if;
   if m.STATUS not in('MES_POSTED','ERROR') or m.STATUS is null then raise_application_error(-20886,'MES_MOVEMENT_STATE_CONFLICT');end if;
   v_uid:=v.get_string('physical_uid');v_target:=v.get_string('target_uid');v_article:=v.get_string('article');
   v_qty:=RRL_STOCK_MATH.quantity(v.get_string('base_quantity'));v_base:=v.get_string('base_uom');v_version:=v.get_number('uom_version');
   v_reservation:=v.get_number('reservation_id');v_new_reservation:=v.get_number('new_reservation_id');v_units:=null;
   if d.get_object('metadata').has('units_by_movement') then
    if d.get_object('metadata').get_object('units_by_movement').has(RRL_STOCK_PLAN_HELPER.decimal_text(m.MOVEMENT_ID)) then
     v_units:=d.get_object('metadata').get_object('units_by_movement').get_array(RRL_STOCK_PLAN_HELPER.decimal_text(m.MOVEMENT_ID)).to_clob;
    end if;
   end if;
   if m.MOVEMENT_TYPE='FG_PALLET_RELEASE' then
    select WARE_ID into v_target_ware from RRL_CELLS where CELL=m.TARGET_LOCATION;
    if v_target_ware!=o.WARE_ID then raise_application_error(-20886,'MES_FINISHED_WAREHOUSE_CONFLICT');end if;
    RRL_STOCK_LOCATION_CORE.assert_ordinary(m.TARGET_LOCATION,v_target_ware,'TARGET');
    select count(*) into v_n from RRL_REMAINS where UID_POLETA=v_uid;
    if v_n>0 then raise_application_error(-20886,'MES_FINISHED_STOCK_ALREADY_EXISTS');end if;
    select count(*) into v_n from RRL_PALLETS where UID_PALLET=v_uid;
    if v_n=0 then
     insert into RRL_PALLETS(UID_PALLET,ARTICUL,UNIT_COUNT,PRIHOD_NAKLAD_ID,PROD_BATCH_ID,SSCC,QUALITY_STATUS)
      values(v_uid,v_article,v_qty,0,m.PROD_BATCH_ID,m.SSCC,'RELEASED');
    else
     select * into p from RRL_PALLETS where UID_PALLET=v_uid;
     if p.ARTICUL!=v_article or p.PROD_BATCH_ID!=m.PROD_BATCH_ID or p.UNIT_COUNT!=v_qty then raise_application_error(-20887,'MES_FINISHED_LOT_CONFLICT');end if;
    end if;
    RRL_STOCK_BALANCE_CORE.apply_delta(v_uid,m.TARGET_LOCATION,v_qty,0,v_base,v_version);
    RRL_STOCK_UNIT_CORE.assert_composition(v_uid,m.TARGET_LOCATION);
    RRL_STOCK_BALANCE_CORE.write_leg(v_uid,null,m.TARGET_LOCATION,v_qty,v_base,v_version,i+1,1,1,p_actor,v_event);
   else
    select * into p from RRL_PALLETS where UID_PALLET=v_uid;
    if p.ARTICUL!=v_article or (m.RAW_ARTICUL is not null and m.RAW_ARTICUL!=v_article) then raise_application_error(-20887,'MES_RAW_ARTICLE_CONFLICT');end if;
    select WARE_ID into v_source_ware from RRL_CELLS where CELL=m.SOURCE_LOCATION;
    if v_reservation is not null then
     select count(*) into v_n from RRL_STOCK_RESERVATION where RESERVATION_ID=v_reservation and
      SOURCE_DOC_TYPE='PRODUCTION_ORDER' and SOURCE_DOC_ID=o.PRODUCTION_ORDER_ID and UID_PALLET=v_uid and CELL=m.SOURCE_LOCATION;
     if v_n!=1 then raise_application_error(-20869,'MES_RESERVATION_OWNER_CONFLICT');end if;
    end if;
    if m.MOVEMENT_TYPE='RAW_CONSUMPTION' then
     RRL_STOCK_EFFECT_CORE.consume(v_uid,m.SOURCE_LOCATION,v_qty,v_base,v_version,v_source_ware,p_actor,i+1,
      v_reservation,'PRODUCTION_ORDER',o.PRODUCTION_ORDER_ID,v_units);
    else
     select WARE_ID into v_target_ware from RRL_CELLS where CELL=m.TARGET_LOCATION;
     if v_target_ware!=o.WARE_ID then raise_application_error(-20886,'MES_PRODUCTION_WAREHOUSE_CONFLICT');end if;
     select REMAIN into v_p from RRL_REMAINS where UID_POLETA=v_uid and CELL=m.SOURCE_LOCATION;
     if RRL_STOCK_PLAN_HELPER.decimal_text(v_p)!=v.get_string('source_p') then raise_application_error(-20890,'CLOSURE_CHANGED: MES source quantity');end if;
     if v_target!=v_uid then
      p.UID_PALLET:=v_target;p.SSCC:=null;p.UNIT_COUNT:=v_qty;p.PRINTED:=0;
      if p.WEIGHT_BRUTTO is not null then p.WEIGHT_BRUTTO:=p.WEIGHT_BRUTTO*v_qty/v_p;end if;
      insert into RRL_PALLETS values p;
     end if;
     RRL_STOCK_TRANSFER_CORE.move(v_uid,v_target,m.SOURCE_LOCATION,m.TARGET_LOCATION,v_qty,v_base,v_version,v_target_ware,
      p_actor,i+1,v_reservation,v_units,v_new_reservation,null,v_source_ware);
    end if;
   end if;
   update RRL_MES_MOVEMENT set STATUS='APPLIED_TO_WMS',SOURCE_UID_PALLET=v_uid,TARGET_UID_PALLET=v_target,
    UID_PALLET=case when MOVEMENT_TYPE='RAW_ISSUE_TO_PRODUCTION' then v_target else UID_PALLET end,
    STOCK_OPERATION_ID=d.get_string('operation_id'),POSTED_BASE_QTY=v_qty,STOCK_BASE_UOM=v_base,
    WMS_APPLIED_AT=sysdate,WMS_APPLIED_BY=p_actor,UPDATED_AT=sysdate,UPDATED_BY=p_actor,LAST_ERROR=null where MOVEMENT_ID=m.MOVEMENT_ID;
   fact:=json_object_t();fact.put('movement_id',m.MOVEMENT_ID);fact.put('uid',v_target);fact.put('base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));
   fact.put('base_uom',v_base);facts.append(fact);
  end loop;
  result.put('operation_id',d.get_string('operation_id'));result.put('production_order_id',o.PRODUCTION_ORDER_ID);result.put('movements',facts);p_result:=result.to_clob;
 end;
end;
/

create or replace package body RRL_STOCK_INTERNAL_CMD as
 procedure compile_move(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t;v json_object_t:=json_object_t();
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();p RRL_PALLETS%rowtype;
  v_from varchar2(60);v_to varchar2(60);v_p number;v_qty number;v_base varchar2(20);v_ver number;
  v_ware number;v_source_ware number;v_target varchar2(200);v_uom_version number;v_sig varchar2(64);v_input varchar2(20);
 begin
  m:=d.get_object('metadata');m.on_error(1);
  select * into p from RRL_PALLETS where UID_PALLET=m.get_string('uid');
  v_to:=m.get_string('target_cell');
  if m.has('source_cell') and not m.get('source_cell').is_null then v_from:=m.get_string('source_cell');
  else select CELL into v_from from RRL_REMAINS where UID_POLETA=p.UID_PALLET and REMAIN>0;end if;
  select REMAIN,BASE_UOM,STOCK_VERSION into v_p,v_base,v_ver from RRL_REMAINS where UID_POLETA=p.UID_PALLET and CELL=v_from;
  select WARE_ID into v_ware from RRL_CELLS where CELL=v_to;
  select WARE_ID into v_source_ware from RRL_CELLS where CELL=v_from;
  if v_source_ware!=v_ware or v_ware is null then raise_application_error(-20886,'INTERNAL_WAREHOUSE_CONFLICT');end if;
  v_input:=nvl(m.get_string('unit'),v_base);
  if m.get_string('quantity')='0' then
   RRL_STOCK_PALLET_UOM.resolve_quantity(p.UID_PALLET,v_base,RRL_STOCK_PLAN_HELPER.decimal_text(v_p),v_base,v_qty,v_uom_version,v_sig);
  else RRL_STOCK_PALLET_UOM.resolve_quantity(p.UID_PALLET,v_input,m.get_string('quantity'),v_base,v_qty,v_uom_version,v_sig);end if;
  v_target:=p.UID_PALLET;
  if v_qty<v_p then v_target:='PART:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256));end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.stock_closure(f,r,p.UID_PALLET,p.ARTICUL,v_from,v_to);
  if p.PRIHOD_NAKLAD_ID is not null and p.PRIHOD_NAKLAD_ID>0 then
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PRIHOD_NAKLAD',RRL_STOCK_PLAN_HELPER.decimal_text(p.PRIHOD_NAKLAD_ID));
  end if;
  if v_target!=p.UID_PALLET then
   RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',v_target);RRL_STOCK_PLAN_HELPER.anchor(r,50,'STOCK',v_target);
   RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','PALLET:'||v_target);
  end if;
  v.put('uid',p.UID_PALLET);v.put('target_uid',v_target);v.put('article',p.ARTICUL);v.put('from',v_from);v.put('to',v_to);
  v.put('source_p',RRL_STOCK_PLAN_HELPER.decimal_text(v_p));v.put('stock_version',v_ver);v.put('base_uom',v_base);
  v.put('base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));v.put('uom_version',v_uom_version);v.put('uom_signature',v_sig);v.put('warehouse',v_ware);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_move(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t;v json_object_t;j json_object_t:=json_object_t();
  p RRL_PALLETS%rowtype;c RRL_CELLS%rowtype;v_plan clob;v_uid varchar2(200);v_target varchar2(200);
  v_p number;v_ver number;v_qty number;v_base varchar2(20);v_uom_version number;v_sig varchar2(64);
  v_n number;v_input varchar2(20);v_condition number;v_pick_cell varchar2(60);v_stop number;v_weight number;v_units clob;
 begin
  if RRL_HAS_WRIGHT(p_actor,'INTERNAL_MOVE')!=1 and RRL_HAS_WRIGHT(p_actor,'stock_posting_manual_move')!=1 then raise_application_error(-20882,'INTERNAL_MOVE_FORBIDDEN');end if;
  select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=d.get_string('operation_id');
  v:=json_object_t.parse(v_plan).get_object('domain');m:=d.get_object('metadata');
  v_uid:=v.get_string('uid');v_target:=v.get_string('target_uid');
  select * into p from RRL_PALLETS where UID_PALLET=v_uid;
  if p.ARTICUL!=v.get_string('article') then raise_application_error(-20890,'CLOSURE_CHANGED: pallet article');end if;
  select REMAIN,BASE_UOM,STOCK_VERSION into v_p,v_base,v_ver from RRL_REMAINS where UID_POLETA=v_uid and CELL=v.get_string('from');
  if v_ver!=v.get_number('stock_version') or RRL_STOCK_PLAN_HELPER.decimal_text(v_p)!=v.get_string('source_p') then raise_application_error(-20890,'CLOSURE_CHANGED: internal stock');end if;
  v_input:=nvl(m.get_string('unit'),v_base);
  if m.get_string('quantity')='0' then
   RRL_STOCK_PALLET_UOM.resolve_quantity(v_uid,v_base,RRL_STOCK_PLAN_HELPER.decimal_text(v_p),v_base,v_qty,v_uom_version,v_sig);
  else RRL_STOCK_PALLET_UOM.resolve_quantity(v_uid,v_input,m.get_string('quantity'),v_base,v_qty,v_uom_version,v_sig);end if;
  if v_sig!=v.get_string('uom_signature') or RRL_STOCK_PLAN_HELPER.decimal_text(v_qty)!=v.get_string('base_quantity') then raise_application_error(-20890,'CLOSURE_CHANGED: internal UOM');end if;
  if p.PRIHOD_NAKLAD_ID>0 then
   select CONDITION into v_condition from RRL_PRIHOD_NAKLAD where ID=p.PRIHOD_NAKLAD_ID for update;
   if v_condition in(0,1) then raise_application_error(-20886,'NAKLAD_NE_ZAKRYTA');end if;
  end if;
  select * into c from RRL_CELLS where CELL=v.get_string('to');
  if nvl(c.OTBOR,0)=0 and nvl(c.IS_SYSTEM,0)=0 then
   select count(*) into v_n from RRL_REMAINS where CELL=c.CELL and REMAIN>0 and UID_POLETA!=v_uid;
   if v_n>0 then raise_application_error(-20886,'CELL_NOT_EMPTY');end if;
  elsif nvl(c.OTBOR,0)=1 then
   select CELL into v_pick_cell from RRL_ARTICULS where ACTICUL=p.ARTICUL;
   if v_pick_cell is null or v_pick_cell!=c.CELL then raise_application_error(-20886,'OTBOR_DRUGOGO_ARTICULA');end if;
  end if;
  select nvl(WEIGHT_LIMIT_STOP,0) into v_stop from RRL_WARES where ID=c.WARE_ID;
  if v_stop=1 and c.LIMIT_WEIGHT is not null then
   if p.WEIGHT_BRUTTO is null or p.UNIT_COUNT is null or p.UNIT_COUNT<=0 then raise_application_error(-20886,'PALLET_WEIGHT_REQUIRED');end if;
   select nvl(sum(pp.WEIGHT_BRUTTO*rr.REMAIN/nullif(pp.UNIT_COUNT,0)),0) into v_weight
    from RRL_REMAINS rr join RRL_PALLETS pp on pp.UID_PALLET=rr.UID_POLETA where rr.CELL=c.CELL and rr.REMAIN>0;
   if v_weight+p.WEIGHT_BRUTTO*v_qty/p.UNIT_COUNT>c.LIMIT_WEIGHT then raise_application_error(-20886,'CELL_WEIGHT_LIMIT');end if;
  end if;
  if v_target!=v_uid then
   select count(*) into v_n from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=v_uid and STOCK_STATUS!='ISSUED';
   if v_n>0 then raise_application_error(-20884,'PARTIAL_MARKED_MOVE_REQUIRES_PHYSICAL_HU_SPLIT');end if;
   p.UID_PALLET:=v_target;p.SSCC:=null;p.UNIT_COUNT:=v_qty;p.PRINTED:=0;
   if p.WEIGHT_BRUTTO is not null then p.WEIGHT_BRUTTO:=p.WEIGHT_BRUTTO*v_qty/v_p;end if;
   insert into RRL_PALLETS values p;
  end if;
  if d.get_array('units').get_size>0 then v_units:=d.get_array('units').to_clob;end if;
  RRL_STOCK_TRANSFER_CORE.move(v_uid,v_target,v.get_string('from'),c.CELL,v_qty,v_base,v_uom_version,c.WARE_ID,p_actor,1,null,v_units);
  j.put('operation_id',d.get_string('operation_id'));j.put('status','APPLIED');j.put('source_uid',v_uid);j.put('uid',v_target);
  j.put('from_cell',v.get_string('from'));j.put('cell',c.CELL);j.put('base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));j.put('base_uom',v_base);
  p_result:=j.to_clob;
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

create or replace package body RRL_STOCK_RECEIPT_PLAN as
 procedure compile_receipt(p_request clob,p_operation varchar2,p_hints clob,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);s json_object_t;m json_object_t;h json_object_t;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();o RRL_SAP_SUPPLY_ORDER%rowtype;
  v_article varchar2(160);v_uid varchar2(200);v_task number;v_target varchar2(60);v_slot number;v_line varchar2(30);
 begin
  if p_hints is null or dbms_lob.getlength(p_hints)>4194304 then raise_application_error(-20871,'RECEIPT_PLAN_REQUIRED');end if;
  h:=json_object_t.parse(p_hints);s:=d.get_object('source');m:=d.get_object('metadata');
  select * into o from RRL_SAP_SUPPLY_ORDER where ORDER_ID=s.get_string('order_id');
  v_line:=m.get_string('line_number');
  select ARTICUL into v_article from RRL_SAP_SUPPLY_LINE where ORDER_ID=o.ORDER_ID and LINE_NUMBER=v_line;
  if h.get_string('article')!=v_article or h.get_number('order_revision')!=o.REVISION or h.get_number('naklad_id')!=o.NAKLAD_ID then
   raise_application_error(-20890,'CLOSURE_CHANGED: receipt source');end if;
  v_uid:=m.get_string('sscc');v_target:=h.get_object('placement').get_string('cell');v_slot:=h.get_object('placement').get_number('slot_id');
  if v_uid is null or v_target is null then raise_application_error(-20871,'RECEIPT_IDENTITY_REQUIRED');end if;
  select RRL_WAREHOUSE_TASK_SQ.nextval into v_task from dual;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SAP_SUPPLY_ORDER',o.ORDER_ID);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PRIHOD_NAKLAD',RRL_STOCK_PLAN_HELPER.decimal_text(o.NAKLAD_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SAP_SUPPLY_LINE',o.ORDER_ID||':'||v_line);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_task));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(v_task));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RECEIPT_LABEL',v_uid);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','PALLET:'||v_uid);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','SAP.RECEIPT:'||p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v_uid,v_article,o.RECEIVE_CELL,v_target);
  if v_slot is not null then RRL_STOCK_PLAN_HELPER.anchor(r,40,'SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(v_slot));end if;
  for u in(select UNIT_KEY from json_table(p_hints,'$.unit_bindings[*]' columns(UNIT_KEY varchar2(64) path '$.key'))) loop
   RRL_STOCK_PLAN_HELPER.anchor(r,60,'UNIT',u.UNIT_KEY);
  end loop;
  for a in(select SYSTEM_CODE,CODE_HASH from json_table(p_hints,'$.aliases[*]' columns(SYSTEM_CODE varchar2(40) path '$.system',CODE_HASH varchar2(64) path '$.hash'))) loop
   RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','MARK:'||a.SYSTEM_CODE||':'||a.CODE_HASH);
  end loop;
  RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',v_uid);
  for a in(select SYSTEM_CODE,CODE_HASH from json_table(p_hints,'$.aggregations[*]' columns(SYSTEM_CODE varchar2(40) path '$.system',CODE_HASH varchar2(64) path '$.hash'))) loop
   RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','AGG:'||a.SYSTEM_CODE||':'||a.CODE_HASH);
  end loop;
  h.put('task_id',v_task);h.put('warehouse_id',o.WARE_ID);h.put('receive_cell',o.RECEIVE_CELL);
  h.put('uid',v_uid);h.put('source_order_id',o.ORDER_ID);h.put('line_number',v_line);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=h.to_clob;
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
  RRL_STOCK_LOCATION_CORE.assert_ordinary(v_cell,o.WARE_ID,'TARGET');
  select count(*) into v_n from RRL_CELLS where CELL=v_cell and WARE_ID=o.WARE_ID and nvl(BLOCKED_FOR_ACCEPT,0)=0;
  if v_n!=1 then raise_application_error(-20886,'RECEIVING_CELL_BLOCKED');end if;
  RRL_STOCK_BALANCE_CORE.apply_delta(v_uid,v_cell,v_qty,0,v_base,v_uom_version);
  RRL_STOCK_UNIT_CORE.assert_composition(v_uid,v_cell);
  RRL_STOCK_BALANCE_CORE.write_leg(v_uid,null,v_cell,v_qty,v_base,v_uom_version,1,1,1,p_actor,v_event);
  v_response:=h.get_object('result');v_response.put('task_id',v_task);p_result:=v_response.to_clob;
  insert into RRL_SAP_PALLET_RECEIPT(OPERATION_ID,ORDER_ID,LINE_NUMBER,UID_PALLET,SUPPLIER_BATCH,PAYLOAD_HASH,RESULT_JSON,
   RECEIVED_BY,POSTED_BASE_QTY,STOCK_BASE_UOM,STOCK_OPERATION_ID)
   values(d.get_string('operation_id'),o.ORDER_ID,h.get_string('line_number'),v_uid,m.get_string('supplier_batch'),
    rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256)),p_result,p_actor,v_qty,v_base,d.get_string('operation_id'));
 end;
end;
/

create or replace package body RRL_STOCK_CONFIG_API as
 procedure begin_change(p_actor varchar2,p_permission varchar2) is
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();v_state varchar2(20);
 begin
  if p_actor is null or p_permission is null or p_permission not in('warehouse_settings_edit','finished_goods_edit')
   or RRL_HAS_WRIGHT(p_actor,p_permission)!=1 then raise_application_error(-20882,'CONFIGURATION_FORBIDDEN');end if;
  select STATE into v_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if v_state not in('PREPARED','ACTIVE') then raise_application_error(-20860,'CONFIGURATION_RELEASE_CLOSED');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE',6);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_POLICY_GUARD','WAREHOUSE.CONFIGURATION');
  RRL_STOCK_LOCK_API.begin_plan;RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  RRL_STOCK_CTX_API.open_configuration(p_actor,p_permission);
 end;
 procedure end_change is
 begin RRL_STOCK_CTX_API.clear_operation;RRL_STOCK_LOCK_API.clear_plan;end;
end;
/

create or replace package body RRL_STOCK_PALLET_UOM as
 procedure resolve_quantity(p_uid varchar2,p_input varchar2,p_quantity varchar2,
  p_base out varchar2,p_quantity_base out number,p_version out number,p_signature out varchar2) is
  p RRL_PALLETS%rowtype;v_input varchar2(20);v_stock_base varchar2(20);
  v_num number;v_den number;v_scale number;v_pack number;v_provenance varchar2(1000);
  v json_object_t:=json_object_t();
 begin
  select * into p from RRL_PALLETS where UID_PALLET=p_uid;
  select min(BASE_UOM),max(BASE_UOM) into v_stock_base,p_base from RRL_REMAINS where UID_POLETA=p_uid and REMAIN>0;
  if v_stock_base is null or p_base!=v_stock_base then raise_application_error(-20887,'PALLET_BASE_UOM_AMBIGUOUS');end if;
  v_input:=nvl(p_input,p_base);
  select max(POLICY_VERSION) into p_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=p.ARTICUL and INPUT_UOM=v_input;
  select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE into p_base,v_num,v_den,v_scale,v_provenance
   from RRL_STOCK_UOM_CONVERSION where ARTICUL=p.ARTICUL and INPUT_UOM=v_input and POLICY_VERSION=p_version;
  if p_base!=v_stock_base then raise_application_error(-20887,'PALLET_BASE_UOM_CONFLICT');end if;
  -- BOX arithmetic follows the actual pallet pack, never a rounded legacy box count.
  if upper(v_input) in ('BOX','KOR','КОР') then
   if upper(p_base) not in ('EA','PCS','ST','ШТ') then
    raise_application_error(-20887,'PALLET_BOX_REQUIRES_EXACT_BASE_ALLOCATION');
   end if;
   if nvl(p.MOD_ID,0)!=0 then
    select SHT_IN_KOR into v_pack from RRL_ARTICUL_MODS where ID=p.MOD_ID and ARTICUL=p.ARTICUL;
    v_provenance:='PALLET.MOD_ID';
   else
    select COUNT_SHT_IN_KOR into v_pack from RRL_ARTICULS where ACTICUL=p.ARTICUL;
    v_provenance:='ARTICLE.DEFAULT_PACK';
   end if;
   if v_pack is null or v_pack<1 or v_pack!=trunc(v_pack) or v_pack>1000000000 then
    raise_application_error(-20887,'PALLET_PACK_FACTOR_INVALID');
   end if;
   v_num:=v_pack;v_den:=1;
  end if;
  p_quantity_base:=RRL_STOCK_MATH.convert_exact(p_quantity,v_num,v_den,v_scale);
  v.put('uid',p_uid);v.put('article',p.ARTICUL);v.put('mod_id',p.MOD_ID);
  v.put('input',v_input);v.put('base',p_base);v.put('version',p_version);
  v.put('numerator',v_num);v.put('denominator',v_den);v.put('scale',v_scale);v.put('provenance',v_provenance);
  p_signature:=rawtohex(sys.dbms_crypto.hash(v.to_clob,sys.dbms_crypto.hash_sh256));
 end;
end;
/

create or replace package body RRL_STOCK_POSTING_API as
 g_request clob;g_resolution clob;g_actor varchar2(50);g_operation varchar2(100);g_kind varchar2(80);g_tx varchar2(100);g_prepared boolean:=false;
 procedure reset_connection is
 begin
  RRL_STOCK_CTX_API.clear_operation;RRL_STOCK_LOCK_API.clear_plan;
  g_request:=null;g_resolution:=null;g_actor:=null;g_operation:=null;g_kind:=null;g_tx:=null;g_prepared:=false;
 end;
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null) is
  v_doc json_object_t;v_policies clob;v_resources clob;v_exists number;v_release varchar2(20);v_domain clob;v_resolution json_object_t:=json_object_t();
  v_plan json_array_t:=json_array_t();v_entry json_object_t:=json_object_t();v_resources_json json_array_t:=json_array_t();
 begin
  p_replay:=null;
  if g_prepared or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is not null then
   raise_application_error(-20862,'POSTING_ALREADY_ENTERED');
  end if;
  if p_request is null or dbms_lob.getlength(p_request)>4194304 then raise_application_error(-20871,'OPERATION_CONTRACT_INVALID'); end if;
  v_doc:=json_object_t.parse(p_request);v_doc.on_error(1);
  g_operation:=v_doc.get_string('operation_id');g_kind:=v_doc.get_string('command_type');
  if v_doc.get_number('contract_version') is null or v_doc.get_number('contract_version')!=2 or v_doc.get_string('actor') is null
   or v_doc.get_string('actor')!=p_actor or p_actor is null or length(p_actor)>50
   or g_operation is null or length(g_operation)>100 or g_kind is null then
   raise_application_error(-20871,'OPERATION_CONTRACT_INVALID');
  end if;
  -- Immutable committed replay is considered before any mutable article/cell/UOM validation.
  select count(*) into v_exists from RRL_STOCK_OPERATION where OPERATION_ID=g_operation;
  if v_exists!=0 then
   v_entry.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key('RELEASE','STOCK')));v_entry.put('mode',4);v_plan.append(v_entry);
   v_entry:=json_object_t();v_entry.put('rank',10);
   v_entry.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key('OP',g_operation)));v_resources_json.append(v_entry);
   v_policies:=v_plan.to_clob;v_resources:=v_resources_json.to_clob;
  else
   if g_kind='MANUAL_MOVE' then RRL_STOCK_COMMAND_PLAN.compile_move(p_request,g_operation,v_policies,v_resources);
   elsif g_kind in('SHIP_DOCUMENT','SHIP_PALLET') then RRL_STOCK_SHIPPING_CORE.compile_shipment(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='INTERNAL_MOVE' then RRL_STOCK_INTERNAL_CMD.compile_move(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='MES_MOVEMENTS' then RRL_STOCK_MES_MOVEMENT_PLAN.compile_movements(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='SAP_RECEIPT' then RRL_STOCK_RECEIPT_PLAN.compile_receipt(p_request,g_operation,p_hints,v_policies,v_resources,v_domain);
   elsif g_kind='TASK_COMPLETE' then RRL_STOCK_TASK_PLAN.compile_task(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in('RESERVATION_CREATE','RESERVATION_PROMOTE','RESERVATION_RELEASE','RESERVATION_CANCEL','RESERVATION_CONSUME') then RRL_STOCK_RESERVATION_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   else raise_application_error(-20888,'COMMAND_HANDLER_NOT_INSTALLED');end if;
  end if;
  RRL_STOCK_LOCK_API.begin_plan;
  RRL_STOCK_LOCK_API.acquire_policies(v_policies);
  RRL_STOCK_LOCK_API.acquire_resources(v_resources);
  select STATE into v_release from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if v_release!='ACTIVE' then raise_application_error(-20860,'STOCK_RELEASE_NOT_ACTIVE'); end if;
  if v_domain is not null then v_resolution.put('domain',json_object_t.parse(v_domain));end if;
  v_resolution.put('stock_before',json_array_t.parse(RRL_STOCK_INVARIANT_CORE.snapshot_stock(v_resources)));
  v_resolution.put('resources',json_array_t.parse(v_resources));
  v_resolution.put('policies',json_array_t.parse(v_policies));
  RRL_STOCK_OPERATION_CORE.begin_operation(p_request,p_actor,g_operation,g_kind,p_replay,v_resolution.to_clob);
  if p_replay is not null then return; end if;
  g_request:=p_request;g_resolution:=v_resolution.to_clob;g_actor:=p_actor;g_tx:=dbms_transaction.local_transaction_id(false);g_prepared:=true;
  if g_kind='SAP_RECEIPT' then RRL_STOCK_CTX_API.begin_staging(v_resolution.get_object('domain').get_string('uid'),v_resolution.get_object('domain').get_string('receive_cell'));end if;
 end;
 procedure execute_prepared(p_result out clob) is
  v_outbox number;v_existing number;v_key varchar2(100);v_json json_object_t;v_resolved json_object_t;
 begin
  if not g_prepared or g_tx is null or dbms_transaction.local_transaction_id(false) is null
   or g_tx!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20850,'WRITE_PLAN_VIOLATION'); end if;
  if g_kind='SAP_RECEIPT' then RRL_STOCK_CTX_API.end_effect;end if;
  if g_kind='MANUAL_MOVE' then RRL_STOCK_MOVE_CORE.manual_whole(g_request,g_actor,p_result);
  elsif g_kind in('SHIP_DOCUMENT','SHIP_PALLET') then RRL_STOCK_SHIPPING_CORE.execute_shipment(g_request,g_actor,p_result);
  elsif g_kind='INTERNAL_MOVE' then RRL_STOCK_INTERNAL_CMD.execute_move(g_request,g_actor,p_result);
  elsif g_kind='MES_MOVEMENTS' then RRL_STOCK_MES_MOVEMENT_CORE.execute_movements(g_request,g_actor,p_result);
  elsif g_kind='SAP_RECEIPT' then RRL_STOCK_RECEIPT_CORE.execute_receipt(g_request,g_actor,p_result);
  elsif g_kind='TASK_COMPLETE' then RRL_STOCK_TASK_CORE.execute_task(g_request,g_actor,p_result);
  elsif g_kind in('RESERVATION_CREATE','RESERVATION_PROMOTE','RESERVATION_RELEASE','RESERVATION_CANCEL','RESERVATION_CONSUME') then RRL_STOCK_RESERVATION_CMD.execute_command(g_request,g_actor,p_result);
  else raise_application_error(-20888,'COMMAND_HANDLER_NOT_INSTALLED'); end if;
  v_resolved:=json_object_t.parse(g_resolution);
  RRL_STOCK_INVARIANT_CORE.verify_posting(v_resolved.get_array('resources').to_clob,v_resolved.get_array('stock_before').to_clob,g_operation);
  v_key:='STOCK:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(g_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256));
  RRL_STOCK_LOCK_API.assert_held(70,RRL_STOCK_LOCK_API.resource_key('UNIQUE','STOCK.OUTBOX:'||substr(v_key,7)));
  select count(*) into v_existing from RRL_EVENT_OUTBOX where IDEMPOTENCY_KEY=v_key;
  if v_existing!=0 then raise_application_error(-20889,'OUTBOX_IDENTITY_CONFLICT'); end if;
  v_outbox:=RRL_TRACEABILITY_API.enqueue_event('STOCK_POSTED','STOCK_OPERATION',g_operation,v_key,p_result,'WMS',g_operation);
  v_json:=json_object_t.parse(p_result);v_json.put('outbox_id',v_outbox);p_result:=v_json.to_clob;
  RRL_STOCK_OPERATION_CORE.finish_operation(g_operation,p_result);
  g_prepared:=false;
 end;
end;
/
