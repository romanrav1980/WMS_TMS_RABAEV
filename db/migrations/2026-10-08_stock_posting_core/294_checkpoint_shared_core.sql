create or replace package RRL_STOCK_TASK_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure execute_task(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_STOCK_TASK_CORE as
 procedure validate_metadata(p_meta json_object_t) is
  v_keys json_key_list:=p_meta.get_keys;v_value json_element_t;v_key varchar2(4000);
 begin
  for i in 1..v_keys.count loop
   v_key:=v_keys(i);v_value:=p_meta.get(v_key);
   if not v_value.is_null then
    if v_key in('resource_id','resource_session_id','equipment_id','document_confirmation') then
     if not v_value.is_number then raise_application_error(-20881,'TASK_METADATA_NUMBER_REQUIRED:'||v_key);end if;
     if v_key!='document_confirmation' and (p_meta.get_number(v_key)<=0 or p_meta.get_number(v_key)!=trunc(p_meta.get_number(v_key))) then
      raise_application_error(-20881,'TASK_RESOURCE_ID_INVALID:'||v_key);end if;
    elsif v_key in('scan_draft_id','scanned_pallet','scanned_from_cell','scanned_to_cell') then
     if not v_value.is_string then raise_application_error(-20881,'TASK_METADATA_STRING_REQUIRED:'||v_key);end if;
    elsif v_key='fact_qty' then
     if not v_value.is_string and not v_value.is_number then raise_application_error(-20881,'TASK_FACT_QUANTITY_TYPE');end if;
    elsif v_key='unit_keys' then
     if not v_value.is_array then raise_application_error(-20881,'TASK_UNIT_KEYS_ARRAY_REQUIRED');end if;
    end if;
   end if;
  end loop;
 end;
 procedure execute_task(p_request clob,p_actor varchar2,p_result out clob) is
  v_doc json_object_t:=json_object_t.parse(p_request);v_meta json_object_t;v_source json_object_t;v_domain json_object_t;v_context json_object_t;
  v_plan clob;v_task RRL_WAREHOUSE_TASK%rowtype;v_residual RRL_WAREHOUSE_TASK%rowtype;v_pallet RRL_PALLETS%rowtype;
  v_task_id number;v_qty number;v_original number;v_qbase number;v_target varchar2(200);v_base varchar2(20);
  v_factor_num number;v_factor_den number;v_scale number;v_version number;v_article varchar2(160);
  v_delivered_reservation number;v_residual_id number;v_reservation number;v_new_reservation number;v_ware number;v_pick_task number;
  v_signature varchar2(64);v_hash varchar2(64);v_op varchar2(100);v_units clob;v_n number;v_doc_status varchar2(40);
  v_result json_object_t:=json_object_t();v_resource number;v_session number;v_equipment number;v_sync_id number;v_sync_key varchar2(400);v_session_actor varchar2(100);v_input_uom varchar2(20);v_source_p number;v_uom_signature varchar2(64);v_sap_header number;v_sap_cell varchar2(60);v_sap_ware number;v_document_confirmation number:=0;
 begin
  v_doc.on_error(1);v_source:=v_doc.get_object('source');v_meta:=v_doc.get_object('metadata');v_meta.on_error(0); -- Oracle 19c HAS raises for missing keys with nonzero error modes.
  validate_metadata(v_meta);
  if v_meta.has('document_confirmation') then v_document_confirmation:=nvl(v_meta.get_number('document_confirmation'),0);end if;
  v_op:=v_doc.get_string('operation_id');v_task_id:=v_source.get_number('task_id');
  
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_task_id)));
  select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
  v_domain:=json_object_t.parse(v_plan).get_object('domain');
  -- Existing assignment/start commands lock the source document before the task.
  -- Read identity without a row lock, validate the planned signature, then use the same order.
  select * into v_task from RRL_WAREHOUSE_TASK where TASK_ID=v_task_id;
  if v_document_confirmation=1 then
   if v_task.TASK_SOURCE!='MES_RAW_SUPPLY' or RRL_HAS_WRIGHT(p_actor,'mes_raw_transfer_confirm')!=1 then raise_application_error(-20882,'MES_DOCUMENT_CONFIRM_FORBIDDEN');end if;
  elsif RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 then raise_application_error(-20882,'TASK_COMPLETE_FORBIDDEN');end if;
  if RRL_STOCK_TASK_PLAN.signature(v_task)!=v_domain.get_string('task_signature') then raise_application_error(-20890,'CLOSURE_CHANGED: task source');end if;
  if v_task.TASK_SOURCE='WAVE' then
   select STATUS into v_doc_status from RRL_PICK_WAVE where PICK_WAVE_ID=v_task.SOURCE_DOC_ID for update;
   if v_doc_status is null or v_doc_status!='LAUNCHED' then raise_application_error(-20886,'WAVE_PHYSICAL_EXECUTION_REQUIRES_LAUNCHED');end if;
  elsif v_task.TASK_SOURCE in('MES_RAW_SUPPLY','MES_COMPLETION') then
   select STATUS into v_doc_status from RRL_PRODUCTION_ORDER where PRODUCTION_ORDER_ID=nvl(v_task.PRODUCTION_ORDER_ID,v_task.SOURCE_DOC_ID) for update;
  elsif v_task.TASK_SOURCE='SAP_RECEIPT' then
   declare
 v_json_sql_1_1 varchar2(32767):=v_domain.get_string('sap_order_id');
begin
select NAKLAD_ID,RECEIVE_CELL,WARE_ID into v_sap_header,v_sap_cell,v_sap_ware from RRL_SAP_SUPPLY_ORDER where ORDER_ID=v_json_sql_1_1 for update;
end;
   if v_sap_header!=v_task.SOURCE_DOC_ID or v_sap_cell!=v_task.FROM_CELL or v_sap_ware!=v_domain.get_number('from_ware_id') then raise_application_error(-20890,'CLOSURE_CHANGED: putaway source order');end if;
   select to_char(CONDITION) into v_doc_status from RRL_PRIHOD_NAKLAD where ID=v_task.SOURCE_DOC_ID for update;
  end if;
  select * into v_task from RRL_WAREHOUSE_TASK where TASK_ID=v_task_id for update;
  if RRL_STOCK_TASK_PLAN.signature(v_task)!=v_domain.get_string('task_signature') then
   raise_application_error(-20890,'CLOSURE_CHANGED: task identity');
  end if;
  if v_task.STATUS is null or v_task.STATUS not in('PLANNED','ASSIGNED','IN_PROGRESS') then
   raise_application_error(-20886,'TASK_STATE_CONFLICT');end if;
  v_task.FROM_WARE_ID:=v_domain.get_number('from_ware_id');v_task.TO_WARE_ID:=v_domain.get_number('to_ware_id');
  if v_task.FROM_WARE_ID is null or v_task.TO_WARE_ID is null or (v_task.FROM_WARE_ID!=v_task.TO_WARE_ID and v_task.TASK_SOURCE not in('MES_RAW_SUPPLY','MES_COMPLETION')) then
   raise_application_error(-20886,'INTERWAREHOUSE_COMMAND_REQUIRED');end if;
  if v_document_confirmation!=1 and (upper(trim(v_meta.get_string('scanned_pallet'))) is null or
   trim(v_meta.get_string('scanned_pallet')) not in(nvl(v_task.UID_PALLET,v_task.SSCC),nvl(v_task.SSCC,v_task.UID_PALLET))
   or upper(trim(v_meta.get_string('scanned_from_cell'))) is null or upper(trim(v_meta.get_string('scanned_from_cell')))!=upper(v_task.FROM_CELL)
   or upper(trim(v_meta.get_string('scanned_to_cell'))) is null or upper(trim(v_meta.get_string('scanned_to_cell')))!=upper(v_task.TO_CELL)) then
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
  if v_task.TASK_SOURCE='WAVE' and v_task.TASK_TYPE='PICKING_MOVE' and v_task.QTY_MODE='PALLET' then
   select count(*) into v_n from RRL_STOCK_RESERVATION where UID_PALLET=v_pallet.UID_PALLET and CELL=v_task.FROM_CELL
    and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING') and
      (SOURCE_DOC_TYPE is null or SOURCE_DOC_TYPE!='PICK_WAVE' or SOURCE_DOC_ID is null or SOURCE_DOC_ID!=v_task.SOURCE_DOC_ID
       or SOURCE_LINE_ID is null or SOURCE_LINE_ID!=v_pick_task or RESERVATION_DOMAIN is null or RESERVATION_DOMAIN!='PICKING');
   if v_n>0 then raise_application_error(-20869,'FULLPAL_OTHER_OWNER_RESERVATION');end if;
   select nvl(sum(BASE_QTY),0) into v_n from RRL_STOCK_RESERVATION where UID_PALLET=v_pallet.UID_PALLET and CELL=v_task.FROM_CELL
    and SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=v_task.SOURCE_DOC_ID and SOURCE_LINE_ID=v_pick_task
    and RESERVATION_DOMAIN='PICKING' and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING');
   if v_n!=v_qbase then raise_application_error(-20869,'FULLPAL_WHOLE_OWNED_RESERVATION_REQUIRED');end if;
  end if;
  if v_task.TASK_SOURCE='WAVE' then
   RRL_STOCK_ELIGIBILITY.assert_source(v_pallet.UID_PALLET,v_task.FROM_CELL,v_task.FROM_WARE_ID,case when v_task.QTY_MODE='PALLET' and v_task.TASK_TYPE in('REPLENISHMENT','PICKING_MOVE') and v_reservation is not null then 0 else v_qbase end,null,null,
    case when v_task.TASK_TYPE='REPLENISHMENT' then 'REPLENISH' else 'ALLOCATE' end,v_reservation,v_article);
  end if;
  if v_task.TASK_SOURCE='WAVE' then
   select STATUS into v_doc_status from RRL_PICK_WAVE where PICK_WAVE_ID=v_task.SOURCE_DOC_ID for update;
   if v_doc_status is null or v_doc_status!='LAUNCHED' then raise_application_error(-20886,'WAVE_PHYSICAL_EXECUTION_REQUIRES_LAUNCHED');end if;
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
  RRL_STOCK_TASK_SCAN.assert_draft(p_request,v_task_id,nvl(v_task.UID_PALLET,v_task.SSCC),v_task.FROM_CELL,p_actor);
  if v_meta.has('unit_keys') and not v_meta.get('unit_keys').is_null and v_meta.get_array('unit_keys').get_size>0 then v_units:=v_meta.get_array('unit_keys').to_clob;end if;
  if v_task.TASK_SOURCE='WAVE' and v_task.TASK_TYPE='REPLENISHMENT' then
   if v_task.QTY_MODE='PALLET' then
    select count(*) into v_n from RRL_STOCK_RESERVATION where UID_PALLET=nvl(v_task.UID_PALLET,v_task.SSCC) and CELL=v_task.FROM_CELL
     and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>0 and RESERVATION_ID!=v_reservation;
    if v_n>0 then raise_application_error(-20886,'WHOLE_REPLENISHMENT_OTHER_RESERVATION');end if;
   end if;
   RRL_STOCK_REPL_CAPACITY.assert_arrival(v_task.SOURCE_TASK_ID,v_qbase);
   RRL_STOCK_REPL_ADMISSION.assert_target(nvl(v_task.UID_PALLET,v_task.SSCC),v_task.TO_CELL,v_task.TO_WARE_ID,v_article);
  end if;
  RRL_STOCK_TRANSFER_CORE.move(nvl(v_task.UID_PALLET,v_task.SSCC),v_target,v_task.FROM_CELL,v_task.TO_CELL,
   v_qbase,v_base,v_version,v_task.TO_WARE_ID,p_actor,1,v_reservation,v_units,v_new_reservation,v_task.TO_CELL_SLOT_ID,v_task.FROM_WARE_ID,case when v_task.TASK_SOURCE='SAP_RECEIPT' then 'PUTAWAY' else 'ORDINARY' end);
  if v_task.TASK_SOURCE='WAVE' and v_task.TASK_TYPE='REPLENISHMENT' then
   select case when UID_PALLET=v_target and CELL=v_task.TO_CELL then RESERVATION_ID else v_new_reservation end
    into v_delivered_reservation from RRL_STOCK_RESERVATION where RESERVATION_ID=v_reservation;
   RRL_STOCK_REPL_BIND.execute_bind(v_task,v_target,v_delivered_reservation,v_domain.get_object('consumer_bindings'),p_actor);
  end if;
  v_resource:=v_meta.get_number('resource_id');v_session:=v_meta.get_number('resource_session_id');v_equipment:=v_meta.get_number('equipment_id');
  if v_document_confirmation!=1 and v_session is null and v_task.ASSIGNED_TO=p_actor then v_session:=v_task.RESOURCE_SESSION_ID;end if;
  for ses in(select SESSION_ID from RRL_RESOURCE_SESSION where SESSION_ID in(v_session,v_task.RESOURCE_SESSION_ID) order by SESSION_ID for update) loop
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_RESOURCE_SESSION',RRL_STOCK_PLAN_HELPER.decimal_text(ses.SESSION_ID)));
  end loop;
  v_context:=json_object_t.parse(RRL_TASK_RESOURCE_POLICY.context_json(v_task_id,case when v_document_confirmation=1 then 'COMPLETE_DOCUMENT' else 'COMPLETE' end,p_actor,p_actor,
   v_meta.get_number('resource_id'),v_meta.get_number('resource_session_id'),v_meta.get_number('equipment_id')));
  if dbms_lob.compare(v_context.to_clob,v_domain.get_object('resource_context').to_clob)!=0 then
   raise_application_error(-20890,'CLOSURE_CHANGED: task resource context');end if;
  v_resource:=v_context.get_number('resource_id');v_session:=v_context.get_number('resource_session_id');v_equipment:=v_context.get_number('equipment_id');
  v_hash:=rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256));
  if v_residual_id is not null then
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_residual_id)));
   v_residual:=v_task;v_residual.TASK_ID:=v_residual_id;v_residual.QTY:=v_original-v_qty;
   v_residual.PARENT_TASK_ID:=v_task_id;v_residual.STATUS:='PLANNED';v_residual.FACT_QTY:=null;
   v_residual.CREATED_BY:=p_actor;v_residual.CREATED_AT:=systimestamp;v_residual.COMPLETION_HASH:=null;
   v_residual.COMPLETION_JSON:=null;v_residual.FINISHED_AT:=null;v_residual.ASSIGNED_TO:=null;
   v_residual.STARTED_AT:=null;v_residual.STARTED_AT_INSTANT:=null;v_residual.STARTED_SHIFT_TIME_ZONE:=null;v_residual.TARGET_UID_PALLET:=null;
   v_residual.RESOURCE_ID:=null;v_residual.RESOURCE_SESSION_ID:=null;v_residual.EQUIPMENT_ID:=null;
   v_residual.PLANNED_START_AT:=null;v_residual.PLANNED_FINISH_AT:=case when v_task.PRIORITY=0 then v_task.PLANNED_FINISH_AT else null end;v_residual.LAST_ERROR:='Residual of task '||v_task_id;
   insert into RRL_WAREHOUSE_TASK values v_residual;
  end if;
  update RRL_WAREHOUSE_TASK set STATUS='DONE',QTY=v_qty,FACT_QTY=v_qty,TARGET_UID_PALLET=v_target,
   FROM_WARE_ID=v_task.FROM_WARE_ID,TO_WARE_ID=v_task.TO_WARE_ID,FINISHED_AT=systimestamp,ASSIGNED_TO=p_actor,RESOURCE_ID=v_resource,
   RESOURCE_SESSION_ID=v_session,EQUIPMENT_ID=v_equipment,
   COMPLETION_HASH=v_hash,COMPLETION_JSON=p_request,LAST_ERROR=null where TASK_ID=v_task_id;
  insert into RRL_WAREHOUSE_TASK_STOCK_MOVE(STOCK_MOVE_ID,TASK_ID,TASK_SOURCE,TASK_TYPE,SOURCE_DOC_TYPE,SOURCE_DOC_ID,
   SOURCE_TASK_ID,UID_PALLET,TARGET_UID_PALLET,FROM_CELL,TO_CELL,QTY,BASE_QTY,BASE_UOM,OPERATION_ID,CREATED_AT,CREATED_BY)
   values(RRL_WH_TASK_STOCK_MOVE_SQ.nextval,v_task_id,v_task.TASK_SOURCE,v_task.TASK_TYPE,v_task.SOURCE_DOC_TYPE,v_task.SOURCE_DOC_ID,
    v_task.SOURCE_TASK_ID,nvl(v_task.UID_PALLET,v_task.SSCC),v_target,v_task.FROM_CELL,v_task.TO_CELL,v_qty,v_qbase,v_base,v_op,systimestamp,p_actor);
  if v_resource is not null or v_session is not null or v_equipment is not null then
   insert into RRL_RESOURCE_FACT_EVENT(EVENT_ID,TASK_ID,SESSION_ID,RESOURCE_ID,EVENT_TYPE,EVENT_AT,EVENT_BY,PAYLOAD_JSON)
    values(RRL_RESOURCE_FACT_EVENT_SQ.nextval,v_task_id,v_session,v_resource,'COMPLETED',systimestamp,p_actor,p_request);
  end if;
  update RRL_RESOURCE_SESSION set CURRENT_TASK_ID=null
   where SESSION_ID in(v_session,v_task.RESOURCE_SESSION_ID) and CURRENT_TASK_ID=v_task_id;
  if v_session is not null then
   update RRL_RESOURCE_SESSION set LAST_CELL=v_task.TO_CELL,LAST_POSITION_AT=systimestamp,
    LAST_HEARTBEAT_AT=systimestamp where SESSION_ID=v_session and OPERATOR_USER_ID=p_actor;
  end if;
  RRL_STOCK_TASK_DOMAIN.sync_fact(v_task,v_qty,v_target,v_residual_id,p_actor);
  RRL_STOCK_REPL_CONTINUATION.create_next(v_task,v_domain,p_actor);
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
  v_result.put('remaining_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_original-v_qty));
  v_result.put('residual_task_id',v_residual_id);v_result.put('movement_id',v_domain.get_number('new_movement_id'));p_result:=v_result.to_clob;
  if v_task.TASK_SOURCE='SAP_RECEIPT' then
   v_result.put('order_id',v_domain.get_string('sap_order_id'));v_result.put('line_number',v_domain.get_string('sap_line_number'));
   v_result.put('article',v_article);p_result:=v_result.to_clob;
   insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)
    values('PUTAWAY:'||RRL_STOCK_PLAN_HELPER.decimal_text(v_task_id),'PALLET_PUTAWAY',p_result);
  end if;
 end;
end;
/
