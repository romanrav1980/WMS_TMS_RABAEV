create or replace package RRL_TRADE_SORT_GUARD authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_INTERNAL_CMD) as
 function is_sort(p_request clob) return number;
 procedure assert_scope(p_request clob,p_actor varchar2);
 procedure assert_selection(p_request clob,p_actor varchar2);
end;
/
create or replace package body RRL_TRADE_SORT_GUARD as
 procedure fail(p_code varchar2) is begin raise_application_error(-20886,p_code);end;
 function is_sort(p_request clob) return number is d json_object_t:=json_object_t.parse(p_request);m json_object_t;
 begin
  if d.get_string('command_type')<>'INTERNAL_MOVE' then return 0;end if;
  m:=d.get_object('metadata');if m.has('tradecase_sorting') and m.get_boolean('tradecase_sorting') then return 1;end if;return 0;
 end;
 procedure assert_scope(p_request clob,p_actor varchar2) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');
  ware number:=m.get_number('warehouse_id');src varchar2(60):=m.get_string('source_cell');dst varchar2(60):=m.get_string('target_cell');n number;units clob:=d.get_array('units').to_clob;
 begin
  select count(*)into n from RRL_CELLS where CELL in(src,dst)and WARE_ID=ware;
  if src=dst or n<>2 then fail('TRADE_SORT_CELL_WAREHOUSE_CONFLICT');end if;
  select count(*)into n from RRL_TRADE_SITE where WARE_ID=ware and ENABLED=1;
  if n<>1 then fail('TRADE_SITE_NOT_ENABLED');end if;
  if RRL_ACCESS_API.allowed(p_actor,'tradecase_stock_sort','WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(ware))<>1 then raise_application_error(-20882,'TRADE_SORT_FORBIDDEN');end if;
  for o in(select distinct a.OWNER_ID from RRL_TRADE_STOCK_ATTR a join json_table(units,'$[*]'columns(K varchar2(64)path '$'))j on j.K=a.PHYSICAL_UNIT_KEY)loop
   RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,ware,o.OWNER_ID,1);
  end loop;
 end;
 procedure assert_selection(p_request clob,p_actor varchar2) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');
  uid varchar2(200):=m.get_string('uid');src varchar2(60):=m.get_string('source_cell');dst varchar2(60):=m.get_string('target_cell');
  units clob:=d.get_array('units').to_clob;n number;qty number;expected number:=d.get_array('units').get_size;groups_count number;
 begin
  assert_scope(p_request,p_actor);
  if expected=0 then fail('TRADE_SORT_SCANS_REQUIRED');end if;
  select count(*)into n from RRL_WMS_HU_LINK where ACTIVE_FLAG=1 and(CHILD_PALLET_UID=uid or PARENT_UID=uid);
  if n>0 then fail('TRADE_SORT_UNPACK_REQUIRED');end if;
  select count(*),sum(u.BASE_QTY)into n,qty from json_table(units,'$[*]'columns(K varchar2(64)path '$'))j
   join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=j.K join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
   where u.CURRENT_UID=uid and u.CURRENT_CELL=src and u.STOCK_STATUS='AVAILABLE'and u.HARD_RESERVATION_ID is null and a.MARK_STATE='VALID'
    and not exists(select 1 from RRL_TRADE_BUYOUT_UNIT b where b.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY and b.HOLD_ACTIVE=1);
  if n<>expected or RRL_STOCK_PLAN_HELPER.decimal_text(qty)<>m.get_string('quantity')then fail('TRADE_SORT_SELECTION_NOT_AVAILABLE');end if;
  select count(*)into groups_count from(select distinct a.OWNER_ID,a.SKU_ID,a.MRC,a.EXPIRY_DATE from RRL_TRADE_STOCK_ATTR a
   join json_table(units,'$[*]'columns(K varchar2(64)path '$'))j on j.K=a.PHYSICAL_UNIT_KEY);
  if groups_count<>1 then fail('TRADE_SORT_SELECTION_MUST_BE_HOMOGENEOUS');end if;
  select count(*)into n from RRL_TRADE_CELL_POLICY where CELL=dst and ZONE_KIND in('STORAGE','SORT','WAIT');
  if n<>1 then fail('TRADE_SORT_TARGET_ZONE_REQUIRED');end if;
 end;
end;
/
