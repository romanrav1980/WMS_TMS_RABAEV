create or replace package body RRL_FULL_SHIPPING_SCOPE as
 procedure warehouse(p_ware number,p_actor varchar2,p_permission varchar2)is n number;begin
  if p_ware is null or p_ware<1 or p_actor is null then raise_application_error(-20882,'SHIPPING_ACTUAL_WARE_REQUIRED');end if;
  select count(*)into n from RRL_WARES where ID=p_ware;if n!=1 then raise_application_error(-20882,'SHIPPING_ACTUAL_WARE_REQUIRED');end if;
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  if n!=1 then raise_application_error(-20882,'SHIPPING_CURRENT_USER_REQUIRED');end if;
  select count(*)into n from RUSERS where ID=p_actor
   and(RRL_HAS_WRIGHT(ID,p_permission)=1 or(p_permission='stock_posting_shipping'and RRL_HAS_WRIGHT(ID,'CLOSE_OTHOD_NAKLAD')=1))
   and(upper(trim(USER_GROUP))='GLOBAL_ADMIN'or WARE_ID=p_ware);
  if n=1 then return;end if;
  if RRL_ACCESS_API.allowed(p_actor,p_permission,'WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(p_ware))!=1
   then raise_application_error(-20882,'SHIPPING_CURRENT_WARE_FORBIDDEN');end if;
 end;
 procedure assert_shipment(p_identifier varchar2,p_actor varchar2)is w number;begin
  select WARE_ID into w from RRL_SBORKA_PALLETS where PALLET_UID=p_identifier;
  warehouse(w,p_actor,'stock_posting_shipping');
  for ct in(select ct.CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK ct join RRL_SBORKA_PALLETS sp on sp.ID=ct.LEGACY_SBORKA_PALLET_ID where sp.PALLET_UID=p_identifier)loop
   RRL_TRADE_CASE_ACCESS.assert_scope(ct.CASE_PICK_TASK_ID,p_actor,1);
  end loop;
  for o in(select distinct a.OWNER_ID from RRL_CUSTOMER_ORDER_FULFILLMENT f join RRL_WMS_RECEIPT_UNIT u on u.CURRENT_UID=f.PICKED_PALLET_UID
   join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY where f.PALLET_UID=p_identifier)loop RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,w,o.OWNER_ID,1);end loop;
 exception when no_data_found or too_many_rows then raise_application_error(-20882,'SHIPPING_ST_WARE_REQUIRED');end;
 procedure assert_hu(p_uid varchar2,p_actor varchar2)is cell_name varchar2(60);shipped varchar2(100);w number;wire clob;d json_object_t;a json_array_t;entry json_object_t;begin
  select HU_CURRENT_CELL,HU_SHIPPED_OPERATION into cell_name,shipped from RRL_PALLETS where UID_PALLET=p_uid;
  if shipped is null then
   select WARE_ID into w from RRL_CELLS where CELL=cell_name;
   warehouse(w,p_actor,'stock_posting_shipping');
   for o in(with links as(select CHILD_PALLET_UID,CHILD_CASE_TASK_ID from RRL_WMS_HU_LINK
    start with PARENT_UID=p_uid and ACTIVE_FLAG=1 connect by nocycle prior CHILD_PALLET_UID=PARENT_UID and ACTIVE_FLAG=1)
    select distinct a.OWNER_ID from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
    where u.CURRENT_UID=p_uid or u.CURRENT_UID in(select CHILD_PALLET_UID from links)
     or u.CURRENT_UID in(select LOT_UID from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID in(select CHILD_CASE_TASK_ID from links)))loop
    RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,w,o.OWNER_ID,1);
   end loop;
  else
   select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=shipped and COMMAND_TYPE='HU_SHIP'and STATE='APPLIED';
   d:=json_object_t.parse(wire).get_object('domain');
   if d.get_string('uid')is null or d.get_string('uid')!=p_uid then raise_application_error(-20886,'SHIPPING_ARCHIVE_IDENTITY_REQUIRED');end if;
   warehouse(d.get_object('snapshot').get_number('warehouse'),p_actor,'stock_posting_shipping');
   a:=d.get_array('shipments');
   for i in 0..a.get_size-1 loop entry:=treat(a.get(i)as json_object_t);
    assert_shipment(entry.get_object('request').get_object('source').get_string('pallet_identifier'),p_actor);
   end loop;
  end if;
 exception when no_data_found or too_many_rows then raise_application_error(-20882,'SHIPPING_HU_WARE_REQUIRED');end;
 procedure assert_trip(p_trip number,p_actor varchar2)is n number:=0;begin
  for x in(select WARE_ID from(
   select WARE_ID from RRL_SBORKA_PALLETS where TRANSTASK_ID=p_trip
   union select WARE_ID from RRL_TT_HU_LOAD_FACT where TT_ID=p_trip
   union select d.WARE_ID from RRL_TT_DOCK d join RRL_TRANSPORT_TASK t on t.DOCK=d.DOCK where t.ID=p_trip)
   fetch first 201 rows only)loop
   n:=n+1;if n>200 then raise_application_error(-20886,'DEPART_WAREHOUSE_BOUND_200');end if;
   warehouse(x.WARE_ID,p_actor,'transport_dispatch_close');
  end loop;
  if n=0 then raise_application_error(-20882,'DEPART_ACTUAL_WARE_REQUIRED');end if;
  for o in(select distinct a.OWNER_ID,lf.WARE_ID from RRL_TT_HU_LOAD_FACT lf,
   json_table(lf.COMPOSITION_JSON,'$.nodes[*]'columns(P_UID varchar2(200)path'$.uid'))x,
   RRL_WMS_RECEIPT_UNIT u,RRL_TRADE_STOCK_ATTR a where lf.TT_ID=p_trip and lf.STATUS in('LOADED','DEPARTED')
    and u.CURRENT_UID=x.P_UID and a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY)loop
   RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,o.WARE_ID,o.OWNER_ID,1);
  end loop;

 end;
 procedure assert_request(p_request clob,p_actor varchar2)is d json_object_t:=json_object_t.parse(p_request);k varchar2(80):=d.get_string('command_type');begin
  if k='HU_SHIP'then assert_hu(d.get_object('source').get_string('uid'),p_actor);
  elsif k='TRIP_DEPART'then assert_trip(d.get_object('source').get_number('task_id'),p_actor);end if;
 end;
end;

/
