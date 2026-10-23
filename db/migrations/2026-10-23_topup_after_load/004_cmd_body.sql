create or replace package body RRL_TRADE_TOPUP_CMD as
 procedure fail(p_code varchar2)is begin raise_application_error(-20911,p_code);end;
 function trip_key(p RRL_TRADE_TOPUP_PROPOSAL%rowtype)return varchar2 is begin return 'TRADE.TOPUP.TRIP:'||p.WARE_ID||':'||p.TRIP_ID;end;
 function need_key(p RRL_TRADE_TOPUP_PROPOSAL%rowtype)return varchar2 is begin return 'TRADE.TOPUP.NEED:'||p.WARE_ID||':'||p.NEED_ID;end;
 function sku_key(p RRL_TRADE_TOPUP_PROPOSAL%rowtype)return varchar2 is begin return 'TRADE.TOPUP.STOCK:'||p.WARE_ID||':'||p.ARTICLE;end;

 procedure common_plan(p RRL_TRADE_TOPUP_PROPOSAL%rowtype,p_operation varchar2,f in out nocopy json_array_t,r in out nocopy json_array_t)is
 begin
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.fence(f,'SKU',p.ARTICLE);
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  -- Capacity of one trip, coverage of one demand and stock of one article are each decided by one confirmation at a time.
  RRL_STOCK_PLAN_HELPER.anchor(r,20,'UNIQUE',trip_key(p));RRL_STOCK_PLAN_HELPER.anchor(r,20,'UNIQUE',need_key(p));
  RRL_STOCK_PLAN_HELPER.anchor(r,20,'UNIQUE',sku_key(p));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TRADE_TOPUP_PROPOSAL',RRL_STOCK_PLAN_HELPER.decimal_text(p.PROPOSAL_ID));
  -- C-0161: the same native transport row as LOAD and DEPART, so a confirmation never lands after a departure or between a load
  -- fact and its basis check.
  for t in(select NATIVE_TASK_ID from RRL_TRADE_TRIP_LINK where WARE_ID=p.WARE_ID and TRIP_ID=p.TRIP_ID)loop
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TRANSPORT_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(t.NATIVE_TASK_ID));
  end loop;
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 end;

 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob)is
  d json_object_t:=json_object_t.parse(p_request);s json_object_t:=d.get_object('source');kind varchar2(80):=d.get_string('command_type');
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();v json_object_t:=json_object_t();sources json_array_t:=json_array_t();
  plan json_array_t;x json_object_t;item json_object_t;p RRL_TRADE_TOPUP_PROPOSAL%rowtype;rid number;total number:=0;needed number;
 begin
  begin declare
   json_arg_1 number:=s.get_number('proposal_id');
  begin
   select*into p from RRL_TRADE_TOPUP_PROPOSAL where PROPOSAL_ID=json_arg_1;
  end;
  exception when no_data_found then fail('TRADE_TOPUP_PROPOSAL_NOT_FOUND');end;
  if s.get_number('warehouse')is null or s.get_number('warehouse')<>p.WARE_ID or nvl(s.get_string('trip_id'),'-')<>p.TRIP_ID then
   fail('TRADE_TOPUP_PROPOSAL_NOT_FOUND');end if;
  common_plan(p,p_operation,f,r);
  if kind='TRADE_TOPUP_CONFIRM'then
   needed:=p.APPROVED_BOXES*p.UNITS_PER_BOX;
   if needed<1 then fail('TRADE_TOPUP_QUANTITY_REQUIRED');end if;
   plan:=json_array_t.parse(RRL_TRADE_TOPUP_READ.candidates(p.WARE_ID,p.ARTICLE,p.SKU_ID,p.SOURCE_OWNER_ID,p.MRC,p.MIN_EXPIRY,needed,p.UNITS_PER_BOX));
   for i in 0..plan.get_size-1 loop
    x:=treat(plan.get(i)as json_object_t);
    select RRL_STOCK_RESERVATION_SQ.nextval into rid from dual;
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(rid));
    RRL_STOCK_PLAN_HELPER.stock_closure(f,r,x.get_string('uid'),p.ARTICLE,x.get_string('cell'),null);
    item:=json_object_t();item.put('reservation_id',rid);item.put('uid',x.get_string('uid'));item.put('cell',x.get_string('cell'));
    item.put('units',x.get_array('units'));item.put('quantity',x.get_array('units').get_size);sources.append(item);
    total:=total+x.get_array('units').get_size;
   end loop;
   -- No partial physical hold: the dispatcher sees the shortage and adjusts the quantity instead.
   if total<>needed then fail('TRADE_TOPUP_SENDER_STOCK_INSUFFICIENT');end if;
  elsif kind='TRADE_TOPUP_RELEASE'then
   -- Read the completed cancellation under the same native row/stock locks.
   for a in(select h.RESERVATION_ID,h.UID_PALLET,h.CELL,ad.PICK_WAVE_ID,ad.PICK_TASK_ID,t.CASE_PICK_TASK_ID
    from RRL_TRADE_TOPUP_HOLD h left join RRL_TRADE_TOPUP_ADOPTION ad on ad.RESERVATION_ID=h.RESERVATION_ID
    left join RRL_PICK_TASK t on t.PICK_TASK_ID=ad.PICK_TASK_ID
    where h.PROPOSAL_ID=p.PROPOSAL_ID and h.STATUS='ADOPTED' order by h.RESERVATION_ID)loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(a.RESERVATION_ID));
    RRL_STOCK_PLAN_HELPER.stock_closure(f,r,a.UID_PALLET,p.ARTICLE,a.CELL,null);
    if a.PICK_WAVE_ID is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(a.PICK_WAVE_ID));end if;
    if a.PICK_TASK_ID is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(a.PICK_TASK_ID));end if;
    if a.CASE_PICK_TASK_ID is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(a.CASE_PICK_TASK_ID));end if;
   end loop;
   for h in(select RESERVATION_ID,UID_PALLET,CELL,BASE_QTY from RRL_TRADE_TOPUP_HOLD where PROPOSAL_ID=p.PROPOSAL_ID and STATUS='ACTIVE'order by RESERVATION_ID)loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(h.RESERVATION_ID));
    RRL_STOCK_PLAN_HELPER.stock_closure(f,r,h.UID_PALLET,p.ARTICLE,h.CELL,null);
    item:=json_object_t();item.put('reservation_id',h.RESERVATION_ID);item.put('quantity',h.BASE_QTY);sources.append(item);
   end loop;
  else fail('TRADE_TOPUP_COMMAND_UNKNOWN');end if;
  v.put('proposal_id',p.PROPOSAL_ID);v.put('warehouse',p.WARE_ID);v.put('sources',sources);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;

 function domain_of(p_operation varchar2)return json_object_t is wire clob;
 begin
  select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=p_operation;
  return json_object_t.parse(wire).get_object('domain');
 end;

 procedure lock_scope(p in out nocopy RRL_TRADE_TOPUP_PROPOSAL%rowtype,p_expected number)is n number;
 begin
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('UNIQUE',trip_key(p)));
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('UNIQUE',need_key(p)));
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('UNIQUE',sku_key(p)));
  -- Same serialization as external document intake: a newer trip/order/demand version cannot slip in meanwhile.
  select ENABLED into n from RRL_TRADE_SITE where WARE_ID=p.WARE_ID for update;
  if n<>1 then fail('TRADE_SITE_DISABLED');end if;
  select*into p from RRL_TRADE_TOPUP_PROPOSAL where PROPOSAL_ID=p.PROPOSAL_ID for update;
  if p_expected is null or p.VERSION_NO<>p_expected then fail('VERSION_CONFLICT');end if;
 end;

 procedure require(p_actor varchar2,p_permission varchar2,p_ware number)is n number;
 begin
  select RRL_ACCESS_API.allowed(p_actor,p_permission,'WAREHOUSE',to_char(p_ware))into n from dual;
  if n<>1 then raise_application_error(-20882,'TRADE_TOPUP_ACCESS_DENIED');end if;
 end;

 function uom_version(p_article varchar2)return number is v number;
 begin
  select max(POLICY_VERSION)into v from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_article and INPUT_UOM='EA'and BASE_UOM='EA'and NUMERATOR=1 and DENOMINATOR=1;
  if v is null then raise_application_error(-20868,'BASE_IDENTITY_POLICY_REQUIRED');end if;
  return v;
 end;

 procedure assert_access(p_request clob,p_actor varchar2)is
  d json_object_t:=json_object_t.parse(p_request);s json_object_t:=d.get_object('source');m json_object_t:=d.get_object('metadata');
  p RRL_TRADE_TOPUP_PROPOSAL%rowtype;
 begin
  begin declare
   json_arg_1 number:=s.get_number('proposal_id');
  begin
   select*into p from RRL_TRADE_TOPUP_PROPOSAL where PROPOSAL_ID=json_arg_1;
  end;
  exception when no_data_found then fail('TRADE_TOPUP_PROPOSAL_NOT_FOUND');end;
  if s.get_number('warehouse')is null or s.get_number('warehouse')<>p.WARE_ID or nvl(s.get_string('trip_id'),'-')<>p.TRIP_ID then
   fail('TRADE_TOPUP_PROPOSAL_NOT_FOUND');end if;
  if d.get_string('command_type')='TRADE_TOPUP_RELEASE'and m.get_string('reason')='SAP_REJECTED'then
   require(p_actor,'tradecase_topup_result',p.WARE_ID);
  else require(p_actor,'tradecase_topup_approve',p.WARE_ID);end if;
  RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,p.WARE_ID,p.SOURCE_OWNER_ID,1);
 end;

 procedure confirm(p in out nocopy RRL_TRADE_TOPUP_PROPOSAL%rowtype,v json_object_t,p_op varchar2,p_actor varchar2)is
  sources json_array_t:=v.get_array('sources');x json_object_t;keys clob;qty number;n number;needed number:=p.APPROVED_BOXES*p.UNITS_PER_BOX;
  ver number:=uom_version(p.ARTICLE);details json_object_t;body json_object_t;outbox number;free_units number;
 begin
  if p.STATUS not in('PROPOSED','ADJUSTED')then fail('TRADE_TOPUP_STATE_CONFLICT');end if;
  -- C-0161: loaded main cargo is in the capacity basis checked next; only a departed trip refuses here (under the transport row lock).
  if RRL_TRADE_TOPUP_READ.departed(p.WARE_ID,p.TRIP_ID)=1 then fail('TOPUP_TRIP_DEPARTED');end if;
  -- C-0161: with main cargo already loaded the planned departure must still be ahead now, at confirmation (not only at calculation/save).
  -- The time is the accepted TRIP's planned_departure_at, ISO-8601 with offset as validated on receipt; unreadable = refused.
  if RRL_TRADE_TOPUP_READ.loading_started(p.WARE_ID,p.TRIP_ID)=1 then
   declare dep timestamp with time zone;begin
    select json_value(BODY_JSON,'$.planned_departure_at'returning timestamp with time zone error on error)into dep
     from RRL_TRADE_DOCUMENT where WARE_ID=p.WARE_ID and ENTITY_TYPE='TRIP'and EXTERNAL_ID=p.TRIP_ID and STATUS='ACCEPTED';
    if dep is null or dep<=systimestamp then fail('TOPUP_DEPARTURE_TIME_PASSED');end if;
   exception when no_data_found then fail('TRADE_TOPUP_TRIP_REQUIRED');
    when others then if sqlcode=-20911 then raise;end if;fail('TOPUP_DEPARTURE_TIME_INVALID');
   end;
  end if;
  -- Someone else confirmed on this trip or the trip/vehicle/orders changed: recalculate, never squeeze in.
  if RRL_TRADE_TOPUP_READ.trip_basis(p.WARE_ID,p.TRIP_ID,p.PROPOSAL_ID)<>p.CAPACITY_BASIS then fail('TRADE_TOPUP_CAPACITY_BASIS_CHANGED');end if;
  select count(*)into n from RRL_TRADE_DOCUMENT where WARE_ID=p.WARE_ID and ENTITY_TYPE='NEED'and EXTERNAL_ID=p.NEED_ID and VERSION_NO=p.NEED_VERSION and STATUS='ACCEPTED';
  if n<>1 then fail('TRADE_TOPUP_NEED_VERSION_CHANGED');end if;
  if systimestamp>p.NEED_SNAPSHOT_AT+numtodsinterval(p.MAX_AGE_MINUTES,'MINUTE')then fail('TRADE_TOPUP_NEED_EXPIRED');end if;
  if RRL_TRADE_TOPUP_READ.need_confirmed_boxes(p.WARE_ID,p.NEED_ID,p.PROPOSAL_ID)+p.APPROVED_BOXES>p.NEED_BOXES then fail('TRADE_TOPUP_NEED_ALREADY_COVERED');end if;
  -- Main orders keep their unallocated quantity: the top-up uses only what remains above it.
  free_units:=RRL_TRADE_TOPUP_READ.eligible_units(p.WARE_ID,p.ARTICLE,p.SKU_ID,p.SOURCE_OWNER_ID,p.MRC,p.MIN_EXPIRY,p.UNITS_PER_BOX);
  if free_units-RRL_TRADE_TOPUP_READ.protected_units(p.WARE_ID,p.SKU_ID,p.SOURCE_OWNER_ID,p.MRC)<needed then fail('TRADE_TOPUP_MAIN_ORDER_STOCK_PROTECTED');end if;
  for i in 0..sources.get_size-1 loop
   x:=treat(sources.get(i)as json_object_t);keys:=x.get_array('units').to_clob;qty:=x.get_number('quantity');
   declare
    json_arg_1 varchar2(32767):=x.get_string('uid');
    json_arg_2 varchar2(32767):=x.get_string('cell');
   begin
    select count(*)into n from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
    where u.CURRENT_UID=json_arg_1 and u.CURRENT_CELL=json_arg_2 and u.STOCK_STATUS='AVAILABLE'and u.HARD_RESERVATION_ID is null
     and a.SKU_ID=p.SKU_ID and a.OWNER_ID=p.SOURCE_OWNER_ID and a.MRC=p.MRC and a.MARK_STATE='VALID'and a.EXPIRY_DATE>=p.MIN_EXPIRY
     and not exists(select 1 from RRL_TRADE_BUYOUT_UNIT bu where bu.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY and bu.HOLD_ACTIVE=1)
     and u.PHYSICAL_UNIT_KEY in(select K from json_table(keys,'$[*]'columns(K varchar2(64)path'$')));
   end;
   if n<>qty then fail('TRADE_TOPUP_STOCK_CHANGED');end if;
   RRL_STOCK_ELIGIBILITY.assert_source(x.get_string('uid'),x.get_string('cell'),p.WARE_ID,qty,null,null,'REPLENISH',null,p.ARTICLE);
   details:=json_object_t();details.put('reservation_scope','QTY');details.put('priority',100);
   RRL_STOCK_RESERVE_CORE.create_hard(x.get_number('reservation_id'),x.get_string('uid'),x.get_string('cell'),qty,'EA',ver,
    'TRADE_TOPUP',p.PROPOSAL_ID,null,'SHIPMENT',p_actor,details.to_clob);
   RRL_STOCK_UNIT_CORE.reserve_units(x.get_string('uid'),x.get_string('cell'),x.get_number('reservation_id'),qty,keys);
   declare
    json_arg_1 number:=x.get_number('reservation_id');
    json_arg_2 varchar2(32767):=x.get_string('uid');
    json_arg_3 varchar2(32767):=x.get_string('cell');
   begin
    insert into RRL_TRADE_TOPUP_HOLD(RESERVATION_ID,PROPOSAL_ID,UID_PALLET,CELL,BASE_QTY,STATUS,CREATED_OPERATION_ID)
    values(json_arg_1,p.PROPOSAL_ID,json_arg_2,json_arg_3,qty,'ACTIVE',p_op);
   end;
  end loop;
  update RRL_TRADE_TOPUP_PROPOSAL set STATUS='CONFIRMED',VERSION_NO=VERSION_NO+1,CONFIRM_OPERATION_ID=p_op,UPDATED_BY=p_actor,UPDATED_AT=systimestamp
   where PROPOSAL_ID=p.PROPOSAL_ID;
  body:=json_object_t.parse(RRL_TRADE_TOPUP_READ.card(p.PROPOSAL_ID));body.put('business_operation_id','TC:TOPUP:'||p.PROPOSAL_ID);
  -- One request per proposal (idempotency key); delivery and SAP order creation stay unconfirmed until SAP answers.
  outbox:=RRL_TRACEABILITY_API.enqueue_event('TRADECASE_TOPUP_REQUESTED','TRADE_TOPUP',to_char(p.PROPOSAL_ID),'TC:TOPUP:REQUEST:'||p.PROPOSAL_ID,
   body.to_clob,'TRADECASE_BUS',p_op);
  update RRL_TRADE_TOPUP_PROPOSAL set REQUEST_OUTBOX_ID=outbox where PROPOSAL_ID=p.PROPOSAL_ID;
 end;

 procedure release(p in out nocopy RRL_TRADE_TOPUP_PROPOSAL%rowtype,v json_object_t,m json_object_t,p_op varchar2,p_actor varchar2)is
  sources json_array_t:=v.get_array('sources');x json_object_t;h RRL_TRADE_TOPUP_HOLD%rowtype;reason_value varchar2(20):=m.get_string('reason');
  sap json_object_t:=json_object_t();ver number:=uom_version(p.ARTICLE);n number;outbox number;body json_object_t;
 begin
  if reason_value='SAP_REJECTED'then
   if p.STATUS<>'CONFIRMED'then fail('TRADE_TOPUP_STATE_CONFLICT');end if;
   sap:=m.get_object('sap');
   if sap is null or sap.get_string('event_id')is null or sap.get_string('reason')is null then fail('TRADE_TOPUP_SAP_REASON_REQUIRED');end if;
   declare
    json_arg_1 varchar2(32767):=sap.get_string('source_id');
   begin
    select count(*)into n from RRL_TRADE_SITE where WARE_ID=p.WARE_ID and SOURCE_ID=json_arg_1;
   end;
   if n<>1 then fail('TRADE_TOPUP_SOURCE_MISMATCH');end if;
   declare
    json_arg_1 varchar2(32767):=sap.get_string('source_id');
    json_arg_2 varchar2(32767):=sap.get_string('event_id');
   begin
    select count(*)into n from RRL_TRADE_TOPUP_EVENT where WARE_ID=p.WARE_ID and SOURCE_ID=json_arg_1 and EVENT_ID=json_arg_2;
   end;
   if n>0 then fail('TRADE_TOPUP_EVENT_ALREADY_RECORDED');end if;
  elsif reason_value='CANCELLED'then
   if p.STATUS not in('CONFIRMED','SAP_ACCEPTED')then fail('TRADE_TOPUP_STATE_CONFLICT');end if;
  else fail('TRADE_TOPUP_RELEASE_REASON_REQUIRED');end if;
  -- A native cancellation before any pick can be reconciled, never a live/consumed wave.
  select count(*)into n from RRL_TRADE_TOPUP_HOLD h where h.PROPOSAL_ID=p.PROPOSAL_ID and h.STATUS='ADOPTED'
   and not exists(select 1 from RRL_TRADE_TOPUP_ADOPTION a
    join RRL_STOCK_RESERVATION sr on sr.RESERVATION_ID=a.RESERVATION_ID
    join RRL_PICK_WAVE w on w.PICK_WAVE_ID=a.PICK_WAVE_ID
    join RRL_PICK_TASK t on t.PICK_TASK_ID=a.PICK_TASK_ID
    where a.RESERVATION_ID=h.RESERVATION_ID and a.PROPOSAL_ID=h.PROPOSAL_ID and a.BASE_QTY=h.BASE_QTY
     and sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.SOURCE_DOC_ID=a.PICK_WAVE_ID and sr.SOURCE_LINE_ID=a.PICK_TASK_ID
     and sr.PICK_PLAN_LINE_ID=a.PICK_PLAN_LINE_ID and sr.UID_PALLET=h.UID_PALLET and sr.CELL=h.CELL
     and sr.STATUS='RELEASED' and sr.BASE_QTY=0 and w.WARE_ID=p.WARE_ID and w.STATUS='CANCELLED'
     and t.STATUS='CANCELLED' and nvl(t.FACT_QTY,0)=0
     and not exists(select 1 from RRL_CASE_CARRIER_LOT lot where lot.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID)
     and not exists(select 1 from RRL_WMS_RECEIPT_UNIT u where u.HARD_RESERVATION_ID=h.RESERVATION_ID)
     and exists(select 1 from RRL_STOCK_OPERATION completed
      join json_table(completed.RESOLVED_PLAN_JSON,'$.domain.reservations[*]'columns(RID number path '$.id')) released on released.RID=h.RESERVATION_ID
      where completed.STATE='APPLIED' and completed.COMMAND_TYPE='WAVE_CANCEL'
       and json_value(completed.RESOLVED_PLAN_JSON,'$.domain.document_type')='PICK_WAVE'
       and json_value(completed.RESOLVED_PLAN_JSON,'$.domain.document_id' returning number)=a.PICK_WAVE_ID));
  if n>0 then fail('TRADE_TOPUP_ADOPTED_RETURN_REQUIRED');end if;
  -- Reservation and units were already released by WAVE_CANCEL. Preserve adoption history; do not release again.
  update RRL_TRADE_TOPUP_HOLD set STATUS='RELEASED',RELEASED_OPERATION_ID=p_op where PROPOSAL_ID=p.PROPOSAL_ID and STATUS='ADOPTED';
  select count(*)into n from RRL_TRADE_TOPUP_HOLD where PROPOSAL_ID=p.PROPOSAL_ID and STATUS='ACTIVE';
  if n<>sources.get_size then fail('TRADE_TOPUP_HOLDS_CHANGED');end if;
  for i in 0..sources.get_size-1 loop
   x:=treat(sources.get(i)as json_object_t);
   declare
    json_arg_1 number:=x.get_number('reservation_id');
   begin
    select*into h from RRL_TRADE_TOPUP_HOLD where RESERVATION_ID=json_arg_1 and PROPOSAL_ID=p.PROPOSAL_ID and STATUS='ACTIVE'for update;
   end;
   RRL_STOCK_UNIT_CORE.release_units(h.RESERVATION_ID,h.BASE_QTY,null,0);
   RRL_STOCK_RESERVE_CORE.release_hard(h.RESERVATION_ID,h.BASE_QTY,ver,'TRADE_TOPUP',p.PROPOSAL_ID,p_actor);
   update RRL_TRADE_TOPUP_HOLD set STATUS='RELEASED',RELEASED_OPERATION_ID=p_op where RESERVATION_ID=h.RESERVATION_ID;
  end loop;
  declare
   json_arg_1 varchar2(32767):=sap.get_string('reason');
  begin
   update RRL_TRADE_TOPUP_PROPOSAL set STATUS=case when reason_value='SAP_REJECTED'then'SAP_REJECTED'else'CANCELLED'end,
   SAP_REASON=case when reason_value='SAP_REJECTED'then substr(json_arg_1,1,2000)else SAP_REASON end,
   VERSION_NO=VERSION_NO+1,UPDATED_BY=p_actor,UPDATED_AT=systimestamp where PROPOSAL_ID=p.PROPOSAL_ID;
  end;
  if reason_value='SAP_REJECTED'then
   declare
    json_arg_1 varchar2(32767):=sap.get_string('source_id');
    json_arg_2 varchar2(32767):=sap.get_string('event_id');
    json_arg_3 varchar2(32767):=sap.get_string('payload_hash');
    json_arg_4 clob:=sap.to_clob;
   begin
    insert into RRL_TRADE_TOPUP_EVENT(WARE_ID,SOURCE_ID,EVENT_ID,PROPOSAL_ID,PAYLOAD_HASH,BODY_JSON,RESULT_JSON)
    values(p.WARE_ID,json_arg_1,json_arg_2,p.PROPOSAL_ID,nvl(json_arg_3,'-'),json_arg_4,
     RRL_TRADE_TOPUP_READ.card(p.PROPOSAL_ID));
   end;
  elsif p.REQUEST_OUTBOX_ID is not null then
   -- SAP already got the request: it must also learn about the cancellation (one event per proposal).
   body:=json_object_t.parse(RRL_TRADE_TOPUP_READ.card(p.PROPOSAL_ID));
   outbox:=RRL_TRACEABILITY_API.enqueue_event('TRADECASE_TOPUP_CANCELLED','TRADE_TOPUP',to_char(p.PROPOSAL_ID),'TC:TOPUP:CANCEL:'||p.PROPOSAL_ID,
    body.to_clob,'TRADECASE_BUS',p_op);
  end if;
 end;

 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');kind varchar2(80):=d.get_string('command_type');
  op varchar2(100):=d.get_string('operation_id');v json_object_t:=domain_of(d.get_string('operation_id'));p RRL_TRADE_TOPUP_PROPOSAL%rowtype;j json_object_t;
  action varchar2(20);
 begin
  declare
   json_arg_1 number:=v.get_number('proposal_id');
  begin
   select*into p from RRL_TRADE_TOPUP_PROPOSAL where PROPOSAL_ID=json_arg_1;
  end;
  lock_scope(p,m.get_number('expected_version'));
  if kind='TRADE_TOPUP_RELEASE'and m.get_string('reason')='SAP_REJECTED'then require(p_actor,'tradecase_topup_result',p.WARE_ID);
  else require(p_actor,'tradecase_topup_approve',p.WARE_ID);end if;
  RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,p.WARE_ID,p.SOURCE_OWNER_ID,1);
  if kind='TRADE_TOPUP_CONFIRM'then confirm(p,v,op,p_actor);action:='CONFIRM';
  else release(p,v,m,op,p_actor);action:=case when m.get_string('reason')='SAP_REJECTED'then'SAP_REJECT'else'RELEASE'end;end if;
  j:=json_object_t.parse(RRL_TRADE_TOPUP_READ.card(p.PROPOSAL_ID));j.put('operation_id',op);j.put('action',action);
  j.put('external_delivery','PENDING');j.put('external_business','NOT_CONFIRMED');p_result:=j.to_clob;
  insert into RRL_TRADE_TOPUP_DECISION(OPERATION_ID,WARE_ID,PROPOSAL_ID,ACTION,BOXES,REQUEST_HASH,ACTOR,RESULT_JSON)
   values(op,p.WARE_ID,p.PROPOSAL_ID,action,p.APPROVED_BOXES,lower(rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256))),p_actor,p_result);
 end;
end;
/
