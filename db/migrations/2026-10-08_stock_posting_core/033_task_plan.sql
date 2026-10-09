create or replace package RRL_STOCK_TASK_PLAN authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE) as
 procedure compile_task(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 function signature(p_task RRL_WAREHOUSE_TASK%rowtype) return varchar2;
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
  v_task_id number;v_residual number;v_reservation number;v_new_reservation number;v_fact number;v_pick_task number;v_movement_id number;v_sync_id number;v_sync_key varchar2(400);v_from_ware number;v_to_ware number;v_source_p number;v_base varchar2(20);v_input varchar2(20);v_sap_order varchar2(100);v_sap_line varchar2(40);v_qbase number;v_num number;v_den number;v_scale number;v_uom_version number;v_uom_signature varchar2(64);
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
   select ORDER_ID,LINE_NUMBER into v_sap_order,v_sap_line from RRL_SAP_PALLET_RECEIPT where UID_PALLET=v_uid;
   RRL_STOCK_PLAN_HELPER.row_key(v_r,'RRL_SAP_SUPPLY_ORDER',v_sap_order);
   v_domain.put('sap_order_id',v_sap_order);v_domain.put('sap_line_number',v_sap_line);
   RRL_STOCK_PLAN_HELPER.anchor(v_r,70,'UNIQUE','SAP.OUTBOX:PUTAWAY:'||RRL_STOCK_PLAN_HELPER.decimal_text(v_task_id));
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
