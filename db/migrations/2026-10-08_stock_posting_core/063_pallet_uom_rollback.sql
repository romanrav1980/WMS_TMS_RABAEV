declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
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
  v_task_id number;v_residual number;v_reservation number;v_new_reservation number;v_fact number;v_pick_task number;v_movement_id number;v_sync_id number;v_sync_key varchar2(400);v_from_ware number;v_to_ware number;v_source_p number;v_base varchar2(20);v_input varchar2(20);v_qbase number;v_num number;v_den number;v_scale number;v_uom_version number;
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
  select max(POLICY_VERSION) into v_uom_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_input;
  select NUMERATOR,DENOMINATOR,BASE_SCALE into v_num,v_den,v_scale from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_input and POLICY_VERSION=v_uom_version;
  v_qbase:=RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(v_fact),v_num,v_den,v_scale);
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
  v_domain.put('source_p',RRL_STOCK_PLAN_HELPER.decimal_text(v_source_p));v_domain.put('uom_version',v_uom_version);v_domain.put('base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qbase));
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
  v_result json_object_t:=json_object_t();v_resource number;v_session number;v_equipment number;v_sync_id number;v_sync_key varchar2(400);v_session_actor varchar2(100);v_input_uom varchar2(20);v_source_p number;
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
  select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_input_uom;
  select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into v_base,v_factor_num,v_factor_den,v_scale
   from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_input_uom and POLICY_VERSION=v_version;
  v_qbase:=RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(v_qty),v_factor_num,v_factor_den,v_scale);
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
