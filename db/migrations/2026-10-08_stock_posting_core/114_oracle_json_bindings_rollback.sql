declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_RESERVE_CORE authid definer
 accessible by(package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_STOCK_MES_CANCEL_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_WAVE_CMD,package RRL_STOCK_EFFECT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,package RRL_STOCK_TRANSFER_CORE) as
 procedure create_hard(p_id number,p_uid varchar2,p_cell varchar2,p_qty number,p_uom varchar2,p_uom_version number,
   p_doc_type varchar2,p_doc_id number,p_line_id number,p_domain varchar2,p_actor varchar2,p_details clob default null);
 procedure release_hard(p_id number,p_qty number,p_uom_version number,p_doc_type varchar2,p_doc_id number,p_actor varchar2);
 procedure consume_hard(p_id number,p_qty number,p_uom_version number,p_doc_type varchar2,p_doc_id number,p_actor varchar2);
 procedure relocate_hard(p_id number,p_new_id number,p_target_uid varchar2,p_target_cell varchar2,
   p_qty number,p_uom_version number,p_actor varchar2);
 procedure move_coverage(p_id number,p_new_id number,p_target_uid varchar2,p_target_cell varchar2,
  p_target_ware number,p_qty number,p_target_slot number,p_actor varchar2,p_result_id out number);
end;
/

create or replace package RRL_STOCK_TASK_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure execute_task(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_RESERVATION_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
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

create or replace package RRL_STOCK_MES_MOVEMENT_PLAN authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_MES_MOVEMENT_CORE) as
 function signature(p_m RRL_MES_MOVEMENT%rowtype) return varchar2;
 procedure compile_movements(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
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

create or replace package RRL_STOCK_SHIPPING_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_shipment(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_shipment(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_WAVE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_reserve(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_reserve(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_DOC_RESERVE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_release(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_release(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_MES_SUPPLY_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_MES_CANCEL_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_EVENT_BRIDGE authid definer
 accessible by(trigger "BIN$UX1xZvUbS6/gYw8CAAo/Yg==$0") as
 procedure after_event(p_operation varchar2,p_line number,p_leg number,p_uid varchar2,p_from varchar2,p_to varchar2,
  p_qty number,p_uom varchar2,p_uom_version number,p_type number);
end;
/

create or replace package RRL_STOCK_INVENTORY_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_count(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_count(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_WAVE_LAUNCH_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_STOCK_RESERVE_CORE as
 procedure lock_identity(p_id number) is
 begin
  if p_id is null or p_id<1 or p_id!=trunc(p_id) then raise_application_error(-20876,'RESERVATION_ID_INVALID'); end if;
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STOCK_RESERVATION',to_char(p_id,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')));
 end;
 procedure check_owner(p_id number,p_qty number,p_doc_type varchar2,p_doc_id number,p_r out RRL_STOCK_RESERVATION%rowtype) is
 begin
  lock_identity(p_id);
  select * into p_r from RRL_STOCK_RESERVATION where RESERVATION_ID=p_id for update;
  if p_r.RESERVATION_KIND is null or p_r.RESERVATION_KIND!='HARD' or p_r.STATUS is null or p_r.STATUS not in('ACTIVE','ALLOCATED','PICKING')
   or p_r.BASE_QTY is null or p_r.BASE_UOM is null or p_qty is null or p_qty<=0 or p_qty>p_r.BASE_QTY
   or p_doc_type is null or p_doc_id is null or p_r.SOURCE_DOC_TYPE is null or p_r.SOURCE_DOC_ID is null or p_r.SOURCE_DOC_TYPE!=p_doc_type or p_r.SOURCE_DOC_ID!=p_doc_id then
   raise_application_error(-20869,'RESERVATION_CONFLICT');
  end if;
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_r.UID_PALLET));
 end;
 procedure decrease(p_r RRL_STOCK_RESERVATION%rowtype,p_qty number,p_status varchar2,p_actor varchar2) is
 begin
  RRL_STOCK_CTX_API.begin_effect('RESERVATION',p_r.UID_PALLET,p_r.CELL,p_r.RESERVATION_ID);
  update RRL_STOCK_RESERVATION set BASE_QTY=BASE_QTY-p_qty,QTY=BASE_QTY-p_qty,UNIT_CODE=BASE_UOM,
   STATUS=case when BASE_QTY=p_qty then p_status else STATUS end,
   CONSUMED_AT=case when BASE_QTY=p_qty and p_status='CONSUMED' then systimestamp else CONSUMED_AT end,
   CONSUMED_BY=case when BASE_QTY=p_qty and p_status='CONSUMED' then p_actor else CONSUMED_BY end,
   RELEASED_AT=case when BASE_QTY=p_qty and p_status='RELEASED' then systimestamp else RELEASED_AT end,
   RELEASED_BY=case when BASE_QTY=p_qty and p_status='RELEASED' then p_actor else RELEASED_BY end,
   RESERVATION_VERSION=RESERVATION_VERSION+1
   where RESERVATION_ID=p_r.RESERVATION_ID and RESERVATION_VERSION=p_r.RESERVATION_VERSION;
  if sql%rowcount!=1 then raise_application_error(-20867,'VERSION_CONFLICT'); end if;
  RRL_STOCK_CTX_API.end_effect;
 end;
 procedure create_hard(p_id number,p_uid varchar2,p_cell varchar2,p_qty number,p_uom varchar2,p_uom_version number,
   p_doc_type varchar2,p_doc_id number,p_line_id number,p_domain varchar2,p_actor varchar2,p_details clob default null) is v_article varchar2(160);v_ware number;v_details json_object_t;
 begin
  lock_identity(p_id);
  select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=p_uid;
  select WARE_ID into v_ware from RRL_CELLS where CELL=p_cell;
  if p_qty is null or p_qty<=0 or p_doc_id is null or p_doc_type is null or p_domain is null then raise_application_error(-20869,'RESERVATION_CONFLICT'); end if;
  RRL_STOCK_BALANCE_CORE.apply_delta(p_uid,p_cell,0,p_qty,p_uom,p_uom_version);
  RRL_STOCK_CTX_API.begin_effect('RESERVATION',p_uid,p_cell,p_id);
  insert into RRL_STOCK_RESERVATION(RESERVATION_ID,RESERVATION_KIND,RESERVATION_SCOPE,RESERVATION_DOMAIN,
   SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_LINE_ID,ARTICUL,QTY,UNIT_CODE,WARE_ID,CELL,UID_PALLET,
   STATUS,PRIORITY,CREATED_BY,BASE_QTY,BASE_UOM,RESERVATION_VERSION)
   values(p_id,'HARD','QTY',p_domain,p_doc_type,p_doc_id,p_line_id,v_article,p_qty,p_uom,v_ware,p_cell,p_uid,
   'ACTIVE',0,p_actor,p_qty,p_uom,0);
  if p_details is not null then
   v_details:=json_object_t.parse(p_details);
   if v_details.get_string('reservation_scope') is null or v_details.get_string('reservation_scope') not in('PALLET','QTY') then raise_application_error(-20869,'RESERVATION_SCOPE_INVALID');end if;
   update RRL_STOCK_RESERVATION set RESERVATION_SCOPE=v_details.get_string('reservation_scope'),
    TASK_ID=v_details.get_number('task_id'),CUSTOMER_ID=v_details.get_number('customer_id'),CUSTOMER_ORDER_ID=v_details.get_number('customer_order_id'),
    PRODUCTION_ORDER_ID=case when p_doc_type='PRODUCTION_ORDER' then p_doc_id else v_details.get_number('production_order_id') end,
    PICK_PLAN_ID=case when p_doc_type='PICK_PLAN' then p_doc_id else v_details.get_number('pick_plan_id') end,
    PICK_PLAN_LINE_ID=v_details.get_number('pick_plan_line_id'),PICK_WAVE_ID=case when p_doc_type='PICK_WAVE' then p_doc_id else v_details.get_number('pick_wave_id') end,
    PICK_WAVE_LINE_ID=v_details.get_number('pick_wave_line_id'),BATCH_ID=v_details.get_string('batch_id'),PROD_BATCH_ID=v_details.get_number('prod_batch_id'),
    CELL_SLOT_ID=v_details.get_number('cell_slot_id'),PRIORITY=nvl(v_details.get_number('priority'),100),RESERVATION_VERSION=RESERVATION_VERSION+1
    where RESERVATION_ID=p_id;
  end if;
  RRL_STOCK_CTX_API.end_effect;
 end;
 procedure release_hard(p_id number,p_qty number,p_uom_version number,p_doc_type varchar2,p_doc_id number,p_actor varchar2) is r RRL_STOCK_RESERVATION%rowtype;
 begin
  check_owner(p_id,p_qty,p_doc_type,p_doc_id,r);
  RRL_STOCK_BALANCE_CORE.apply_delta(r.UID_PALLET,r.CELL,0,-p_qty,r.BASE_UOM,p_uom_version);
  decrease(r,p_qty,'RELEASED',p_actor);
 end;
 procedure consume_hard(p_id number,p_qty number,p_uom_version number,p_doc_type varchar2,p_doc_id number,p_actor varchar2) is r RRL_STOCK_RESERVATION%rowtype;
 begin
  check_owner(p_id,p_qty,p_doc_type,p_doc_id,r);
  RRL_STOCK_BALANCE_CORE.apply_delta(r.UID_PALLET,r.CELL,-p_qty,-p_qty,r.BASE_UOM,p_uom_version);
  decrease(r,p_qty,'CONSUMED',p_actor);
 end;
 procedure relocate_hard(p_id number,p_new_id number,p_target_uid varchar2,p_target_cell varchar2,
   p_qty number,p_uom_version number,p_actor varchar2) is
  r RRL_STOCK_RESERVATION%rowtype;v_art varchar2(160);v_ware number;
 begin
  lock_identity(p_id);lock_identity(p_new_id);
  select * into r from RRL_STOCK_RESERVATION where RESERVATION_ID=p_id for update;
  if r.RESERVATION_KIND!='HARD' or r.STATUS not in('ACTIVE','ALLOCATED','PICKING')
   or r.BASE_QTY is null or p_qty is null or p_qty<=0 or r.BASE_QTY<p_qty then raise_application_error(-20869,'RESERVATION_CONFLICT'); end if;
  select ARTICUL into v_art from RRL_PALLETS where UID_PALLET=p_target_uid;
  select WARE_ID into v_ware from RRL_CELLS where CELL=p_target_cell;
  if v_art!=r.ARTICUL then raise_application_error(-20869,'RESERVATION_ARTICLE_CONFLICT'); end if;
  -- Must accompany physical movement of the same q; source/destination P/H changed together.
  RRL_STOCK_BALANCE_CORE.apply_delta(r.UID_PALLET,r.CELL,-p_qty,-p_qty,r.BASE_UOM,p_uom_version);
  RRL_STOCK_BALANCE_CORE.apply_delta(p_target_uid,p_target_cell,p_qty,p_qty,r.BASE_UOM,p_uom_version);
  RRL_STOCK_CTX_API.begin_effect('RESERVATION',p_target_uid,p_target_cell,p_new_id);
  insert into RRL_STOCK_RESERVATION(RESERVATION_ID,RESERVATION_KIND,RESERVATION_SCOPE,RESERVATION_DOMAIN,
   SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_LINE_ID,TASK_ID,CUSTOMER_ID,CUSTOMER_ORDER_ID,PRODUCTION_ORDER_ID,
   PICK_PLAN_ID,PICK_PLAN_LINE_ID,PICK_WAVE_ID,PICK_WAVE_LINE_ID,ARTICUL,QTY,UNIT_CODE,WARE_ID,CELL,
   BATCH_ID,PROD_BATCH_ID,UID_PALLET,SSCC,STATUS,PRIORITY,CREATED_BY,BASE_QTY,BASE_UOM,RESERVATION_VERSION)
   values(p_new_id,'HARD',r.RESERVATION_SCOPE,r.RESERVATION_DOMAIN,r.SOURCE_DOC_TYPE,r.SOURCE_DOC_ID,
   r.SOURCE_LINE_ID,r.TASK_ID,r.CUSTOMER_ID,r.CUSTOMER_ORDER_ID,r.PRODUCTION_ORDER_ID,r.PICK_PLAN_ID,
   r.PICK_PLAN_LINE_ID,r.PICK_WAVE_ID,r.PICK_WAVE_LINE_ID,r.ARTICUL,p_qty,r.BASE_UOM,v_ware,p_target_cell,
   r.BATCH_ID,r.PROD_BATCH_ID,p_target_uid,null,r.STATUS,r.PRIORITY,p_actor,p_qty,r.BASE_UOM,0);
  RRL_STOCK_CTX_API.end_effect;
  decrease(r,p_qty,'CONSUMED',p_actor);
 end;
 procedure move_coverage(p_id number,p_new_id number,p_target_uid varchar2,p_target_cell varchar2,
  p_target_ware number,p_qty number,p_target_slot number,p_actor varchar2,p_result_id out number) is
  v_r RRL_STOCK_RESERVATION%rowtype;v_new RRL_STOCK_RESERVATION%rowtype;
 begin
  lock_identity(p_id);
  select * into v_r from RRL_STOCK_RESERVATION where RESERVATION_ID=p_id for update;
  if v_r.BASE_QTY is null or p_qty is null or p_qty<=0 or p_qty>v_r.BASE_QTY
   or v_r.RESERVATION_KIND is null or v_r.RESERVATION_KIND!='HARD'
   or v_r.STATUS is null or v_r.STATUS not in('ACTIVE','ALLOCATED','PICKING')
   or v_r.BASE_UOM is null then raise_application_error(-20869,'RESERVATION_COVERAGE_CONFLICT');end if;
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null
   or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then
   raise_application_error(-20863,'STOCK_WRITE_FORBIDDEN');end if;
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',v_r.UID_PALLET));
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_target_uid));
  if p_target_slot is not null then
   RRL_STOCK_LOCK_API.assert_held(40,RRL_STOCK_LOCK_API.resource_key('SLOT',to_char(p_target_slot,'TM9')));
  end if;
  if p_qty=v_r.BASE_QTY then
   RRL_STOCK_CTX_API.begin_effect('RESERVATION',p_target_uid,p_target_cell,p_id);
   update RRL_STOCK_RESERVATION set UID_PALLET=p_target_uid,CELL=p_target_cell,WARE_ID=p_target_ware,
    CELL_SLOT_ID=p_target_slot,RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=p_id;
   RRL_STOCK_CTX_API.end_effect;
   p_result_id:=p_id;
  else
   lock_identity(p_new_id);v_new:=v_r;v_new.RESERVATION_ID:=p_new_id;
   v_new.UID_PALLET:=p_target_uid;v_new.CELL:=p_target_cell;v_new.WARE_ID:=p_target_ware;
   v_new.CELL_SLOT_ID:=p_target_slot;v_new.BASE_QTY:=p_qty;v_new.QTY:=p_qty;v_new.UNIT_CODE:=v_new.BASE_UOM;
   v_new.RESERVATION_VERSION:=0;v_new.CREATED_AT:=systimestamp;v_new.CREATED_BY:=p_actor;
   v_new.RELEASED_AT:=null;v_new.RELEASED_BY:=null;v_new.CONSUMED_AT:=null;v_new.CONSUMED_BY:=null;
   RRL_STOCK_CTX_API.begin_effect('RESERVATION',p_target_uid,p_target_cell,p_new_id);
   insert into RRL_STOCK_RESERVATION values v_new;
   RRL_STOCK_CTX_API.end_effect;
   RRL_STOCK_CTX_API.begin_effect('RESERVATION',v_r.UID_PALLET,v_r.CELL,p_id);
   update RRL_STOCK_RESERVATION set BASE_QTY=BASE_QTY-p_qty,QTY=BASE_QTY-p_qty,UNIT_CODE=BASE_UOM,
    RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=p_id;
   RRL_STOCK_CTX_API.end_effect;
   p_result_id:=p_new_id;
  end if;
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
  v_result json_object_t:=json_object_t();v_resource number;v_session number;v_equipment number;v_sync_id number;v_sync_key varchar2(400);v_session_actor varchar2(100);v_input_uom varchar2(20);v_source_p number;v_uom_signature varchar2(64);v_sap_header number;v_sap_cell varchar2(60);v_sap_ware number;v_document_confirmation number:=0;
 begin
  v_doc.on_error(1);v_source:=v_doc.get_object('source');v_meta:=v_doc.get_object('metadata');v_meta.on_error(1);
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
  elsif v_task.TASK_SOURCE in('MES_RAW_SUPPLY','MES_COMPLETION') then
   select STATUS into v_doc_status from RRL_PRODUCTION_ORDER where PRODUCTION_ORDER_ID=nvl(v_task.PRODUCTION_ORDER_ID,v_task.SOURCE_DOC_ID) for update;
  elsif v_task.TASK_SOURCE='SAP_RECEIPT' then
   select NAKLAD_ID,RECEIVE_CELL,WARE_ID into v_sap_header,v_sap_cell,v_sap_ware from RRL_SAP_SUPPLY_ORDER where ORDER_ID=v_domain.get_string('sap_order_id') for update;
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
   v_qbase,v_base,v_version,v_task.TO_WARE_ID,p_actor,1,v_reservation,v_units,v_new_reservation,v_task.TO_CELL_SLOT_ID,v_task.FROM_WARE_ID,case when v_task.TASK_SOURCE='SAP_RECEIPT' then 'PUTAWAY' else 'ORDINARY' end);
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

create or replace package body RRL_STOCK_RESERVATION_CMD as
 procedure source_anchor(p_r in out nocopy json_array_t,p_type varchar2,p_id number) is v_table varchar2(40);
 begin
  if p_id is null or p_id<1 or p_id!=trunc(p_id) then raise_application_error(-20869,'RESERVATION_DOCUMENT_REQUIRED');end if;
  case p_type when 'PRODUCTION_ORDER' then v_table:='RRL_PRODUCTION_ORDER';
   when 'PICK_WAVE' then v_table:='RRL_PICK_WAVE';when 'PICK_PLAN' then v_table:='RRL_PICK_PLAN';
   else raise_application_error(-20869,'RESERVATION_DOCUMENT_TYPE_UNSUPPORTED');end case;
  RRL_STOCK_PLAN_HELPER.row_key(p_r,v_table,RRL_STOCK_PLAN_HELPER.decimal_text(p_id));
 end;
 procedure validate_source(p_type varchar2,p_id number,p_allow_closed number default 0) is v_status varchar2(40);
 begin
  case p_type when 'PRODUCTION_ORDER' then
    select STATUS into v_status from RRL_PRODUCTION_ORDER where PRODUCTION_ORDER_ID=p_id for update;
   when 'PICK_WAVE' then select STATUS into v_status from RRL_PICK_WAVE where PICK_WAVE_ID=p_id for update;
   when 'PICK_PLAN' then select STATUS into v_status from RRL_PICK_PLAN where PICK_PLAN_ID=p_id for update;
   else raise_application_error(-20869,'RESERVATION_DOCUMENT_TYPE_UNSUPPORTED');end case;
  if p_allow_closed=0 and (v_status is null or v_status in('CANCELLED','CLOSED','COMPLETED','SHIPPED')) then
   raise_application_error(-20869,'RESERVATION_DOCUMENT_NOT_OPEN');end if;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t;s json_object_t;
  r json_array_t:=json_array_t();f json_array_t:=json_array_t();v json_object_t:=json_object_t();
  old RRL_STOCK_RESERVATION%rowtype;v_id number;v_uid varchar2(200);v_cell varchar2(60);v_article varchar2(160);
  v_type varchar2(50);v_doc number;v_version number;
 begin
  m:=d.get_object('metadata');s:=d.get_object('source');
  if d.get_string('command_type')='RESERVATION_CREATE' then
   select RRL_STOCK_RESERVATION_SQ.nextval into v_id from dual;
   v_uid:=m.get_string('uid_pallet');v_cell:=m.get_string('cell');v_article:=m.get_string('articul');
   v_type:=m.get_string('source_doc_type');v_doc:=m.get_number('source_doc_id');
  else
   v_id:=s.get_number('reservation_id');
   select * into old from RRL_STOCK_RESERVATION where RESERVATION_ID=v_id;
   v_uid:=old.UID_PALLET;v_cell:=old.CELL;v_article:=old.ARTICUL;v_type:=old.SOURCE_DOC_TYPE;v_doc:=old.SOURCE_DOC_ID;
   v_version:=old.RESERVATION_VERSION;
   if d.get_string('command_type')='RESERVATION_PROMOTE' then
    v_uid:=m.get_string('uid_pallet');v_cell:=m.get_string('cell');
   end if;
  end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(v_id));
  source_anchor(r,v_type,v_doc);
  if v_uid is not null and v_cell is not null then RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v_uid,v_article,v_cell,null);
  else RRL_STOCK_PLAN_HELPER.fence(f,'SKU',v_article);end if;
  v.put('reservation_id',v_id);v.put('uid',v_uid);v.put('cell',v_cell);v.put('article',v_article);
  v.put('doc_type',v_type);v.put('doc_id',v_doc);v.put('version',v_version);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t;v json_object_t;j json_object_t:=json_object_t();
  old RRL_STOCK_RESERVATION%rowtype;v_plan clob;v_id number;v_kind varchar2(80);v_qty number;v_input varchar2(20);
  v_base varchar2(20);v_num number;v_den number;v_scale number;v_version number;v_ware number;v_article varchar2(160);
  v_uid varchar2(200);v_cell varchar2(60);v_type varchar2(50);v_doc number;v_units clob;v_event number;v_n number;
 begin
  if RRL_HAS_WRIGHT(p_actor,'stock_reservation_edit')!=1 then raise_application_error(-20882,'RESERVATION_FORBIDDEN');end if;
  m:=d.get_object('metadata');v_kind:=d.get_string('command_type');
  if v_kind='RESERVATION_CREATE' and (m.get_string('reservation_kind') is null or m.get_string('reservation_kind') not in('SOFT','HARD')) then raise_application_error(-20869,'RESERVATION_KIND_INVALID');end if;
  select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=d.get_string('operation_id');
  v:=json_object_t.parse(v_plan).get_object('domain');
  v_id:=v.get_number('reservation_id');v_uid:=v.get_string('uid');v_cell:=v.get_string('cell');
  v_article:=v.get_string('article');v_type:=v.get_string('doc_type');v_doc:=v.get_number('doc_id');
  validate_source(v_type,v_doc,case when v_kind in('RESERVATION_RELEASE','RESERVATION_CANCEL') then 1 else 0 end);
  if v_kind!='RESERVATION_CREATE' then
   select * into old from RRL_STOCK_RESERVATION where RESERVATION_ID=v_id for update;
   if old.RESERVATION_VERSION!=v.get_number('version') or old.SOURCE_DOC_TYPE!=v_type or old.SOURCE_DOC_ID!=v_doc
    or (v_kind!='RESERVATION_PROMOTE' and (old.UID_PALLET!=v_uid or old.CELL!=v_cell)) then
    raise_application_error(-20890,'CLOSURE_CHANGED: reservation');end if;
  end if;
  -- Release/cancellation remains legal after its source document is closed.

  if d.get_array('units').get_size>0 then v_units:=d.get_array('units').to_clob;end if;
  if v_kind='RESERVATION_CREATE' and (m.get_string('reservation_scope') is null or m.get_string('reservation_scope') not in('PALLET','QTY')) then raise_application_error(-20869,'RESERVATION_SCOPE_INVALID');end if;
  if v_kind='RESERVATION_CREATE' and m.get_string('reservation_kind')='SOFT' then
   if m.get_string('uid_pallet') is not null or m.get_string('cell') is not null or m.get_number('ware_id') is not null or m.get_string('batch_id') is not null or m.get_number('prod_batch_id') is not null or m.get_string('sscc') is not null then raise_application_error(-20869,'SOFT_HAS_PHYSICAL_BINDING');end if;
   v_qty:=RRL_STOCK_MATH.quantity(m.get_string('qty'));
   RRL_STOCK_CTX_API.begin_effect('RESERVATION',null,null,v_id);
   insert into RRL_STOCK_RESERVATION(RESERVATION_ID,RESERVATION_KIND,RESERVATION_SCOPE,RESERVATION_DOMAIN,
    SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_LINE_ID,TASK_ID,CUSTOMER_ID,CUSTOMER_ORDER_ID,PRODUCTION_ORDER_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID,PICK_WAVE_ID,PICK_WAVE_LINE_ID,ARTICUL,QTY,UNIT_CODE,STATUS,PRIORITY,CREATED_BY,RESERVATION_VERSION)
    values(v_id,'SOFT',m.get_string('reservation_scope'),m.get_string('reservation_domain'),v_type,v_doc,
     m.get_number('source_line_id'),m.get_number('task_id'),m.get_number('customer_id'),m.get_number('customer_order_id'),
     case when v_type='PRODUCTION_ORDER' then v_doc else null end,case when v_type='PICK_PLAN' then v_doc else null end,m.get_number('pick_plan_line_id'),case when v_type='PICK_WAVE' then v_doc else null end,m.get_number('pick_wave_line_id'),v_article,v_qty,m.get_string('unit_code'),'ACTIVE',nvl(m.get_number('priority'),100),p_actor,0);
   RRL_STOCK_CTX_API.end_effect;
  elsif old.RESERVATION_KIND='SOFT' and v_kind in('RESERVATION_RELEASE','RESERVATION_CANCEL') then
   if old.STATUS not in('ACTIVE','ALLOCATED') then raise_application_error(-20869,'SOFT_RELEASE_STATE_CONFLICT');end if;
   RRL_STOCK_CTX_API.begin_effect('RESERVATION',null,null,v_id);
   update RRL_STOCK_RESERVATION set STATUS=case when v_kind='RESERVATION_CANCEL' then 'CANCELLED' else 'RELEASED' end,
    RELEASED_AT=systimestamp,RELEASED_BY=p_actor,RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=v_id;
   RRL_STOCK_CTX_API.end_effect;
  else
   if v_uid is null or v_cell is null then raise_application_error(-20869,'HARD_STOCK_REQUIRED');end if;
   select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=v_uid;
   if v_article!=v.get_string('article') then raise_application_error(-20869,'RESERVATION_ARTICLE_CONFLICT');end if;
   select WARE_ID into v_ware from RRL_CELLS where CELL=v_cell;
   if v_kind in('RESERVATION_CREATE','RESERVATION_PROMOTE') then
    RRL_STOCK_LOCATION_CORE.assert_ordinary(v_cell,v_ware,'SOURCE');
    if m.get_number('ware_id') is null or m.get_number('ware_id')!=v_ware then raise_application_error(-20869,'RESERVATION_WAREHOUSE_CONFLICT');end if;
    v_input:=nvl(m.get_string('unit_code'),old.UNIT_CODE);
    v_qty:=case when m.has('qty') and not m.get('qty').is_null then RRL_STOCK_MATH.quantity(m.get_string('qty')) else old.QTY end;
    select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_input;
    select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into v_base,v_num,v_den,v_scale
     from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_input and POLICY_VERSION=v_version;
    v_qty:=RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(v_qty),v_num,v_den,v_scale);
    if v_kind='RESERVATION_PROMOTE' then
     if old.RESERVATION_KIND!='SOFT' or old.STATUS not in('ACTIVE','ALLOCATED') then raise_application_error(-20869,'SOFT_PROMOTION_CONFLICT');end if;
     RRL_STOCK_BALANCE_CORE.apply_delta(v_uid,v_cell,0,v_qty,v_base,v_version);
     RRL_STOCK_CTX_API.begin_effect('RESERVATION',v_uid,v_cell,v_id);
     update RRL_STOCK_RESERVATION set RESERVATION_KIND='HARD',RESERVATION_SCOPE=m.get_string('reservation_scope'),
      UID_PALLET=v_uid,CELL=v_cell,WARE_ID=v_ware,QTY=v_qty,UNIT_CODE=v_base,BASE_QTY=v_qty,BASE_UOM=v_base,
      STATUS='ACTIVE',RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=v_id;
     RRL_STOCK_CTX_API.end_effect;
    else RRL_STOCK_RESERVE_CORE.create_hard(v_id,v_uid,v_cell,v_qty,v_base,v_version,v_type,v_doc,
      m.get_number('source_line_id'),m.get_string('reservation_domain'),p_actor,m.to_clob);end if;
    select nvl(max(MARKING_REQUIRED),0) into v_n from RRL_SKU_RECEIPT_POLICY where ARTICUL=v_article;
    if v_n=1 then
     select count(*) into v_n from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=v_uid and CURRENT_CELL=v_cell and STOCK_STATUS!='ISSUED';
     if v_n=0 then raise_application_error(-20884,'MARKED_BINDING_REQUIRED');end if;
    end if;
    RRL_STOCK_UNIT_CORE.reserve_units(v_uid,v_cell,v_id,v_qty,v_units);
   else
    v_qty:=old.BASE_QTY;v_base:=old.BASE_UOM;
    select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_base and BASE_UOM=v_base and NUMERATOR=DENOMINATOR;
    if v_kind='RESERVATION_CONSUME' then
     RRL_STOCK_LOCATION_CORE.assert_ordinary(v_cell,v_ware,'SOURCE');
     RRL_STOCK_UNIT_CORE.release_units(v_id,v_qty,v_units,1);
     RRL_STOCK_RESERVE_CORE.consume_hard(v_id,v_qty,v_version,v_type,v_doc,p_actor);
     RRL_STOCK_BALANCE_CORE.write_leg(v_uid,v_cell,null,-v_qty,v_base,v_version,1,1,3,p_actor,v_event);
    else
     RRL_STOCK_UNIT_CORE.release_units(v_id,v_qty,v_units,0);
     RRL_STOCK_RESERVE_CORE.release_hard(v_id,v_qty,v_version,v_type,v_doc,p_actor);
     if v_kind='RESERVATION_CANCEL' then RRL_STOCK_CTX_API.begin_effect('RESERVATION',v_uid,v_cell,v_id);update RRL_STOCK_RESERVATION set STATUS='CANCELLED',RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=v_id;RRL_STOCK_CTX_API.end_effect;end if;
    end if;
   end if;
  end if;
  j.put('operation_id',d.get_string('operation_id'));j.put('reservation_id',v_id);j.put('action',v_kind);p_result:=j.to_clob;
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
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','SAP.OUTBOX:'||p_operation);
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
  v_base varchar2(20);v_unit varchar2(20);v_article varchar2(160);v_uom_version number;v_base_version number;v_num number;v_den number;v_scale number;
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
  select max(POLICY_VERSION) into v_base_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_base and BASE_UOM=v_base and NUMERATOR=1 and DENOMINATOR=1;
  if v_base_version is null then raise_application_error(-20868,'RECEIPT_BASE_POLICY_REQUIRED');end if;
  RRL_STOCK_BALANCE_CORE.apply_delta(v_uid,v_cell,v_qty,0,v_base,v_base_version);
  RRL_STOCK_UNIT_CORE.assert_composition(v_uid,v_cell);
  RRL_STOCK_UNIT_CORE.admit_captured(v_uid,v_cell);
  update RRL_PALLETS set STOCK_ORIGIN_UID=v_uid,CREATED_BY_STOCK_OP=d.get_string('operation_id') where UID_PALLET=v_uid;
  RRL_STOCK_BALANCE_CORE.write_leg(v_uid,null,v_cell,v_qty,v_base,v_base_version,1,1,1,p_actor,v_event);
  v_response:=h.get_object('result');v_response.put('task_id',v_task);p_result:=v_response.to_clob;
  insert into RRL_SAP_PALLET_RECEIPT(OPERATION_ID,ORDER_ID,LINE_NUMBER,UID_PALLET,SUPPLIER_BATCH,PAYLOAD_HASH,RESULT_JSON,
   RECEIVED_BY,POSTED_BASE_QTY,STOCK_BASE_UOM,STOCK_OPERATION_ID)
   values(d.get_string('operation_id'),o.ORDER_ID,h.get_string('line_number'),v_uid,m.get_string('supplier_batch'),
    rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256)),p_result,p_actor,v_qty,v_base,d.get_string('operation_id'));
  select count(*) into v_n from RRL_SAP_SUPPLY_LINE sl where sl.ORDER_ID=o.ORDER_ID and (
   not exists(select 1 from RRL_STOCK_UOM_CONVERSION u where u.ARTICUL=sl.ARTICUL and u.INPUT_UOM=sl.BASE_UOM)
   or nvl((select sum(rec.POSTED_BASE_QTY) from RRL_SAP_PALLET_RECEIPT rec where rec.ORDER_ID=sl.ORDER_ID and rec.LINE_NUMBER=sl.LINE_NUMBER),0)<
     (select RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(sl.PLANNED_QTY),u.NUMERATOR,u.DENOMINATOR,u.BASE_SCALE)
      from RRL_STOCK_UOM_CONVERSION u where u.ARTICUL=sl.ARTICUL and u.INPUT_UOM=sl.BASE_UOM and u.POLICY_VERSION=(select max(x.POLICY_VERSION) from RRL_STOCK_UOM_CONVERSION x where x.ARTICUL=sl.ARTICUL and x.INPUT_UOM=sl.BASE_UOM)));
  if v_n=0 then update RRL_PRIHOD_NAKLAD set CONDITION=1,DATE_OF_ACCEPT=nvl(DATE_OF_ACCEPT,sysdate) where ID=o.NAKLAD_ID;end if;
  insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)
   values(d.get_string('operation_id'),'PALLET_RECEIVED',p_result);
 end;
end;
/

create or replace package body RRL_STOCK_MES_MOVEMENT_PLAN as
 function signature(p_m RRL_MES_MOVEMENT%rowtype) return varchar2 is v json_object_t:=json_object_t();
 begin
  v.put('id',p_m.MOVEMENT_ID);v.put('type',p_m.MOVEMENT_TYPE);v.put('order',p_m.PRODUCTION_ORDER_ID);
  v.put('uid',p_m.UID_PALLET);v.put('sscc',p_m.SSCC);v.put('batch',p_m.PROD_BATCH_ID);v.put('raw',p_m.RAW_ARTICUL);
  v.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(p_m.QUANTITY));v.put('unit',p_m.UNIT_CODE);
  v.put('from',p_m.SOURCE_LOCATION);v.put('to',p_m.TARGET_LOCATION);
  return rawtohex(sys.dbms_crypto.hash(v.to_clob,sys.dbms_crypto.hash_sh256));
 end;
 procedure compile_movements(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);s json_object_t;ids json_array_t;a json_array_t:=json_array_t();
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();v json_object_t:=json_object_t();h json_object_t:=json_object_t();
  m RRL_MES_MOVEMENT%rowtype;o RRL_PRODUCTION_ORDER%rowtype;v_id number;v_article varchar2(160);
  v_p number;v_target varchar2(200);v_reservation number;v_new_reservation number;v_qty number;
  v_num number;v_den number;v_scale number;v_base varchar2(20);v_version number;
  type quantity_map is table of number index by varchar2(2000);v_balances quantity_map;v_target_reservations quantity_map;
  type identity_map is table of varchar2(200) index by varchar2(2000);v_targets identity_map;
  v_source_key varchar2(2000);v_target_key varchar2(2000);v_physical_uid varchar2(200);
  function projected(p_uid varchar2,p_cell varchar2) return number is k varchar2(2000);n number;
  begin
   k:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid,p_cell));
   if not v_balances.exists(k) then
    begin select REMAIN into n from RRL_REMAINS where UID_POLETA=p_uid and CELL=p_cell;exception when no_data_found then n:=0;end;
    v_balances(k):=n;
   end if;
   return v_balances(k);
  end;

 begin
  s:=d.get_object('source');ids:=s.get_array('movement_ids');
  if ids is null or ids.get_size<1 or ids.get_size>200 then raise_application_error(-20871,'MES_MOVEMENT_BATCH_SIZE');end if;
  select * into o from RRL_PRODUCTION_ORDER where PRODUCTION_ORDER_ID=s.get_number('production_order_id');
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PRODUCTION_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(o.PRODUCTION_ORDER_ID));
  for i in 0..ids.get_size-1 loop
   v_id:=ids.get_number(i);select * into m from RRL_MES_MOVEMENT where MOVEMENT_ID=v_id;
   if m.PRODUCTION_ORDER_ID!=o.PRODUCTION_ORDER_ID or m.UID_PALLET is null
    or m.MOVEMENT_TYPE not in('RAW_ISSUE_TO_PRODUCTION','RAW_CONSUMPTION','FG_PALLET_RELEASE') then
    raise_application_error(-20886,'MES_MOVEMENT_IDENTITY_CONFLICT');end if;
   v_physical_uid:=m.UID_PALLET;
   v_source_key:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',m.UID_PALLET,m.SOURCE_LOCATION));
   if m.MOVEMENT_TYPE='RAW_CONSUMPTION' and v_targets.exists(v_source_key) then v_physical_uid:=v_targets(v_source_key);end if;
   if m.MOVEMENT_TYPE='FG_PALLET_RELEASE' then v_article:=o.TARGET_ARTICUL;
   else select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=m.UID_PALLET;end if;
   select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=m.UNIT_CODE;
   select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into v_base,v_num,v_den,v_scale
    from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=m.UNIT_CODE and POLICY_VERSION=v_version;
   v_qty:=RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(m.QUANTITY),v_num,v_den,v_scale);
   select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_base and BASE_UOM=v_base and NUMERATOR=1 and DENOMINATOR=1;
   if v_version is null then raise_application_error(-20868,'MES_BASE_POLICY_REQUIRED');end if;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_MES_MOVEMENT',RRL_STOCK_PLAN_HELPER.decimal_text(v_id));
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v_physical_uid,v_article,
    case when m.MOVEMENT_TYPE!='FG_PALLET_RELEASE' then m.SOURCE_LOCATION end,
    case when m.MOVEMENT_TYPE!='RAW_CONSUMPTION' then m.TARGET_LOCATION end);
   v_target:=v_physical_uid;v_reservation:=null;v_new_reservation:=null;v_p:=null;
   if m.MOVEMENT_TYPE='RAW_ISSUE_TO_PRODUCTION' then
    v_p:=projected(v_physical_uid,m.SOURCE_LOCATION);
    if v_qty<v_p then
     v_target:='PART:'||substr(rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation||':'||RRL_STOCK_PLAN_HELPER.decimal_text(v_id),'AL32UTF8'),sys.dbms_crypto.hash_sh256)),1,64);
     select RRL_STOCK_RESERVATION_SQ.nextval into v_new_reservation from dual;
     RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(v_new_reservation));
     RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',v_target);RRL_STOCK_PLAN_HELPER.anchor(r,50,'STOCK',v_target);
     RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','PALLET:'||v_target);
    end if;
   end if;
   if m.MOVEMENT_TYPE!='FG_PALLET_RELEASE' then
    begin select RESERVATION_ID into v_reservation from RRL_STOCK_RESERVATION where UID_PALLET=m.UID_PALLET and CELL=m.SOURCE_LOCATION
     and SOURCE_DOC_TYPE='PRODUCTION_ORDER' and SOURCE_DOC_ID=o.PRODUCTION_ORDER_ID and RESERVATION_KIND='HARD'
     and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>=v_qty;
    exception when no_data_found then null;when too_many_rows then raise_application_error(-20869,'MES_RESERVATION_AMBIGUOUS');end;
   else RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','PALLET:'||m.UID_PALLET);end if;
   if m.MOVEMENT_TYPE='RAW_CONSUMPTION' and v_target_reservations.exists(v_source_key) then v_reservation:=v_target_reservations(v_source_key);end if;
   if m.MOVEMENT_TYPE='RAW_ISSUE_TO_PRODUCTION' then
    v_source_key:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',v_physical_uid,m.SOURCE_LOCATION));
    v_balances(v_source_key):=projected(v_physical_uid,m.SOURCE_LOCATION)-v_qty;
    v_target_key:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',v_target,m.TARGET_LOCATION));
    v_balances(v_target_key):=projected(v_target,m.TARGET_LOCATION)+v_qty;
    v_target_key:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',m.UID_PALLET,m.TARGET_LOCATION));
    if v_targets.exists(v_target_key) and v_targets(v_target_key)!=v_target then
     raise_application_error(-20886,'MES_CONSUMPTION_REQUIRES_PHYSICAL_PALLET_ALLOCATION');end if;
    v_targets(v_target_key):=v_target;
    if v_reservation is not null then v_target_reservations(v_target_key):=case when v_target=m.UID_PALLET then v_reservation else v_new_reservation end;end if;
   elsif m.MOVEMENT_TYPE='RAW_CONSUMPTION' then
    v_source_key:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',v_physical_uid,m.SOURCE_LOCATION));
    if projected(v_physical_uid,m.SOURCE_LOCATION)<v_qty then raise_application_error(-20868,'MES_CONSUMPTION_STOCK_INSUFFICIENT');end if;
    v_balances(v_source_key):=v_balances(v_source_key)-v_qty;
   end if;
   v:=json_object_t();v.put('physical_uid',v_physical_uid);v.put('movement_id',v_id);v.put('signature',signature(m));v.put('article',v_article);
   v.put('base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));v.put('base_uom',v_base);v.put('uom_version',v_version);
   v.put('source_p',case when v_p is not null then RRL_STOCK_PLAN_HELPER.decimal_text(v_p) end);
   v.put('target_uid',v_target);v.put('reservation_id',v_reservation);v.put('new_reservation_id',v_new_reservation);a.append(v);
  end loop;
  h.put('production_order_id',o.PRODUCTION_ORDER_ID);h.put('movements',a);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=h.to_clob;
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
      p.STOCK_ORIGIN_UID:=nvl(p.STOCK_ORIGIN_UID,p.UID_PALLET);p.CREATED_BY_STOCK_OP:=d.get_string('operation_id');
      if p.WEIGHT_BRUTTO is not null then
       if p.UNIT_COUNT is null or p.UNIT_COUNT<=0 then raise_application_error(-20887,'PALLET_BIRTH_QUANTITY_REQUIRED');end if;
       p.WEIGHT_BRUTTO:=p.WEIGHT_BRUTTO*v_qty/p.UNIT_COUNT;
      end if;
      p.UID_PALLET:=v_target;p.SSCC:=null;p.UNIT_COUNT:=v_qty;p.PRINTED:=0;
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
  if d.get_string('command_type')='MOVE_QUARANTINE' and RRL_HAS_WRIGHT(p_actor,'QUARANTINE_MOVE')!=1 then raise_application_error(-20882,'QUARANTINE_MOVE_FORBIDDEN');end if;
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
  if d.get_string('command_type')='MOVE_QUARANTINE' then
   if v_qty!=v_p then raise_application_error(-20886,'QUARANTINE_MOVE_REQUIRES_WHOLE_PALLET');end if;
   select count(*) into v_n from RRL_CELLS where CELL in(v.get_string('from'),c.CELL) and nvl(BLOCKED_FOR_REMAINS,0)=1;
   if v_n=0 then raise_application_error(-20879,'QUARANTINE_CELL_REQUIRED');end if;
  end if;
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
   p.STOCK_ORIGIN_UID:=nvl(p.STOCK_ORIGIN_UID,p.UID_PALLET);p.CREATED_BY_STOCK_OP:=d.get_string('operation_id');
   if p.WEIGHT_BRUTTO is not null then
    if p.UNIT_COUNT is null or p.UNIT_COUNT<=0 then raise_application_error(-20887,'PALLET_BIRTH_QUANTITY_REQUIRED');end if;
    p.WEIGHT_BRUTTO:=p.WEIGHT_BRUTTO*v_qty/p.UNIT_COUNT;
   end if;
   p.UID_PALLET:=v_target;p.SSCC:=null;p.UNIT_COUNT:=v_qty;p.PRINTED:=0;
   insert into RRL_PALLETS values p;
  end if;
  if d.get_array('units').get_size>0 then v_units:=d.get_array('units').to_clob;end if;
  RRL_STOCK_TRANSFER_CORE.move(v_uid,v_target,v.get_string('from'),c.CELL,v_qty,v_base,v_uom_version,c.WARE_ID,p_actor,1,null,v_units,null,null,null,case when d.get_string('command_type')='MOVE_QUARANTINE' then 'QUARANTINE' else 'ORDINARY' end);
  j.put('operation_id',d.get_string('operation_id'));j.put('status','APPLIED');j.put('source_uid',v_uid);j.put('uid',v_target);
  j.put('from_cell',v.get_string('from'));j.put('cell',c.CELL);j.put('base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));j.put('base_uom',v_base);
  p_result:=j.to_clob;
 end;
end;
/

create or replace package body RRL_STOCK_SHIPPING_CORE as
 function rows_json(p_kind varchar2,p_id number,p_uid varchar2) return clob is a json_array_t:=json_array_t();v json_object_t;
 begin
  for l in(
   select ID,ARTICUL,COUNT1 QTY,cast(null as varchar2(20)) INPUT_UOM from RRL_OTHOD_NAKLAD_ROWS where p_kind='SHIP_DOCUMENT' and ID_NAKLAD=p_id
   union all select ID,ARTICUL,QUANTITY,EI from RRL_SBORKA_PALLET_ROWS where p_kind='SHIP_PALLET' and PALLET_UID=p_uid
   order by ID
  ) loop
   v:=json_object_t();v.put('id',l.ID);v.put('article',l.ARTICUL);v.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(l.QTY));v.put('input_uom',l.INPUT_UOM);a.append(v);
  end loop;
  return a.to_clob;
 end;
 procedure compile_shipment(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);s json_object_t;v json_object_t:=json_object_t();leg json_object_t;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t;legs json_array_t:=json_array_t();
  l json_object_t;v_kind varchar2(80);v_id number;v_uid varchar2(200);v_ware number;v_cell varchar2(60);
  v_article varchar2(160);v_qty number;v_take number;v_base varchar2(20);v_version number;v_row_json clob;v_available number;v_customer_order number;v_order_count number;v_num number;v_den number;v_scale number;v_input varchar2(20);
  type quantity_map is table of number index by varchar2(2000);used quantity_map;reserved_used quantity_map;k varchar2(2000);sk varchar2(2000);
 begin
  s:=d.get_object('source');v_kind:=d.get_string('command_type');v_id:=s.get_number('document_id');v_uid:=s.get_string('pallet_identifier');
  if v_kind='SHIP_DOCUMENT' then select WARE_ID into v_ware from RRL_OTHOD_NAKLAD where ID=v_id;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_OTHOD_NAKLAD',RRL_STOCK_PLAN_HELPER.decimal_text(v_id));
  elsif v_kind='SHIP_PALLET' then select ID,WARE_ID into v_id,v_ware from RRL_SBORKA_PALLETS where PALLET_UID=v_uid;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(v_id));
  else raise_application_error(-20871,'SHIPPING_SOURCE_TYPE_INVALID');end if;
  if v_kind='SHIP_PALLET' then
   select count(distinct CUSTOMER_ORDER_ID),min(CUSTOMER_ORDER_ID) into v_order_count,v_customer_order from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=v_id and PALLET_UID=v_uid;
   if v_order_count>1 then raise_application_error(-20887,'SHIPMENT_CUSTOMER_ORDER_AMBIGUOUS');end if;
   if v_customer_order is not null then
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(v_customer_order));
    for ff in(select FULFILLMENT_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=v_id and PALLET_UID=v_uid order by FULFILLMENT_ID) loop
     RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(ff.FULFILLMENT_ID));
    end loop;
   end if;
  end if;
  if v_ware is null then raise_application_error(-20886,'SHIPPING_WAREHOUSE_REQUIRED');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  v_row_json:=rows_json(v_kind,v_id,v_uid);a:=json_array_t.parse(v_row_json);
  if a.get_size<1 or a.get_size>200 then raise_application_error(-20881,'SHIPPING_DOCUMENT_LINE_BOUND');end if;
  for i in 0..a.get_size-1 loop
   l:=treat(a.get(i) as json_object_t);v_article:=l.get_string('article');v_qty:=RRL_STOCK_MATH.quantity(l.get_string('quantity'));
   RRL_STOCK_PLAN_HELPER.row_key(r,case when v_kind='SHIP_DOCUMENT' then 'RRL_OTHOD_NAKLAD_ROWS' else 'RRL_SBORKA_PALLET_ROWS' end,RRL_STOCK_PLAN_HELPER.decimal_text(l.get_number('id')));
   RRL_STOCK_PLAN_HELPER.fence(f,'SKU',v_article);
   if v_customer_order is not null then
    v_input:=l.get_string('input_uom');
    select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_input;
    select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into v_base,v_num,v_den,v_scale from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_input and POLICY_VERSION=v_version;
    v_qty:=RRL_STOCK_MATH.convert_exact(l.get_string('quantity'),v_num,v_den,v_scale);
    for c in(select sr.RESERVATION_ID,sr.SOURCE_DOC_TYPE,sr.SOURCE_DOC_ID,sr.RESERVATION_VERSION,sr.BASE_QTY,sr.BASE_UOM,rr.UID_POLETA,rr.CELL,rr.REMAIN
     from RRL_STOCK_RESERVATION sr join RRL_REMAINS rr on rr.UID_POLETA=sr.UID_PALLET and rr.CELL=sr.CELL
     join RRL_PALLETS pp on pp.UID_PALLET=sr.UID_PALLET join RRL_CELLS cc on cc.CELL=sr.CELL
     left join RRL_PROD_BATCH_READY_V br on br.PROD_BATCH_ID=pp.PROD_BATCH_ID
     where sr.CUSTOMER_ORDER_ID=v_customer_order and sr.ARTICUL=v_article and sr.RESERVATION_KIND='HARD'
      and sr.RESERVATION_DOMAIN='PICKING' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING') and sr.BASE_QTY>0
      and sr.BASE_UOM=v_base and cc.WARE_ID=v_ware and nvl(cc.BLOCKED_FOR_REMAINS,0)=0 and nvl(cc.BLOCKED_FOR_POPOLNENIE,0)=0
      and nvl(br.IS_SHIPMENT_ALLOWED,1)=1
      and exists(select 1 from RRL_PICK_TASK pt where pt.PICK_TASK_ID=sr.SOURCE_LINE_ID and pt.STATUS='DONE')
     order by pp.EXPIRY_DATE nulls last,sr.RESERVATION_ID) loop
     exit when v_qty=0;
     sk:=RRL_STOCK_PLAN_HELPER.decimal_text(c.RESERVATION_ID);if not reserved_used.exists(sk) then reserved_used(sk):=0;end if;
     k:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',c.UID_POLETA,c.CELL));if not used.exists(k) then used(k):=0;end if;
     v_available:=c.BASE_QTY-reserved_used(sk);
     if v_available>0 then
      v_take:=least(v_qty,v_available);
      select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=c.BASE_UOM and BASE_UOM=c.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
      if v_version is null then raise_application_error(-20868,'SHIPPING_BASE_POLICY_REQUIRED');end if;
      RRL_STOCK_PLAN_HELPER.row_key(r,case when c.SOURCE_DOC_TYPE='PICK_WAVE' then 'RRL_PICK_WAVE' else 'RRL_PICK_PLAN' end,RRL_STOCK_PLAN_HELPER.decimal_text(c.SOURCE_DOC_ID));
      RRL_STOCK_PLAN_HELPER.stock_closure(f,r,c.UID_POLETA,v_article,c.CELL,null);
      leg:=json_object_t();leg.put('row_id',l.get_number('id'));leg.put('uid',c.UID_POLETA);leg.put('cell',c.CELL);leg.put('article',v_article);
      leg.put('source_p',RRL_STOCK_PLAN_HELPER.decimal_text(c.REMAIN-used(k)));leg.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_take));
      leg.put('base_uom',c.BASE_UOM);leg.put('uom_version',v_version);leg.put('reservation_id',c.RESERVATION_ID);leg.put('owner_type',c.SOURCE_DOC_TYPE);leg.put('owner_id',c.SOURCE_DOC_ID);
      leg.put('reservation_version',c.RESERVATION_VERSION);legs.append(leg);used(k):=used(k)+v_take;reserved_used(sk):=reserved_used(sk)+v_take;v_qty:=v_qty-v_take;
      if legs.get_size>200 then raise_application_error(-20881,'SHIPPING_ALLOCATION_BOUND');end if;
     end if;
    end loop;
    if v_qty>0 then raise_application_error(-20868,'SHIPMENT_OWN_PICKED_RESERVATION_INSUFFICIENT');end if;
   else
   select CELL into v_cell from RRL_ARTICULS where ACTICUL=v_article;
   -- Plan only matching article, warehouse and eligible physical cells. No fabricated excess stock.
   for c in(select rr.UID_POLETA,rr.CELL,rr.REMAIN,rr.HARD_RESERVED_BASE,rr.STOCK_VERSION,rr.BASE_UOM,pp.EXPIRY_DATE
    from RRL_REMAINS rr join RRL_PALLETS pp on pp.UID_PALLET=rr.UID_POLETA
    join RRL_CELLS cc on cc.CELL=rr.CELL
    where pp.ARTICUL=v_article and rr.CELL=v_cell and rr.REMAIN>rr.HARD_RESERVED_BASE and cc.WARE_ID=v_ware
     and nvl(cc.BLOCKED_FOR_REMAINS,0)=0 and nvl(cc.BLOCKED_FOR_POPOLNENIE,0)=0
    order by pp.EXPIRY_DATE nulls last,pp.CREATION_DATE nulls last,rr.UID_POLETA
   ) loop
    exit when v_qty=0;
    k:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',c.UID_POLETA,c.CELL));
    if not used.exists(k) then used(k):=0;end if;
    v_available:=c.REMAIN-c.HARD_RESERVED_BASE-used(k);
    if v_available>0 then
     v_take:=least(v_qty,v_available);
     select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=c.BASE_UOM and BASE_UOM=c.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
     if v_version is null then raise_application_error(-20868,'SHIPPING_BASE_POLICY_REQUIRED');end if;
     RRL_STOCK_PLAN_HELPER.stock_closure(f,r,c.UID_POLETA,v_article,c.CELL,null);
     leg:=json_object_t();leg.put('row_id',l.get_number('id'));leg.put('uid',c.UID_POLETA);leg.put('cell',c.CELL);leg.put('article',v_article);
     leg.put('source_p',RRL_STOCK_PLAN_HELPER.decimal_text(c.REMAIN-used(k)));leg.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_take));
     leg.put('base_uom',c.BASE_UOM);leg.put('uom_version',v_version);
     legs.append(leg);used(k):=used(k)+v_take;v_qty:=v_qty-v_take;
     if legs.get_size>200 then raise_application_error(-20881,'SHIPPING_ALLOCATION_BOUND');end if;
    end if;
   end loop;
   if v_qty>0 then raise_application_error(-20868,'SHIPMENT_AVAILABLE_STOCK_INSUFFICIENT');end if;
   end if;
  end loop;
  v.put('customer_order_id',v_customer_order);v.put('document_id',v_id);v.put('pallet_identifier',v_uid);v.put('warehouse',v_ware);
  v.put('rows_signature',rawtohex(sys.dbms_crypto.hash(v_row_json,sys.dbms_crypto.hash_sh256)));v.put('legs',legs);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_shipment(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;l json_object_t;j json_object_t:=json_object_t();
  a json_array_t;facts json_array_t:=json_array_t();v_plan clob;v_condition number;v_id number;v_uid varchar2(200);
  v_row_json clob;v_p number;v_article varchar2(160);v_units clob;v_row_id number;v_qty number;v_kind varchar2(80);v_ready number;sr RRL_STOCK_RESERVATION%rowtype;
 begin
  if RRL_HAS_WRIGHT(p_actor,'CLOSE_OTHOD_NAKLAD')!=1 and RRL_HAS_WRIGHT(p_actor,'stock_posting_shipping')!=1 then raise_application_error(-20882,'SHIPPING_FORBIDDEN');end if;
  v_kind:=d.get_string('command_type');
  select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=d.get_string('operation_id');
  v:=json_object_t.parse(v_plan).get_object('domain');v_id:=v.get_number('document_id');v_uid:=v.get_string('pallet_identifier');
  if v_kind='SHIP_DOCUMENT' then select CONDITION into v_condition from RRL_OTHOD_NAKLAD where ID=v_id for update;
  else select CONDITION into v_condition from RRL_SBORKA_PALLETS where ID=v_id for update;end if;
  if nvl(v_condition,0)>=2 then raise_application_error(-20886,'SHIPMENT_ALREADY_CLOSED_WITH_OTHER_OPERATION');end if;
  v_row_json:=rows_json(v_kind,v_id,v_uid);
  if rawtohex(sys.dbms_crypto.hash(v_row_json,sys.dbms_crypto.hash_sh256))!=v.get_string('rows_signature') then raise_application_error(-20890,'CLOSURE_CHANGED: shipment rows');end if;
  -- Lock actual document rows before stock DML, consistently with the planned domain.
  if v_kind='SHIP_DOCUMENT' then
   for z in(select ID from RRL_OTHOD_NAKLAD_ROWS where ID_NAKLAD=v_id order by ID for update) loop null;end loop;
  else
   for z in(select ID from RRL_SBORKA_PALLET_ROWS where PALLET_UID=v_uid order by ID for update) loop null;end loop;
  end if;
  v_row_json:=rows_json(v_kind,v_id,v_uid);
  if rawtohex(sys.dbms_crypto.hash(v_row_json,sys.dbms_crypto.hash_sh256))!=v.get_string('rows_signature') then raise_application_error(-20890,'CLOSURE_CHANGED: shipment rows');end if;
  a:=v.get_array('legs');
  for i in 0..a.get_size-1 loop
   l:=treat(a.get(i) as json_object_t);v_units:=null;v_row_id:=l.get_number('row_id');v_qty:=RRL_STOCK_MATH.quantity(l.get_string('quantity'));
   select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=l.get_string('uid');
   if v_article!=l.get_string('article') then raise_application_error(-20890,'CLOSURE_CHANGED: shipment article');end if;
   select nvl(br.IS_SHIPMENT_ALLOWED,1) into v_ready from RRL_PALLETS pp left join RRL_PROD_BATCH_READY_V br on br.PROD_BATCH_ID=pp.PROD_BATCH_ID where pp.UID_PALLET=l.get_string('uid');
   if v_ready!=1 then raise_application_error(-20886,'SHIPMENT_REGULATORY_NOT_READY');end if;
   if l.has('reservation_id') then
    select * into sr from RRL_STOCK_RESERVATION where RESERVATION_ID=l.get_number('reservation_id') for update;
    if sr.CUSTOMER_ORDER_ID!=v.get_number('customer_order_id') or sr.RESERVATION_KIND!='HARD' or sr.RESERVATION_DOMAIN!='PICKING'
     or sr.STATUS not in('ACTIVE','ALLOCATED','PICKING') or sr.UID_PALLET!=l.get_string('uid') or sr.CELL!=l.get_string('cell') then raise_application_error(-20890,'CLOSURE_CHANGED: shipment owner');end if;
   end if;
   select REMAIN into v_p from RRL_REMAINS where UID_POLETA=l.get_string('uid') and CELL=l.get_string('cell');
   if RRL_STOCK_PLAN_HELPER.decimal_text(v_p)!=l.get_string('source_p') then raise_application_error(-20890,'CLOSURE_CHANGED: shipment stock');end if;
   if d.get_object('metadata').has('units_by_allocation') then
    if d.get_object('metadata').get_object('units_by_allocation').has(RRL_STOCK_PLAN_HELPER.decimal_text(i+1)) then
     v_units:=d.get_object('metadata').get_object('units_by_allocation').get_array(RRL_STOCK_PLAN_HELPER.decimal_text(i+1)).to_clob;
    end if;
   end if;
   RRL_STOCK_EFFECT_CORE.consume(l.get_string('uid'),l.get_string('cell'),v_qty,l.get_string('base_uom'),l.get_number('uom_version'),v.get_number('warehouse'),
    p_actor,i+1,l.get_number('reservation_id'),l.get_string('owner_type'),l.get_number('owner_id'),v_units,case when v_kind='SHIP_DOCUMENT' then v_id end,case when v_kind='SHIP_PALLET' then v_row_id end);
   if v_kind='SHIP_PALLET' then
    update RRL_SBORKA_PALLET_ROWS set PRIHOD_PALLET_UID=l.get_string('uid') where ID=v_row_id;
   end if;
   facts.append(l);
  end loop;
  if v_kind='SHIP_DOCUMENT' then update RRL_OTHOD_NAKLAD set CONDITION=2 where ID=v_id;
  else update RRL_SBORKA_PALLETS set CONDITION=2 where ID=v_id;end if;
  if v.get_number('customer_order_id') is not null then
   update RRL_CUSTOMER_ORDER_FULFILLMENT set STATUS='SHIPPED',FACT_QTY=(select sum(QUANTITY) from RRL_SBORKA_PALLET_ROWS where PALLET_UID=v_uid),UPDATED_AT=sysdate,UPDATED_BY=p_actor
    where LEGACY_SBORKA_PALLET_ID=v_id and PALLET_UID=v_uid and CUSTOMER_ORDER_ID=v.get_number('customer_order_id');
  end if;
  j.put('operation_id',d.get_string('operation_id'));j.put('status','APPLIED');j.put('document_id',v_id);j.put('allocations',facts);
  p_result:=j.to_clob;
 end;
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
  v_uid varchar2(200);v_cell varchar2(60);v_uom varchar2(20);v_free number;v_own_id number;v_own_qty number;v_num number;v_den number;v_scale number;
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
   v_own_id:=null;v_own_qty:=null;
   for own in(select sr.RESERVATION_ID,sr.BASE_QTY,sr.UID_PALLET,sr.CELL,sr.BASE_UOM,rr.REMAIN
    from RRL_STOCK_RESERVATION sr join RRL_REMAINS rr on rr.UID_POLETA=sr.UID_PALLET and rr.CELL=sr.CELL
    join RRL_CELLS cc on cc.CELL=sr.CELL
    where sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.SOURCE_DOC_ID=v_wave and sr.SOURCE_LINE_ID=rt.PICK_TASK_ID
     and sr.RESERVATION_DOMAIN='PICKING' and sr.RESERVATION_KIND='HARD' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING')
     and sr.BASE_QTY>=rt.QTY and cc.WARE_ID=v_ware and nvl(cc.BLOCKED_FOR_REMAINS,0)=0 and nvl(cc.BLOCKED_FOR_POPOLNENIE,0)=0
    order by sr.RESERVATION_ID) loop
    v_own_id:=own.RESERVATION_ID;v_own_qty:=own.BASE_QTY;v_uid:=own.UID_PALLET;v_cell:=own.CELL;v_uom:=own.BASE_UOM;
    v_qty:=case when rt.REPLENISHMENT_QTY_MODE='FULL_PALLET' then own.REMAIN else rt.QTY end;
    select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=rt.ARTICUL and INPUT_UOM=v_uom and BASE_UOM=v_uom and NUMERATOR=1 and DENOMINATOR=1;
    if v_version is null then raise_application_error(-20868,'WAVE_BASE_POLICY_REQUIRED');end if;
    exit;
   end loop;
   if v_own_id is null then
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
   end if;
   x:=json_object_t();x.put('own_reservation_id',v_own_id);x.put('own_qty',case when v_own_qty is not null then RRL_STOCK_PLAN_HELPER.decimal_text(v_own_qty) end);x.put('task_id',rt.PICK_WAVE_REPLENISH_TASK_ID);x.put('signature',signature(rt));x.put('uid',v_uid);
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
    if x.get('own_reservation_id').is_null then
    v_units:=RRL_STOCK_UNIT_CORE.automatic_units(x.get_string('uid'),x.get_string('cell'),v_qty);
    v_details:=json_object_t();v_details.put('pick_wave_id',v.get_number('wave_id'));
    v_details.put('reservation_scope',case when rt.REPLENISHMENT_QTY_MODE='FULL_PALLET' then 'PALLET' else 'QTY' end);
    RRL_STOCK_RESERVE_CORE.create_hard(v_id,x.get_string('uid'),x.get_string('cell'),v_qty,x.get_string('base_uom'),x.get_number('uom_version'),
     'PICK_WAVE',v.get_number('wave_id'),rt.PICK_WAVE_REPLENISH_TASK_ID,'WAVE',p_actor,v_details.to_clob);
    RRL_STOCK_UNIT_CORE.reserve_units(x.get_string('uid'),x.get_string('cell'),v_id,v_qty,v_units);
    else
     select * into own from RRL_STOCK_RESERVATION where RESERVATION_ID=v_id for update;
     if own.SOURCE_DOC_TYPE!='PICK_WAVE' or own.SOURCE_DOC_ID!=v.get_number('wave_id') or own.SOURCE_LINE_ID!=rt.PICK_TASK_ID
      or own.RESERVATION_DOMAIN!='PICKING' or own.RESERVATION_KIND!='HARD' or own.STATUS not in('ACTIVE','ALLOCATED','PICKING')
      or own.UID_PALLET!=x.get_string('uid') or own.CELL!=x.get_string('cell') or RRL_STOCK_PLAN_HELPER.decimal_text(own.BASE_QTY)!=x.get_string('own_qty') then
      raise_application_error(-20890,'CLOSURE_CHANGED: own picking reserve');end if;
    end if;
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

create or replace package body RRL_STOCK_DOC_RESERVE_CMD as
 function document_table(p_type varchar2) return varchar2 is
 begin
  case p_type when 'PICK_WAVE' then return 'RRL_PICK_WAVE';when 'PICK_PLAN' then return 'RRL_PICK_PLAN';
   when 'PRODUCTION_ORDER' then return 'RRL_PRODUCTION_ORDER';else raise_application_error(-20869,'RESERVATION_DOCUMENT_TYPE_UNSUPPORTED');end case;
 end;
 procedure compile_release(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);s json_object_t;v_type varchar2(40);v_doc number;v_only number;v_kind varchar2(10);
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t:=json_array_t();v json_object_t:=json_object_t();x json_object_t;
 begin
  s:=d.get_object('source');v_type:=s.get_string('document_type');v_doc:=s.get_number('document_id');
  v_only:=nvl(d.get_object('metadata').get_number('only_cancelled_replenishment'),0);v_kind:=d.get_object('metadata').get_string('reservation_kind');
  if v_kind is not null and v_kind not in('SOFT','HARD') then raise_application_error(-20869,'RESERVATION_KIND_INVALID');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.row_key(r,document_table(v_type),RRL_STOCK_PLAN_HELPER.decimal_text(v_doc));
  for sr in(select * from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE=v_type and SOURCE_DOC_ID=v_doc
   and STATUS in('ACTIVE','ALLOCATED','PICKING') and (v_kind is null or RESERVATION_KIND=v_kind) and
    (v_only=0 or (v_type='PICK_WAVE' and RESERVATION_DOMAIN='WAVE' and exists(
     select 1 from RRL_PICK_WAVE_REPLENISH_TASK rt where rt.PICK_WAVE_ID=v_doc and rt.PICK_WAVE_REPLENISH_TASK_ID=SOURCE_LINE_ID and rt.STATUS in('CANCELLED','FAILED'))))
   order by RESERVATION_ID) loop
   if a.get_size>=10000 then raise_application_error(-20881,'DOCUMENT_RESERVATION_BOUND');end if;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(sr.RESERVATION_ID));
   if sr.UID_PALLET is not null then RRL_STOCK_PLAN_HELPER.stock_closure(f,r,sr.UID_PALLET,sr.ARTICUL,sr.CELL,null);
   else RRL_STOCK_PLAN_HELPER.fence(f,'SKU',sr.ARTICUL);end if;
   if v_only=1 then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_REPLENISH_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(sr.SOURCE_LINE_ID));end if;
   x:=json_object_t();x.put('id',sr.RESERVATION_ID);x.put('version',sr.RESERVATION_VERSION);x.put('uid',sr.UID_PALLET);x.put('cell',sr.CELL);a.append(x);
  end loop;
  if d.get_string('command_type') in('WAVE_CANCEL','WAVE_RELEASE') then
   for z in(select PICK_WAVE_TASK_ID,PICK_TASK_ID from RRL_PICK_WAVE_TASK where PICK_WAVE_ID=v_doc order by PICK_WAVE_TASK_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(z.PICK_WAVE_TASK_ID));
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(z.PICK_TASK_ID));
   end loop;
   for z in(select PICK_RESERVATION_ID from RRL_PICK_RESERVATION where PICK_PLAN_ID in(select PICK_PLAN_ID from RRL_PICK_WAVE_ORDER where PICK_WAVE_ID=v_doc) order by PICK_RESERVATION_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(z.PICK_RESERVATION_ID));
   end loop;
   for z in(select PICK_WAVE_REPLENISH_TASK_ID from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=v_doc order by PICK_WAVE_REPLENISH_TASK_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_REPLENISH_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(z.PICK_WAVE_REPLENISH_TASK_ID));
   end loop;
   for z in(select TASK_ID from RRL_WAREHOUSE_TASK where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=v_doc order by TASK_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(z.TASK_ID));
   end loop;
  end if;
  v.put('document_type',v_type);v.put('document_id',v_doc);v.put('only_cancelled',v_only);v.put('reservations',a);
  p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure execute_release(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;x json_object_t;j json_object_t:=json_object_t();
  a json_array_t;sr RRL_STOCK_RESERVATION%rowtype;v_plan clob;v_type varchar2(40);v_doc number;v_status varchar2(40);v_version number;
 begin
  select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=d.get_string('operation_id');
  v:=json_object_t.parse(v_plan).get_object('domain');v_type:=v.get_string('document_type');v_doc:=v.get_number('document_id');a:=v.get_array('reservations');
  if RRL_HAS_WRIGHT(p_actor,'stock_reservation_edit')!=1
   and not(v_type='PICK_WAVE' and (RRL_HAS_WRIGHT(p_actor,'pick_wave_launch')=1 or RRL_HAS_WRIGHT(p_actor,'pick_wave_cancel')=1 or RRL_HAS_WRIGHT(p_actor,'pick_wave_release_reserves')=1))
   and not(v_type='PICK_PLAN' and RRL_HAS_WRIGHT(p_actor,'pick_plan_cancel')=1)
   and not(v_type='PRODUCTION_ORDER' and (RRL_HAS_WRIGHT(p_actor,'mes_raw_transfer_create')=1 or RRL_HAS_WRIGHT(p_actor,'mes_raw_transfer_cancel')=1 or RRL_HAS_WRIGHT(p_actor,'mes_raw_supply_calculate')=1))
   then raise_application_error(-20882,'DOCUMENT_RESERVATION_RELEASE_FORBIDDEN');end if;
  case v_type when 'PICK_WAVE' then select STATUS into v_status from RRL_PICK_WAVE where PICK_WAVE_ID=v_doc for update;
   when 'PICK_PLAN' then select STATUS into v_status from RRL_PICK_PLAN where PICK_PLAN_ID=v_doc for update;
   when 'PRODUCTION_ORDER' then select STATUS into v_status from RRL_PRODUCTION_ORDER where PRODUCTION_ORDER_ID=v_doc for update;
   else raise_application_error(-20869,'DOCUMENT_TYPE_INVALID');end case;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   select * into sr from RRL_STOCK_RESERVATION where RESERVATION_ID=x.get_number('id') for update;
   if sr.RESERVATION_VERSION!=x.get_number('version') or sr.SOURCE_DOC_TYPE!=v_type or sr.SOURCE_DOC_ID!=v_doc or sr.STATUS not in('ACTIVE','ALLOCATED','PICKING') then raise_application_error(-20890,'CLOSURE_CHANGED: document reservation');end if;
   if v.get_number('only_cancelled')=1 then
    select STATUS into v_status from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=v_doc and PICK_WAVE_REPLENISH_TASK_ID=sr.SOURCE_LINE_ID for update;
    if v_status not in('CANCELLED','FAILED') then raise_application_error(-20890,'CLOSURE_CHANGED: replenishment cancellation');end if;
   end if;
   if sr.RESERVATION_KIND='HARD' then
    select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=sr.ARTICUL and INPUT_UOM=sr.BASE_UOM and BASE_UOM=sr.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
    if v_version is null then raise_application_error(-20868,'RESERVATION_RELEASE_BASE_POLICY_REQUIRED');end if;
    RRL_STOCK_UNIT_CORE.release_units(sr.RESERVATION_ID,sr.BASE_QTY,null,0);
    RRL_STOCK_RESERVE_CORE.release_hard(sr.RESERVATION_ID,sr.BASE_QTY,v_version,v_type,v_doc,p_actor);
   elsif sr.RESERVATION_KIND='SOFT' then
    RRL_STOCK_CTX_API.begin_effect('RESERVATION',sr.UID_PALLET,sr.CELL,sr.RESERVATION_ID);
    update RRL_STOCK_RESERVATION set STATUS='RELEASED',RELEASED_AT=systimestamp,RELEASED_BY=p_actor,
     RELEASE_REASON=d.get_object('metadata').get_string('reason'),RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=sr.RESERVATION_ID;
    RRL_STOCK_CTX_API.end_effect;
   else raise_application_error(-20869,'RESERVATION_KIND_INVALID');end if;
  end loop;
  if d.get_string('command_type') in('WAVE_CANCEL','WAVE_RELEASE') then
   for task in(select TASK_ID,STATUS from RRL_WAREHOUSE_TASK where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=v_doc order by TASK_ID for update) loop
    if task.STATUS in('IN_PROGRESS','DONE') then raise_application_error(-20886,'WAVE_PHYSICAL_TASK_ALREADY_STARTED');end if;
    update RRL_WAREHOUSE_TASK set STATUS='CANCELLED' where TASK_ID=task.TASK_ID and STATUS in('PLANNED','ASSIGNED');
   end loop;
  end if;
  if d.get_string('command_type')='WAVE_CANCEL' then
   if RRL_HAS_WRIGHT(p_actor,'pick_wave_cancel')!=1 then raise_application_error(-20882,'WAVE_CANCEL_FORBIDDEN');end if;
   RRL_PICK_WAVE_META.cancel_wave(v_doc,d.get_object('metadata').get_string('reason'),p_actor);
  elsif d.get_string('command_type')='WAVE_RELEASE' then
   if RRL_HAS_WRIGHT(p_actor,'pick_wave_release_reserves')!=1 then raise_application_error(-20882,'WAVE_RELEASE_FORBIDDEN');end if;
   RRL_PICK_WAVE_META.release_reservations(v_doc,p_actor);
  end if;
  j.put('operation_id',d.get_string('operation_id'));j.put('document_type',v_type);j.put('document_id',v_doc);j.put('released_count',a.get_size);p_result:=j.to_clob;
 end;
end;
/

create or replace package body RRL_STOCK_MES_SUPPLY_CMD as
 function nonnegative(p_text varchar2) return number is
 begin if p_text='0' then return 0;end if;return RRL_STOCK_MATH.quantity(p_text);end;

 function convert_qty(p_article varchar2,p_unit varchar2,p_qty number,p_base out varchar2) return number is
  n number;dn number;sc number;ver number;
 begin
  if p_qty is null or p_qty<0 then raise_application_error(-20869,'MES_QUANTITY_INVALID');end if;
  select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_article and INPUT_UOM=p_unit;
  if ver is null then raise_application_error(-20868,'MES_UOM_REQUIRED');end if;
  select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into p_base,n,dn,sc from RRL_STOCK_UOM_CONVERSION
   where ARTICUL=p_article and INPUT_UOM=p_unit and POLICY_VERSION=ver;
  if p_qty=0 then return 0;end if;
  return RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(p_qty),n,dn,sc);
 end;
 function lines_json(p_order number) return clob is a json_array_t:=json_array_t();x json_object_t;
  req number;iss number;b varchar2(20);mb varchar2(20);n number;
 begin
  for l in(select * from RRL_PROD_ORDER_BOM_LINE where PRODUCTION_ORDER_ID=p_order and COMPONENT_ARTICUL is not null order by ORDER_LINE_ID) loop
   if a.get_size>=200 then raise_application_error(-20881,'MES_BOM_BATCH_BOUND');end if;
   req:=convert_qty(l.COMPONENT_ARTICUL,l.UNIT_CODE,l.PLANNED_QTY,b);iss:=0;
   for m in(select BOM_LINE_ID,QUANTITY,UNIT_CODE from RRL_MES_MOVEMENT where PRODUCTION_ORDER_ID=p_order and MOVEMENT_TYPE='RAW_ISSUE_TO_PRODUCTION'
    and STATUS<>'CANCELLED' and RAW_ARTICUL=l.COMPONENT_ARTICUL and (BOM_LINE_ID=l.BOM_LINE_ID or BOM_LINE_ID is null)) loop
    if m.BOM_LINE_ID is null then
     select count(*) into n from RRL_PROD_ORDER_BOM_LINE where PRODUCTION_ORDER_ID=p_order and COMPONENT_ARTICUL=l.COMPONENT_ARTICUL;
     if n!=1 then raise_application_error(-20869,'MES_ISSUED_BOM_LINE_AMBIGUOUS');end if;
    end if;
    iss:=iss+convert_qty(l.COMPONENT_ARTICUL,m.UNIT_CODE,m.QUANTITY,mb);
    if mb!=b then raise_application_error(-20868,'MES_BASE_UOM_CONFLICT');end if;
   end loop;
   x:=json_object_t();x.put('line',l.ORDER_LINE_ID);x.put('bom',l.BOM_ID);x.put('bom_line',l.BOM_LINE_ID);x.put('article',l.COMPONENT_ARTICUL);
   x.put('required',RRL_STOCK_PLAN_HELPER.decimal_text(req));x.put('issued',RRL_STOCK_PLAN_HELPER.decimal_text(iss));x.put('base',b);a.append(x);
  end loop;return a.to_clob;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t:=json_object_t();x json_object_t;y json_object_t;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t;b json_array_t:=json_array_t();oldsr json_array_t:=json_array_t();
  doc number;task number;sr number;wid number;id number;qty number;remainq number;freeq number;total number;ware number;target varchar2(60);
  base varchar2(20);ver number;pending number;raw clob;
  type qty_map is table of number index by varchar2(2000);used qty_map;k varchar2(2000);
 begin
  doc:=d.get_object('source').get_number('production_order_id');target:=d.get_object('metadata').get_string('to_cell');
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PRODUCTION_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(doc));
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  select count(*) into pending from RRL_MES_RAW_TRANSFER_TASK where PRODUCTION_ORDER_ID=doc and TASK_STATUS in('PLANNED','IN_PROGRESS');
  v.put('pending',pending);v.put('document',doc);
  if pending=0 then
   if d.get_string('command_type')='MES_RELEASE_TO_PRODUCTION' then
   select WARE_ID into ware from RRL_CELLS where CELL=target;
   if d.get_object('metadata').get_number('to_ware_id') is not null and d.get_object('metadata').get_number('to_ware_id')!=ware then raise_application_error(-20869,'MES_TARGET_WARE_CONFLICT');end if;
   RRL_STOCK_PLAN_HELPER.fence(f,'CELL',target);end if;v.put('target',target);v.put('warehouse',ware);
   raw:=lines_json(doc);a:=json_array_t.parse(raw);v.put('signature',rawtohex(sys.dbms_crypto.hash(raw,sys.dbms_crypto.hash_sh256)));
   for s in(select * from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PRODUCTION_ORDER' and SOURCE_DOC_ID=doc and RESERVATION_KIND='SOFT' and STATUS in('ACTIVE','ALLOCATED')) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(s.RESERVATION_ID));x:=json_object_t();x.put('id',s.RESERVATION_ID);x.put('version',s.RESERVATION_VERSION);oldsr.append(x);
   end loop;
   for i in 0..a.get_size-1 loop
    x:=treat(a.get(i) as json_object_t);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PROD_ORDER_BOM_LINE',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('line')));
    RRL_STOCK_PLAN_HELPER.fence(f,'SKU',x.get_string('article'));
    select RRL_MES_RAW_DEMAND_SQ.nextval into id from dual;x.put('demand',id);
    remainq:=greatest(nonnegative(x.get_string('required'))-nonnegative(x.get_string('issued')),0);
    x.put('open',RRL_STOCK_PLAN_HELPER.decimal_text(remainq));x.put_null('soft');
    if remainq>0 then select RRL_STOCK_RESERVATION_SQ.nextval into sr from dual;x.put('soft',sr);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(sr));end if;
    for c in(select rr.UID_POLETA,rr.CELL,rr.REMAIN,rr.HARD_RESERVED_BASE,rr.BASE_UOM,cc.WARE_ID
     from RRL_REMAINS rr join RRL_PALLETS pp on pp.UID_PALLET=rr.UID_POLETA join RRL_CELLS cc on cc.CELL=rr.CELL join RRL_WARES ww on ww.ID=cc.WARE_ID
     where pp.ARTICUL=x.get_string('article') and ww.FLAG_RAW_MATERIAL=1 and rr.REMAIN>rr.HARD_RESERVED_BASE
      and nvl(cc.BLOCKED_FOR_REMAINS,0)=0 and nvl(cc.BLOCKED_FOR_POPOLNENIE,0)=0 and (target is null or rr.CELL!=target)
     order by pp.EXPIRY_DATE nulls last,pp.PRODUCED_DATE nulls last,rr.CELL,rr.UID_POLETA) loop
     exit when remainq=0;if b.get_size>=1000 then raise_application_error(-20881,'MES_ALLOCATION_BATCH_BOUND');end if;
     if c.BASE_UOM!=x.get_string('base') then raise_application_error(-20868,'MES_SOURCE_BASE_CONFLICT');end if;
     k:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',c.UID_POLETA,c.CELL));if not used.exists(k) then used(k):=0;end if;
     freeq:=c.REMAIN-c.HARD_RESERVED_BASE-used(k);if freeq<=0 then continue;end if;
     qty:=least(freeq,remainq);used(k):=used(k)+qty;remainq:=remainq-qty;
     select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=x.get_string('article') and INPUT_UOM=c.BASE_UOM and BASE_UOM=c.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
     if ver is null then raise_application_error(-20868,'MES_BASE_POLICY_REQUIRED');end if;
     select RRL_STOCK_RESERVATION_SQ.nextval,RRL_MES_RAW_TRANSFER_TASK_SQ.nextval,RRL_WAREHOUSE_TASK_SQ.nextval,RRL_MES_RAW_SUPPLY_CANDIDATE_SQ.nextval into sr,task,wid,id from dual;
     RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(sr));
     RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_MES_RAW_TRANSFER_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(task));RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(wid));
     RRL_STOCK_PLAN_HELPER.stock_closure(f,r,c.UID_POLETA,x.get_string('article'),c.CELL,null);
     y:=json_object_t();y.put('demand',x.get_number('demand'));y.put('reservation',sr);y.put('task',task);y.put('warehouse_task',wid);y.put('candidate',id);
     y.put('uid',c.UID_POLETA);y.put('cell',c.CELL);y.put('ware',c.WARE_ID);y.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));y.put('physical',RRL_STOCK_PLAN_HELPER.decimal_text(c.REMAIN));
     y.put('hard',RRL_STOCK_PLAN_HELPER.decimal_text(c.HARD_RESERVED_BASE));y.put('uom_version',ver);y.put('line_index',i);b.append(y);
    end loop;
    x.put('shortage',RRL_STOCK_PLAN_HELPER.decimal_text(remainq));
    if remainq>0 then select RRL_MES_RAW_SHORTAGE_SQ.nextval into id from dual;x.put('shortage_id',id);end if;
    a.put(i,x);
   end loop;
   v.put('lines',a);v.put('allocations',b);v.put('old_soft',oldsr);
  end if;
  p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;x json_object_t;y json_object_t;detail json_object_t;result json_object_t:=json_object_t();
  plan clob;a json_array_t;b json_array_t;oldsr json_array_t;doc number;pending number;qty number;req number;iss number;oq number;shortq number;n number;cnt number:=0;physical number;hard number;
  status varchar2(40);raw clob;unitkeys clob;pal RRL_PALLETS%rowtype;old RRL_STOCK_RESERVATION%rowtype;
 begin
  if (d.get_string('command_type')='MES_CALCULATE_SUPPLY' and RRL_HAS_WRIGHT(p_actor,'mes_raw_supply_calculate')!=1) or (d.get_string('command_type')='MES_RELEASE_TO_PRODUCTION' and RRL_HAS_WRIGHT(p_actor,'mes_raw_transfer_create')!=1) then raise_application_error(-20882,'MES_SUPPLY_FORBIDDEN');end if;
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=d.get_string('operation_id');v:=json_object_t.parse(plan).get_object('domain');doc:=v.get_number('document');
  select STATUS into status from RRL_PRODUCTION_ORDER where PRODUCTION_ORDER_ID=doc for update;
  if status is null or status in('COMPLETED','CANCELLED') then raise_application_error(-20886,'MES_ORDER_NOT_OPEN');end if;
  select count(*) into pending from RRL_MES_RAW_TRANSFER_TASK where PRODUCTION_ORDER_ID=doc and TASK_STATUS in('PLANNED','IN_PROGRESS');
  if pending!=v.get_number('pending') then raise_application_error(-20890,'CLOSURE_CHANGED: MES pending tasks');end if;
  if pending>0 then
   select count(*) into n from RRL_MES_RAW_DEMAND where PRODUCTION_ORDER_ID=doc;result.put('demand_count',n);
   select count(*) into n from RRL_MES_RAW_SUPPLY_CANDIDATE where PRODUCTION_ORDER_ID=doc;result.put('candidate_count',n);
   select count(*) into n from RRL_MES_RAW_SHORTAGE where PRODUCTION_ORDER_ID=doc and STATUS='OPEN';result.put('shortage_count',n);
   result.put('task_count',pending);result.put('existing',1);p_result:=result.to_clob;return;end if;
  a:=v.get_array('lines');b:=v.get_array('allocations');oldsr:=v.get_array('old_soft');
  for i in 0..a.get_size-1 loop x:=treat(a.get(i) as json_object_t);select ORDER_LINE_ID into n from RRL_PROD_ORDER_BOM_LINE where ORDER_LINE_ID=x.get_number('line') for update;end loop;
  raw:=lines_json(doc);if rawtohex(sys.dbms_crypto.hash(raw,sys.dbms_crypto.hash_sh256))!=v.get_string('signature') then raise_application_error(-20890,'CLOSURE_CHANGED: MES requirements');end if;
  if d.get_string('command_type')='MES_RELEASE_TO_PRODUCTION' then RRL_STOCK_LOCATION_CORE.assert_ordinary(v.get_string('target'),v.get_number('warehouse'),'TARGET');end if;
  for i in 0..b.get_size-1 loop
   y:=treat(b.get(i) as json_object_t);
   select REMAIN,HARD_RESERVED_BASE into physical,hard from RRL_REMAINS where UID_POLETA=y.get_string('uid') and CELL=y.get_string('cell');
   if physical!=RRL_STOCK_MATH.quantity(y.get_string('physical')) or hard!=nonnegative(y.get_string('hard')) then raise_application_error(-20890,'CLOSURE_CHANGED: MES source availability');end if;
  end loop;
  for i in 0..oldsr.get_size-1 loop
   x:=treat(oldsr.get(i) as json_object_t);select * into old from RRL_STOCK_RESERVATION where RESERVATION_ID=x.get_number('id') for update;
   if old.RESERVATION_VERSION!=x.get_number('version') or old.RESERVATION_KIND!='SOFT' or old.STATUS not in('ACTIVE','ALLOCATED') then raise_application_error(-20890,'CLOSURE_CHANGED: MES soft demand');end if;
   RRL_STOCK_CTX_API.begin_effect('RESERVATION',null,null,old.RESERVATION_ID);
   update RRL_STOCK_RESERVATION set STATUS='CANCELLED',RELEASED_AT=systimestamp,RELEASED_BY=p_actor,RELEASE_REASON='MES raw supply recalculation',RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=old.RESERVATION_ID;RRL_STOCK_CTX_API.end_effect;
  end loop;
  delete from RRL_MES_RAW_SUPPLY_CANDIDATE where PRODUCTION_ORDER_ID=doc;delete from RRL_MES_RAW_SHORTAGE where PRODUCTION_ORDER_ID=doc;delete from RRL_MES_RAW_DEMAND where PRODUCTION_ORDER_ID=doc;
  shortq:=0;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);req:=nonnegative(x.get_string('required'));iss:=nonnegative(x.get_string('issued'));oq:=nonnegative(x.get_string('open'));qty:=nonnegative(x.get_string('shortage'));
   if oq>0 then
    RRL_STOCK_CTX_API.begin_effect('RESERVATION',null,null,x.get_number('soft'));
    insert into RRL_STOCK_RESERVATION(RESERVATION_ID,RESERVATION_KIND,RESERVATION_SCOPE,RESERVATION_DOMAIN,SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_LINE_ID,PRODUCTION_ORDER_ID,ARTICUL,QTY,UNIT_CODE,STATUS,PRIORITY,CREATED_BY,RESERVATION_VERSION)
     values(x.get_number('soft'),'SOFT','QTY','MES_RAW','PRODUCTION_ORDER',doc,x.get_number('line'),doc,x.get_string('article'),oq,x.get_string('base'),'ACTIVE',100,p_actor,0);RRL_STOCK_CTX_API.end_effect;
   end if;
   insert into RRL_MES_RAW_DEMAND(DEMAND_ID,PRODUCTION_ORDER_ID,ORDER_LINE_ID,BOM_ID,BOM_LINE_ID,RAW_ARTICUL,REQUIRED_QTY,ISSUED_QTY,OPEN_QTY,UNIT_CODE,SOFT_RESERVATION_ID,STATUS,CALCULATED_BY)
    values(x.get_number('demand'),doc,x.get_number('line'),x.get_number('bom'),x.get_number('bom_line'),x.get_string('article'),req,iss,oq,x.get_string('base'),x.get_number('soft'),case when oq>0 then 'OPEN' else 'COVERED' end,p_actor);
   if qty>0 then
    shortq:=shortq+1;
    insert into RRL_MES_RAW_SHORTAGE(SHORTAGE_ID,PRODUCTION_ORDER_ID,DEMAND_ID,RAW_ARTICUL,REQUIRED_QTY,ISSUED_QTY,AVAILABLE_QTY,SHORTAGE_QTY,UNIT_CODE,STATUS)
     values(x.get_number('shortage_id'),doc,x.get_number('demand'),x.get_string('article'),req,iss,oq-qty,qty,x.get_string('base'),'OPEN');
   end if;
  end loop;
  for i in 0..b.get_size-1 loop
   y:=treat(b.get(i) as json_object_t);x:=treat(a.get(y.get_number('line_index')) as json_object_t);qty:=RRL_STOCK_MATH.quantity(y.get_string('quantity'));
   select * into pal from RRL_PALLETS where UID_PALLET=y.get_string('uid');
   if pal.ARTICUL!=x.get_string('article') then raise_application_error(-20890,'CLOSURE_CHANGED: MES source article');end if;
   RRL_STOCK_LOCATION_CORE.assert_ordinary(y.get_string('cell'),y.get_number('ware'),'SOURCE');
   physical:=RRL_STOCK_MATH.quantity(y.get_string('physical'));hard:=nonnegative(y.get_string('hard'));req:=nonnegative(x.get_string('required'));
   insert into RRL_MES_RAW_SUPPLY_CANDIDATE(CANDIDATE_ID,DEMAND_ID,PRODUCTION_ORDER_ID,RAW_ARTICUL,UID_PALLET,BATCH_ID,RAW_BATCH_ID,SSCC,FROM_WARE_ID,FROM_CELL,PHYSICAL_QTY,HARD_RESERVED_QTY,AVAILABLE_QTY,SUGGESTED_QTY,EXPIRY_DATE,QUALITY_STATUS,SORT_ORDER)
    values(y.get_number('candidate'),x.get_number('demand'),doc,x.get_string('article'),pal.UID_PALLET,to_char(pal.PRIHOD_NAKLAD_ID),pal.PRIHOD_NAKLAD_ID,pal.SSCC,y.get_number('ware'),y.get_string('cell'),physical,hard,qty,qty,pal.EXPIRY_DATE,pal.QUALITY_STATUS,i+1);
   if d.get_string('command_type')='MES_RELEASE_TO_PRODUCTION' and (shortq=0 or d.get_object('metadata').get_number('allow_partial')=1) then
    detail:=json_object_t();detail.put('reservation_scope','QTY');detail.put('task_id',y.get_number('task'));detail.put('production_order_id',doc);detail.put('batch_id',to_char(pal.PRIHOD_NAKLAD_ID));
    RRL_STOCK_RESERVE_CORE.create_hard(y.get_number('reservation'),pal.UID_PALLET,y.get_string('cell'),qty,x.get_string('base'),y.get_number('uom_version'),'PRODUCTION_ORDER',doc,x.get_number('line'),'MES_RAW',p_actor,detail.to_clob);
    unitkeys:=RRL_STOCK_UNIT_CORE.automatic_units(pal.UID_PALLET,y.get_string('cell'),qty);RRL_STOCK_UNIT_CORE.reserve_units(pal.UID_PALLET,y.get_string('cell'),y.get_number('reservation'),qty,unitkeys);
    insert into RRL_MES_RAW_TRANSFER_TASK(TASK_ID,PRODUCTION_ORDER_ID,ORDER_LINE_ID,BOM_ID,BOM_LINE_ID,RAW_ARTICUL,RAW_BATCH_ID,BATCH_ID,UID_PALLET,SSCC,FROM_WARE_ID,FROM_CELL,TO_WARE_ID,TO_CELL,REQUIRED_QTY,TASK_QTY,UNIT_CODE,RESERVATION_ID,TASK_STATUS,PRIORITY,CREATED_BY)
     values(y.get_number('task'),doc,x.get_number('line'),x.get_number('bom'),x.get_number('bom_line'),x.get_string('article'),pal.PRIHOD_NAKLAD_ID,to_char(pal.PRIHOD_NAKLAD_ID),pal.UID_PALLET,pal.SSCC,y.get_number('ware'),y.get_string('cell'),v.get_number('warehouse'),v.get_string('target'),req,qty,x.get_string('base'),y.get_number('reservation'),'PLANNED',100,p_actor);
    insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,PRODUCTION_ORDER_ID,RAW_ARTICUL,UID_PALLET,SSCC,FROM_WARE_ID,FROM_CELL,TO_WARE_ID,TO_CELL,QTY,UNIT_CODE,QTY_MODE,PRIORITY,STATUS,CREATED_AT,CREATED_BY)
     values(y.get_number('warehouse_task'),'RAW_TO_PRODUCTION','MES_RAW_SUPPLY',y.get_number('task'),'PRODUCTION_ORDER',doc,doc,x.get_string('article'),pal.UID_PALLET,pal.SSCC,y.get_number('ware'),y.get_string('cell'),v.get_number('warehouse'),v.get_string('target'),qty,x.get_string('base'),'QTY',100,'PLANNED',systimestamp,p_actor);cnt:=cnt+1;
   end if;
  end loop;
  if cnt>0 then update RRL_PRODUCTION_ORDER set STATUS=case when STATUS='DRAFT' then 'RELEASED' else STATUS end,UPDATED_AT=systimestamp,UPDATED_BY=p_actor where PRODUCTION_ORDER_ID=doc;end if;
  result.put('operation_id',d.get_string('operation_id'));result.put('task_count',cnt);result.put('shortage_count',shortq);result.put('demand_count',a.get_size);result.put('candidate_count',b.get_size);p_result:=result.to_clob;
 end;
end;
/

create or replace package body RRL_STOCK_MES_CANCEL_CMD as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);t RRL_MES_RAW_TRANSFER_TASK%rowtype;sr RRL_STOCK_RESERVATION%rowtype;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();v json_object_t:=json_object_t();a json_array_t:=json_array_t();
 begin
  select * into t from RRL_MES_RAW_TRANSFER_TASK where TASK_ID=d.get_object('source').get_number('raw_task_id');
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PRODUCTION_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(t.PRODUCTION_ORDER_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_MES_RAW_TRANSFER_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(t.TASK_ID));
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  if t.RESERVATION_ID is not null then
   select * into sr from RRL_STOCK_RESERVATION where RESERVATION_ID=t.RESERVATION_ID;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(sr.RESERVATION_ID));
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,sr.UID_PALLET,sr.ARTICUL,sr.CELL,null);
   v.put('reservation',sr.RESERVATION_ID);v.put('reservation_version',sr.RESERVATION_VERSION);
  end if;
  for w in(select TASK_ID from RRL_WAREHOUSE_TASK where TASK_SOURCE='MES_RAW_SUPPLY' and SOURCE_TASK_ID=t.TASK_ID and STATUS not in('DONE','CANCELLED') order by TASK_ID) loop
   if a.get_size>=200 then raise_application_error(-20881,'MES_CANCEL_TASK_BOUND');end if;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(w.TASK_ID));a.append(w.TASK_ID);
  end loop;
  v.put('document',t.PRODUCTION_ORDER_ID);v.put('raw_task',t.TASK_ID);v.put('warehouse_tasks',a);
  p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;j json_object_t:=json_object_t();a json_array_t;
  plan clob;t RRL_MES_RAW_TRANSFER_TASK%rowtype;sr RRL_STOCK_RESERVATION%rowtype;status varchar2(40);ver number;n number;id number;
 begin
  if RRL_HAS_WRIGHT(p_actor,'mes_raw_transfer_cancel')!=1 then raise_application_error(-20882,'MES_CANCEL_FORBIDDEN');end if;
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=d.get_string('operation_id');v:=json_object_t.parse(plan).get_object('domain');a:=v.get_array('warehouse_tasks');
  select STATUS into status from RRL_PRODUCTION_ORDER where PRODUCTION_ORDER_ID=v.get_number('document') for update;
  select * into t from RRL_MES_RAW_TRANSFER_TASK where TASK_ID=v.get_number('raw_task') for update;
  if t.PRODUCTION_ORDER_ID!=v.get_number('document') or nvl(t.RESERVATION_ID,-1)!=nvl(v.get_number('reservation'),-1) then raise_application_error(-20890,'CLOSURE_CHANGED: MES cancellation');end if;
  if t.TASK_STATUS='DONE' then raise_application_error(-20886,'COMPLETED_TASK_CANNOT_CANCEL');end if;
  select count(*) into n from RRL_WAREHOUSE_TASK where TASK_SOURCE='MES_RAW_SUPPLY' and SOURCE_TASK_ID=t.TASK_ID and STATUS not in('DONE','CANCELLED');
  if n!=a.get_size then raise_application_error(-20890,'CLOSURE_CHANGED: MES task children');end if;
  if t.RESERVATION_ID is not null then
   select * into sr from RRL_STOCK_RESERVATION where RESERVATION_ID=t.RESERVATION_ID for update;
   if sr.RESERVATION_VERSION!=v.get_number('reservation_version') or sr.SOURCE_DOC_TYPE!='PRODUCTION_ORDER' or sr.SOURCE_DOC_ID!=t.PRODUCTION_ORDER_ID then raise_application_error(-20890,'CLOSURE_CHANGED: MES reservation');end if;
   if sr.STATUS in('ACTIVE','ALLOCATED','PICKING') then
    if sr.RESERVATION_KIND!='HARD' then raise_application_error(-20869,'MES_HARD_RESERVATION_REQUIRED');end if;
    select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=sr.ARTICUL and INPUT_UOM=sr.BASE_UOM and BASE_UOM=sr.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
    if ver is null then raise_application_error(-20868,'MES_BASE_POLICY_REQUIRED');end if;
    RRL_STOCK_UNIT_CORE.release_units(sr.RESERVATION_ID,sr.BASE_QTY,null,0);
    RRL_STOCK_RESERVE_CORE.release_hard(sr.RESERVATION_ID,sr.BASE_QTY,ver,'PRODUCTION_ORDER',t.PRODUCTION_ORDER_ID,p_actor);
    RRL_STOCK_CTX_API.begin_effect('RESERVATION',sr.UID_PALLET,sr.CELL,sr.RESERVATION_ID);
    update RRL_STOCK_RESERVATION set STATUS='CANCELLED',RELEASE_REASON=d.get_object('metadata').get_string('reason'),RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=sr.RESERVATION_ID;
    RRL_STOCK_CTX_API.end_effect;
   end if;
  end if;
  for i in 0..a.get_size-1 loop
   id:=a.get_number(i);select STATUS into status from RRL_WAREHOUSE_TASK where TASK_ID=id for update;
   if status in('DONE','CANCELLED') then raise_application_error(-20890,'CLOSURE_CHANGED: MES child state');end if;
   update RRL_WAREHOUSE_TASK set STATUS='CANCELLED',CANCELLED_AT=systimestamp,CANCELLED_BY=p_actor,LAST_ERROR=d.get_object('metadata').get_string('reason') where TASK_ID=id;
  end loop;
  update RRL_MES_RAW_TRANSFER_TASK set TASK_STATUS='CANCELLED',CANCELLED_AT=systimestamp,CANCELLED_BY=p_actor,LAST_ERROR=d.get_object('metadata').get_string('reason') where TASK_ID=t.TASK_ID;
  j.put('operation_id',d.get_string('operation_id'));j.put('raw_task_id',t.TASK_ID);j.put('status','CANCELLED');p_result:=j.to_clob;
 end;
end;
/

create or replace package body RRL_STOCK_EVENT_BRIDGE as
 procedure after_event(p_operation varchar2,p_line number,p_leg number,p_uid varchar2,p_from varchar2,p_to varchar2,
  p_qty number,p_uom varchar2,p_uom_version number,p_type number) is
  setting varchar2(20);req clob;d json_object_t;a json_array_t;l json_object_t;found boolean:=false;
  base varchar2(20);num number;den number;scale number;ver number;qty number;
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','MODE')='EXPLICIT' then return;end if;
  select nvl(max(SETTING_VALUE),'0') into setting from RRL_SYSTEM_SETTINGS where SETTING_KEY='STOCK_LEGACY_TRIGGER_ENABLED';
  if setting!='1' then raise_application_error(-20863,'LEGACY_STOCK_POSTING_DISABLED');end if;
  if sys_context('RRL_STOCK_WRITE_CTX','MODE') is null or sys_context('RRL_STOCK_WRITE_CTX','MODE')!='COMPAT'
   or p_operation is null or p_operation!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')
   or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then
   raise_application_error(-20863,'LEGACY_PLAN_REQUIRED');end if;
  select CANONICAL_REQUEST into req from RRL_STOCK_OPERATION where OPERATION_ID=p_operation and COMMAND_TYPE='COMPAT_MANUAL_MOVE' and STATE='IN_FLIGHT';
  d:=json_object_t.parse(req);a:=d.get_array('lines');
  for i in 0..a.get_size-1 loop
   l:=treat(a.get(i) as json_object_t);
   if l.get_number('line_number')=p_line then
    if found then raise_application_error(-20870,'LEGACY_MANIFEST_LINE_REPEATED');end if;found:=true;
    select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=l.get_string('article') and INPUT_UOM=l.get_string('unit');
    select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into base,num,den,scale from RRL_STOCK_UOM_CONVERSION
     where ARTICUL=l.get_string('article') and INPUT_UOM=l.get_string('unit') and POLICY_VERSION=ver;
    qty:=RRL_STOCK_MATH.convert_exact(l.get_string('quantity'),num,den,scale);
    select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=l.get_string('article') and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
    if p_leg!=1 or p_type!=2 or p_from is null or p_to is null or p_from!=l.get_string('source_cell') or p_to!=l.get_string('target_cell')
     or p_uid!=l.get_string('uid') or p_qty!=qty or p_uom!=base or p_uom_version!=ver then raise_application_error(-20870,'LEGACY_MANIFEST_EVENT_CONFLICT');end if;
   end if;
  end loop;
  if not found then raise_application_error(-20870,'LEGACY_MANIFEST_LINE_REQUIRED');end if;
  RRL_STOCK_BALANCE_CORE.apply_delta(p_uid,p_from,-p_qty,0,p_uom,p_uom_version);
  RRL_STOCK_BALANCE_CORE.apply_delta(p_uid,p_to,p_qty,0,p_uom,p_uom_version);
 end;
end;
/

create or replace package body RRL_STOCK_INVENTORY_CMD as
 procedure compile_count(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);a json_array_t;b json_array_t:=json_array_t();x json_object_t;y json_object_t;v json_object_t:=json_object_t();
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();doc number;ware number;article varchar2(160);base varchar2(20);inputu varchar2(20);
  qty number;ver number;stockver number;signature varchar2(64);p number;h number;k varchar2(2000);
  type keys is table of boolean index by varchar2(2000);seen keys;
 begin
  doc:=d.get_object('source').get_number('revision_id');select WARE_ID into ware from RRL_REVIZION where ID=doc;
  a:=d.get_object('metadata').get_array('counts');
  if a is null or a.get_size<1 or a.get_size>200 then raise_application_error(-20881,'INVENTORY_COUNT_BATCH_BOUND');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_REVIZION',RRL_STOCK_PLAN_HELPER.decimal_text(doc));
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);select ARTICUL into article from RRL_PALLETS where UID_PALLET=x.get_string('uid');
   if article is null or article!=x.get_string('article') then raise_application_error(-20887,'INVENTORY_LOT_ARTICLE_CONFLICT');end if;
   k:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',x.get_string('uid'),x.get_string('cell')));if seen.exists(k) then raise_application_error(-20885,'INVENTORY_LOT_REPEATED');end if;seen(k):=true;
   inputu:=x.get_string('unit');
   RRL_STOCK_PALLET_UOM.resolve_quantity(x.get_string('uid'),inputu,
    case when regexp_like(x.get_string('quantity'),'^0([.]0{1,9})?$') then '1' else x.get_string('quantity') end,base,qty,ver,signature);
   if regexp_like(x.get_string('quantity'),'^0([.]0{1,9})?$') then qty:=0;end if;
   begin select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION into p,h,stockver from RRL_REMAINS where UID_POLETA=x.get_string('uid') and CELL=x.get_string('cell');
   exception when no_data_found then p:=0;h:=0;stockver:=0;end;
   if x.get_number('expected_stock_version') is null or x.get_number('expected_stock_version')!=stockver then raise_application_error(-20867,'INVENTORY_SNAPSHOT_STALE');end if;
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,x.get_string('uid'),article,x.get_string('cell'),null);
   y:=json_object_t();y.put('uid',x.get_string('uid'));y.put('cell',x.get_string('cell'));y.put('article',article);
   y.put('base',base);y.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));y.put('p',RRL_STOCK_PLAN_HELPER.decimal_text(p));
   y.put('h',RRL_STOCK_PLAN_HELPER.decimal_text(h));y.put('version',stockver);y.put('uom_version',ver);y.put('signature',signature);b.append(y);
  end loop;
  v.put('document',doc);v.put('warehouse',ware);v.put('counts',b);p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure execute_count(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;x json_object_t;sourcex json_object_t;fact json_object_t;result json_object_t:=json_object_t();
  a json_array_t;original json_array_t;facts json_array_t:=json_array_t();plan clob;doc number;ware number;cond number;
  p number;h number;stockver number;qty number;delta number;ver number;basever number;eventid number;marking number;signature varchar2(64);base varchar2(20);units clob;
 begin
  if RRL_HAS_WRIGHT(p_actor,'stock_inventory_count')!=1 then raise_application_error(-20882,'INVENTORY_COUNT_FORBIDDEN');end if;
  if trim(d.get_object('metadata').get_string('reason')) is null then raise_application_error(-20883,'INVENTORY_REASON_REQUIRED');end if;
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=d.get_string('operation_id');v:=json_object_t.parse(plan).get_object('domain');
  doc:=v.get_number('document');select WARE_ID,CONDITION into ware,cond from RRL_REVIZION where ID=doc for update;
  if ware!=v.get_number('warehouse') or cond is null or cond in(2,3) then raise_application_error(-20886,'INVENTORY_DOCUMENT_NOT_OPEN');end if;
  a:=v.get_array('counts');original:=d.get_object('metadata').get_array('counts');
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);sourcex:=treat(original.get(i) as json_object_t);
   RRL_STOCK_LOCATION_CORE.assert_quarantine(x.get_string('cell'),ware);
   begin select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION into p,h,stockver from RRL_REMAINS where UID_POLETA=x.get_string('uid') and CELL=x.get_string('cell');
   exception when no_data_found then p:=0;h:=0;stockver:=0;end;
   if stockver!=x.get_number('version') or RRL_STOCK_PLAN_HELPER.decimal_text(p)!=x.get_string('p') or RRL_STOCK_PLAN_HELPER.decimal_text(h)!=x.get_string('h') then raise_application_error(-20890,'CLOSURE_CHANGED: inventory stock');end if;
   RRL_STOCK_PALLET_UOM.resolve_quantity(x.get_string('uid'),sourcex.get_string('unit'),
    case when regexp_like(sourcex.get_string('quantity'),'^0([.]0{1,9})?$') then '1' else sourcex.get_string('quantity') end,base,qty,ver,signature);
   if regexp_like(sourcex.get_string('quantity'),'^0([.]0{1,9})?$') then qty:=0;end if;
   if signature!=x.get_string('signature') or base!=x.get_string('base') then raise_application_error(-20890,'CLOSURE_CHANGED: inventory UOM');end if;
   if qty<h then raise_application_error(-20869,'INVENTORY_COUNT_BELOW_HARD: explicitly release conflicting reservations first');end if;
   select max(POLICY_VERSION) into basever from RRL_STOCK_UOM_CONVERSION where ARTICUL=x.get_string('article') and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
   if basever is null then raise_application_error(-20868,'INVENTORY_BASE_POLICY_REQUIRED');end if;
   delta:=qty-p;eventid:=null;units:=null;
   if sourcex.has('unit_keys') and sourcex.get_array('unit_keys').get_size>0 then units:=sourcex.get_array('unit_keys').to_clob;end if;
   if delta>0 then
    select greatest(nvl((select MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY where ARTICUL=x.get_string('article')),0),
      nvl((select CRPT_REQUIRED from RRL_FINISHED_GOODS_SKU where ARTICUL=x.get_string('article')),0),
      case when exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=x.get_string('article')) then 1 else 0 end) into marking from dual;
    if marking!=0 then raise_application_error(-20884,'MARKED_INVENTORY_INCREASE_REQUIRES_CAPTURED_UNITS');end if;
    RRL_STOCK_BALANCE_CORE.apply_delta(x.get_string('uid'),x.get_string('cell'),delta,0,base,basever,stockver);
    RRL_STOCK_BALANCE_CORE.write_leg(x.get_string('uid'),null,x.get_string('cell'),delta,base,basever,i+1,1,1,p_actor,eventid);
   elsif delta<0 then
    RRL_STOCK_UNIT_CORE.issue_free_units(x.get_string('uid'),x.get_string('cell'),-delta,units);
    RRL_STOCK_BALANCE_CORE.apply_delta(x.get_string('uid'),x.get_string('cell'),delta,0,base,basever,stockver);
    RRL_STOCK_BALANCE_CORE.write_leg(x.get_string('uid'),x.get_string('cell'),null,delta,base,basever,i+1,1,3,p_actor,eventid);
   end if;
   fact:=json_object_t();fact.put('uid',x.get_string('uid'));fact.put('cell',x.get_string('cell'));fact.put('base_uom',base);
   fact.put('before',RRL_STOCK_PLAN_HELPER.decimal_text(p));fact.put('after',RRL_STOCK_PLAN_HELPER.decimal_text(qty));fact.put('delta',RRL_STOCK_PLAN_HELPER.decimal_text(delta));fact.put('event_id',eventid);facts.append(fact);
  end loop;
  result.put('operation_id',d.get_string('operation_id'));result.put('revision_id',doc);result.put('counts',facts);p_result:=result.to_clob;
 end;
end;
/

create or replace package body RRL_STOCK_WAVE_LAUNCH_CMD as
 function signature(p RRL_PICK_RESERVATION%rowtype) return varchar2 is j json_object_t:=json_object_t();
 begin
  j.put('id',p.PICK_RESERVATION_ID);j.put('plan',p.PICK_PLAN_ID);j.put('line',p.PICK_PLAN_LINE_ID);j.put('task',p.PICK_TASK_ID);
  j.put('uid',p.PALLET_UID);j.put('cell',p.SOURCE_CELL_CODE);j.put('article',p.ARTICUL);j.put('qty',RRL_STOCK_PLAN_HELPER.decimal_text(p.RESERVED_QTY));
  j.put('status',p.RESERVATION_STATUS);j.put('level',p.RESERVATION_LEVEL);
  j.put('customer',p.CUSTOMER_ID);j.put('order',p.CUSTOMER_ORDER_ID);
  return rawtohex(sys.dbms_crypto.hash(j.to_clob,sys.dbms_crypto.hash_sh256));
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);v_wave number;v_ware number;v_id number;v_uom varchar2(20);v_ver number;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t:=json_array_t();v json_object_t:=json_object_t();x json_object_t;
 begin
  v_wave:=d.get_object('source').get_number('wave_id');select WARE_ID into v_ware from RRL_PICK_WAVE where PICK_WAVE_ID=v_wave;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(v_wave));
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  for o in(select * from RRL_PICK_WAVE_ORDER where PICK_WAVE_ID=v_wave and STATUS='ACTIVE' order by PICK_WAVE_ORDER_ID) loop
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(o.PICK_WAVE_ORDER_ID));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_PLAN',RRL_STOCK_PLAN_HELPER.decimal_text(o.PICK_PLAN_ID));
   for t in(select PICK_TASK_ID from RRL_PICK_TASK where PICK_PLAN_ID=o.PICK_PLAN_ID order by PICK_TASK_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(t.PICK_TASK_ID));
   end loop;
  end loop;
  for pr in(select pr.* from RRL_PICK_RESERVATION pr join RRL_PICK_WAVE_ORDER wo on wo.PICK_PLAN_ID=pr.PICK_PLAN_ID
   where wo.PICK_WAVE_ID=v_wave and wo.STATUS='ACTIVE' and pr.RESERVATION_STATUS='ACTIVE' and pr.RESERVATION_LEVEL='SOFT' order by pr.PICK_RESERVATION_ID) loop
   if a.get_size>=200 then raise_application_error(-20881,'WAVE_LAUNCH_BATCH_BOUND');end if;
   if pr.PALLET_UID is null or pr.SOURCE_CELL_CODE is null or pr.RESERVED_QTY<=0 then raise_application_error(-20884,'WAVE_SOURCE_IDENTITY_REQUIRED');end if;
   select BASE_UOM into v_uom from RRL_REMAINS where UID_POLETA=pr.PALLET_UID and CELL=pr.SOURCE_CELL_CODE;
   select max(POLICY_VERSION) into v_ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=pr.ARTICUL and INPUT_UOM=v_uom and BASE_UOM=v_uom and NUMERATOR=1 and DENOMINATOR=1;
   if v_ver is null then raise_application_error(-20868,'WAVE_BASE_POLICY_REQUIRED');end if;
   select RRL_STOCK_RESERVATION_SQ.nextval into v_id from dual;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(pr.PICK_RESERVATION_ID));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(v_id));
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,pr.PALLET_UID,pr.ARTICUL,pr.SOURCE_CELL_CODE,null);
   x:=json_object_t();x.put('projection_id',pr.PICK_RESERVATION_ID);x.put('reservation_id',v_id);x.put('signature',signature(pr));
   x.put('uom',v_uom);x.put('version',v_ver);a.append(x);
  end loop;
  if a.get_size=0 then raise_application_error(-20886,'WAVE_NO_SOFT_RESERVATIONS');end if;
  v.put('wave',v_wave);v.put('warehouse',v_ware);v.put('reservations',a);p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;x json_object_t;j json_object_t:=json_object_t();details json_object_t;
  a json_array_t;plan clob;status varchar2(30);cnt number;ware number;ready number;units clob;pr RRL_PICK_RESERVATION%rowtype;
 begin
  if RRL_HAS_WRIGHT(p_actor,'pick_wave_launch')!=1 then raise_application_error(-20882,'WAVE_LAUNCH_FORBIDDEN');end if;
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=d.get_string('operation_id');v:=json_object_t.parse(plan).get_object('domain');a:=v.get_array('reservations');
  select STATUS,WARE_ID into status,ware from RRL_PICK_WAVE where PICK_WAVE_ID=v.get_number('wave') for update;
  if status not in('DRAFT','PREVIEW') or ware!=v.get_number('warehouse') then raise_application_error(-20886,'WAVE_NOT_LAUNCHABLE');end if;
  select count(*) into cnt from RRL_PICK_RESERVATION pr join RRL_PICK_WAVE_ORDER wo on wo.PICK_PLAN_ID=pr.PICK_PLAN_ID
   where wo.PICK_WAVE_ID=v.get_number('wave') and wo.STATUS='ACTIVE' and pr.RESERVATION_STATUS='ACTIVE' and pr.RESERVATION_LEVEL='SOFT';
  if cnt!=a.get_size then raise_application_error(-20890,'CLOSURE_CHANGED: wave sources');end if;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);select * into pr from RRL_PICK_RESERVATION where PICK_RESERVATION_ID=x.get_number('projection_id') for update;
   if signature(pr)!=x.get_string('signature') then raise_application_error(-20890,'CLOSURE_CHANGED: wave reservation');end if;
   RRL_STOCK_LOCATION_CORE.assert_ordinary(pr.SOURCE_CELL_CODE,ware,'SOURCE');
   select nvl(br.IS_SHIPMENT_ALLOWED,1) into ready from RRL_PALLETS pp left join RRL_PROD_BATCH_READY_V br on br.PROD_BATCH_ID=pp.PROD_BATCH_ID where pp.UID_PALLET=pr.PALLET_UID;
   if ready!=1 then raise_application_error(-20886,'WAVE_SOURCE_REGULATORY_NOT_READY');end if;
   units:=RRL_STOCK_UNIT_CORE.automatic_units(pr.PALLET_UID,pr.SOURCE_CELL_CODE,pr.RESERVED_QTY);
   details:=json_object_t();details.put('reservation_scope','QTY');details.put('pick_wave_id',v.get_number('wave'));
   details.put('pick_plan_id',pr.PICK_PLAN_ID);details.put('pick_plan_line_id',pr.PICK_PLAN_LINE_ID);
   details.put('customer_order_id',pr.CUSTOMER_ORDER_ID);details.put('customer_id',pr.CUSTOMER_ID);
   RRL_STOCK_RESERVE_CORE.create_hard(x.get_number('reservation_id'),pr.PALLET_UID,pr.SOURCE_CELL_CODE,pr.RESERVED_QTY,x.get_string('uom'),x.get_number('version'),
    'PICK_WAVE',v.get_number('wave'),pr.PICK_TASK_ID,'PICKING',p_actor,details.to_clob);
   RRL_STOCK_UNIT_CORE.reserve_units(pr.PALLET_UID,pr.SOURCE_CELL_CODE,x.get_number('reservation_id'),pr.RESERVED_QTY,units);
  end loop;
  RRL_PICK_WAVE_META.launch_wave(v.get_number('wave'),p_actor);
  j.put('operation_id',d.get_string('operation_id'));j.put('wave_id',v.get_number('wave'));j.put('reserved_count',a.get_size);j.put('status','LAUNCHED');p_result:=j.to_clob;
 end;
end;
/
