create or replace package body RRL_TRADE_BUYOUT_CORE as
 procedure fail(p_code varchar2)is begin raise_application_error(-20913,p_code);end;
 procedure party_access(p_actor varchar2,b RRL_TRADE_BUYOUT%rowtype,p_write number)is begin
  if p_write=1 then
   RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,b.WARE_ID,b.SOURCE_OWNER_ID,1);
   RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,b.WARE_ID,b.TARGET_OWNER_ID,1);
  elsif RRL_TRADE_STOCK_GUARD.owner_allowed(p_actor,b.WARE_ID,b.SOURCE_OWNER_ID,0)<>1
   and RRL_TRADE_STOCK_GUARD.owner_allowed(p_actor,b.WARE_ID,b.TARGET_OWNER_ID,0)<>1 then raise_application_error(-20882,'TRADE_BUYOUT_PARTY_ACCESS_DENIED');end if;
 end;
 procedure assert_replay(p_ware number,p_actor varchar2,j json_object_t)is b RRL_TRADE_BUYOUT%rowtype;v_id varchar2(100):=j.get_string('buyout_id');begin
  select *into b from RRL_TRADE_BUYOUT where BUYOUT_ID=v_id and WARE_ID=p_ware;party_access(p_actor,b,1);
 end;
 function event_key(p_ware number,p_skm varchar2,p_event varchar2)return varchar2 is x json_object_t:=json_object_t();begin
  x.put('ware',p_ware);x.put('skm',p_skm);x.put('event',p_event);
  return 'TC:BUYOUT:R:'||rawtohex(sys.dbms_crypto.hash(x.to_clob,sys.dbms_crypto.hash_sh256));
 end;
 function current_mixed(b RRL_TRADE_BUYOUT%rowtype)return number is n number;begin
  select count(*)into n from(select u.CURRENT_UID from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
   where(b.BUYOUT_MODE='IN_TRANSIT'or u.STOCK_STATUS<>'ISSUED')and u.CURRENT_UID in(
    select x.CURRENT_UID from RRL_WMS_RECEIPT_UNIT x join RRL_TRADE_BUYOUT_UNIT y on y.PHYSICAL_UNIT_KEY=x.PHYSICAL_UNIT_KEY where y.BUYOUT_ID=b.BUYOUT_ID)
   group by u.CURRENT_UID having count(distinct a.OWNER_ID)>1);return least(n,1);
 end;
 function card(b RRL_TRADE_BUYOUT%rowtype)return json_object_t is o json_object_t:=json_object_t();begin
  o.put('buyout_id',b.BUYOUT_ID);o.put('warehouse_id',b.WARE_ID);o.put('basis_order_id',b.BASIS_ORDER_ID);o.put('basis_line_id',b.BASIS_LINE_ID);
  o.put('basis_version',b.BASIS_VERSION);o.put('sku_id',b.SKU_ID);o.put('mrc',RRL_STOCK_PLAN_HELPER.decimal_text(b.MRC));
  o.put('source_owner_id',b.SOURCE_OWNER_ID);o.put('target_owner_id',b.TARGET_OWNER_ID);o.put('buyout_mode',b.BUYOUT_MODE);
  o.put('demand_order_id',b.DEMAND_ORDER_ID);o.put('demand_line_id',b.DEMAND_LINE_ID);o.put('load_operation_id',b.LOAD_OPERATION_ID);
  o.put('skm_id',b.SKM_ID);o.put('external_document_id',b.EXTERNAL_DOCUMENT_ID);o.put('status',b.STATUS);o.put('version',b.VERSION_NO);
  o.put('requested_units',b.REQUESTED_UNITS);o.put('confirmed_units',b.CONFIRMED_UNITS);o.put('rejected_units',b.REJECTED_UNITS);o.put('pending_units',b.PENDING_UNITS);
  o.put('requires_sorting',b.REQUIRES_SORTING=1 and b.BUYOUT_MODE<>'IN_TRANSIT');o.put('requires_transit_reconciliation',b.REQUIRES_SORTING=1 and b.BUYOUT_MODE='IN_TRANSIT');
  o.put('request_journal_id',b.REQUEST_JOURNAL_ID);o.put('created_at',to_char(b.CREATED_AT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));return o;
 end;
 procedure request_transfer(p_ware number,p_actor varchar2,j json_object_t,result_json in out nocopy json_object_t)is
  id_value varchar2(100):=j.get_string('buyout_id');basis_id varchar2(100):=j.get_string('basis_order_id');basis_line varchar2(100):=j.get_string('basis_line_id');
  hash_value varchar2(64):=j.get_string('business_hash');request_text clob:=j.to_clob;basis_text clob;sku_text clob;
  b RRL_TRADE_BUYOUT%rowtype;old_row RRL_TRADE_BUYOUT%rowtype;a RRL_TRADE_STOCK_ATTR%rowtype;u RRL_WMS_RECEIPT_UNIT%rowtype;
  basis json_object_t;line json_object_t;sku json_object_t;rows_json json_array_t;keys_json json_array_t:=j.get_array('unit_keys');
  payload json_object_t:=json_object_t();units_json json_array_t:=json_array_t();unit_json json_object_t;codes_json json_array_t;code_json json_object_t;
  found boolean:=false;n number;v_consumed number;v_approved number;v_article varchar2(160);v_price number;v_min_date date;
  v_ware number;zone varchar2(12);demand_native_row number;demand_mode varchar2(20);v_key varchar2(64);v_operation varchar2(100):=j.get_string('operation_id');
  v_demand varchar2(100):=j.get_string('demand_order_id');v_demand_line varchar2(100):=j.get_string('demand_line_id');v_load varchar2(100):=j.get_string('load_operation_id');
  v_journal number;v_outbox number;raw_text varchar2(32767);body_text clob;reply_text clob;
 begin
  if keys_json.get_size<1 or keys_json.get_size>10000 then fail('TRADE_BUYOUT_UNIT_BOUND');end if;
  begin
   select *into old_row from RRL_TRADE_BUYOUT where BUYOUT_ID=id_value;
   if old_row.WARE_ID<>p_ware or old_row.REQUEST_HASH<>hash_value then fail('TRADE_BUYOUT_BUSINESS_CONFLICT');end if;
   party_access(p_actor,old_row,1);result_json:=json_object_t.parse(old_row.REQUEST_RESULT);result_json.put('business_replayed',true);return;
  exception when no_data_found then null;end;
  select BODY_JSON,VERSION_NO into basis_text,b.BASIS_VERSION from RRL_TRADE_DOCUMENT where WARE_ID=p_ware and ENTITY_TYPE='ORDER'and EXTERNAL_ID=basis_id and STATUS='ACCEPTED';
  if j.get_number('expected_basis_version')is null or b.BASIS_VERSION<>j.get_number('expected_basis_version')then fail('VERSION_CONFLICT');end if;
  basis:=json_object_t.parse(basis_text);
  if basis.get_string('order_kind')<>'BUYOUT'or basis.get_boolean('cancelled')then fail('TRADE_FINANCIAL_BUYOUT_BASIS_REQUIRED');end if;
  b.BUYOUT_MODE:=basis.get_string('buyout_mode');
  if b.BUYOUT_MODE is null or b.BUYOUT_MODE not in('BEFORE_PICK','AFTER_PICK','IN_TRANSIT')then fail('TRADE_BUYOUT_MODE_REQUIRED');end if;
  rows_json:=basis.get_array('lines');
  for i in 0..rows_json.get_size-1 loop line:=treat(rows_json.get(i)as json_object_t);if line.get_string('line_id')=basis_line then found:=true;exit;end if;end loop;
  if not found then fail('TRADE_BUYOUT_BASIS_LINE_REQUIRED');end if;
  b.SKU_ID:=line.get_string('sku_id');b.SOURCE_OWNER_ID:=line.get_string('source_owner_id');b.TARGET_OWNER_ID:=line.get_string('target_owner_id');b.MRC:=line.get_number('mrc');b.WARE_ID:=p_ware;
  if b.SOURCE_OWNER_ID=b.TARGET_OWNER_ID then fail('TRADE_BUYOUT_DISTINCT_OWNERS_REQUIRED');end if;party_access(p_actor,b,1);
  select count(*)into n from RRL_TRADE_DOCUMENT where WARE_ID=p_ware and ENTITY_TYPE='OWNER'and EXTERNAL_ID in(b.SOURCE_OWNER_ID,b.TARGET_OWNER_ID)and STATUS='ACCEPTED'and json_value(BODY_JSON,'$.active')='true';
  if n<>2 then fail('TRADE_BUYOUT_ACTIVE_OWNERS_REQUIRED');end if;
  select BODY_JSON into sku_text from RRL_TRADE_DOCUMENT where WARE_ID=p_ware and ENTITY_TYPE='SKU'and EXTERNAL_ID=b.SKU_ID and STATUS='ACCEPTED';
  sku:=json_object_t.parse(sku_text);v_article:=sku.get_string('wms_article_id');
  if v_article is null or not sku.get_boolean('active')then fail('TRADE_BUYOUT_SKU_MAPPING_REQUIRED');end if;
  if line.get_string('uom')<>'EA'then fail('TRADE_BUYOUT_BASE_UNIT_REQUIRED');end if;
  v_approved:=line.get_number('quantity');
  select nvl(sum(bu.REQUESTED_UNITS-bu.REJECTED_UNITS),0)into v_consumed from RRL_TRADE_BUYOUT bu where WARE_ID=p_ware and BASIS_ORDER_ID=basis_id and BASIS_LINE_ID=basis_line;
  if v_approved<>trunc(v_approved)or v_consumed+keys_json.get_size>v_approved then fail('TRADE_BUYOUT_BASIS_QUANTITY_EXCEEDED');end if;
  v_min_date:=to_date(substr(basis.get_string('planned_ship_at'),1,10),'FXYYYY-MM-DD')+line.get_number('min_osg_days');
  if v_demand is not null then
   select ol.CUSTOMER_ORDER_ROW_ID,ol.BUYOUT_MODE into demand_native_row,demand_mode from RRL_TRADE_ORDER_LINK l
    join RRL_TRADE_ORDER_LINE ol on ol.CUSTOMER_ORDER_ID=l.CUSTOMER_ORDER_ID
    join RRL_TRADE_DOCUMENT d on d.WARE_ID=l.WARE_ID and d.ENTITY_TYPE='ORDER'and d.EXTERNAL_ID=l.EXTERNAL_ID and d.VERSION_NO=l.DOCUMENT_VERSION and d.STATUS='ACCEPTED'
    where l.WARE_ID=p_ware and l.EXTERNAL_ID=v_demand and ol.EXTERNAL_LINE_ID=v_demand_line and ol.SKU_ID=b.SKU_ID and ol.MRC=b.MRC
     and ol.SOURCE_OWNER_ID=b.SOURCE_OWNER_ID and ol.TARGET_OWNER_ID=b.TARGET_OWNER_ID;
   if demand_mode<>b.BUYOUT_MODE then fail('TRADE_BUYOUT_DEMAND_MODE_MISMATCH');end if;
  elsif b.BUYOUT_MODE<>'BEFORE_PICK'then fail('TRADE_BUYOUT_DEMAND_REQUIRED');end if;
  select ACTIVE_SKM,VERSION_NO into b.SKM_ID,b.SITE_VERSION from RRL_TRADE_SITE where WARE_ID=p_ware;
  b.BUYOUT_ID:=id_value;b.BASIS_ORDER_ID:=basis_id;b.BASIS_LINE_ID:=basis_line;b.DEMAND_ORDER_ID:=v_demand;b.DEMAND_LINE_ID:=v_demand_line;b.LOAD_OPERATION_ID:=v_load;
  b.STATUS:='PENDING';b.VERSION_NO:=1;b.REQUESTED_UNITS:=keys_json.get_size;b.CONFIRMED_UNITS:=0;b.REJECTED_UNITS:=0;b.PENDING_UNITS:=b.REQUESTED_UNITS;b.REQUIRES_SORTING:=0;
  if b.BUYOUT_MODE='IN_TRANSIT'then RRL_TRADE_TRANSIT_PROOF.assert_load(v_load,p_ware);end if;
  b.REQUEST_HASH:=hash_value;b.REQUEST_JSON:=request_text;b.CREATED_BY:=p_actor;b.CREATED_AT:=systimestamp;b.UPDATED_AT:=systimestamp;
  insert into RRL_TRADE_BUYOUT values b;
  for i in 0..keys_json.get_size-1 loop
   v_key:=keys_json.get_string(i);
   select *into a from RRL_TRADE_STOCK_ATTR where PHYSICAL_UNIT_KEY=v_key for update wait 5;
   select *into u from RRL_WMS_RECEIPT_UNIT where PHYSICAL_UNIT_KEY=v_key;
   if a.SKU_ID<>b.SKU_ID or a.OWNER_ID<>b.SOURCE_OWNER_ID or a.MRC<>b.MRC or a.MARK_STATE<>'VALID'or a.EXPIRY_DATE<v_min_date or u.BASE_QTY<>1 or u.BASE_UOM<>'EA'then fail('TRADE_BUYOUT_UNIT_NOT_ELIGIBLE');end if;
   select count(*)into n from RRL_TRADE_BUYOUT_UNIT where PHYSICAL_UNIT_KEY=v_key and HOLD_ACTIVE=1;
   if n>0 then fail('TRADE_BUYOUT_UNIT_ALREADY_HELD');end if;
   if b.BUYOUT_MODE<>'IN_TRANSIT'then
    select c.WARE_ID,cp.ZONE_KIND into v_ware,zone from RRL_CELLS c join RRL_TRADE_CELL_POLICY cp on cp.CELL=c.CELL where c.CELL=u.CURRENT_CELL;
    if v_ware<>p_ware or u.STOCK_STATUS='ISSUED'then fail('TRADE_BUYOUT_CURRENT_WARE_REQUIRED');end if;
   end if;
   if b.BUYOUT_MODE='BEFORE_PICK'then
    if zone not in('STORAGE','PICK')then fail('TRADE_BUYOUT_PREPARED_STORAGE_REQUIRED');end if;
    if u.HARD_RESERVATION_ID is not null then
     select count(*)into n from RRL_STOCK_RESERVATION sr join RRL_PICK_TASK pt on sr.SOURCE_DOC_TYPE='PICK_WAVE'and sr.SOURCE_LINE_ID=pt.PICK_TASK_ID
      join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=pt.PICK_PLAN_LINE_ID where sr.RESERVATION_ID=u.HARD_RESERVATION_ID and pl.CUSTOMER_ORDER_ROW_ID=demand_native_row;
     if n<>1 then fail('TRADE_BUYOUT_FOREIGN_PHYSICAL_RESERVATION');end if;
    end if;
   else
    select count(*)into n from RRL_CASE_CARRIER_LOT lot join RRL_CASE_PICK_LINE cl on cl.CASE_PICK_LINE_ID=lot.CASE_PICK_LINE_ID
     join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=lot.CASE_PICK_TASK_ID
     join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=cl.PICK_PLAN_LINE_ID
     where lot.LOT_UID=u.CURRENT_UID and pl.CUSTOMER_ORDER_ROW_ID=demand_native_row and ct.CLOSED_AT is not null and ct.STATUS in('WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP','SHIPPED','DONE','CLOSED');
    if n=0 then
     select count(*)into n from RRL_PICK_TASK pt join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=pt.PICK_PLAN_LINE_ID
      where pt.PALLET_UID=u.CURRENT_UID and pt.TASK_TYPE='FULL_PALLET'and pt.STATUS='DONE'and pl.CUSTOMER_ORDER_ROW_ID=demand_native_row;
    end if;
    if n<>1 then fail('TRADE_BUYOUT_PICKED_ORDER_COMPOSITION_REQUIRED');end if;
    if b.BUYOUT_MODE='AFTER_PICK'and zone<>'WAIT'then fail('TRADE_BUYOUT_WAIT_ZONE_REQUIRED');end if;
    if b.BUYOUT_MODE='IN_TRANSIT'then
     select count(*)into n from RRL_TT_HU_LOAD_FACT lf,json_table(lf.COMPOSITION_JSON,'$.nodes[*]'columns(UID_VALUE varchar2(200)path'$.uid'))x
      where lf.LOAD_OPERATION_ID=v_load and lf.WARE_ID=p_ware and lf.STATUS='DEPARTED'and lf.DEPARTED_AT is not null
       and lf.DEPARTURE_OPERATION_ID is not null and lf.CUSTODY_RELEASE_OPERATION_ID is null and x.UID_VALUE=u.CURRENT_UID;
     if n<>1 then fail('TRADE_BUYOUT_ACTUAL_TRANSIT_REQUIRED');end if;
    end if;
   end if;
   insert into RRL_TRADE_BUYOUT_UNIT(BUYOUT_ID,PHYSICAL_UNIT_KEY,INITIAL_ATTRIBUTE_VERSION,INITIAL_UID,INITIAL_CELL)
    values(id_value,v_key,a.VERSION_NO,u.CURRENT_UID,u.CURRENT_CELL);
   unit_json:=json_object_t();unit_json.put('physical_unit_key',v_key);unit_json.put('pallet_identifier',u.CURRENT_UID);codes_json:=json_array_t();
   for code in(select SYSTEM_CODE,CODE_HASH,CANONICAL_CODE,RAW_CODE,PROFILES_JSON from RRL_WMS_RECEIPT_CODE where UID_PALLET=u.UID_PALLET and UNIT_ID=u.UNIT_ID order by SYSTEM_CODE,CODE_HASH)loop
    if dbms_lob.getlength(code.RAW_CODE)>4000 then fail('TRADE_BUYOUT_RAW_CODE_BOUND');end if;
    raw_text:=dbms_lob.substr(code.RAW_CODE,4000,1);code_json:=json_object_t();code_json.put('system_code',code.SYSTEM_CODE);code_json.put('code_hash',code.CODE_HASH);
    code_json.put('code',raw_text);code_json.put('canonical_code',code.CANONICAL_CODE);code_json.put('profiles',json_array_t.parse(code.PROFILES_JSON));codes_json.append(code_json);
   end loop;
   if codes_json.get_size=0 then fail('TRADE_BUYOUT_CODE_COMPOSITION_REQUIRED');end if;
   unit_json.put('codes',codes_json);units_json.append(unit_json);
  end loop;
  if b.BUYOUT_MODE='IN_TRANSIT'then
   for group_row in(select INITIAL_UID,count(*)N from RRL_TRADE_BUYOUT_UNIT where BUYOUT_ID=id_value group by INITIAL_UID)loop
    select count(*)into n from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=group_row.INITIAL_UID;
    if n<>group_row.N then fail('TRADE_BUYOUT_TRANSIT_WHOLE_LEAF_REQUIRED');end if;
   end loop;
  end if;
  b.REQUIRES_SORTING:=current_mixed(b);
  update RRL_TRADE_BUYOUT set REQUIRES_SORTING=b.REQUIRES_SORTING where BUYOUT_ID=id_value;
  payload:=card(b);payload.put('units',units_json);payload.put('business_operation_id',id_value);body_text:=payload.to_clob;
  v_journal:=RRL_REGULATORY_API.write_journal(p_system_code=>'SKM',p_entity_type=>'TRADE_BUYOUT',p_entity_id=>id_value,p_operation_type=>'BUYOUT_REQUEST',p_new_status=>'PENDING',p_document_id=>basis_id,p_payload_json=>body_text,p_created_by=>p_actor);
  v_outbox:=RRL_TRACEABILITY_API.enqueue_event('TRADECASE_BUYOUT_REQUESTED','TRADE_BUYOUT',id_value,'TC:BUYOUT:REQUEST:'||id_value,body_text,'TRADECASE_BUS',v_operation);
  b.REQUEST_JOURNAL_ID:=v_journal;
  result_json:=card(b);result_json.put('request_accepted',true);result_json.put('owner_changes',0);result_json.put('outbox_id',v_outbox);result_json.put('regulatory_journal_id',v_journal);result_json.put('external_delivery','PENDING');result_json.put('external_business','NOT_CONFIRMED');
  reply_text:=result_json.to_clob;update RRL_TRADE_BUYOUT set REQUEST_RESULT=reply_text,REQUEST_JOURNAL_ID=v_journal where BUYOUT_ID=id_value;
 end;
 procedure receive_result(p_ware number,p_actor varchar2,j json_object_t,result_json in out nocopy json_object_t)is
  id_value varchar2(100):=j.get_string('buyout_id');v_skm varchar2(100):=j.get_string('skm_id');v_event varchar2(100):=j.get_string('external_event_id');
  v_doc varchar2(100):=j.get_string('external_document_id');v_hash varchar2(64):=j.get_string('business_hash');v_body clob:=j.to_clob;v_reply clob;
  b RRL_TRADE_BUYOUT%rowtype;old_event RRL_TRADE_BUYOUT_EVENT%rowtype;bu RRL_TRADE_BUYOUT_UNIT%rowtype;a RRL_TRADE_STOCK_ATTR%rowtype;
  items json_array_t:=j.get_array('items');item json_object_t;v_key varchar2(64);v_outcome varchar2(12);v_reason varchar2(2000);changed number:=0;
  v_confirmed number;v_rejected number;v_pending number;v_mixed number;v_status varchar2(20);v_journal number;v_outbox number;v_op varchar2(100):=j.get_string('operation_id');
 begin
  select *into b from RRL_TRADE_BUYOUT where BUYOUT_ID=id_value and WARE_ID=p_ware for update wait 5;
  party_access(p_actor,b,1);
  if v_skm is null or v_skm<>b.SKM_ID or v_event is null or v_doc is null then fail('TRADE_BUYOUT_SKM_CORRELATION_REQUIRED');end if;
  begin
   select *into old_event from RRL_TRADE_BUYOUT_EVENT where WARE_ID=p_ware and SKM_ID=v_skm and EVENT_ID=v_event;
   if old_event.BUYOUT_ID<>id_value or old_event.PAYLOAD_HASH<>v_hash then fail('TRADE_BUYOUT_EXTERNAL_EVENT_CONFLICT');end if;
   result_json:=json_object_t.parse(old_event.RESULT_JSON);result_json.put('business_replayed',true);return;
  exception when no_data_found then null;end;
  if j.get_number('expected_version')is null or j.get_number('expected_version')<>b.VERSION_NO then fail('VERSION_CONFLICT');end if;
  if b.EXTERNAL_DOCUMENT_ID is not null and b.EXTERNAL_DOCUMENT_ID<>v_doc then fail('TRADE_BUYOUT_EXTERNAL_DOCUMENT_CONFLICT');end if;
  if items.get_size<1 or items.get_size>10000 then fail('TRADE_BUYOUT_RESULT_BOUND');end if;
  select count(*)into v_mixed from RRL_TRADE_BUYOUT where WARE_ID=p_ware and SKM_ID=v_skm and EXTERNAL_DOCUMENT_ID=v_doc and BUYOUT_ID<>id_value;
  if v_mixed>0 then fail('TRADE_BUYOUT_EXTERNAL_DOCUMENT_ALREADY_BOUND');end if;
  update RRL_TRADE_BUYOUT set EXTERNAL_DOCUMENT_ID=v_doc where BUYOUT_ID=id_value;
  for i in 0..items.get_size-1 loop
   item:=treat(items.get(i)as json_object_t);v_key:=item.get_string('physical_unit_key');v_outcome:=item.get_string('outcome');v_reason:=item.get_string('reason');
   if v_outcome is null or v_outcome not in('CONFIRMED','REJECTED','PENDING')then fail('TRADE_BUYOUT_OUTCOME_INVALID');end if;
   if v_outcome='REJECTED'and v_reason is null then fail('TRADE_BUYOUT_REFUSAL_REASON_REQUIRED');end if;
   begin select *into bu from RRL_TRADE_BUYOUT_UNIT where BUYOUT_ID=id_value and PHYSICAL_UNIT_KEY=v_key for update wait 5;
   exception when no_data_found then fail('TRADE_BUYOUT_RESULT_UNIT_NOT_REQUESTED');end;
   if bu.OUTCOME<>'PENDING'then
    if bu.OUTCOME<>v_outcome then fail('TRADE_BUYOUT_FINAL_RESULT_REQUIRES_NEW_BASIS');end if;
    continue;
   end if;
   if v_outcome='CONFIRMED'then
    select *into a from RRL_TRADE_STOCK_ATTR where PHYSICAL_UNIT_KEY=v_key for update wait 5;
    if a.OWNER_ID<>b.SOURCE_OWNER_ID or a.SKU_ID<>b.SKU_ID or a.MRC<>b.MRC then fail('TRADE_BUYOUT_OWNER_OR_PRODUCT_CONFLICT');end if;
    update RRL_TRADE_STOCK_ATTR set OWNER_ID=b.TARGET_OWNER_ID,VERSION_NO=VERSION_NO+1 where PHYSICAL_UNIT_KEY=v_key;
    changed:=changed+1;
   end if;
   update RRL_TRADE_BUYOUT_UNIT set OUTCOME=v_outcome,HOLD_ACTIVE=case when v_outcome='PENDING'then 1 else 0 end,EXTERNAL_REASON=v_reason
    where BUYOUT_ID=id_value and PHYSICAL_UNIT_KEY=v_key;
  end loop;
  select nvl(sum(case when OUTCOME='CONFIRMED'then 1 else 0 end),0),nvl(sum(case when OUTCOME='REJECTED'then 1 else 0 end),0),
   nvl(sum(case when OUTCOME='PENDING'then 1 else 0 end),0)into v_confirmed,v_rejected,v_pending from RRL_TRADE_BUYOUT_UNIT where BUYOUT_ID=id_value;
  v_mixed:=current_mixed(b);
  if v_pending>0 then if v_confirmed+v_rejected>0 then v_status:='PARTIAL_PENDING';else v_status:='PENDING';end if;
  elsif v_confirmed=b.REQUESTED_UNITS then v_status:='CONFIRMED';elsif v_confirmed=0 then v_status:='REJECTED';else v_status:='PARTIAL';end if;
  update RRL_TRADE_BUYOUT set STATUS=v_status,VERSION_NO=VERSION_NO+1,CONFIRMED_UNITS=v_confirmed,REJECTED_UNITS=v_rejected,
   PENDING_UNITS=v_pending,REQUIRES_SORTING=least(v_mixed,1),UPDATED_AT=systimestamp where BUYOUT_ID=id_value;
  select *into b from RRL_TRADE_BUYOUT where BUYOUT_ID=id_value;
  v_journal:=RRL_REGULATORY_API.write_journal(p_system_code=>'SKM',p_entity_type=>'TRADE_BUYOUT',p_entity_id=>id_value,
   p_operation_type=>'BUYOUT_RESULT',p_new_status=>v_status,p_document_id=>b.BASIS_ORDER_ID,p_external_operation_id=>v_doc,p_payload_json=>v_body,p_created_by=>p_actor);
  result_json:=card(b);result_json.put('owner_changes',changed);result_json.put('external_event_id',v_event);result_json.put('regulatory_journal_id',v_journal);result_json.put('physical_quantity_changed',false);
  v_outbox:=RRL_TRACEABILITY_API.enqueue_event('TRADECASE_BUYOUT_RESULT','TRADE_BUYOUT',id_value,event_key(p_ware,v_skm,v_event),result_json.to_clob,'TRADECASE_BUS',v_op);
  result_json.put('outbox_id',v_outbox);v_reply:=result_json.to_clob;
  insert into RRL_TRADE_BUYOUT_EVENT(WARE_ID,SKM_ID,EVENT_ID,BUYOUT_ID,PAYLOAD_HASH,BODY_JSON,RESULT_JSON)values(p_ware,v_skm,v_event,id_value,v_hash,v_body,v_reply);
 end;
 procedure execute_command(p_ware number,p_actor varchar2,p_kind varchar2,j json_object_t,result_json in out nocopy json_object_t)is begin
  if RRL_TRADE_STOCK_API.writes_allowed<>1 then raise_application_error(-20863,'TRADE_BUYOUT_WRITER_REQUIRED');end if;
  if p_kind='BUYOUT_REQUEST'then request_transfer(p_ware,p_actor,j,result_json);
  elsif p_kind='BUYOUT_RESULT'then receive_result(p_ware,p_actor,j,result_json);else fail('TRADE_BUYOUT_COMMAND');end if;
 end;
 procedure read_state(p_ware number,p_actor varchar2,p_kind varchar2,j json_object_t,p_result out clob)is
  b RRL_TRADE_BUYOUT%rowtype;result_json json_object_t:=json_object_t();items json_array_t:=json_array_t();item json_object_t;
  id_value varchar2(100):=j.get_string('buyout_id');after_value varchar2(100):=j.get_string('after');v_limit number:=j.get_number('limit');fetch_limit number;n number:=0;admin_flag number;after_sequence number;pending_only number:=case when j.get_boolean('pending_only')then 1 else 0 end;
 begin
  if p_kind='BUYOUT_DETAIL'then
   select *into b from RRL_TRADE_BUYOUT where BUYOUT_ID=id_value and WARE_ID=p_ware;party_access(p_actor,b,0);b.REQUIRES_SORTING:=current_mixed(b);result_json:=card(b);result_json.put('composition_checked',true);p_result:=result_json.to_clob;return;
  end if;
  if v_limit is null or v_limit<1 or v_limit>100 or v_limit<>trunc(v_limit)then fail('TRADE_BUYOUT_PAGE_LIMIT');end if;fetch_limit:=v_limit+1;
  if p_kind='BUYOUT_UNITS'then
   select *into b from RRL_TRADE_BUYOUT where BUYOUT_ID=id_value and WARE_ID=p_ware;party_access(p_actor,b,0);
   for r in(select bu.*,a.OWNER_ID,a.VERSION_NO,u.CURRENT_UID,u.CURRENT_CELL from RRL_TRADE_BUYOUT_UNIT bu
    join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=bu.PHYSICAL_UNIT_KEY join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=bu.PHYSICAL_UNIT_KEY
    where bu.BUYOUT_ID=id_value and(after_value is null or bu.PHYSICAL_UNIT_KEY>after_value)order by bu.PHYSICAL_UNIT_KEY fetch first fetch_limit rows only)loop
    n:=n+1;if n>v_limit then result_json.put('has_more',true);exit;end if;
    item:=json_object_t();item.put('physical_unit_key',r.PHYSICAL_UNIT_KEY);item.put('outcome',r.OUTCOME);item.put('reason',r.EXTERNAL_REASON);
    item.put('owner_id',r.OWNER_ID);item.put('attribute_version',r.VERSION_NO);item.put('pallet_identifier',r.CURRENT_UID);item.put('cell',r.CURRENT_CELL);item.put('buyout_hold',r.HOLD_ACTIVE=1);
    items.append(item);result_json.put('next_after',r.PHYSICAL_UNIT_KEY);
   end loop;
  elsif p_kind='BUYOUT_LIST'then
   admin_flag:=RRL_ACCESS_API.is_admin(p_actor);after_sequence:=j.get_number('after');
   for r in(select *from RRL_TRADE_BUYOUT bo where WARE_ID=p_ware and(after_sequence is null or after_sequence=0 or bo.REQUEST_JOURNAL_ID<after_sequence)and(pending_only=0 or bo.PENDING_UNITS>0)
    and(admin_flag=1 or exists(select 1 from RRL_TRADE_OWNER_GRANT g where g.USERNAME=p_actor and g.WARE_ID=p_ware and g.CAN_VIEW=1 and g.OWNER_ID in(bo.SOURCE_OWNER_ID,bo.TARGET_OWNER_ID)))
    order by bo.REQUEST_JOURNAL_ID desc fetch first fetch_limit rows only)loop
    n:=n+1;if n>v_limit then result_json.put('has_more',true);exit;end if;item:=card(r);item.put_null('requires_sorting');item.put_null('requires_transit_reconciliation');item.put('composition_checked',false);items.append(item);result_json.put('next_after',to_char(r.REQUEST_JOURNAL_ID,'TM9'));
   end loop;
  else fail('TRADE_BUYOUT_READ_COMMAND');end if;
  if n<=v_limit then result_json.put('has_more',false);result_json.put_null('next_after');end if;result_json.put('items',items);result_json.put('warehouse_id',p_ware);p_result:=result_json.to_clob;
 end;
end;
/
