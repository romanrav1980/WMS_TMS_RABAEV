create or replace package RRL_STOCK_RECEIPT_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure execute_receipt(p_request clob,p_actor varchar2,p_result out clob);
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
  declare
 v_json_sql_1_1 varchar2(32767):=d.get_string('operation_id');
begin
select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=v_json_sql_1_1;
end;
  h:=json_object_t.parse(v_plan).get_object('domain');m:=d.get_object('metadata');
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),4);
  declare
 v_json_sql_2_1 varchar2(32767):=h.get_string('source_order_id');
begin
select * into o from RRL_SAP_SUPPLY_ORDER where ORDER_ID=v_json_sql_2_1 for update;
end;
  if o.REVISION!=h.get_number('order_revision') or o.NAKLAD_ID!=h.get_number('naklad_id')
   or o.WARE_ID!=h.get_number('warehouse_id') or o.RECEIVE_CELL!=h.get_string('receive_cell') then
   raise_application_error(-20890,'CLOSURE_CHANGED: SAP receipt order');end if;
  select CONDITION into v_header from RRL_PRIHOD_NAKLAD where ID=o.NAKLAD_ID for update;
  if nvl(v_header,0)!=0 then raise_application_error(-20886,'RECEIPT_DOCUMENT_CLOSED');end if;
  declare
 v_json_sql_3_1 varchar2(32767):=h.get_string('line_number');
begin
select ARTICUL,PLANNED_QTY,BASE_UOM into v_article,v_planned,v_unit from RRL_SAP_SUPPLY_LINE
   where ORDER_ID=o.ORDER_ID and LINE_NUMBER=v_json_sql_3_1;
end;
  if v_article!=h.get_string('article') or v_unit!=h.get_string('input_uom') then raise_application_error(-20890,'CLOSURE_CHANGED: SAP receipt line');end if;
  select max(POLICY_VERSION) into v_uom_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_unit;
  select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into v_base,v_num,v_den,v_scale
   from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_unit and POLICY_VERSION=v_uom_version;
  v_qty:=RRL_STOCK_MATH.convert_exact(m.get_string('quantity'),v_num,v_den,v_scale);
  v_planned:=RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(v_planned),v_num,v_den,v_scale);
  if h.get_number('uom_version')!=v_uom_version or h.get_string('base_uom')!=v_base or
   RRL_STOCK_MATH.quantity(h.get_string('base_quantity'))!=v_qty then raise_application_error(-20890,'CLOSURE_CHANGED: receipt UOM');end if;
  declare
 v_json_sql_4_1 varchar2(32767):=h.get_string('line_number');
begin
select count(*) into v_n from RRL_SAP_PALLET_RECEIPT where ORDER_ID=o.ORDER_ID and LINE_NUMBER=v_json_sql_4_1
   and (POSTED_BASE_QTY is null or STOCK_BASE_UOM is null or STOCK_BASE_UOM!=v_base);
end;
  if v_n>0 then raise_application_error(-20884,'LEGACY_RECEIPT_BASELINE_REQUIRED');end if;
  declare
 v_json_sql_5_1 varchar2(32767):=h.get_string('line_number');
begin
select nvl(sum(POSTED_BASE_QTY),0) into v_done from RRL_SAP_PALLET_RECEIPT where ORDER_ID=o.ORDER_ID and LINE_NUMBER=v_json_sql_5_1;
end;
  if v_done+v_qty>v_planned then raise_application_error(-20886,'RECEIPT_OVER_SUPPLY');end if;
  select POLICY_VERSION into v_policy from RRL_SKU_RECEIPT_POLICY where ARTICUL=v_article;
  if v_policy!=h.get_number('marking_policy_version') then raise_application_error(-20890,'CLOSURE_CHANGED: marking policy');end if;
  v_uid:=h.get_string('uid');v_cell:=o.RECEIVE_CELL;v_task:=h.get_number('task_id');
  declare
 v_json_sql_6_1 varchar2(32767):=m.get_string('expiry_date');
begin
select count(*) into v_n from RRL_PALLETS where UID_PALLET=v_uid and ARTICUL=v_article and PRIHOD_NAKLAD_ID=o.NAKLAD_ID
   and UNIT_COUNT=v_qty and EXPIRY_DATE=to_date(v_json_sql_6_1,'YYYY-MM-DD');
end;
  if v_n!=1 then raise_application_error(-20884,'RECEIPT_STAGING_PALLET_CONFLICT');end if;
  declare
 v_json_sql_7_1 varchar2(32767):=h.get_object('placement').get_string('cell');
begin
select count(*) into v_n from RRL_WAREHOUSE_TASK where TASK_ID=v_task and UID_PALLET=v_uid and STATUS='PLANNED'
   and FROM_CELL=v_cell and TO_CELL=v_json_sql_7_1;
end;
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
  declare
 v_json_sql_8_1 varchar2(32767):=d.get_string('operation_id');
begin
update RRL_PALLETS set STOCK_ORIGIN_UID=v_uid,CREATED_BY_STOCK_OP=v_json_sql_8_1 where UID_PALLET=v_uid;
end;
  RRL_STOCK_BALANCE_CORE.write_leg(v_uid,null,v_cell,v_qty,v_base,v_base_version,1,1,1,p_actor,v_event);
  v_response:=h.get_object('result');v_response.put('task_id',v_task);p_result:=v_response.to_clob;
  declare
 v_json_sql_9_1 varchar2(32767):=d.get_string('operation_id');
 v_json_sql_9_2 varchar2(32767):=h.get_string('line_number');
 v_json_sql_9_3 varchar2(32767):=m.get_string('supplier_batch');
 v_json_sql_9_4 varchar2(32767):=d.get_string('operation_id');
begin
insert into RRL_SAP_PALLET_RECEIPT(OPERATION_ID,ORDER_ID,LINE_NUMBER,UID_PALLET,SUPPLIER_BATCH,PAYLOAD_HASH,RESULT_JSON,
   RECEIVED_BY,POSTED_BASE_QTY,STOCK_BASE_UOM,STOCK_OPERATION_ID)
   values(v_json_sql_9_1,o.ORDER_ID,v_json_sql_9_2,v_uid,v_json_sql_9_3,
    rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256)),p_result,p_actor,v_qty,v_base,v_json_sql_9_4);
end;
  select count(*) into v_n from RRL_SAP_SUPPLY_LINE sl where sl.ORDER_ID=o.ORDER_ID and (
   not exists(select 1 from RRL_STOCK_UOM_CONVERSION u where u.ARTICUL=sl.ARTICUL and u.INPUT_UOM=sl.BASE_UOM)
   or nvl((select sum(rec.POSTED_BASE_QTY) from RRL_SAP_PALLET_RECEIPT rec where rec.ORDER_ID=sl.ORDER_ID and rec.LINE_NUMBER=sl.LINE_NUMBER),0)<
     (select RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(sl.PLANNED_QTY),u.NUMERATOR,u.DENOMINATOR,u.BASE_SCALE)
      from RRL_STOCK_UOM_CONVERSION u where u.ARTICUL=sl.ARTICUL and u.INPUT_UOM=sl.BASE_UOM and u.POLICY_VERSION=(select max(x.POLICY_VERSION) from RRL_STOCK_UOM_CONVERSION x where x.ARTICUL=sl.ARTICUL and x.INPUT_UOM=sl.BASE_UOM)));
  if v_n=0 then update RRL_PRIHOD_NAKLAD set CONDITION=1,DATE_OF_ACCEPT=nvl(DATE_OF_ACCEPT,sysdate) where ID=o.NAKLAD_ID;end if;
  declare
 v_json_sql_10_1 varchar2(32767):=d.get_string('operation_id');
begin
insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)
   values(v_json_sql_10_1,'PALLET_RECEIVED',p_result);
end;
 end;
end;
/
