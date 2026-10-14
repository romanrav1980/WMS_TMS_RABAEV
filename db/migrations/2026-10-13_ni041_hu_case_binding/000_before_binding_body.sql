create or replace package body RRL_STOCK_CASE_BIND_MOVE as

 function source_snapshot(p_case RRL_CASE_PICK_TASK%rowtype)return json_object_t is

  f RRL_CUSTOMER_ORDER_FULFILLMENT%rowtype;s RRL_SBORKA_PALLETS%rowtype;n number;j json_object_t:=json_object_t();

 begin

  if p_case.LEGACY_SBORKA_PALLET_ID is null then return null;end if;

  select *into s from RRL_SBORKA_PALLETS where ID=p_case.LEGACY_SBORKA_PALLET_ID;

  select count(*)into n from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=s.ID;

  if n!=1 then raise_application_error(-20886,'CASE_MOVE_SINGLE_BOUND_FULFILLMENT_REQUIRED');end if;

  select *into f from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=s.ID;

  if s.WARE_ID is null or s.WARE_ID!=p_case.WARE_ID or nvl(s.CONDITION,0)=2 or s.RETURN_SUPPLIER_ID is not null

   or f.STATUS!='PICKED'or f.PICKED_CASE_TASK_ID is null or f.PICKED_CASE_TASK_ID!=p_case.CASE_PICK_TASK_ID

   or f.CUSTOMER_ORDER_ID!=p_case.CUSTOMER_ORDER_ID or f.PALLET_UID!=s.PALLET_UID

   or f.PICKED_CONTENT_VERSION is null or f.PICKED_CONTENT_VERSION!=p_case.CONTENT_VERSION

   then raise_application_error(-20886,'CASE_MOVE_CURRENT_BOUND_FULFILLMENT_REQUIRED');end if;

  select count(*)into n from RRL_TT_HU_LOAD_ST ls join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=ls.LOAD_OPERATION_ID

   where ls.SBORKA_PALLET_ID=s.ID and ls.ACTIVE_FLAG=1 and l.STATUS in('LOADED','DEPARTED');

  if n>0 then raise_application_error(-20886,'CASE_MOVE_BOUND_LOAD_ALREADY_ACTIVE');end if;

  j.put('st_member_id',s.ID);j.put('st_number',s.ST_NUMBER);j.put('shipment_identifier',s.PALLET_UID);

  j.put('warehouse',s.WARE_ID);j.put('trip',s.TRANSTASK_ID);j.put('st_condition',s.CONDITION);

  j.put('fulfillment_id',f.FULFILLMENT_ID);j.put('customer_order_id',f.CUSTOMER_ORDER_ID);j.put('case_task_id',f.PICKED_CASE_TASK_ID);

  j.put('content_version',f.PICKED_CONTENT_VERSION);j.put('status',f.STATUS);j.put('fact_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(f.FACT_QTY));j.put('fact_uom',f.FACT_UOM);

  if f.FACT_COMPOSITION_JSON is null then raise_application_error(-20886,'CASE_MOVE_ORIGINAL_COMPOSITION_REQUIRED');end if;

  j.put('composition_hash',lower(rawtohex(sys.dbms_crypto.hash(f.FACT_COMPOSITION_JSON,sys.dbms_crypto.hash_sh256))));

  return j;

 exception when no_data_found then raise_application_error(-20886,'CASE_MOVE_BOUND_SOURCE_NOT_FOUND');

 end;

 procedure plan_move(p_case RRL_CASE_PICK_TASK%rowtype,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t)is j json_object_t;

 begin

  j:=source_snapshot(p_case);if j is null then return;end if;

  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(j.get_number('st_member_id')));

  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(j.get_number('fulfillment_id')));

  p_domain.put('shipment_binding',j);

 end;

 procedure validate_move(p_case RRL_CASE_PICK_TASK%rowtype,p_frozen json_object_t)is j json_object_t;

 begin

  j:=source_snapshot(p_case);

  if j is null and p_frozen is null then return;end if;

  if j is null or p_frozen is null or dbms_lob.compare(j.to_clob,p_frozen.to_clob)!=0

   then raise_application_error(-20890,'CLOSURE_CHANGED: CASE shipment binding');end if;

 end;

 procedure finish_move(p_case RRL_CASE_PICK_TASK%rowtype,p_frozen json_object_t,p_version number,p_actor varchar2)is ff_id number;

 begin

  if p_case.LEGACY_SBORKA_PALLET_ID is null then

   if p_frozen is not null then raise_application_error(-20890,'CLOSURE_CHANGED: CASE shipment removed');end if;return;

  end if;

  if p_frozen is null or p_version!=p_case.CONTENT_VERSION+1 or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is null

   or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)

   then raise_application_error(-20886,'CASE_MOVE_ROOT_BINDING_VERSION_REQUIRED');end if;

  ff_id:=p_frozen.get_number('fulfillment_id');

  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(ff_id)));

  update RRL_CUSTOMER_ORDER_FULFILLMENT set PICKED_CONTENT_VERSION=p_version,UPDATED_AT=sysdate,UPDATED_BY=p_actor

   where FULFILLMENT_ID=ff_id and STATUS='PICKED'and PICKED_CASE_TASK_ID=p_case.CASE_PICK_TASK_ID and PICKED_CONTENT_VERSION=p_case.CONTENT_VERSION;

  if sql%rowcount!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: CASE fulfillment after move');end if;

 end;

end;


/
