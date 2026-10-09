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
  select count(*) into v_sum from RRL_CASE_CARRIER_LOT where LOT_UID=p_uid;
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
