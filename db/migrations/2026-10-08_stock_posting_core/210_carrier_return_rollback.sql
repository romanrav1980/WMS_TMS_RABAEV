declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_RESERVE_CORE authid definer
 accessible by(package RRL_STOCK_CASE_SHORT_CMD,package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_STOCK_MES_CANCEL_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_WAVE_CMD,package RRL_STOCK_EFFECT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,package RRL_STOCK_TRANSFER_CORE) as
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

create or replace package RRL_STOCK_TRANSFER_CORE authid definer
 accessible by(package RRL_STOCK_CASE_MOVE_CMD,package RRL_STOCK_CASE_PICK_CMD,package RRL_STOCK_INTERNAL_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE,
 package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_MOVE_CORE,package RRL_STOCK_MES_CORE) as
 procedure move(p_uid varchar2,p_target_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,
  p_uom varchar2,p_uom_version number,p_warehouse number,p_actor varchar2,p_line number,
  p_reservation number default null,p_units clob default null,p_new_reservation number default null,p_target_slot number default null,p_source_warehouse number default null,p_location_mode varchar2 default 'ORDINARY');
end;
/

create or replace package RRL_STOCK_UNIT_CORE authid definer
 accessible by(package RRL_STOCK_INVENTORY_BIRTH,package RRL_STOCK_CASE_SHORT_CMD,package RRL_STOCK_RECEIPT_REVERSE,package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_MES_CANCEL_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_WAVE_CMD,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_INVARIANT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_TRANSFER_CORE,
 package RRL_STOCK_EFFECT_CORE,package RRL_STOCK_RECEIPT_CORE) as
 function automatic_units(p_uid varchar2,p_cell varchar2,p_qty number) return clob;
 procedure admit_captured(p_uid varchar2,p_cell varchar2);
 procedure assert_composition(p_uid varchar2,p_cell varchar2);
 procedure issue_free_units(p_uid varchar2,p_cell varchar2,p_qty number,p_units clob);
 procedure reserve_units(p_uid varchar2,p_cell varchar2,p_id number,p_qty number,p_units clob);
 procedure release_units(p_id number,p_qty number,p_units clob,p_issue number default 0);
end;
/

create or replace package RRL_STOCK_CASE_PICK_CMD authid definer
 accessible by(package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_CASE_SHORT_CMD,package RRL_STOCK_CASE_MOVE_CMD,package RRL_STOCK_POSTING_API) as
 function carrier_rows(p_task number) return clob;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_POSTING_API authid definer as
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null);
 procedure execute_prepared(p_result out clob);
 procedure stage_birth(p_uid varchar2);
 procedure finish_birth_capture;
 procedure reset_connection;
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
   p_doc_type varchar2,p_doc_id number,p_line_id number,p_domain varchar2,p_actor varchar2,p_details clob default null) is v_article varchar2(160);v_ware number;v_details json_object_t;v_carrier number;
 begin
  lock_identity(p_id);
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',p_uid));
  select count(*) into v_carrier from RRL_CASE_CARRIER_LOT where LOT_UID=p_uid;
  if v_carrier>0 then raise_application_error(-20869,'CASE_CARRIER_NOT_ALLOCATABLE: unpack through carrier return');end if;
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
   declare
 v_json_sql_1_1 varchar2(32767):=v_details.get_string('reservation_scope');
 v_json_sql_1_2 number:=v_details.get_number('task_id');
 v_json_sql_1_3 number:=v_details.get_number('customer_id');
 v_json_sql_1_4 number:=v_details.get_number('customer_order_id');
 v_json_sql_1_5 number:=v_details.get_number('production_order_id');
 v_json_sql_1_6 number:=v_details.get_number('pick_plan_id');
 v_json_sql_1_7 number:=v_details.get_number('pick_plan_line_id');
 v_json_sql_1_8 number:=v_details.get_number('pick_wave_id');
 v_json_sql_1_9 number:=v_details.get_number('pick_wave_line_id');
 v_json_sql_1_10 varchar2(32767):=v_details.get_string('batch_id');
 v_json_sql_1_11 number:=v_details.get_number('prod_batch_id');
 v_json_sql_1_12 number:=v_details.get_number('cell_slot_id');
 v_json_sql_1_13 number:=v_details.get_number('priority');
begin
update RRL_STOCK_RESERVATION set RESERVATION_SCOPE=v_json_sql_1_1,
    TASK_ID=v_json_sql_1_2,CUSTOMER_ID=v_json_sql_1_3,CUSTOMER_ORDER_ID=v_json_sql_1_4,
    PRODUCTION_ORDER_ID=case when p_doc_type='PRODUCTION_ORDER' then p_doc_id else v_json_sql_1_5 end,
    PICK_PLAN_ID=case when p_doc_type='PICK_PLAN' then p_doc_id else v_json_sql_1_6 end,
    PICK_PLAN_LINE_ID=v_json_sql_1_7,PICK_WAVE_ID=case when p_doc_type='PICK_WAVE' then p_doc_id else v_json_sql_1_8 end,
    PICK_WAVE_LINE_ID=v_json_sql_1_9,BATCH_ID=v_json_sql_1_10,PROD_BATCH_ID=v_json_sql_1_11,
    CELL_SLOT_ID=v_json_sql_1_12,PRIORITY=nvl(v_json_sql_1_13,100),RESERVATION_VERSION=RESERVATION_VERSION+1
    where RESERVATION_ID=p_id;
end;
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
  v_r RRL_STOCK_RESERVATION%rowtype;v_result_reservation number;v_system number;v_command varchar2(80);v_operation varchar2(100);
 begin
  if p_uid is null or p_target_uid is null or p_from is null or p_to is null or (p_from=p_to and p_uid=p_target_uid)
   or p_qty is null or p_qty<=0 then raise_application_error(-20886,'TRANSFER_CONTRACT_INVALID');end if;
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',p_uid));
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',p_target_uid));
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_target_uid));
  select count(*) into v_sum from RRL_CASE_CARRIER_LOT where LOT_UID in(p_uid,p_target_uid);
  if v_sum>0 then
   v_operation:=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
   select COMMAND_TYPE into v_command from RRL_STOCK_OPERATION where OPERATION_ID=v_operation;
   if v_command not in('CASE_PICK_CONFIRM','CASE_CARRIER_MOVE','CASE_CARRIER_RETURN') then raise_application_error(-20886,'CASE_MEMBER_REQUIRES_CARRIER_COMMAND');end if;
  end if;
  if p_location_mode='CASE_TRANSIT' then
   if p_to!='CPT_'||RRL_STOCK_PLAN_HELPER.decimal_text(p_warehouse) then raise_application_error(-20886,'CASE_TRANSIT_TARGET_REQUIRED');end if;
   select IS_SYSTEM into v_system from RRL_CELLS where CELL=p_to;
   if v_system is null or v_system!=1 then raise_application_error(-20886,'CASE_TRANSIT_SYSTEM_LOCATION_REQUIRED');end if;
   if p_from=p_to then RRL_STOCK_LOCATION_CORE.assert_quarantine(p_from,p_warehouse);
   else RRL_STOCK_LOCATION_CORE.assert_ordinary(p_from,nvl(p_source_warehouse,p_warehouse),'SOURCE');end if;
   RRL_STOCK_LOCATION_CORE.assert_quarantine(p_to,p_warehouse);
  elsif p_location_mode='CASE_EXIT' then
   if p_from!='CPT_'||RRL_STOCK_PLAN_HELPER.decimal_text(nvl(p_source_warehouse,p_warehouse)) then raise_application_error(-20886,'CASE_TRANSIT_SOURCE_REQUIRED');end if;
   RRL_STOCK_LOCATION_CORE.assert_quarantine(p_from,nvl(p_source_warehouse,p_warehouse));
   RRL_STOCK_LOCATION_CORE.assert_ordinary(p_to,p_warehouse,'TARGET');
  elsif p_location_mode='PUTAWAY' then
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
  if p_qty=v_p then
   v_hmove:=v_h;
  elsif p_reservation is not null then
   require_row(p_reservation);
   select * into v_r from RRL_STOCK_RESERVATION where RESERVATION_ID=p_reservation;
   if v_r.UID_PALLET is null or v_r.UID_PALLET!=p_uid or v_r.CELL is null or v_r.CELL!=p_from
    or v_r.RESERVATION_KIND!='HARD' or v_r.STATUS not in('ACTIVE','ALLOCATED','PICKING')
    or v_r.BASE_QTY is null or v_r.BASE_QTY<=0 then raise_application_error(-20869,'TRANSFER_RESERVATION_CONFLICT');end if;
   v_hmove:=least(p_qty,v_r.BASE_QTY);
   if p_qty-v_hmove>v_p-v_h then raise_application_error(-20869,'TRANSFER_FREE_PORTION_INSUFFICIENT');end if;
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
   -- CURRENT_UID is the warehouse physical authority. Published regulatory
   -- aggregations are retained; the coordinator queues composition before/after
   -- in the same transaction, for asynchronous regulatory reaggregation.
   -- Birth UID/code and external acknowledgement are never rewritten here.
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
     case when p_qty=v_p then r.BASE_QTY else v_hmove end,p_target_slot,p_actor,v_result_reservation);
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
  v_p number;v_base varchar2(20);v_total number;v_count number;v_bad number;v_article varchar2(160);v_marked number;v_scale number;
 begin
  select REMAIN,BASE_UOM into v_p,v_base from RRL_REMAINS where UID_POLETA=p_uid and CELL=p_cell;
  select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=p_uid;
  select greatest(nvl((select MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY where ARTICUL=v_article),0),
   nvl((select CRPT_REQUIRED from RRL_FINISHED_GOODS_SKU where ARTICUL=v_article),0),
   case when exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=v_article) then 1 else 0 end) into v_marked from dual;
  select count(*),nvl(sum(BASE_QTY),0),nvl(sum(case when PHYSICAL_UNIT_KEY is null or STOCK_STATUS is null or BASE_QTY<=0 or BASE_UOM is null or BASE_UOM!=v_base then 1 else 0 end),0)
   into v_count,v_total,v_bad from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and (STOCK_STATUS is null or STOCK_STATUS!='ISSUED');
  select max(BASE_SCALE) into v_scale from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and BASE_UOM=v_base;
  if v_scale is null then raise_application_error(-20868,'COMPOSITION_BASE_POLICY_REQUIRED');end if;
  select count(*) into v_bad from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and (STOCK_STATUS is null or STOCK_STATUS!='ISSUED')
   and (STOCK_STATUS is null or BASE_QTY is null or BASE_QTY<=0 or abs(BASE_QTY)>=power(10,18) or trunc(BASE_QTY,v_scale)!=BASE_QTY or BASE_UOM is null or BASE_UOM!=v_base or PHYSICAL_UNIT_KEY is null);
  if v_bad>0 or (v_count>0 and v_total!=v_p) or (v_marked=1 and v_p>0 and v_count=0) then
   raise_application_error(-20884,'PHYSICAL_COMPOSITION_CONFLICT');end if;
 end;
 function automatic_units(p_uid varchar2,p_cell varchar2,p_qty number) return clob is
  a json_array_t:=json_array_t();v_n number;v_qty number:=0;
 begin
  require_context;assert_composition(p_uid,p_cell);
  select count(*) into v_n from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED';
  if v_n=0 then return null;end if;
  for u in(select PHYSICAL_UNIT_KEY,BASE_QTY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS='AVAILABLE' and HARD_RESERVATION_ID is null order by PHYSICAL_UNIT_KEY) loop
   exit when v_qty=p_qty;
   own_unit(u.PHYSICAL_UNIT_KEY);
   if v_qty+u.BASE_QTY>p_qty then raise_application_error(-20884,'PHYSICAL_UNIT_ALLOCATION_REQUIRES_SELECTION');end if;
   a.append(u.PHYSICAL_UNIT_KEY);v_qty:=v_qty+u.BASE_QTY;
   if a.get_size>10000 then raise_application_error(-20884,'UNIT_SELECTION_BOUND');end if;
  end loop;
  if v_qty!=p_qty then raise_application_error(-20884,'ADMITTED_FREE_UNITS_INSUFFICIENT');end if;
  return a.to_clob;
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

create or replace package body RRL_STOCK_CASE_PICK_CMD as
 function carrier_rows(p_task number) return clob is
  a json_array_t:=json_array_t();x json_object_t;
 begin
  for r in(select h.LOT_UID,s.CELL,s.REMAIN,s.STOCK_VERSION,s.BASE_UOM,p.ARTICUL,h.CASE_PICK_LINE_ID
   from RRL_CASE_CARRIER_LOT h join RRL_REMAINS s on s.UID_POLETA=h.LOT_UID join RRL_PALLETS p on p.UID_PALLET=h.LOT_UID
   where h.CASE_PICK_TASK_ID=p_task and s.REMAIN>0 order by h.LOT_UID,s.CELL fetch first 201 rows only) loop
   if a.get_size=200 then raise_application_error(-20881,'CASE_CARRIER_LOT_BOUND');end if;
   x:=json_object_t();x.put('uid',r.LOT_UID);x.put('cell',r.CELL);x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(r.REMAIN));
   x.put('version',r.STOCK_VERSION);x.put('base',r.BASE_UOM);x.put('article',r.ARTICUL);x.put('case_line',r.CASE_PICK_LINE_ID);a.append(x);
  end loop;
  return a.to_clob;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t:=json_object_t();
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t;chunks json_array_t:=json_array_t();x json_object_t;selected_wire clob;
  ct RRL_CASE_PICK_TASK%rowtype;l RRL_CASE_PICK_LINE%rowtype;pt RRL_PICK_TASK%rowtype;
  task_id number;line_id number;fact number;remaining number;q number;basever number;newres number;target varchar2(150);n number:=0;v_cell varchar2(60);target_cell varchar2(60);
  type source_numbers is table of number index by varchar2(150);consumed source_numbers;steps source_numbers;
 begin
  task_id:=d.get_object('source').get_number('case_task_id');line_id:=d.get_object('source').get_number('case_line_id');
  select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_id;
  select * into l from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=line_id and CASE_PICK_TASK_ID=task_id;
  select * into pt from RRL_PICK_TASK where PICK_TASK_ID=l.PICK_TASK_ID;
  if ct.WARE_ID is null or ct.WARE_ID<1 or ct.SSCC is null or l.CELL_CODE is null or l.ARTICUL is null or l.PICK_TASK_ID is null or l.PICK_WAVE_TASK_ID is null or l.CUSTOMER_ORDER_ID is null then raise_application_error(-20887,'CASE_TASK_IDENTITY_REQUIRED');end if;
  fact:=RRL_STOCK_MATH.quantity(m.get_string('fact_qty'));remaining:=fact-nvl(l.PICKED_QTY,0);v_cell:=l.CELL_CODE;target_cell:='CPT_'||RRL_STOCK_PLAN_HELPER.decimal_text(ct.WARE_ID);
  if remaining<=0 or fact>l.PLANNED_QTY then raise_application_error(-20886,'CASE_PICK_FACT_NOT_INCREASING_OR_EXCEEDS_PLAN');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(task_id));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_LINE',RRL_STOCK_PLAN_HELPER.decimal_text(line_id));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_TASK_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_WAVE_TASK_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_WAVE_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(l.CUSTOMER_ORDER_ID));
  RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU','CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(task_id));
  a:=json_array_t.parse(carrier_rows(task_id));
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,x.get_string('uid'),x.get_string('article'),x.get_string('cell'),target_cell);
  end loop;
  selected_wire:=d.get_array('units').to_clob;
  for sr in(select sr.RESERVATION_ID,sr.UID_PALLET,sr.CELL,sr.BASE_QTY,sr.BASE_UOM,s.REMAIN,s.STOCK_VERSION,p.EXPIRY_DATE
   from RRL_STOCK_RESERVATION sr join RRL_REMAINS s on s.UID_POLETA=sr.UID_PALLET and s.CELL=sr.CELL
    join RRL_PALLETS p on p.UID_PALLET=sr.UID_PALLET
   where sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.SOURCE_DOC_ID=l.PICK_WAVE_ID and sr.SOURCE_LINE_ID=l.PICK_TASK_ID
    and sr.RESERVATION_KIND='HARD' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING') and sr.CELL=v_cell
    and p.ARTICUL=l.ARTICUL and not exists(select 1 from RRL_CASE_CARRIER_LOT h where h.LOT_UID=sr.UID_PALLET)
   order by p.EXPIRY_DATE nulls last,sr.UID_PALLET,sr.RESERVATION_ID fetch first 201 rows only) loop
   exit when remaining=0;n:=n+1;
   if n>200 or sr.BASE_QTY is null or sr.BASE_QTY<=0 then raise_application_error(-20881,'CASE_SOURCE_RESERVATION_BOUND_OR_INVALID');end if;
   if d.get_array('units').get_size>0 then
    select nvl(sum(u.BASE_QTY),0) into q from RRL_WMS_RECEIPT_UNIT u
     join json_table(selected_wire,'$[*]' columns(K varchar2(64) path '$'))j on j.K=u.PHYSICAL_UNIT_KEY
     where u.CURRENT_UID=sr.UID_PALLET and u.CURRENT_CELL=v_cell and u.HARD_RESERVATION_ID=sr.RESERVATION_ID and u.STOCK_STATUS!='ISSUED';
    if q=0 then continue;end if;
    if q>remaining or q>sr.BASE_QTY then raise_application_error(-20884,'CASE_SCANNED_UNIT_QUANTITY_CONFLICT');end if;
   else q:=least(remaining,sr.BASE_QTY);end if;
   remaining:=remaining-q;
   select max(POLICY_VERSION) into basever from RRL_STOCK_UOM_CONVERSION where ARTICUL=l.ARTICUL and INPUT_UOM=sr.BASE_UOM and BASE_UOM=sr.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
   if basever is null then raise_application_error(-20868,'CASE_BASE_POLICY_REQUIRED');end if;
   target:='CASELOT:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256))||':'||RRL_STOCK_PLAN_HELPER.decimal_text(n);
   select RRL_STOCK_RESERVATION_SQ.nextval into newres from dual;
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,sr.UID_PALLET,l.ARTICUL,v_cell,target_cell);
   RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',target);RRL_STOCK_PLAN_HELPER.anchor(r,50,'STOCK',target);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(newres));
   RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','PALLET:'||target);
   x:=json_object_t();x.put('source_uid',sr.UID_PALLET);x.put('target_uid',target);x.put('reservation',sr.RESERVATION_ID);x.put('new_reservation',newres);
   x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(q));x.put('base',sr.BASE_UOM);x.put('policy',basever);
   if not consumed.exists(sr.UID_PALLET) then consumed(sr.UID_PALLET):=0;steps(sr.UID_PALLET):=0;end if;
   x.put('stock_version',sr.STOCK_VERSION+steps(sr.UID_PALLET));x.put('source_p',RRL_STOCK_PLAN_HELPER.decimal_text(sr.REMAIN-consumed(sr.UID_PALLET)));
   consumed(sr.UID_PALLET):=consumed(sr.UID_PALLET)+q;steps(sr.UID_PALLET):=steps(sr.UID_PALLET)+1;chunks.append(x);
  end loop;
  if remaining!=0 then raise_application_error(-20869,'CASE_OWN_HARD_IN_PICK_CELL_INSUFFICIENT');end if;
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  v.put('task_id',task_id);v.put('line_id',line_id);v.put('pick_task',l.PICK_TASK_ID);v.put('wave_task',l.PICK_WAVE_TASK_ID);
  v.put('wave_id',l.PICK_WAVE_ID);v.put('customer_order',l.CUSTOMER_ORDER_ID);v.put('warehouse',ct.WARE_ID);v.put('cell',v_cell);v.put('transit_cell',target_cell);v.put('article',l.ARTICUL);
  v.put('previous_qty',RRL_STOCK_PLAN_HELPER.decimal_text(nvl(l.PICKED_QTY,0)));v.put('planned_qty',RRL_STOCK_PLAN_HELPER.decimal_text(l.PLANNED_QTY));
  v.put('content_version',ct.CONTENT_VERSION);v.put('carrier_identifier',ct.SSCC);v.put('carrier',a);v.put('chunks',chunks);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t;x json_object_t;
  a json_array_t;chunks json_array_t;facts json_array_t:=json_array_t();factx json_object_t;keys json_array_t;selected json_array_t;keyx json_element_t;unit_wire clob;
  ct RRL_CASE_PICK_TASK%rowtype;l RRL_CASE_PICK_LINE%rowtype;pt RRL_PICK_TASK%rowtype;p RRL_PALLETS%rowtype;
  plan clob;nowrows clob;oldrows clob;op varchar2(100);task_id number;line_id number;ware number;v_cell varchar2(60);article varchar2(160);target_cell varchar2(60);
  qty number;fact number;before_qty number;ver number;stockver number;physical number;owned number;base varchar2(20);uid varchar2(150);target varchar2(150);sid number;new_sid number;
  wave_status varchar2(40);n number;posted number;line_no number:=0;unit_key varchar2(64);matched number;scan_product varchar2(4000);newstatus varchar2(20);eventid number;offline varchar2(100);
 begin
  if RRL_HAS_WRIGHT(p_actor,'case_pick_execute')!=1 then raise_application_error(-20882,'CASE_PICK_FORBIDDEN');end if;
  op:=d.get_string('operation_id');select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');
  task_id:=v.get_number('task_id');line_id:=v.get_number('line_id');ware:=v.get_number('warehouse');v_cell:=v.get_string('cell');article:=v.get_string('article');target_cell:=v.get_string('transit_cell');
  declare
 v_json_sql_1_1 number:=v.get_number('wave_id');
begin
select STATUS into wave_status from RRL_PICK_WAVE where PICK_WAVE_ID=v_json_sql_1_1 for update;
end;
  if wave_status in('CANCELLED','CLOSED','DRAFT','PREVIEW') or wave_status is null then raise_application_error(-20886,'CASE_WAVE_STATE_CONFLICT');end if;
  select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_id for update;
  select * into l from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=line_id for update;
  select * into pt from RRL_PICK_TASK where PICK_TASK_ID=l.PICK_TASK_ID for update;
  if ct.WARE_ID!=ware or ct.CONTENT_VERSION!=v.get_number('content_version') or ct.SSCC!=v.get_string('carrier_identifier')
   or l.CASE_PICK_TASK_ID!=task_id or l.PICK_TASK_ID!=v.get_number('pick_task') or l.PICK_WAVE_TASK_ID!=v.get_number('wave_task')
   or l.PICK_WAVE_ID!=v.get_number('wave_id') or l.CUSTOMER_ORDER_ID!=v.get_number('customer_order') or l.CELL_CODE!=v_cell or l.ARTICUL!=article
   or RRL_STOCK_PLAN_HELPER.decimal_text(l.PLANNED_QTY)!=v.get_string('planned_qty')
   or RRL_STOCK_PLAN_HELPER.decimal_text(nvl(l.PICKED_QTY,0))!=v.get_string('previous_qty') then raise_application_error(-20890,'CLOSURE_CHANGED: case task identity');end if;
  if ct.STATUS is null or ct.STATUS not in('IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT') or l.STATUS is null or l.STATUS not in('NEW','ACTIVE','SKIPPED','IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT')
   or pt.TASK_TYPE is null or pt.TASK_TYPE!='CASE_PICK' or pt.STATUS is null or pt.STATUS in('DONE','CANCELLED','FAILED') or pt.CUSTOMER_ORDER_ID!=l.CUSTOMER_ORDER_ID or pt.ARTICUL!=article then raise_application_error(-20886,'CASE_TASK_LINE_STATE_CONFLICT');end if;
  -- Reporting/rejecting a short uses CONFIG exclusive; this command holds CONFIG shared
  -- and the same task/line anchors, so the pending decision cannot change this fact mid-post.
  select count(*) into n from RRL_CASE_PICK_SHORT where CASE_PICK_LINE_ID=line_id
   and STATUS in('CREATED','PENDING_APPROVAL');
  if n>0 then raise_application_error(-20886,'CASE_SHORT_DECISION_PENDING');end if;
  if ct.ASSIGNED_TO is not null and ct.ASSIGNED_TO!=p_actor and RRL_HAS_WRIGHT(p_actor,'case_pick_manage')!=1 then raise_application_error(-20882,'CASE_TASK_ACTOR_CONFLICT');end if;
  if m.get_string('scan_cell') is null or upper(m.get_string('scan_cell'))!=upper(v_cell)
   or m.get_string('scan_container') is null or m.get_string('scan_container')!=ct.SSCC then raise_application_error(-20886,'CASE_CELL_CARRIER_SCAN_REQUIRED');end if;
  scan_product:=m.get_string('scan_product');
  select count(*) into n from RRL_ARTICULS where ACTICUL=article and scan_product in(ACTICUL,BARCODE_SHT,BARCODE_KOR,BARCODE_BL);
  if n!=1 and d.get_array('units').get_size=0 then raise_application_error(-20886,'CASE_PRODUCT_SCAN_CONFLICT');end if;
  nowrows:=carrier_rows(task_id);a:=v.get_array('carrier');oldrows:=a.to_clob;
  if dbms_lob.compare(nowrows,oldrows)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: case carrier stock');end if;
  before_qty:=nvl(l.PICKED_QTY,0);posted:=0;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   if x.get_number('case_line')=line_id then posted:=posted+RRL_STOCK_MATH.quantity(x.get_string('quantity'));end if;
  end loop;
  if posted!=before_qty then raise_application_error(-20886,'CASE_PRIOR_FACT_WITHOUT_PHYSICAL_POSTING');end if;
  fact:=RRL_STOCK_MATH.quantity(m.get_string('fact_qty'));
  if fact<=before_qty or fact>l.PLANNED_QTY then raise_application_error(-20886,'CASE_PICK_FACT_CONFLICT');end if;
  keys:=d.get_array('units');unit_wire:=keys.to_clob;matched:=0;
  -- Move already picked contents with their carrier to the newly scanned pick v_cell.
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);uid:=x.get_string('uid');
   if ct.CURRENT_CELL is null or ct.CURRENT_CELL!=x.get_string('cell') then raise_application_error(-20887,'CASE_CARRIER_LOCATION_CONFLICT');end if;
   if x.get_string('cell')!=target_cell then
    base:=x.get_string('base');
    declare
 v_json_sql_2_1 varchar2(32767):=x.get_string('article');
begin
select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_json_sql_2_1 and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
end;
    line_no:=line_no+1;
    RRL_STOCK_TRANSFER_CORE.move(uid,uid,x.get_string('cell'),target_cell,RRL_STOCK_MATH.quantity(x.get_string('quantity')),base,ver,ware,p_actor,line_no,null,null,null,null,null,'CASE_TRANSIT');
   end if;
  end loop;
  chunks:=v.get_array('chunks');
  for i in 0..chunks.get_size-1 loop
   x:=treat(chunks.get(i) as json_object_t);uid:=x.get_string('source_uid');target:=x.get_string('target_uid');
   qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));base:=x.get_string('base');sid:=x.get_number('reservation');new_sid:=x.get_number('new_reservation');
   select REMAIN,STOCK_VERSION into physical,stockver from RRL_REMAINS where UID_POLETA=uid and CELL=v_cell;
   if stockver!=x.get_number('stock_version') or RRL_STOCK_PLAN_HELPER.decimal_text(physical)!=x.get_string('source_p') then raise_application_error(-20890,'CLOSURE_CHANGED: case source stock');end if;
   select BASE_QTY into owned from RRL_STOCK_RESERVATION where RESERVATION_ID=sid and UID_PALLET=uid and CELL=v_cell
    and SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=l.PICK_WAVE_ID and SOURCE_LINE_ID=l.PICK_TASK_ID
    and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING');
   if owned<qty then raise_application_error(-20869,'CASE_OWN_HARD_INSUFFICIENT');end if;
   select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=article and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
   if ver is null or ver!=x.get_number('policy') then raise_application_error(-20890,'CLOSURE_CHANGED: case UOM policy');end if;
   selected:=json_array_t();
   for selected_unit in(select u.PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT u
    join json_table(unit_wire,'$[*]' columns(K varchar2(64) path '$'))j on j.K=u.PHYSICAL_UNIT_KEY
    where u.CURRENT_UID=uid and u.CURRENT_CELL=v_cell and u.HARD_RESERVATION_ID=sid and u.STOCK_STATUS!='ISSUED'
    order by u.PHYSICAL_UNIT_KEY) loop
    selected.append(selected_unit.PHYSICAL_UNIT_KEY);matched:=matched+1;
   end loop;
   select count(*) into n from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=uid and CURRENT_CELL=v_cell and STOCK_STATUS!='ISSUED';
   if n>0 and selected.get_size=0 then raise_application_error(-20884,'CASE_MARKED_UNIT_SCANS_REQUIRED');end if;
   select * into p from RRL_PALLETS where UID_PALLET=uid;
   if p.ARTICUL!=article then raise_application_error(-20887,'CASE_LOT_ARTICLE_CONFLICT');end if;
   p.STOCK_ORIGIN_UID:=nvl(p.STOCK_ORIGIN_UID,p.UID_PALLET);p.CREATED_BY_STOCK_OP:=op;p.UID_PALLET:=target;p.SSCC:=null;p.PRINTED:=0;
   if p.WEIGHT_BRUTTO is not null or p.WEIGHT_TN is not null or p.COUNT_KOR is not null then
    if p.UNIT_COUNT is null or p.UNIT_COUNT<=0 then raise_application_error(-20887,'CASE_LOT_BIRTH_QUANTITY_REQUIRED');end if;
    p.WEIGHT_BRUTTO:=p.WEIGHT_BRUTTO*qty/p.UNIT_COUNT;
    p.WEIGHT_TN:=p.WEIGHT_TN*qty/p.UNIT_COUNT;p.COUNT_KOR:=p.COUNT_KOR*qty/p.UNIT_COUNT;
   end if;
   p.UNIT_COUNT:=qty;insert into RRL_PALLETS values p;
   line_no:=line_no+1;
   RRL_STOCK_TRANSFER_CORE.move(uid,target,v_cell,target_cell,qty,base,ver,ware,p_actor,line_no,sid,
    case when selected.get_size>0 then selected.to_clob else null end,new_sid,null,null,'CASE_TRANSIT');
   insert into RRL_CASE_CARRIER_LOT(LOT_UID,CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,CREATED_OPERATION,CREATED_BY)
    values(target,task_id,line_id,op,p_actor);
   factx:=json_object_t();factx.put('uid',target);factx.put('source_uid',uid);factx.put('quantity',x.get_string('quantity'));factx.put('unit',base);facts.append(factx);
  end loop;
  if matched!=keys.get_size then raise_application_error(-20884,'CASE_SELECTED_UNIT_NOT_OWNED');end if;
  newstatus:=case when fact=l.PLANNED_QTY then 'PICKED' else 'PARTIAL' end;offline:=m.get_string('offline_event_id');
  update RRL_CASE_PICK_LINE set PICKED_QTY=fact,STATUS=newstatus,LAST_OFFLINE_EVENT_ID=offline,
   STARTED_AT=nvl(STARTED_AT,systimestamp),DONE_AT=case when newstatus='PICKED' then systimestamp else DONE_AT end,UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_LINE_ID=line_id;
  update RRL_PICK_TASK set FACT_QTY=fact,STATUS=case when newstatus='PICKED' then 'DONE' else 'IN_PROGRESS' end,
   DONE_AT=case when newstatus='PICKED' then sysdate else DONE_AT end,DONE_BY=p_actor,UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_TASK_ID=l.PICK_TASK_ID;
  update RRL_PICK_WAVE_TASK set FACT_QTY=fact,STATUS=case when newstatus='PICKED' then 'DONE' else 'IN_PROGRESS' end,
   DONE_AT=case when newstatus='PICKED' then sysdate else DONE_AT end,DONE_BY=p_actor,UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_WAVE_TASK_ID=l.PICK_WAVE_TASK_ID;
  update RRL_CASE_PICK_TASK t set CURRENT_CELL=target_cell,CONTENT_VERSION=CONTENT_VERSION+1,
   (TOTAL_LINES,PICKED_LINES,PLANNED_QTY,PICKED_QTY)=(select count(*),nvl(sum(case when STATUS in('PICKED','SHORT_PICKED','CANCELLED') then 1 else 0 end),0),nvl(sum(PLANNED_QTY),0),nvl(sum(PICKED_QTY),0) from RRL_CASE_PICK_LINE z where z.CASE_PICK_TASK_ID=task_id),
   UPDATED_AT=systimestamp,UPDATED_BY=p_actor where t.CASE_PICK_TASK_ID=task_id;
  select RRL_CASE_PICK_EVENT_SQ.nextval into eventid from dual;
  insert into RRL_CASE_PICK_EVENT(CASE_PICK_EVENT_ID,CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,EVENT_TYPE,OFFLINE_EVENT_ID,PAYLOAD_JSON,CREATED_BY)
   values(eventid,task_id,line_id,'LINE_CONFIRMED',offline,p_request,p_actor);
  v:=json_object_t();v.put('operation_id',op);v.put('case_pick_task_id',task_id);v.put('case_pick_line_id',line_id);v.put('status',newstatus);
  v.put('fact_qty',RRL_STOCK_PLAN_HELPER.decimal_text(fact));v.put('carrier_identifier',ct.SSCC);v.put('cell',target_cell);v.put('picked_from_cell',v_cell);v.put('lots',facts);p_result:=v.to_clob;
 end;
end;
/

create or replace package body RRL_STOCK_POSTING_API as
 g_request clob;g_resolution clob;g_change_before clob;g_actor varchar2(50);g_operation varchar2(100);g_kind varchar2(80);g_tx varchar2(100);g_prepared boolean:=false;
 procedure reset_connection is
 begin
  RRL_STOCK_CTX_API.clear_operation;RRL_STOCK_LOCK_API.clear_plan;
  g_request:=null;g_resolution:=null;g_change_before:=null;g_actor:=null;g_operation:=null;g_kind:=null;g_tx:=null;g_prepared:=false;
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
   begin
   if g_kind in('MANUAL_MOVE','COMPAT_MANUAL_MOVE') then RRL_STOCK_COMMAND_PLAN.compile_move(p_request,g_operation,v_policies,v_resources);
   elsif g_kind='WAVE_LAUNCH' then RRL_STOCK_WAVE_LAUNCH_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='OUTGOING_PALLET_CHECK' then RRL_STOCK_PALLET_QC_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='CASE_SHORT_APPROVE' then RRL_STOCK_CASE_SHORT_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='CASE_CARRIER_MOVE' then RRL_STOCK_CASE_MOVE_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='CASE_PICK_CONFIRM' then RRL_STOCK_CASE_PICK_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='RECEIPT_REVERSE' then RRL_STOCK_RECEIPT_REVERSE.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='INVENTORY_REGISTER_LOT' then RRL_STOCK_INVENTORY_BIRTH.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='INVENTORY_COUNT' then RRL_STOCK_INVENTORY_CMD.compile_count(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='MES_RAW_TASK_CANCEL' then RRL_STOCK_MES_CANCEL_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in('MES_RELEASE_TO_PRODUCTION','MES_CALCULATE_SUPPLY') then RRL_STOCK_MES_SUPPLY_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in('DOCUMENT_RELEASE_RESERVATIONS','WAVE_CANCEL','WAVE_RELEASE','PICK_PLAN_CANCEL') then RRL_STOCK_DOC_RESERVE_CMD.compile_release(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='WAVE_RESERVE_SOURCES' then RRL_STOCK_WAVE_CMD.compile_reserve(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in('SHIP_DOCUMENT','SHIP_PALLET') then RRL_STOCK_SHIPPING_CORE.compile_shipment(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in('INTERNAL_MOVE','MOVE_QUARANTINE') then RRL_STOCK_INTERNAL_CMD.compile_move(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='MES_MOVEMENTS' then RRL_STOCK_MES_MOVEMENT_PLAN.compile_movements(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind='SAP_RECEIPT' then RRL_STOCK_RECEIPT_PLAN.compile_receipt(p_request,g_operation,p_hints,v_policies,v_resources,v_domain);
   elsif g_kind='TASK_COMPLETE' then RRL_STOCK_TASK_PLAN.compile_task(p_request,g_operation,v_policies,v_resources,v_domain);
   elsif g_kind in('RESERVATION_CREATE','RESERVATION_PROMOTE','RESERVATION_RELEASE','RESERVATION_CANCEL','RESERVATION_CONSUME') then RRL_STOCK_RESERVATION_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);
   else raise_application_error(-20888,'COMMAND_HANDLER_NOT_INSTALLED');end if;
   exception when others then
    -- A concurrent identical command may have committed while this planner read mutable stock.
    -- Rebuild only the existing replay lock plan; never take OP before the full resource plan.
    select count(*) into v_exists from RRL_STOCK_OPERATION where OPERATION_ID=g_operation;
    if v_exists=0 then raise;end if;
    v_domain:=null;v_plan:=json_array_t();v_resources_json:=json_array_t();
    v_entry:=json_object_t();v_entry.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key('RELEASE','STOCK')));v_entry.put('mode',4);v_plan.append(v_entry);
    v_entry:=json_object_t();v_entry.put('rank',10);v_entry.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key('OP',g_operation)));v_resources_json.append(v_entry);
    v_policies:=v_plan.to_clob;v_resources:=v_resources_json.to_clob;
   end;
  end if;
  if v_domain is not null and p_hints is not null and g_kind in('INVENTORY_REGISTER_LOT','MES_MOVEMENTS') then
   declare h json_object_t:=json_object_t.parse(p_hints);a json_array_t;b json_object_t;u json_object_t;
    rr json_array_t:=json_array_t.parse(v_resources);dom json_object_t:=json_object_t.parse(v_domain);
    uid varchar2(150);qty varchar2(30);base varchar2(20);cell varchar2(60);found boolean;total number;
   begin
    a:=h.get_array('births');if a.get_size>200 then raise_application_error(-20881,'BIRTH_CAPTURE_BOUND');end if;
    for i in 0..a.get_size-1 loop
     b:=treat(a.get(i) as json_object_t);uid:=b.get_string('uid');found:=false;
     if g_kind='INVENTORY_REGISTER_LOT' and dom.get_string('uid')=uid then
      found:=true;qty:=dom.get_string('quantity');base:=dom.get_string('base');cell:=dom.get_string('cell');
     elsif g_kind='MES_MOVEMENTS' then
      for z in 0..dom.get_array('movements').get_size-1 loop
       u:=treat(dom.get_array('movements').get(z) as json_object_t);
       if u.get_string('physical_uid')=uid and u.get_number('movement_id')=b.get_number('movement_id') then
        declare m RRL_MES_MOVEMENT%rowtype;mid number:=u.get_number('movement_id');begin
         select * into m from RRL_MES_MOVEMENT where MOVEMENT_ID=mid;
         if m.MOVEMENT_TYPE!='FG_PALLET_RELEASE' then raise_application_error(-20884,'NOT_A_BIRTH_MOVEMENT');end if;
         found:=true;qty:=u.get_string('base_quantity');base:=u.get_string('base_uom');cell:=m.TARGET_LOCATION;
        end;
       end if;
      end loop;
     end if;
     if not found or b.get_string('quantity')!=qty or b.get_string('base')!=base or b.get_string('cell')!=cell
      then raise_application_error(-20890,'CLOSURE_CHANGED: birth capture');end if;
     total:=0;
     if b.get_array('unit_bindings').get_size<1 or b.get_array('unit_bindings').get_size>10000 then raise_application_error(-20881,'BIRTH_UNIT_BOUND');end if;
     for z in 0..b.get_array('unit_bindings').get_size-1 loop
      u:=treat(b.get_array('unit_bindings').get(z) as json_object_t);
      total:=total+RRL_STOCK_MATH.quantity(u.get_string('quantity'));
      RRL_STOCK_PLAN_HELPER.anchor(rr,60,'UNIT',u.get_string('key'));
     end loop;
     if total!=RRL_STOCK_MATH.quantity(qty) then raise_application_error(-20884,'BIRTH_UNIT_QUANTITY_CONFLICT');end if;
     for z in 0..b.get_array('aliases').get_size-1 loop
      u:=treat(b.get_array('aliases').get(z) as json_object_t);
      RRL_STOCK_PLAN_HELPER.anchor(rr,70,'UNIQUE','MARK:'||u.get_string('system')||':'||u.get_string('hash'));
     end loop;
    end loop;
    v_resources:=rr.to_clob;v_resolution.put('births',a);
   end;
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
  g_change_before:=RRL_STOCK_CHANGE_AUDIT.snapshot(v_resources);
  g_request:=p_request;g_resolution:=v_resolution.to_clob;g_actor:=p_actor;g_tx:=dbms_transaction.local_transaction_id(false);g_prepared:=true;
  if g_kind='SAP_RECEIPT' then RRL_STOCK_CTX_API.begin_staging(v_resolution.get_object('domain').get_string('uid'),v_resolution.get_object('domain').get_string('receive_cell'));end if;
 end;
 procedure stage_birth(p_uid varchar2) is
  d json_object_t:=json_object_t.parse(g_resolution);b json_object_t;v json_object_t;a json_array_t;
  n number;policy number;found boolean:=false;uid varchar2(150);article varchar2(160);cell varchar2(60);qty number;
  doc number;expiry date;price number;mid number;m RRL_MES_MOVEMENT%rowtype;
 begin
  if not g_prepared or g_tx is null or g_tx!=dbms_transaction.local_transaction_id(false)
   or g_kind not in('INVENTORY_REGISTER_LOT','MES_MOVEMENTS') then raise_application_error(-20850,'WRITE_PLAN_VIOLATION');end if;
  if RRL_HAS_WRIGHT(g_actor,case when g_kind='INVENTORY_REGISTER_LOT' then 'stock_inventory_count' else 'mes_apply_wms' end)!=1
   then raise_application_error(-20882,'BIRTH_CAPTURE_FORBIDDEN');end if;
  a:=d.get_array('births');
  for i in 0..a.get_size-1 loop
   b:=treat(a.get(i) as json_object_t);
   if b.get_string('uid')=p_uid then found:=true;exit;end if;
  end loop;
  if not found then raise_application_error(-20884,'BIRTH_CAPTURE_NOT_PLANNED');end if;
  uid:=b.get_string('uid');article:=b.get_string('article');cell:=b.get_string('cell');qty:=RRL_STOCK_MATH.quantity(b.get_string('quantity'));
  select POLICY_VERSION into policy from RRL_SKU_RECEIPT_POLICY where ARTICUL=article and MARKING_REQUIRED=1;
  if policy!=b.get_number('policy_version') then raise_application_error(-20890,'CLOSURE_CHANGED: birth marking policy');end if;
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',uid));
  select count(*) into n from RRL_REMAINS where UID_POLETA=uid and REMAIN>0;
  if n>0 then raise_application_error(-20886,'BIRTH_STOCK_ALREADY_EXISTS');end if;
  select count(*) into n from RRL_PALLETS where UID_PALLET=uid;
  if n=0 then
   if g_kind='INVENTORY_REGISTER_LOT' then
    v:=d.get_object('domain');doc:=v.get_number('document');expiry:=to_date(v.get_string('expiry_date'),'FXYYYY-MM-DD');price:=v.get_number('price');
    insert into RRL_PALLETS(UID_PALLET,ARTICUL,CREATION_DATE,EXPIRY_DATE,UNIT_COUNT,PRICE,PRIHOD_NAKLAD_ID,STOCK_ORIGIN_UID,CREATED_BY_STOCK_OP)
     values(uid,article,systimestamp,expiry,qty,price,-doc,uid,g_operation);
   else
    mid:=b.get_number('movement_id');select * into m from RRL_MES_MOVEMENT where MOVEMENT_ID=mid;
    insert into RRL_PALLETS(UID_PALLET,ARTICUL,UNIT_COUNT,PRIHOD_NAKLAD_ID,PROD_BATCH_ID,SSCC,QUALITY_STATUS,CREATED_BY_STOCK_OP)
     values(uid,article,qty,0,m.PROD_BATCH_ID,m.SSCC,'RELEASED',g_operation);
   end if;
  end if;
  RRL_STOCK_CTX_API.begin_staging(uid,cell);
 end;
 procedure finish_birth_capture is
 begin
  if not g_prepared or g_tx!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20850,'WRITE_PLAN_VIOLATION');end if;
  RRL_STOCK_CTX_API.end_effect;
 end;
 procedure execute_prepared(p_result out clob) is
  v_outbox number;v_existing number;v_key varchar2(100);v_json json_object_t;v_resolved json_object_t;v_event json_object_t;v_changes clob;v_resources clob;v_after clob;v_composition json_object_t;v_unit_changes json_array_t;v_unit_change json_object_t;v_old_unit json_object_t;v_new_unit json_object_t;v_repacking boolean:=false;
 begin
  if not g_prepared or g_tx is null or dbms_transaction.local_transaction_id(false) is null
   or g_tx!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20850,'WRITE_PLAN_VIOLATION'); end if;
  if g_kind='SAP_RECEIPT' then RRL_STOCK_CTX_API.end_effect;end if;
  if g_kind in('MANUAL_MOVE','COMPAT_MANUAL_MOVE') then RRL_STOCK_MOVE_CORE.manual_whole(g_request,g_actor,p_result);
  elsif g_kind='WAVE_LAUNCH' then RRL_STOCK_WAVE_LAUNCH_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind='OUTGOING_PALLET_CHECK' then RRL_STOCK_PALLET_QC_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind='CASE_SHORT_APPROVE' then RRL_STOCK_CASE_SHORT_CMD.execute_command(g_request,g_actor,p_result);
  elsif g_kind='CASE_CARRIER_MOVE' then RRL_STOCK_CASE_MOVE_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind='CASE_PICK_CONFIRM' then RRL_STOCK_CASE_PICK_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind='RECEIPT_REVERSE' then RRL_STOCK_RECEIPT_REVERSE.execute_command(g_request,g_actor,p_result);
   elsif g_kind='INVENTORY_REGISTER_LOT' then RRL_STOCK_INVENTORY_BIRTH.execute_command(g_request,g_actor,p_result);
   elsif g_kind='INVENTORY_COUNT' then RRL_STOCK_INVENTORY_CMD.execute_count(g_request,g_actor,p_result);
   elsif g_kind='MES_RAW_TASK_CANCEL' then RRL_STOCK_MES_CANCEL_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind in('MES_RELEASE_TO_PRODUCTION','MES_CALCULATE_SUPPLY') then RRL_STOCK_MES_SUPPLY_CMD.execute_command(g_request,g_actor,p_result);
   elsif g_kind in('DOCUMENT_RELEASE_RESERVATIONS','WAVE_CANCEL','WAVE_RELEASE','PICK_PLAN_CANCEL') then RRL_STOCK_DOC_RESERVE_CMD.execute_release(g_request,g_actor,p_result);
  elsif g_kind='WAVE_RESERVE_SOURCES' then RRL_STOCK_WAVE_CMD.execute_reserve(g_request,g_actor,p_result);
  elsif g_kind in('SHIP_DOCUMENT','SHIP_PALLET') then RRL_STOCK_SHIPPING_CORE.execute_shipment(g_request,g_actor,p_result);
  elsif g_kind in('INTERNAL_MOVE','MOVE_QUARANTINE') then RRL_STOCK_INTERNAL_CMD.execute_move(g_request,g_actor,p_result);
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
  v_resources:=v_resolved.get_array('resources').to_clob;
  v_after:=RRL_STOCK_CHANGE_AUDIT.snapshot(v_resources);v_changes:=RRL_STOCK_CHANGE_AUDIT.differences(g_change_before,v_after);
  v_event:=json_object_t();v_event.put('contract_version',3);v_event.put('operation_id',g_operation);v_event.put('command_type',g_kind);
  v_event.put('source',json_object_t.parse(g_request).get_object('source'));v_event.put('result',json_object_t.parse(p_result));
  v_event.put('stock_before',v_resolved.get_array('stock_before'));
  v_event.put('stock_after',json_array_t.parse(RRL_STOCK_INVARIANT_CORE.snapshot_stock(v_resources)));
  v_composition:=json_object_t.parse(v_changes);v_unit_changes:=v_composition.get_array('units');
  for i in 0..v_unit_changes.get_size-1 loop
   v_unit_change:=treat(v_unit_changes.get(i) as json_object_t);
   if not v_unit_change.get('before').is_null and not v_unit_change.get('after').is_null then
    v_old_unit:=v_unit_change.get_object('before');v_new_unit:=v_unit_change.get_object('after');
    if v_old_unit.get_string('uid')!=v_new_unit.get_string('uid') then v_repacking:=true;end if;
   end if;
  end loop;
  v_event.put('composition_changes',v_composition);
  if v_repacking then
   v_event.put('regulatory_composition_status','PENDING');
   v_event.put('regulatory_action','PHYSICAL_REPACK_PROPOSED');
  end if;
  v_event.put('immutable_request_reference',g_operation);
  v_outbox:=RRL_TRACEABILITY_API.enqueue_event('STOCK_POSTED','STOCK_OPERATION',g_operation,v_key,v_event.to_clob,'WMS',g_operation);
  v_json:=json_object_t.parse(p_result);v_json.put('outbox_id',v_outbox);
  if v_repacking then v_json.put('regulatory_composition_status','PENDING');end if;
  p_result:=v_json.to_clob;
  RRL_STOCK_OPERATION_CORE.finish_operation(g_operation,p_result);
  g_prepared:=false;
 end;
end;
/
