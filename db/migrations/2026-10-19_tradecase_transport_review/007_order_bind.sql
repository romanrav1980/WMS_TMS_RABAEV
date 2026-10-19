create or replace package body RRL_TRADE_ORDER_API as
 g_tx varchar2(100);
 function writes_allowed return number is begin
  if g_tx is not null and g_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;
 end;
 procedure fail(p_code varchar2)is begin raise_application_error(-20912,p_code);end;
 procedure bind_order(p_ware number,p_actor varchar2,p_json clob,p_result out clob)is
  j json_object_t:=json_object_t.parse(p_json);b json_object_t;profile json_object_t;sku json_object_t;line json_object_t;mapping json_object_t;
  rows_json json_array_t;maps json_array_t:=j.get_array('lines');result_json json_object_t:=json_object_t();old_cmd RRL_TRADE_ORDER_COMMAND%rowtype;
  body_text clob;recipient_text clob;sku_text clob;doc_version number;profile_version number;v_native number:=j.get_number('customer_order_id');
  v_external varchar2(100):=j.get_string('order_id');op varchar2(100):=j.get_string('operation_id');hash_value varchar2(64):=j.get_string('payload_hash');
  v_recipient varchar2(100);ware number;customer number;enabled number;n number;row_id number;matched boolean;v_row RRL_CUSTOMER_ORDER_ROW%rowtype;
  v_box_units number;v_sku_version number;v_sku varchar2(100);v_source varchar2(100);v_target varchar2(100);v_mrc number;v_min_expiry date;v_mode varchar2(20);v_line varchar2(100);
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();outbox_id number;v_actor varchar2(50):=p_actor;
 begin
  if RRL_ACCESS_API.allowed(p_actor,'tradecase_order_bind','WAREHOUSE',to_char(p_ware,'TM9'))<>1 then raise_application_error(-20882,'ACCESS_DENIED');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE',6);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_POLICY_GUARD','WAREHOUSE.CONFIGURATION');
  RRL_STOCK_LOCK_API.begin_plan;
  RRL_ACCESS_API.assert_allowed(p_actor,'tradecase_order_bind','WAREHOUSE',to_char(p_ware,'TM9'));
  RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  select ENABLED into enabled from RRL_TRADE_SITE where WARE_ID=p_ware for update wait 5;
  begin
   select *into old_cmd from RRL_TRADE_ORDER_COMMAND where OPERATION_ID=op;
   if old_cmd.WARE_ID<>p_ware or old_cmd.ACTOR<>p_actor or old_cmd.PAYLOAD_HASH<>hash_value then fail('OPERATION_CONFLICT');end if;
   result_json:=json_object_t.parse(old_cmd.RESULT_JSON);result_json.put('replayed',true);p_result:=result_json.to_clob;RRL_STOCK_LOCK_API.clear_plan;return;
  exception when no_data_found then null;end;
  if enabled<>1 then fail('TRADE_SITE_DISABLED');end if;
  select BODY_JSON,VERSION_NO into body_text,doc_version from RRL_TRADE_DOCUMENT where WARE_ID=p_ware and ENTITY_TYPE='ORDER'and EXTERNAL_ID=v_external and STATUS='ACCEPTED';
  if j.get_number('expected_order_version')is null or doc_version<>j.get_number('expected_order_version')then fail('VERSION_CONFLICT');end if;
  b:=json_object_t.parse(body_text);if b.get_string('order_kind')='BUYOUT'then fail('TRADE_BUYOUT_BASIS_IS_NOT_SHIPMENT');end if;v_recipient:=b.get_string('recipient_id');
  select BODY_JSON,VERSION_NO into recipient_text,profile_version from RRL_TRADE_DOCUMENT where WARE_ID=p_ware and ENTITY_TYPE='RECIPIENT'and EXTERNAL_ID=v_recipient and STATUS='ACCEPTED';
  profile:=json_object_t.parse(recipient_text);
  if not profile.get_boolean('active')or b.get_boolean('cancelled')then fail('TRADE_ORDER_INACTIVE');end if;
  if profile.get_number('wms_customer_id')is null then fail('TRADE_CUSTOMER_MAPPING_REQUIRED');end if;
  select WARE_ID,CUSTOMER_ID into ware,customer from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=v_native and STATUS not in('CANCELLED','DONE','CLOSED')for update wait 5;
  if ware<>p_ware or customer<>profile.get_number('wms_customer_id')then fail('TRADE_NATIVE_CUSTOMER_OR_WARE_MISMATCH');end if;
  select count(*)into n from RRL_TRADE_ORDER_LINK where CUSTOMER_ORDER_ID=v_native or(WARE_ID=p_ware and EXTERNAL_ID=v_external);
  if n>0 then fail('TRADE_ORDER_ALREADY_BOUND');end if;
  rows_json:=b.get_array('lines');
  select count(*)into n from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=v_native and STATUS<>'CANCELLED';
  if n<>rows_json.get_size or n<>maps.get_size or n<1 or n>200 then fail('TRADE_ORDER_LINE_SET_MISMATCH');end if;
  g_tx:=dbms_transaction.local_transaction_id(true);
  insert into RRL_TRADE_ORDER_LINK(CUSTOMER_ORDER_ID,WARE_ID,EXTERNAL_ID,DOCUMENT_VERSION,RECIPIENT_ID,RECIPIENT_VERSION,CREATED_BY)
   values(v_native,p_ware,v_external,doc_version,v_recipient,profile_version,v_actor);
  for i in 0..rows_json.get_size-1 loop
   line:=treat(rows_json.get(i)as json_object_t);v_line:=line.get_string('line_id');matched:=false;
   for k in 0..maps.get_size-1 loop
    mapping:=treat(maps.get(k)as json_object_t);
    if mapping.get_string('line_id')=v_line then
     if matched then fail('TRADE_DUPLICATE_LINE_MAPPING');end if;
     matched:=true;row_id:=mapping.get_number('customer_order_row_id');
    end if;
   end loop;
   if not matched or row_id is null then fail('TRADE_ORDER_LINE_MAPPING_REQUIRED');end if;
   select *into v_row from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ROW_ID=row_id and CUSTOMER_ORDER_ID=v_native and STATUS<>'CANCELLED'for update wait 5;
   v_sku:=line.get_string('sku_id');
   select BODY_JSON,VERSION_NO into sku_text,v_sku_version from RRL_TRADE_DOCUMENT where WARE_ID=p_ware and ENTITY_TYPE='SKU'and EXTERNAL_ID=v_sku and STATUS='ACCEPTED';
   sku:=json_object_t.parse(sku_text);
   if sku.get_string('wms_article_id')is null or sku.get_string('wms_article_id')<>v_row.ARTICUL or v_row.WARE_ID<>p_ware
    or v_row.UNIT_CODE<>line.get_string('uom')or v_row.ORDER_QTY<>line.get_number('quantity')then fail('TRADE_NATIVE_LINE_MISMATCH');end if;
   v_box_units:=sku.get_number('units_per_box');
   select count(*)into n from RRL_STOCK_UOM_CONVERSION cv where cv.ARTICUL=v_row.ARTICUL and cv.INPUT_UOM=v_row.UNIT_CODE and cv.BASE_UOM='EA'
    and cv.POLICY_VERSION=(select max(POLICY_VERSION)from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_row.ARTICUL and INPUT_UOM=v_row.UNIT_CODE)
    and cv.NUMERATOR/cv.DENOMINATOR=case when v_row.UNIT_CODE='EA'then 1 when v_row.UNIT_CODE='BOX'then v_box_units end;
   if n<>1 then fail('TRADE_NATIVE_PACKAGING_MISMATCH');end if;
   v_source:=line.get_string('source_owner_id');v_target:=line.get_string('target_owner_id');v_mrc:=line.get_number('mrc');v_mode:=profile.get_string('buyout_mode');
   v_min_expiry:=to_date(substr(b.get_string('planned_ship_at'),1,10),'FXYYYY-MM-DD')+greatest(line.get_number('min_osg_days'),profile.get_number('min_osg_days'));
   if profile.get_string('osg_basis')='DELIVERY_DATE'then v_min_expiry:=v_min_expiry+profile.get_number('lead_time_days');end if;
   insert into RRL_TRADE_ORDER_LINE(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,EXTERNAL_LINE_ID,SKU_ID,SKU_VERSION,SOURCE_OWNER_ID,TARGET_OWNER_ID,MRC,MIN_EXPIRY_DATE,BUYOUT_MODE)
    values(row_id,v_native,v_line,v_sku,v_sku_version,v_source,v_target,v_mrc,v_min_expiry,v_mode);
  end loop;
  result_json.put('customer_order_id',v_native);result_json.put('order_id',v_external);result_json.put('order_version',doc_version);
  result_json.put('bound_lines',rows_json.get_size);result_json.put('stock_changed',false);result_json.put('replayed',false);result_json.put('operation_id',op);
  outbox_id:=RRL_TRACEABILITY_API.enqueue_event('TRADECASE_ORDER_BOUND','TRADE_ORDER',v_external,'TC:ORDER:'||op,result_json.to_clob,'TRADECASE_BUS',op);
  result_json.put('outbox_id',outbox_id);p_result:=result_json.to_clob;
  insert into RRL_TRADE_ORDER_COMMAND(OPERATION_ID,WARE_ID,ACTOR,PAYLOAD_HASH,RESULT_JSON)values(op,p_ware,v_actor,hash_value,p_result);
  g_tx:=null;RRL_STOCK_LOCK_API.clear_plan;
 exception when others then g_tx:=null;RRL_STOCK_LOCK_API.clear_plan;raise;
 end;
end;
/
