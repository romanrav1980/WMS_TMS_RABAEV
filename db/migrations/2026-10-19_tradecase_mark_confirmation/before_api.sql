create or replace package RRL_TRADE_STOCK_API authid definer as
 function writes_allowed return number;
 procedure execute_command(p_ware number,p_actor varchar2,p_json clob,p_codes clob,p_result out clob);
end;
/
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
  v_limit number:=j.get_number('limit');row_limit number;after_key varchar2(64):=j.get_string('after');n number:=0;admin_flag number;
 begin
  if v_limit is null or v_limit<1 or v_limit>100 or v_limit<>trunc(v_limit)then fail('TRADE_STOCK_PAGE_LIMIT');end if;
  row_limit:=v_limit+1;admin_flag:=RRL_ACCESS_API.is_admin(p_actor);
  for u in(select a.PHYSICAL_UNIT_KEY,a.SKU_ID,a.OWNER_ID,a.MRC,a.EXPIRY_DATE,a.MARK_STATE,a.VERSION_NO,
   u.CURRENT_UID,u.CURRENT_CELL,u.BASE_QTY,u.BASE_UOM,u.UNIT_VERSION,u.HARD_RESERVATION_ID
   from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY
   join RRL_CELLS c on c.CELL=u.CURRENT_CELL
   where c.WARE_ID=p_ware and u.STOCK_STATUS<>'ISSUED' and(after_key is null or a.PHYSICAL_UNIT_KEY>after_key)
    and(admin_flag=1 or exists(select 1 from RRL_TRADE_OWNER_GRANT g where g.USERNAME=p_actor and g.WARE_ID=p_ware and g.OWNER_ID=a.OWNER_ID and g.CAN_VIEW=1))
   order by a.PHYSICAL_UNIT_KEY fetch first row_limit rows only)loop
   n:=n+1;if n>v_limit then result_json.put('has_more',true);exit;end if;
   item:=json_object_t();item.put('physical_unit_key',u.PHYSICAL_UNIT_KEY);item.put('sku_id',u.SKU_ID);item.put('owner_id',u.OWNER_ID);
   item.put('mrc',to_char(u.MRC,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''));item.put('expiry_date',to_char(u.EXPIRY_DATE,'YYYY-MM-DD'));
   item.put('pallet_identifier',u.CURRENT_UID);item.put('cell',u.CURRENT_CELL);item.put('mark_state',u.MARK_STATE);
   item.put('base_quantity',to_char(u.BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''));item.put('base_uom',u.BASE_UOM);
   item.put('attribute_version',u.VERSION_NO);item.put('unit_version',u.UNIT_VERSION);
   item.put('allocation_enabled',false);
   items.append(item);result_json.put('next_after',u.PHYSICAL_UNIT_KEY);
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
 procedure execute_command(p_ware number,p_actor varchar2,p_json clob,p_codes clob,p_result out clob) is
  j json_object_t:=json_object_t.parse(p_json);result_json json_object_t:=json_object_t();old_cmd RRL_TRADE_STOCK_COMMAND%rowtype;
  v_operation varchar2(100):=j.get_string('operation_id');v_hash varchar2(64):=j.get_string('payload_hash');
  v_kind varchar2(20):=j.get_string('command_type');v_permission varchar2(40);site_enabled number;outbox_id number;
 begin
  if v_kind='VIEW'then authorize(p_ware,p_actor,'tradecase_view');read_stock(p_ware,p_actor,j,p_result);return;end if;
  if v_kind in('CELL','GRANT')then v_permission:='warehouse_settings_edit';elsif v_kind='BIND'then v_permission:='tradecase_stock_bind';else fail('TRADE_STOCK_COMMAND');end if;
  authorize(p_ware,p_actor,v_permission);metadata_fence;
  RRL_ACCESS_API.assert_allowed(p_actor,v_permission,'WAREHOUSE',to_char(p_ware,'TM9'));
  select ENABLED into site_enabled from RRL_TRADE_SITE where WARE_ID=p_ware for update wait 5;
  begin
   select *into old_cmd from RRL_TRADE_STOCK_COMMAND where OPERATION_ID=v_operation;
   if old_cmd.WARE_ID<>p_ware or old_cmd.ACTOR<>p_actor or old_cmd.PAYLOAD_HASH<>v_hash then fail('OPERATION_CONFLICT');end if;
   result_json:=json_object_t.parse(old_cmd.RESULT_JSON);
   if v_kind='BIND'then RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,p_ware,result_json.get_string('owner_id'),1);end if;
   if v_kind='GRANT'and RRL_ACCESS_API.is_admin(p_actor)<>1 then raise_application_error(-20882,'TRADE_OWNER_GRANT_ADMIN_REQUIRED');end if;
   result_json.put('replayed',true);p_result:=result_json.to_clob;RRL_STOCK_LOCK_API.clear_plan;return;
  exception when no_data_found then null;end;
  if site_enabled<>1 then fail('TRADE_SITE_DISABLED');end if;
  g_write_tx:=dbms_transaction.local_transaction_id(true);
  if v_kind='CELL'then save_cell(p_ware,p_actor,j,result_json);
  elsif v_kind='GRANT'then save_grant(p_ware,p_actor,j,result_json);
  else bind_attributes(p_ware,p_actor,j,p_codes,result_json);end if;
  result_json.put('warehouse_id',p_ware);result_json.put('operation_id',v_operation);result_json.put('stock_changed',false);result_json.put('replayed',false);
  if v_kind='BIND'then
   outbox_id:=RRL_TRACEABILITY_API.enqueue_event('TRADECASE_ATTRIBUTES_BOUND','TRADE_SUPPLY',j.get_string('supply_id'),
    'TC:ATTR:'||v_operation,result_json.to_clob,'TRADECASE_BUS',v_operation);result_json.put('outbox_id',outbox_id);
  end if;
  p_result:=result_json.to_clob;
  insert into RRL_TRADE_STOCK_COMMAND(OPERATION_ID,WARE_ID,ACTOR,PAYLOAD_HASH,RESULT_JSON)values(v_operation,p_ware,p_actor,v_hash,p_result);
  g_write_tx:=null;RRL_STOCK_LOCK_API.clear_plan;
 exception when others then g_write_tx:=null;RRL_STOCK_LOCK_API.clear_plan;raise;
 end;
end;
/