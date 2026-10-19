create or replace package body RRL_TRADE_STOCK_API as
 g_write_tx varchar2(100);
 function writes_allowed return number is begin
  if g_write_tx is not null and g_write_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;
 end;
 procedure fail(p_code varchar2) is begin raise_application_error(-20911,p_code);end;
 procedure authorize(p_ware number,p_actor varchar2,p_permission varchar2) is begin
  if RRL_ACCESS_API.allowed(p_actor,p_permission,'WAREHOUSE',to_char(p_ware,'TM9'))<>1 then
   raise_application_error(-20882,'ACCESS_DENIED');
  end if;
 end;
 procedure metadata_fence is
  policies json_array_t:=json_array_t();resources json_array_t:=json_array_t();
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null then fail('TRADE_METADATA_NESTED_IN_STOCK');end if;
  RRL_STOCK_PLAN_HELPER.fence(policies,'RELEASE','STOCK');
  RRL_STOCK_PLAN_HELPER.fence(policies,'CONFIG','WAREHOUSE',6);
  RRL_STOCK_PLAN_HELPER.row_key(resources,'RRL_STOCK_POLICY_GUARD','WAREHOUSE.CONFIGURATION');
  RRL_STOCK_LOCK_API.begin_plan;
  lock table RRL_ACCESS_REV in share mode wait 5;
  RRL_STOCK_LOCK_API.acquire_policies(policies.to_clob);RRL_STOCK_LOCK_API.acquire_resources(resources.to_clob);
 end;
 function owner_exists(p_ware number,p_owner varchar2) return number is n number;begin
  select count(*)into n from RRL_TRADE_DOCUMENT where WARE_ID=p_ware and ENTITY_TYPE='OWNER' and EXTERNAL_ID=p_owner and STATUS='ACCEPTED';
  return least(n,1);
 end;
 procedure read_stock(p_ware number,p_actor varchar2,j json_object_t,p_result out clob) is
  result_json json_object_t:=json_object_t();items json_array_t:=json_array_t();item json_object_t;
  v_limit number:=j.get_number('limit');row_limit number;after_key varchar2(64):=j.get_string('after');n number:=0;admin_flag number;v_pallet_filter varchar2(200):=j.get_string('pallet_identifier');v_alt varchar2(200):=j.get_string('pallet_identifier_alt');
 begin
  if v_limit is null or v_limit<1 or v_limit>100 or v_limit<>trunc(v_limit)then fail('TRADE_STOCK_PAGE_LIMIT');end if;
  row_limit:=v_limit+1;admin_flag:=RRL_ACCESS_API.is_admin(p_actor);
  if v_pallet_filter is not null then
   select count(*)into n from(
    select distinct 'P:'||u.CURRENT_UID R_ID from RRL_WMS_RECEIPT_UNIT u join RRL_CELLS c on c.CELL=u.CURRENT_CELL join RRL_PALLETS p on p.UID_PALLET=u.CURRENT_UID
     where c.WARE_ID=p_ware and u.STOCK_STATUS<>'ISSUED'and(u.CURRENT_UID in(v_pallet_filter,v_alt)or p.SSCC in(v_pallet_filter,v_alt))
    union select distinct 'C:'||ct.CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK ct join RRL_CASE_CARRIER_LOT h on h.CASE_PICK_TASK_ID=ct.CASE_PICK_TASK_ID
     join RRL_WMS_RECEIPT_UNIT u on u.CURRENT_UID=h.LOT_UID join RRL_CELLS c on c.CELL=u.CURRENT_CELL
     where c.WARE_ID=p_ware and u.STOCK_STATUS<>'ISSUED'and(ct.SSCC in(v_pallet_filter,v_alt)or 'CASE:'||ct.CASE_PICK_TASK_ID in(v_pallet_filter,v_alt)));
   if n>1 then fail('TRADE_PALLET_IDENTIFIER_AMBIGUOUS');end if;n:=0;
  end if;

  for u in(select a.PHYSICAL_UNIT_KEY,a.SKU_ID,a.OWNER_ID,a.MRC,a.EXPIRY_DATE,a.MARK_STATE,a.VERSION_NO,
   u.CURRENT_UID,u.CURRENT_CELL,u.BASE_QTY,u.BASE_UOM,u.UNIT_VERSION,u.HARD_RESERVATION_ID,
   case when exists(select 1 from RRL_TRADE_BUYOUT_UNIT bu where bu.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY and bu.HOLD_ACTIVE=1)then 1 else 0 end BUYOUT_HELD
   from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY
   join RRL_CELLS c on c.CELL=u.CURRENT_CELL
   where c.WARE_ID=p_ware and u.STOCK_STATUS<>'ISSUED'and(v_pallet_filter is null or u.CURRENT_UID in(v_pallet_filter,v_alt)
    or exists(select 1 from RRL_PALLETS p where p.UID_PALLET=u.CURRENT_UID and p.SSCC in(v_pallet_filter,v_alt))
    or exists(select 1 from RRL_CASE_CARRIER_LOT h join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=h.CASE_PICK_TASK_ID where h.LOT_UID=u.CURRENT_UID and(ct.SSCC in(v_pallet_filter,v_alt)or 'CASE:'||ct.CASE_PICK_TASK_ID in(v_pallet_filter,v_alt)))) and(after_key is null or a.PHYSICAL_UNIT_KEY>after_key)
    and(admin_flag=1 or exists(select 1 from RRL_TRADE_OWNER_GRANT g where g.USERNAME=p_actor and g.WARE_ID=p_ware and g.OWNER_ID=a.OWNER_ID and g.CAN_VIEW=1))
   order by a.PHYSICAL_UNIT_KEY fetch first row_limit rows only)loop
   n:=n+1;if n>v_limit then result_json.put('has_more',true);exit;end if;
   item:=json_object_t();item.put('physical_unit_key',u.PHYSICAL_UNIT_KEY);item.put('sku_id',u.SKU_ID);item.put('owner_id',u.OWNER_ID);
   item.put('mrc',to_char(u.MRC,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''));item.put('expiry_date',to_char(u.EXPIRY_DATE,'YYYY-MM-DD'));
   item.put('pallet_identifier',u.CURRENT_UID);item.put('cell',u.CURRENT_CELL);item.put('mark_state',u.MARK_STATE);
   item.put('base_quantity',to_char(u.BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''));item.put('base_uom',u.BASE_UOM);
   item.put('attribute_version',u.VERSION_NO);item.put('unit_version',u.UNIT_VERSION);
   item.put('hard_reserved',u.HARD_RESERVATION_ID is not null);item.put('buyout_hold',u.BUYOUT_HELD=1);
   item.put('allocation_enabled',false);
   items.append(item);result_json.put('next_after',u.PHYSICAL_UNIT_KEY);
  end loop;
  if n<=v_limit then result_json.put('has_more',false);result_json.put_null('next_after');end if;
  result_json.put('items',items);result_json.put('warehouse_id',p_ware);p_result:=result_json.to_clob;
 end;
 procedure read_transit(p_ware number,p_actor varchar2,j json_object_t,p_result out clob)is
  result_json json_object_t:=json_object_t();items json_array_t:=json_array_t();item json_object_t;
  v_limit number:=j.get_number('limit');row_limit number;after_key varchar2(64):=j.get_string('after');n number:=0;admin_flag number;
  load_id varchar2(100):=j.get_string('load_operation_id');manifest clob;
 begin
  if v_limit is null or v_limit<1 or v_limit>100 or v_limit<>trunc(v_limit)then fail('TRADE_STOCK_PAGE_LIMIT');end if;
  select COMPOSITION_JSON into manifest from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=load_id and WARE_ID=p_ware and STATUS='DEPARTED'and CUSTODY_RELEASED_AT is null;
  row_limit:=v_limit+1;admin_flag:=RRL_ACCESS_API.is_admin(p_actor);
  for u in(select a.PHYSICAL_UNIT_KEY,a.SKU_ID,a.OWNER_ID,a.MRC,a.EXPIRY_DATE,a.MARK_STATE,a.VERSION_NO,
   u.CURRENT_UID,u.CURRENT_CELL,u.BASE_QTY,u.BASE_UOM,u.UNIT_VERSION,
   case when exists(select 1 from RRL_TRADE_BUYOUT_UNIT bu where bu.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY and bu.HOLD_ACTIVE=1)then 1 else 0 end BUYOUT_HELD
   from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY
   where u.STOCK_STATUS='ISSUED'and exists(select 1 from json_table(manifest,'$.nodes[*]'columns(P_UID varchar2(200)path'$.uid'))x where x.P_UID=u.CURRENT_UID)
    and(after_key is null or a.PHYSICAL_UNIT_KEY>after_key)
    and(admin_flag=1 or exists(select 1 from RRL_TRADE_OWNER_GRANT g where g.USERNAME=p_actor and g.WARE_ID=p_ware and g.OWNER_ID=a.OWNER_ID and g.CAN_VIEW=1))
   order by a.PHYSICAL_UNIT_KEY fetch first row_limit rows only)loop
   n:=n+1;if n>v_limit then result_json.put('has_more',true);exit;end if;
   item:=json_object_t();item.put('physical_unit_key',u.PHYSICAL_UNIT_KEY);item.put('sku_id',u.SKU_ID);item.put('owner_id',u.OWNER_ID);
   item.put('mrc',RRL_STOCK_PLAN_HELPER.decimal_text(u.MRC));item.put('expiry_date',to_char(u.EXPIRY_DATE,'YYYY-MM-DD'));
   item.put('pallet_identifier',u.CURRENT_UID);item.put_null('cell');item.put('location_kind','VEHICLE_TRANSIT');item.put('last_warehouse_cell',u.CURRENT_CELL);item.put('mark_state',u.MARK_STATE);
   item.put('base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY));item.put('base_uom',u.BASE_UOM);item.put('attribute_version',u.VERSION_NO);item.put('unit_version',u.UNIT_VERSION);
   item.put('hard_reserved',false);item.put('buyout_hold',u.BUYOUT_HELD=1);item.put('allocation_enabled',false);
   items.append(item);result_json.put('next_after',u.PHYSICAL_UNIT_KEY);
  end loop;
  if n<=v_limit then result_json.put('has_more',false);result_json.put_null('next_after');end if;
  result_json.put('items',items);result_json.put('warehouse_id',p_ware);result_json.put('load_operation_id',load_id);p_result:=result_json.to_clob;
 end;
 procedure read_summary(p_ware number,p_actor varchar2,j json_object_t,p_result out clob) is
  result_json json_object_t:=json_object_t();items json_array_t:=json_array_t();item json_object_t;
  v_limit number:=j.get_number('limit');row_limit number;after_key varchar2(64):=j.get_string('after');n number:=0;admin_flag number;
 begin
  if v_limit is null or v_limit<1 or v_limit>100 or v_limit<>trunc(v_limit)then fail('TRADE_STOCK_PAGE_LIMIT');end if;
  row_limit:=v_limit+1;admin_flag:=RRL_ACCESS_API.is_admin(p_actor);
  for r in(select min(a.PHYSICAL_UNIT_KEY)PAGE_KEY,u.CURRENT_UID,u.CURRENT_CELL,a.SKU_ID,a.OWNER_ID,a.MRC,a.EXPIRY_DATE,u.BASE_UOM,
   count(*)UNITS,sum(u.BASE_QTY)BASE_QTY,sum(case when u.HARD_RESERVATION_ID is not null then u.BASE_QTY else 0 end)RESERVED_QTY,
   sum(case when a.MARK_STATE='PENDING'then 1 else 0 end)PENDING_UNITS,
   sum(case when a.MARK_STATE='VALID'then 1 else 0 end)VALID_UNITS,
   sum(case when a.MARK_STATE='REJECTED'then 1 else 0 end)REJECTED_UNITS
   from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY
   join RRL_CELLS c on c.CELL=u.CURRENT_CELL where c.WARE_ID=p_ware and u.STOCK_STATUS<>'ISSUED'
   and(admin_flag=1 or exists(select 1 from RRL_TRADE_OWNER_GRANT g where g.USERNAME=p_actor and g.WARE_ID=p_ware and g.OWNER_ID=a.OWNER_ID and g.CAN_VIEW=1))
   group by u.CURRENT_UID,u.CURRENT_CELL,a.SKU_ID,a.OWNER_ID,a.MRC,a.EXPIRY_DATE,u.BASE_UOM
   having after_key is null or min(a.PHYSICAL_UNIT_KEY)>after_key
   order by min(a.PHYSICAL_UNIT_KEY)fetch first row_limit rows only)loop
   n:=n+1;if n>v_limit then result_json.put('has_more',true);exit;end if;
   item:=json_object_t();item.put('pallet_identifier',r.CURRENT_UID);item.put('cell',r.CURRENT_CELL);
   item.put('sku_id',r.SKU_ID);item.put('owner_id',r.OWNER_ID);item.put('mrc',RRL_STOCK_PLAN_HELPER.decimal_text(r.MRC));
   item.put('expiry_date',to_char(r.EXPIRY_DATE,'YYYY-MM-DD'));item.put('base_uom',r.BASE_UOM);
   item.put('base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(r.BASE_QTY));item.put('hard_reserved_base',RRL_STOCK_PLAN_HELPER.decimal_text(r.RESERVED_QTY));
   item.put('unit_count',r.UNITS);item.put('pending_units',r.PENDING_UNITS);item.put('valid_units',r.VALID_UNITS);item.put('rejected_units',r.REJECTED_UNITS);
   items.append(item);result_json.put('next_after',r.PAGE_KEY);
  end loop;
  if n<=v_limit then result_json.put('has_more',false);result_json.put_null('next_after');end if;
  result_json.put('items',items);result_json.put('warehouse_id',p_ware);p_result:=result_json.to_clob;
 end;
 procedure save_cell(p_ware number,p_actor varchar2,j json_object_t,result_json in out nocopy json_object_t) is
  v_cell varchar2(60):=j.get_string('cell');v_zone varchar2(12):=j.get_string('zone_kind');v_owner varchar2(100):=j.get_string('owner_id');
  v_reason varchar2(2000):=j.get_string('reason');v_version number;n number;
 begin
  select WARE_ID into n from RRL_CELLS where CELL=v_cell;
  if n<>p_ware then fail('TRADE_CELL_WAREHOUSE_CONFLICT');end if;
  if v_zone='PICK' and v_owner is null then fail('TRADE_PICK_OWNER_REQUIRED');end if;
  if v_owner is not null and owner_exists(p_ware,v_owner)<>1 then fail('TRADE_OWNER_NOT_FOUND');end if;
  begin select VERSION_NO into v_version from RRL_TRADE_CELL_POLICY where CELL=v_cell;exception when no_data_found then v_version:=0;end;
  if j.get_number('expected_version')<>v_version then fail('VERSION_CONFLICT');end if;
  merge into RRL_TRADE_CELL_POLICY d using(select v_cell CELL from dual)x on(d.CELL=x.CELL)
   when matched then update set WARE_ID=p_ware,ZONE_KIND=v_zone,OWNER_ID=v_owner,VERSION_NO=v_version+1,REASON=v_reason,CHANGED_BY=p_actor,CHANGED_AT=systimestamp
   when not matched then insert(CELL,WARE_ID,ZONE_KIND,OWNER_ID,VERSION_NO,REASON,CHANGED_BY)values(v_cell,p_ware,v_zone,v_owner,1,v_reason,p_actor);
  RRL_TRADE_STOCK_GUARD.assert_cell(v_cell);result_json.put('cell',v_cell);result_json.put('version',v_version+1);
 end;
 procedure save_grant(p_ware number,p_actor varchar2,j json_object_t,result_json in out nocopy json_object_t) is
  v_user nvarchar2(50):=j.get_string('username');v_owner varchar2(100):=j.get_string('owner_id');v_version number;n number;
  view_flag number:=case when j.get_boolean('can_view')then 1 else 0 end;
  write_flag number:=case when j.get_boolean('can_operate')then 1 else 0 end;v_reason varchar2(2000):=j.get_string('reason');
 begin
  if RRL_ACCESS_API.is_admin(p_actor)<>1 then raise_application_error(-20882,'TRADE_OWNER_GRANT_ADMIN_REQUIRED');end if;
  select count(*)into n from RUSERS where ID=v_user and nvl(DELETED,0)=0;
  if n<>1 or owner_exists(p_ware,v_owner)<>1 then fail('TRADE_GRANT_USER_OR_OWNER_NOT_FOUND');end if;
  if write_flag>view_flag then fail('TRADE_OPERATE_REQUIRES_VIEW');end if;
  begin select VERSION_NO into v_version from RRL_TRADE_OWNER_GRANT where USERNAME=v_user and WARE_ID=p_ware and OWNER_ID=v_owner;
  exception when no_data_found then v_version:=0;end;
  if j.get_number('expected_version')<>v_version then fail('VERSION_CONFLICT');end if;
  merge into RRL_TRADE_OWNER_GRANT d using(select v_user USERNAME,p_ware WARE_ID,v_owner OWNER_ID from dual)x
   on(d.USERNAME=x.USERNAME and d.WARE_ID=x.WARE_ID and d.OWNER_ID=x.OWNER_ID)
   when matched then update set CAN_VIEW=view_flag,CAN_OPERATE=write_flag,VERSION_NO=v_version+1,REASON=v_reason,CHANGED_BY=p_actor
   when not matched then insert(USERNAME,WARE_ID,OWNER_ID,CAN_VIEW,CAN_OPERATE,VERSION_NO,REASON,CHANGED_BY)
    values(v_user,p_ware,v_owner,view_flag,write_flag,1,v_reason,p_actor);
  result_json.put('version',v_version+1);result_json.put('owner_id',v_owner);result_json.put('username',v_user);
 end;
 procedure bind_attributes(p_ware number,p_actor varchar2,j json_object_t,p_codes clob,result_json in out nocopy json_object_t) is
  supply_id varchar2(100):=j.get_string('supply_id');v_pallet varchar2(200):=j.get_string('scanned_pallet');supply_json clob;
  b json_object_t;receipt_json clob;receipt json_object_t;version_no number;source_owner varchar2(100);sku_id varchar2(100);
  expected_article varchar2(160);actual_article varchar2(160);actual_ware number;actual_order varchar2(100);actual_line varchar2(100);
  n number;wanted number;matched number;invalid_units number;cell varchar2(60);source_expiry date;actual_expiry date;
  source_mrc number;source_batch varchar2(100);codes_count number;
 begin
  select BODY_JSON,VERSION_NO into supply_json,version_no from RRL_TRADE_DOCUMENT
   where WARE_ID=p_ware and ENTITY_TYPE='SUPPLY' and EXTERNAL_ID=supply_id and STATUS='ACCEPTED';
  if version_no<>j.get_number('expected_supply_version')then fail('TRADE_SUPPLY_VERSION_CHANGED');end if;
  b:=json_object_t.parse(supply_json);source_owner:=b.get_string('owner_id');sku_id:=b.get_string('sku_id');
  RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,p_ware,source_owner,1);
  if b.get_string('pallet_identifier')<>v_pallet then fail('TRADE_PALLET_SCAN_MISMATCH');end if;
  if b.get_string('composition_source')<>'SAP' then fail('TRADE_COMPOSITION_SOURCE_NOT_CONFIGURED');end if;
  expected_article:=b.get_string('wms_article_id');source_mrc:=b.get_number('mrc');source_batch:=b.get_string('supplier_batch');
  if source_mrc is null or source_mrc<0 or trunc(source_mrc,2)<>source_mrc or source_mrc>=10000000000 then fail('TRADE_MRC_PRECISION');end if;
  source_expiry:=to_date(b.get_string('expiry_date'),'FXYYYY-MM-DD');actual_order:=b.get_string('sap_order_id');actual_line:=b.get_string('sap_line_id');
  select r.RESULT_JSON,so.WARE_ID,p.ARTICUL,p.EXPIRY_DATE into receipt_json,actual_ware,actual_article,actual_expiry
   from RRL_SAP_PALLET_RECEIPT r join RRL_SAP_SUPPLY_ORDER so on so.ORDER_ID=r.ORDER_ID join RRL_PALLETS p on p.UID_PALLET=r.UID_PALLET
   where r.UID_PALLET=v_pallet and r.ORDER_ID=actual_order and r.LINE_NUMBER=actual_line;
  if actual_ware<>p_ware or actual_article<>expected_article then fail('TRADE_RECEIPT_MAPPING_MISMATCH');end if;
  receipt:=json_object_t.parse(receipt_json);
  if actual_expiry is null or trunc(actual_expiry)<>source_expiry or receipt.get_string('supplier_batch')is null
   or receipt.get_string('supplier_batch')<>source_batch then fail('TRADE_RECEIPT_BATCH_OR_EXPIRY_MISMATCH');end if;
  wanted:=b.get_array('codes').get_size;
  select count(*)into codes_count from json_table(p_codes,'$[*]' columns(code_hash varchar2(64) path '$.code_hash'));
  if codes_count<>wanted then fail('TRADE_SUPPLY_HINT_COUNT');end if;
  select count(*),min(CURRENT_CELL),nvl(sum(case when HARD_RESERVATION_ID is not null or STOCK_STATUS not in('CAPTURED','AVAILABLE')or BASE_QTY<>1 or BASE_UOM<>'EA' then 1 else 0 end),0)
   into n,cell,invalid_units from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=v_pallet and STOCK_STATUS<>'ISSUED';
  if n<>wanted or invalid_units>0 then fail('TRADE_RECEIPT_UNIT_SET_CHANGED');end if;
  select count(distinct u.PHYSICAL_UNIT_KEY)into matched from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE c
   on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID
   join json_table(p_codes,'$[*]' columns(system_code varchar2(30) path '$.system_code',code_hash varchar2(64) path '$.code_hash'))h
   on h.system_code=c.SYSTEM_CODE and h.code_hash=c.CODE_HASH
   where u.CURRENT_UID=v_pallet and u.CURRENT_CELL=cell and u.STOCK_STATUS<>'ISSUED' and u.PHYSICAL_UNIT_KEY is not null;
  if matched<>wanted then fail('TRADE_SOURCE_CODES_DIFFER');end if;
  select count(*)into n from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY where u.CURRENT_UID=v_pallet and u.STOCK_STATUS<>'ISSUED';
  if n>0 then fail('TRADE_ATTRIBUTES_ALREADY_BOUND');end if;
  insert into RRL_TRADE_STOCK_ATTR(PHYSICAL_UNIT_KEY,RECEIPT_UID,UNIT_ID,CAPTURE_WARE_ID,SUPPLY_ID,SUPPLY_VERSION,SKU_ID,OWNER_ID,MRC,EXPIRY_DATE,SUPPLIER_BATCH,CREATED_BY)
   select PHYSICAL_UNIT_KEY,UID_PALLET,UNIT_ID,p_ware,supply_id,version_no,sku_id,source_owner,source_mrc,source_expiry,source_batch,p_actor
    from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=v_pallet and CURRENT_CELL=cell and STOCK_STATUS<>'ISSUED';
  RRL_TRADE_STOCK_GUARD.assert_cell(cell);
  result_json.put('supply_id',supply_id);result_json.put('owner_id',source_owner);result_json.put('bound_units',wanted);
  result_json.put('pallet_identifier',v_pallet);result_json.put('mark_state','PENDING');result_json.put('attributes_bound',true);
 end;
 procedure confirm_marks(p_ware number,p_actor varchar2,j json_object_t,result_json in out nocopy json_object_t) is
  skm varchar2(100):=j.get_string('skm_id');event_id varchar2(100):=j.get_string('external_event_id');
  event_json clob;event_operation varchar2(100):=j.get_string('operation_id');event_hash varchar2(64):=j.get_string('payload_hash');
  active_skm varchar2(100);site_version number;old_event RRL_TRADE_MARK_EVENT%rowtype;
  a RRL_TRADE_STOCK_ATTR%rowtype;current_ware number;current_status varchar2(30);updated_count number:=0;
  items json_array_t:=j.get_array('items');item json_object_t;v_key varchar2(64);verdict varchar2(10);
 begin
  select ACTIVE_SKM,VERSION_NO into active_skm,site_version from RRL_TRADE_SITE where WARE_ID=p_ware;
  if skm is null or j.get_number('expected_site_version')is null or skm<>active_skm or site_version<>j.get_number('expected_site_version')then fail('TRADE_SKM_VERSION_CONFLICT');end if;
  if event_id is null or length(event_id)>100 or items.get_size<1 or items.get_size>1000 then fail('TRADE_MARK_EVENT_INVALID');end if;
  begin
   select *into old_event from RRL_TRADE_MARK_EVENT where WARE_ID=p_ware and SKM_ID=skm and EXTERNAL_EVENT_ID=event_id;
   fail('TRADE_EXTERNAL_EVENT_ALREADY_RECORDED');
  exception when no_data_found then null;end;
  for i in 0..items.get_size-1 loop
   item:=treat(items.get(i)as json_object_t);v_key:=item.get_string('physical_unit_key');verdict:=item.get_string('verdict');
   if verdict is null or verdict not in('VALID','REJECTED')then fail('TRADE_MARK_VERDICT_INVALID');end if;
   begin
    select *into a from RRL_TRADE_STOCK_ATTR where PHYSICAL_UNIT_KEY=v_key for update wait 5;
    select c.WARE_ID,u.STOCK_STATUS into current_ware,current_status from RRL_WMS_RECEIPT_UNIT u join RRL_CELLS c on c.CELL=u.CURRENT_CELL
      where u.PHYSICAL_UNIT_KEY=v_key;
   exception when no_data_found then fail('TRADE_MARK_UNIT_NOT_FOUND');end;
   if current_ware<>p_ware or current_status='ISSUED' then fail('TRADE_MARK_CURRENT_WARE_CONFLICT');end if;
   RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,p_ware,a.OWNER_ID,1);
   if item.get_number('expected_attribute_version')is null or a.VERSION_NO<>item.get_number('expected_attribute_version')or a.MARK_STATE<>'PENDING'then fail('TRADE_MARK_ATTRIBUTE_VERSION_CONFLICT');end if;
   update RRL_TRADE_STOCK_ATTR set MARK_STATE=verdict,VERSION_NO=VERSION_NO+1 where PHYSICAL_UNIT_KEY=v_key;
   updated_count:=updated_count+1;
  end loop;
  event_json:=j.to_clob;
  insert into RRL_TRADE_MARK_EVENT(WARE_ID,SKM_ID,EXTERNAL_EVENT_ID,OPERATION_ID,PAYLOAD_HASH,BODY_JSON)
   values(p_ware,skm,event_id,event_operation,event_hash,event_json);
  result_json.put('confirmed_units',updated_count);result_json.put('external_event_id',event_id);result_json.put('skm_id',skm);
  result_json.put('owner_changed',false);
 end;
 procedure execute_command(p_ware number,p_actor varchar2,p_json clob,p_codes clob,p_result out clob) is
  j json_object_t:=json_object_t.parse(p_json);result_json json_object_t:=json_object_t();old_cmd RRL_TRADE_STOCK_COMMAND%rowtype;
  v_operation varchar2(100):=j.get_string('operation_id');v_hash varchar2(64):=j.get_string('payload_hash');
  v_kind varchar2(20):=j.get_string('command_type');v_permission varchar2(40);site_enabled number;outbox_id number;
 begin
  if v_kind='TRIP_STATE'then authorize(p_ware,p_actor,'tradecase_view');RRL_TRADE_TRANSPORT_CORE.read_state(p_ware,p_actor,j,p_result);return;end if;
  if v_kind in('BUYOUT_LIST','BUYOUT_DETAIL','BUYOUT_UNITS')then authorize(p_ware,p_actor,'tradecase_view');RRL_TRADE_BUYOUT_CORE.read_state(p_ware,p_actor,v_kind,j,p_result);return;end if;
  if v_kind='VIEW_TRANSIT'then authorize(p_ware,p_actor,'tradecase_view');read_transit(p_ware,p_actor,j,p_result);return;end if;
  if v_kind='VIEW_SUMMARY'then authorize(p_ware,p_actor,'tradecase_view');read_summary(p_ware,p_actor,j,p_result);return;end if;
  if v_kind='VIEW'then authorize(p_ware,p_actor,'tradecase_view');read_stock(p_ware,p_actor,j,p_result);return;end if;
  if v_kind in('CELL','GRANT')then v_permission:='warehouse_settings_edit';elsif v_kind='BIND'then v_permission:='tradecase_stock_bind';elsif v_kind='CONFIRM_MARKS'then v_permission:='tradecase_code_confirm';elsif v_kind='BUYOUT_REQUEST'then v_permission:='tradecase_buyout_request';elsif v_kind='BUYOUT_RESULT'then v_permission:='tradecase_buyout_confirm';elsif v_kind='BIND_TRIP'then v_permission:='tradecase_trip_bind';elsif v_kind='TRANSPORT_RESULT'then v_permission:='tradecase_transport_confirm';else fail('TRADE_STOCK_COMMAND');end if;
  authorize(p_ware,p_actor,v_permission);metadata_fence;
  RRL_ACCESS_API.assert_allowed(p_actor,v_permission,'WAREHOUSE',to_char(p_ware,'TM9'));
  select ENABLED into site_enabled from RRL_TRADE_SITE where WARE_ID=p_ware for update wait 5;
  begin
   select *into old_cmd from RRL_TRADE_STOCK_COMMAND where OPERATION_ID=v_operation;
   if old_cmd.WARE_ID<>p_ware or old_cmd.ACTOR<>p_actor or old_cmd.PAYLOAD_HASH<>v_hash then fail('OPERATION_CONFLICT');end if;
   result_json:=json_object_t.parse(old_cmd.RESULT_JSON);
   if v_kind in('BUYOUT_REQUEST','BUYOUT_RESULT')then RRL_TRADE_BUYOUT_CORE.assert_replay(p_ware,p_actor,j);end if;
   if v_kind='BIND'then RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,p_ware,result_json.get_string('owner_id'),1);end if;
   if v_kind='CONFIRM_MARKS'then
    for o in(select distinct a.OWNER_ID from RRL_TRADE_STOCK_ATTR a join json_table(p_json,'$.items[*]'columns(PHYSICAL_UNIT_KEY varchar2(64)path'$.physical_unit_key'))x on x.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY)loop
     RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,p_ware,o.OWNER_ID,1);
    end loop;
   end if;
   if v_kind='GRANT'and RRL_ACCESS_API.is_admin(p_actor)<>1 then raise_application_error(-20882,'TRADE_OWNER_GRANT_ADMIN_REQUIRED');end if;
   result_json.put('replayed',true);p_result:=result_json.to_clob;RRL_STOCK_LOCK_API.clear_plan;return;
  exception when no_data_found then null;end;
  if site_enabled<>1 and v_kind not in('BUYOUT_RESULT','TRANSPORT_RESULT')then fail('TRADE_SITE_DISABLED');end if;
  g_write_tx:=dbms_transaction.local_transaction_id(true);
  if v_kind='BIND_TRIP'then RRL_TRADE_TRANSPORT_CORE.bind_trip(p_ware,p_actor,j,result_json);
  elsif v_kind='TRANSPORT_RESULT'then RRL_TRADE_TRANSPORT_CORE.confirm_document(p_ware,p_actor,j,result_json);
  elsif v_kind='CELL'then save_cell(p_ware,p_actor,j,result_json);
  elsif v_kind='GRANT'then save_grant(p_ware,p_actor,j,result_json);
  elsif v_kind='CONFIRM_MARKS'then confirm_marks(p_ware,p_actor,j,result_json);
  elsif v_kind in('BUYOUT_REQUEST','BUYOUT_RESULT')then RRL_TRADE_BUYOUT_CORE.execute_command(p_ware,p_actor,v_kind,j,result_json);
  else bind_attributes(p_ware,p_actor,j,p_codes,result_json);end if;
  result_json.put('warehouse_id',p_ware);result_json.put('operation_id',v_operation);result_json.put('stock_changed',false);result_json.put('replayed',false);
  if v_kind='BIND'then
   outbox_id:=RRL_TRACEABILITY_API.enqueue_event('TRADECASE_ATTRIBUTES_BOUND','TRADE_SUPPLY',j.get_string('supply_id'),
    'TC:ATTR:'||v_operation,result_json.to_clob,'TRADECASE_BUS',v_operation);result_json.put('outbox_id',outbox_id);
  end if;
  if v_kind='CONFIRM_MARKS'then
   outbox_id:=RRL_TRACEABILITY_API.enqueue_event('TRADECASE_MARK_CONFIRMATION_ACCEPTED','TRADE_MARK_EVENT',j.get_string('external_event_id'),
    'TC:MARK:'||v_operation,result_json.to_clob,'TRADECASE_BUS',v_operation);result_json.put('outbox_id',outbox_id);
  end if;
  p_result:=result_json.to_clob;
  insert into RRL_TRADE_STOCK_COMMAND(OPERATION_ID,WARE_ID,ACTOR,PAYLOAD_HASH,RESULT_JSON)values(v_operation,p_ware,p_actor,v_hash,p_result);
  g_write_tx:=null;RRL_STOCK_LOCK_API.clear_plan;
 exception when others then g_write_tx:=null;RRL_STOCK_LOCK_API.clear_plan;raise;
 end;
end;



/
