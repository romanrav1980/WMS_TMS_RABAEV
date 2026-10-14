create or replace package RRL_STOCK_ST_ROW_CMD accessible by(package RRL_STOCK_POSTING_API)as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_ST_ROW_CMD as
 function describe_request(p_request clob,p_actor varchar2)return json_object_t is
  d json_object_t:=json_object_t.parse(p_request);src json_object_t:=d.get_object('source');
  m json_object_t:=d.get_object('metadata');j json_object_t;w number;keys json_key_list;
 begin
  keys:=src.get_keys;
  if keys.count!=3 or src.get_number('order_id')is null or src.get_number('row_id')is null or src.get_number('target_shipment_id')is null
   or d.get_array('lines').get_size!=0 or d.get_array('units').get_size!=0 then raise_application_error(-20881,'ST_LAYOUT_CANONICAL_SOURCE_REQUIRED');end if;
  keys:=m.get_keys;
  if keys.count!=2 or m.get_string('reason')is null or length(m.get_string('reason'))>500
   or m.get_string('expected_signature')is null or not regexp_like(m.get_string('expected_signature'),'^[A-F0-9]{64}$')then raise_application_error(-20881,'ST_LAYOUT_SIGNATURE_REASON_REQUIRED');end if;
  w:=RRL_ST_LAYOUT_READ.scope_order(src.get_number('order_id'),p_actor,'outgoing_pallet_edit');
  j:=json_object_t.parse(RRL_ST_LAYOUT_READ.snapshot(src.get_number('order_id'),src.get_number('row_id'),src.get_number('target_shipment_id'),p_actor));
  if j.get_string('signature')!=m.get_string('expected_signature')then raise_application_error(-20886,'ST_LAYOUT_CHANGED_REVIEW_AGAIN');end if;
  return j;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob)is
  d json_object_t:=json_object_t.parse(p_request);j json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t;x json_object_t;
 begin
  j:=describe_request(p_request,d.get_string('actor'));
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(j.get_number('order_id')));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(j.get_number('source_shipment_id')));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(j.get_number('target_shipment_id')));
  if nvl(j.get_number('trip_id'),0)>0 then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TRANSPORT_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(j.get_number('trip_id')));end if;
  a:=j.get_array('fulfillments');
  for i in 0..a.get_size-1 loop x:=treat(a.get(i)as json_object_t);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('id')));end loop;
  a:=j.get_array('before');
  for i in 0..a.get_size-1 loop x:=treat(a.get(i)as json_object_t);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SBORKA_PALLET_ROWS',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('id')));end loop;
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  p_domain:=j.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);j json_object_t;fresh json_object_t;plan clob;op varchar2(100):=d.get_string('operation_id');
  source_id number;target_id number;trip_id number;row_id number;result_id number;n number;a json_array_t;x json_object_t;row_value RRL_SBORKA_PALLET_ROWS%rowtype;
 begin
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;j:=json_object_t.parse(plan).get_object('domain');
  source_id:=j.get_number('source_shipment_id');target_id:=j.get_number('target_shipment_id');trip_id:=j.get_number('trip_id');row_id:=j.get_number('row_id');
  -- Actual row locks also serialize old transport callers that do not use Root advisory locks.
  if nvl(trip_id,0)>0 then select ID into n from RRL_TRANSPORT_TASK where ID=trip_id for update nowait;end if;
  for rec in(select ID from RRL_SBORKA_PALLETS where ID in(source_id,target_id)order by ID for update nowait)loop null;end loop;
  for rec in(select FULFILLMENT_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID in(source_id,target_id)order by FULFILLMENT_ID for update nowait)loop null;end loop;
  for rec in(select r.ID from RRL_SBORKA_PALLET_ROWS r join RRL_SBORKA_PALLETS s on s.PALLET_UID=r.PALLET_UID where s.ID in(source_id,target_id)order by r.ID for update of r.QUANTITY nowait)loop null;end loop;
  fresh:=describe_request(p_request,p_actor);
  if fresh.get_string('signature')!=j.get_string('signature')then raise_application_error(-20890,'CLOSURE_CHANGED: prepared row move');end if;
  result_id:=RRL_UPDATE_SBORKA_PALLET_ROWS2(j.get_string('target_pallet'),row_id);
  -- Compare every expected remaining row; this also proves exact quantity/pack/weight conservation.
  a:=j.get_array('after');
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i)as json_object_t);n:=x.get_number('id');
   select *into row_value from RRL_SBORKA_PALLET_ROWS where ID=n;
   if row_value.PALLET_UID!=x.get_string('pallet')or row_value.ARTICUL!=x.get_string('article')or row_value.EI!=x.get_string('unit')
    or RRL_STOCK_PLAN_HELPER.decimal_text(row_value.QUANTITY)!=x.get_string('quantity')
    or RRL_STOCK_PLAN_HELPER.decimal_text(row_value.ORDER_WEIGHT)!=x.get_string('weight')
    or RRL_STOCK_PLAN_HELPER.decimal_text(row_value.PACK_COUNT)!=x.get_string('packs')then raise_application_error(-20886,'ST_LAYOUT_WRITER_RESULT_CONFLICT');end if;
  end loop;
  select count(*)into n from RRL_SBORKA_PALLET_ROWS r join RRL_SBORKA_PALLETS s on s.PALLET_UID=r.PALLET_UID where s.ID in(source_id,target_id);
  if n!=a.get_size then raise_application_error(-20886,'ST_LAYOUT_ROW_SET_CHANGED');end if;
  j.put('operation_id',op);j.put('status','APPLIED');j.put('result_row_id',result_id);j.put('reason',d.get_object('metadata').get_string('reason'));
  j.put('physical_binding_changed',false);j.put('trip_assignment_changed',false);p_result:=j.to_clob;
 end;
end;
/

