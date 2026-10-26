create or replace package body RRL_TRADE_SHIP_EVENT as
 procedure publish(p_operation varchar2,p_trip number)is
  link_value RRL_TRADE_TRIP_LINK%rowtype;site RRL_TRADE_SITE%rowtype;
  units json_array_t;lines json_array_t;event_value json_object_t;unit_value json_object_t;codes json_array_t;code_value json_object_t;line_value json_object_t;identity_value json_object_t;
  previous_key varchar2(64);line_id varchar2(100);unit_quantity number;order_quantity number;trip_quantity number:=0;expected_quantity number;
  count_units number;outbox_no number;depart_instant timestamp with time zone;event_key varchar2(100);identity_hash varchar2(64);plate varchar2(100);n number;previous_code varchar2(64);previous_system varchar2(40);
  type number_map is table of number index by varchar2(100);
  type text_map is table of varchar2(100) index by varchar2(100);
  type seen_map is table of boolean index by varchar2(64);
  quantities number_map;skus text_map;seen seen_map;
  procedure finish_unit is
  begin
   if previous_key is null then return;end if;
   if codes.get_size=0 then raise_application_error(-20886,'TRADE_SHIPMENT_CODE_REQUIRED');end if;
   unit_value.put('codes',codes);units.append(unit_value);
   if not quantities.exists(line_id)then quantities(line_id):=0;end if;
   quantities(line_id):=quantities(line_id)+unit_quantity;order_quantity:=order_quantity+unit_quantity;trip_quantity:=trip_quantity+unit_quantity;
  end;
 begin
  select count(*)into n from RRL_TRADE_TRIP_LINK where NATIVE_TASK_ID=p_trip;
  if n=0 then return;end if;
  select *into link_value from RRL_TRADE_TRIP_LINK where NATIVE_TASK_ID=p_trip;
  select *into site from RRL_TRADE_SITE where WARE_ID=link_value.WARE_ID;
  select TRANSPORT into plate from RRL_TRANSPORT_TASK where ID=p_trip;
  select max(DEPARTED_AT)into depart_instant from RRL_TT_HU_LOAD_FACT where TT_ID=p_trip and DEPARTURE_OPERATION_ID=p_operation and STATUS='DEPARTED';
  if depart_instant is null then raise_application_error(-20886,'TRADE_SHIPMENT_DEPARTURE_REQUIRED');end if;
  for ld in(select LOAD_OPERATION_ID from RRL_TT_HU_LOAD_FACT where TT_ID=p_trip and DEPARTURE_OPERATION_ID=p_operation and STATUS='DEPARTED'order by LOAD_OPERATION_ID)loop
   RRL_TRADE_TRANSIT_PROOF.assert_load(ld.LOAD_OPERATION_ID,link_value.WARE_ID);
  end loop;
  for od in(
   select distinct tl.EXTERNAL_ID,tl.DOCUMENT_VERSION,tl.RECIPIENT_ID
   from RRL_TT_HU_LOAD_FACT lf join RRL_TT_HU_LOAD_ST ls on ls.LOAD_OPERATION_ID=lf.LOAD_OPERATION_ID and ls.ACTIVE_FLAG=1
   join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.LEGACY_SBORKA_PALLET_ID=ls.SBORKA_PALLET_ID
   join RRL_TRADE_ORDER_LINK tl on tl.CUSTOMER_ORDER_ID=f.CUSTOMER_ORDER_ID and tl.WARE_ID=lf.WARE_ID
   where lf.TT_ID=p_trip and lf.DEPARTURE_OPERATION_ID=p_operation and lf.STATUS='DEPARTED'order by tl.EXTERNAL_ID
  )loop
   units:=json_array_t();lines:=json_array_t();previous_key:=null;order_quantity:=0;count_units:=0;quantities.delete;skus.delete;
   for u in(
    with members as (
 select lf.LOAD_OPERATION_ID,lf.ROOT_UID,lf.WARE_ID,f.FULFILLMENT_ID,f.CUSTOMER_ORDER_ID,
        f.PICKED_CASE_TASK_ID,f.PICKED_WAREHOUSE_TASK_ID,f.PICKED_PALLET_UID
 from RRL_TT_HU_LOAD_FACT lf
 join RRL_TT_HU_LOAD_ST ls on ls.LOAD_OPERATION_ID=lf.LOAD_OPERATION_ID and ls.ACTIVE_FLAG=1
 join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.LEGACY_SBORKA_PALLET_ID=ls.SBORKA_PALLET_ID
 where lf.TT_ID=p_trip and lf.DEPARTURE_OPERATION_ID=p_operation and lf.STATUS='DEPARTED'
), sources as (
 select m.LOAD_OPERATION_ID,m.ROOT_UID,m.WARE_ID,m.CUSTOMER_ORDER_ID,lot.LOT_UID UID_VALUE,
        pl.CUSTOMER_ORDER_ROW_ID,ct.SSCC CARRIER
 from members m
 join RRL_CASE_CARRIER_LOT lot on lot.CASE_PICK_TASK_ID=m.PICKED_CASE_TASK_ID
 join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=lot.CASE_PICK_TASK_ID
 join RRL_CASE_PICK_LINE cl on cl.CASE_PICK_LINE_ID=lot.CASE_PICK_LINE_ID
 join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=cl.PICK_PLAN_LINE_ID
 union all
 select m.LOAD_OPERATION_ID,m.ROOT_UID,m.WARE_ID,m.CUSTOMER_ORDER_ID,m.PICKED_PALLET_UID,
        pl.CUSTOMER_ORDER_ROW_ID,m.PICKED_PALLET_UID
 from members m
 join RRL_WAREHOUSE_TASK wt on wt.TASK_ID=m.PICKED_WAREHOUSE_TASK_ID
 join RRL_PICK_WAVE_TASK wpt on wpt.PICK_WAVE_TASK_ID=wt.SOURCE_TASK_ID and wpt.PICK_WAVE_ID=wt.SOURCE_DOC_ID
 join RRL_PICK_TASK pt on pt.PICK_TASK_ID=wpt.PICK_TASK_ID
 join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=pt.PICK_PLAN_LINE_ID
 where m.PICKED_CASE_TASK_ID is null
)
select tl.EXTERNAL_ID ORDER_ID,tl.DOCUMENT_VERSION ORDER_VERSION,tl.RECIPIENT_ID,
       ol.EXTERNAL_LINE_ID LINE_ID,ol.SKU_ID,s.LOAD_OPERATION_ID,s.ROOT_UID,s.CARRIER,
       u.PHYSICAL_UNIT_KEY,u.BASE_QTY,u.BASE_UOM,u.STOCK_STATUS,
       a.SKU_ID ATTR_SKU_ID,a.OWNER_ID,a.MRC,a.EXPIRY_DATE,a.MARK_STATE,
       c.SYSTEM_CODE,c.CODE_HASH,c.RAW_CODE
from sources s
join RRL_TRADE_ORDER_LINK tl on tl.CUSTOMER_ORDER_ID=s.CUSTOMER_ORDER_ID and tl.WARE_ID=s.WARE_ID
join RRL_TRADE_ORDER_LINE ol on ol.CUSTOMER_ORDER_ID=tl.CUSTOMER_ORDER_ID and ol.CUSTOMER_ORDER_ROW_ID=s.CUSTOMER_ORDER_ROW_ID
join RRL_WMS_RECEIPT_UNIT u on u.CURRENT_UID=s.UID_VALUE
left join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
left join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID
where tl.EXTERNAL_ID=od.EXTERNAL_ID
order by tl.EXTERNAL_ID,ol.EXTERNAL_LINE_ID,u.PHYSICAL_UNIT_KEY,c.SYSTEM_CODE,c.CODE_HASH

   )loop
    if previous_key is null or previous_key<>u.PHYSICAL_UNIT_KEY then
     finish_unit;
     if u.STOCK_STATUS<>'ISSUED'or u.BASE_UOM<>'EA'or u.BASE_QTY is null or u.BASE_QTY<=0
      or u.ATTR_SKU_ID is null or u.ATTR_SKU_ID<>u.SKU_ID or u.OWNER_ID is null then
      raise_application_error(-20886,'TRADE_SHIPMENT_EXACT_ISSUED_ATTRIBUTES_REQUIRED');end if;
     if seen.exists(u.PHYSICAL_UNIT_KEY)then raise_application_error(-20886,'TRADE_SHIPMENT_UNIT_DUPLICATED');end if;
     seen(u.PHYSICAL_UNIT_KEY):=true;count_units:=count_units+1;
     if count_units>10000 then raise_application_error(-20881,'TRADE_SHIPMENT_ORDER_UNIT_BOUND_10000');end if;
     previous_key:=u.PHYSICAL_UNIT_KEY;line_id:=u.LINE_ID;unit_quantity:=u.BASE_QTY;skus(line_id):=u.SKU_ID;
     unit_value:=json_object_t();codes:=json_array_t();previous_code:=null;previous_system:=null;unit_value.put('physical_unit_key',previous_key);unit_value.put('line_id',line_id);
     unit_value.put('sku_id',u.SKU_ID);unit_value.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY));unit_value.put('base_uom',u.BASE_UOM);
     unit_value.put('owner_id',u.OWNER_ID);unit_value.put('mrc',u.MRC);unit_value.put('expiry_date',to_char(u.EXPIRY_DATE,'YYYY-MM-DD'));unit_value.put('mark_state',u.MARK_STATE);
     unit_value.put('load_unit_identifier',u.CARRIER);unit_value.put('top_unit_identifier',u.ROOT_UID);unit_value.put('load_operation_id',u.LOAD_OPERATION_ID);
    elsif line_id<>u.LINE_ID or unit_value.get_string('load_operation_id')<>u.LOAD_OPERATION_ID then
     raise_application_error(-20886,'TRADE_SHIPMENT_UNIT_DUPLICATED');
    end if;
    if u.RAW_CODE is not null then
     if previous_code=u.CODE_HASH and previous_system=u.SYSTEM_CODE then raise_application_error(-20886,'TRADE_SHIPMENT_CODE_DUPLICATED');end if;
     if dbms_lob.getlength(u.RAW_CODE)>4000 then raise_application_error(-20881,'TRADE_SHIPMENT_CODE_BOUND_4000');end if;
     code_value:=json_object_t();code_value.put('system_code',u.SYSTEM_CODE);code_value.put('code',dbms_lob.substr(u.RAW_CODE,4000,1));codes.append(code_value);
     previous_code:=u.CODE_HASH;previous_system:=u.SYSTEM_CODE;
    end if;
   end loop;
   finish_unit;
   if count_units=0 then raise_application_error(-20886,'TRADE_SHIPMENT_ORDER_UNITS_REQUIRED');end if;
   line_id:=quantities.first;
   while line_id is not null loop
    line_value:=json_object_t();line_value.put('line_id',line_id);line_value.put('sku_id',skus(line_id));line_value.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(quantities(line_id)));line_value.put('base_uom','EA');lines.append(line_value);
    line_id:=quantities.next(line_id);
   end loop;
   event_value:=json_object_t();event_value.put('schema_version',1);event_value.put('event_type','SHIPMENT_DEPARTED');event_value.put('operation_id',p_operation);
   event_value.put('warehouse_id',link_value.WARE_ID);event_value.put('trip_id',link_value.TRIP_ID);event_value.put('trip_version',link_value.TRIP_VERSION);event_value.put('native_task_id',p_trip);
   event_value.put('vehicle_identifier',plate);event_value.put('occurred_at',to_char(depart_instant,'YYYY-MM-DD"T"HH24:MI:SS.FF3TZH:TZM'));
   event_value.put('order_id',od.EXTERNAL_ID);event_value.put('order_version',od.DOCUMENT_VERSION);event_value.put('recipient_id',od.RECIPIENT_ID);
   event_value.put('unit_count',count_units);event_value.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(order_quantity));event_value.put('base_uom','EA');event_value.put('lines',lines);event_value.put('units',units);
   identity_value:=json_object_t();identity_value.put('operation_id',p_operation);identity_value.put('warehouse_id',link_value.WARE_ID);identity_value.put('order_id',od.EXTERNAL_ID);
   identity_hash:=lower(rawtohex(sys.dbms_crypto.hash(identity_value.to_clob,sys.dbms_crypto.hash_sh256)));
   for target in(select 'SAP' SYSTEM_CODE,site.SOURCE_ID DESTINATION_ID from dual union all select 'SKM',site.ACTIVE_SKM from dual)loop
    event_value.put('system_code',target.SYSTEM_CODE);event_value.put('destination_id',target.DESTINATION_ID);
    event_key:='TC.SHIP.'||target.SYSTEM_CODE||'.'||identity_hash;
    outbox_no:=RRL_TRACEABILITY_API.enqueue_event('TRADECASE_SHIPMENT_'||target.SYSTEM_CODE,'TRADE_ORDER',od.EXTERNAL_ID,event_key,event_value.to_clob,'TRADECASE_BUS',p_operation);
   end loop;
  end loop;
  select nvl(sum(n.QUANTITY),0)into expected_quantity from RRL_TT_HU_LOAD_FACT lf,
   json_table(lf.COMPOSITION_JSON,'$.nodes[*]'columns(KIND varchar2(20)path'$.kind',QUANTITY number path'$.quantity'))n
   where lf.TT_ID=p_trip and lf.DEPARTURE_OPERATION_ID=p_operation and lf.STATUS='DEPARTED'and n.KIND='STOCK';
  if trip_quantity<>expected_quantity or trip_quantity<=0 then raise_application_error(-20886,'TRADE_SHIPMENT_EXACT_LOAD_QUANTITY_REQUIRED');end if;
 end;
end;

/
