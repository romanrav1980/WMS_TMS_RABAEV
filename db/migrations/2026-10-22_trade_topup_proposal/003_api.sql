create or replace package RRL_TRADE_TOPUP_API authid definer as
 -- Non-stock decisions only. Confirmation and release of physical holds are StockPosting commands (RRL_TRADE_TOPUP_CMD).
 procedure save(p_request clob,p_actor varchar2,p_result out clob);
 procedure load_saved(p_ware number,p_trip varchar2,p_operation varchar2,p_request_hash varchar2,p_actor varchar2,p_result out clob);
 procedure decide(p_request clob,p_actor varchar2,p_result out clob);
 procedure sap_accept(p_request clob,p_actor varchar2,p_result out clob);
 function list_trip(p_ware number,p_trip varchar2,p_actor varchar2)return clob;
end;
/
create or replace package body RRL_TRADE_TOPUP_API as
 procedure fail(p_code varchar2)is begin raise_application_error(-20911,p_code);end;
 function sha(p_text clob)return varchar2 is
 begin return lower(rawtohex(sys.dbms_crypto.hash(p_text,sys.dbms_crypto.hash_sh256)));end;

 -- A proposal is addressed through its own warehouse and trip; another scope does not reveal or change it.
 procedure same_scope(p RRL_TRADE_TOPUP_PROPOSAL%rowtype,d json_object_t)is
 begin
  if d.get_number('warehouse_id')is null or d.get_number('warehouse_id')<>p.WARE_ID or nvl(d.get_string('trip_id'),'-')<>p.TRIP_ID then
   fail('TRADE_TOPUP_PROPOSAL_NOT_FOUND');end if;
 end;

 procedure lock_site(p_ware number)is n number;
 begin
  lock table RRL_ACCESS_REV in share mode wait 5;
  select ENABLED into n from RRL_TRADE_SITE where WARE_ID=p_ware for update;
  if n<>1 then fail('TRADE_SITE_DISABLED');end if;
 exception when no_data_found then fail('TRADE_SITE_REQUIRED');
 end;

 procedure require(p_actor varchar2,p_permission varchar2,p_ware number)is n number;
 begin
  select RRL_ACCESS_API.allowed(p_actor,p_permission,'WAREHOUSE',to_char(p_ware))into n from dual;
  if n<>1 then raise_application_error(-20882,'TRADE_TOPUP_ACCESS_DENIED');end if;
 end;

 -- Exact replay returns the stored result; a different body under the same operation is a conflict.
 function replay(p_operation varchar2,p_hash varchar2,p_ware number,p_result out clob)return boolean is d RRL_TRADE_TOPUP_DECISION%rowtype;j json_object_t;
 begin
  select*into d from RRL_TRADE_TOPUP_DECISION where OPERATION_ID=p_operation;
  if d.REQUEST_HASH<>p_hash or d.WARE_ID<>p_ware then fail('TRADE_TOPUP_OPERATION_CONFLICT');end if;
  j:=json_object_t.parse(d.RESULT_JSON);j.put('replayed',true);p_result:=j.to_clob;return true;
 exception when no_data_found then return false;
 end;

 procedure journal(p_operation varchar2,p_ware number,p_id number,p_action varchar2,p_boxes number,p_hash varchar2,p_actor varchar2,p_result clob)is
 begin
  insert into RRL_TRADE_TOPUP_DECISION(OPERATION_ID,WARE_ID,PROPOSAL_ID,ACTION,BOXES,REQUEST_HASH,ACTOR,RESULT_JSON)
   values(p_operation,p_ware,p_id,p_action,p_boxes,p_hash,p_actor,p_result);
 end;

 procedure load_saved(p_ware number,p_trip varchar2,p_operation varchar2,p_request_hash varchar2,p_actor varchar2,p_result out clob)is
  d RRL_TRADE_TOPUP_DECISION%rowtype;j json_object_t;a json_array_t;x json_object_t;p RRL_TRADE_TOPUP_PROPOSAL%rowtype;
 begin
  p_result:=null;lock_site(p_ware);require(p_actor,'tradecase_topup_approve',p_ware);
  begin select*into d from RRL_TRADE_TOPUP_DECISION where OPERATION_ID=p_operation;
  exception when no_data_found then return;end;
  if d.WARE_ID<>p_ware or d.ACTION<>'SAVE'or d.REQUEST_HASH<>p_request_hash then fail('TRADE_TOPUP_OPERATION_CONFLICT');end if;
  j:=json_object_t.parse(d.RESULT_JSON);
  if nvl(j.get_string('trip_id'),'-')<>p_trip then fail('TRADE_TOPUP_OPERATION_CONFLICT');end if;
  a:=j.get_array('proposals');
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i)as json_object_t);
   declare
    json_arg_1 number:=x.get_number('proposal_id');
   begin
    select*into p from RRL_TRADE_TOPUP_PROPOSAL where PROPOSAL_ID=json_arg_1;
   end;
   RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,p_ware,p.SOURCE_OWNER_ID,1);
  end loop;
  j.put('replayed',true);p_result:=j.to_clob;
 end;

 procedure save(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);items json_array_t;x json_object_t;out_json json_array_t:=json_array_t();r json_object_t:=json_object_t();
  ware number:=d.get_number('warehouse_id');trip varchar2(100):=d.get_string('trip_id');op varchar2(100):=d.get_string('operation_id');
  hash_value varchar2(64):=d.get_string('client_request_hash');basis varchar2(64);old_row RRL_TRADE_TOPUP_PROPOSAL%rowtype;id_value number;reuse boolean;
 begin
  if op is null or ware is null or trip is null or hash_value is null or not regexp_like(hash_value,'^[a-f0-9]{64}$')then fail('TRADE_TOPUP_REQUEST_INVALID');end if;
  lock_site(ware);
  require(p_actor,'tradecase_topup_approve',ware);
  items:=d.get_array('items');
  if items is null or items.get_size<1 or items.get_size>20 then fail('TRADE_TOPUP_ITEM_BOUND');end if;
  for i in 0..items.get_size-1 loop
   x:=treat(items.get(i)as json_object_t);
   RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,ware,x.get_string('source_owner_id'),1);
  end loop;
  if replay(op,hash_value,ware,p_result)then return;end if;
  basis:=RRL_TRADE_TOPUP_READ.trip_basis(ware,trip);
  if basis<>d.get_string('capacity_basis')then fail('TRADE_TOPUP_CAPACITY_BASIS_CHANGED');end if;
  if RRL_TRADE_TOPUP_READ.loading_started(ware,trip)=1 then fail('TOPUP_LOADING_ALREADY_STARTED');end if;
  items:=d.get_array('items');
  if items.get_size<1 or items.get_size>20 then fail('TRADE_TOPUP_ITEM_BOUND');end if;
  for i in 0..items.get_size-1 loop
   x:=treat(items.get(i)as json_object_t);
   RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,ware,x.get_string('source_owner_id'),1);
   reuse:=false;
   begin
    declare
     json_arg_1 varchar2(32767):=x.get_string('need_id');
    begin
     select*into old_row from RRL_TRADE_TOPUP_PROPOSAL where WARE_ID=ware and TRIP_ID=trip and NEED_ID=json_arg_1
     and STATUS in('PROPOSED','ADJUSTED')for update;
    end;
    -- Same inputs, same space: the existing proposal stays (no second proposal for the same volume).
    if old_row.NEED_VERSION=x.get_number('need_version')and old_row.NEED_SIGNATURE=x.get_string('need_signature')
     and old_row.CAPACITY_BASIS=basis and old_row.PROPOSED_BOXES=x.get_number('proposed_boxes')and old_row.PRIORITY=x.get_number('priority')then
     reuse:=true;id_value:=old_row.PROPOSAL_ID;
    else
     update RRL_TRADE_TOPUP_PROPOSAL set STATUS='SUPERSEDED',VERSION_NO=VERSION_NO+1,UPDATED_BY=p_actor,UPDATED_AT=systimestamp where PROPOSAL_ID=old_row.PROPOSAL_ID;
    end if;
   exception when no_data_found then null;end;
   if not reuse then
    select RRL_TRADE_TOPUP_PROPOSAL_SQ.nextval into id_value from dual;
    declare
     json_arg_1 number:=d.get_number('trip_version');
     json_arg_2 varchar2(32767):=x.get_string('need_id');
     json_arg_3 number:=x.get_number('need_version');
     json_arg_4 varchar2(32767):=x.get_string('need_signature');
     json_arg_5 varchar2(32767):=x.get_string('need_snapshot_at');
     json_arg_6 number:=d.get_number('max_age_minutes');
     json_arg_7 number:=x.get_number('priority');
     json_arg_8 varchar2(32767):=x.get_string('recipient_id');
     json_arg_9 varchar2(32767):=x.get_string('sku_id');
     json_arg_10 varchar2(32767):=x.get_string('article');
     json_arg_11 number:=x.get_number('units_per_box');
     json_arg_12 varchar2(32767):=x.get_string('source_owner_id');
     json_arg_13 varchar2(32767):=x.get_string('target_owner_id');
     json_arg_14 number:=x.get_number('mrc');
     json_arg_15 varchar2(32767):=x.get_string('min_expiry_date');
     json_arg_16 number:=x.get_number('need_boxes');
     json_arg_17 number:=x.get_number('proposed_boxes');
     json_arg_18 varchar2(32767):=d.get_string('calculation_signature');
     json_arg_19 clob:=x.get_object('calculation').to_clob;
    begin
     insert into RRL_TRADE_TOPUP_PROPOSAL(PROPOSAL_ID,WARE_ID,TRIP_ID,TRIP_VERSION,NEED_ID,NEED_VERSION,NEED_SIGNATURE,NEED_SNAPSHOT_AT,
     MAX_AGE_MINUTES,PRIORITY,RECIPIENT_ID,SKU_ID,ARTICLE,UNITS_PER_BOX,SOURCE_OWNER_ID,TARGET_OWNER_ID,MRC,MIN_EXPIRY,NEED_BOXES,
     PROPOSED_BOXES,APPROVED_BOXES,CAPACITY_BASIS,CALC_SIGNATURE,CALC_JSON,STATUS,VERSION_NO,CREATED_BY,UPDATED_BY)
    values(id_value,ware,trip,json_arg_1,json_arg_2,json_arg_3,json_arg_4,
     to_timestamp_tz(json_arg_5,'YYYY-MM-DD"T"HH24:MI:SS.FFTZH:TZM'),json_arg_6,json_arg_7,
     json_arg_8,json_arg_9,json_arg_10,json_arg_11,json_arg_12,
     json_arg_13,json_arg_14,to_date(json_arg_15,'FXYYYY-MM-DD'),json_arg_16,
     json_arg_17,json_arg_17,basis,json_arg_18,json_arg_19,
     'PROPOSED',1,p_actor,p_actor);
    end;
   end if;
   out_json.append(json_object_t.parse(RRL_TRADE_TOPUP_READ.card(id_value)));
  end loop;
  r.put('operation_id',op);r.put('warehouse_id',ware);r.put('trip_id',trip);r.put('capacity_basis',basis);r.put('proposals',out_json);
  r.put('replayed',false);r.put('stock_reserved',false);r.put('sap_requested',false);p_result:=r.to_clob;
  journal(op,ware,null,'SAVE',null,hash_value,p_actor,p_result);
 end;

 procedure decide(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);p RRL_TRADE_TOPUP_PROPOSAL%rowtype;r json_object_t;
  op varchar2(100):=d.get_string('operation_id');action varchar2(20):=d.get_string('action');boxes number:=d.get_number('boxes');hash_value varchar2(64):=sha(p_request);
 begin
  if op is null or action is null or action not in('ADJUST','REJECT')then fail('TRADE_TOPUP_REQUEST_INVALID');end if;
  begin declare
   json_arg_1 number:=d.get_number('proposal_id');
  begin
   select*into p from RRL_TRADE_TOPUP_PROPOSAL where PROPOSAL_ID=json_arg_1;
  end;
  exception when no_data_found then fail('TRADE_TOPUP_PROPOSAL_NOT_FOUND');end;
  same_scope(p,d);lock_site(p.WARE_ID);
  require(p_actor,'tradecase_topup_approve',p.WARE_ID);RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,p.WARE_ID,p.SOURCE_OWNER_ID,1);
  if replay(op,hash_value,p.WARE_ID,p_result)then return;end if;
  select*into p from RRL_TRADE_TOPUP_PROPOSAL where PROPOSAL_ID=p.PROPOSAL_ID for update;
  if p.STATUS not in('PROPOSED','ADJUSTED')then fail('TRADE_TOPUP_STATE_CONFLICT');end if;
  if d.get_number('expected_version')is null or p.VERSION_NO<>d.get_number('expected_version')then fail('VERSION_CONFLICT');end if;
  if action='ADJUST'then
   -- Only down to the calculated fit: more boxes would need a new calculation of the free space.
   if boxes is null or boxes<1 or boxes<>trunc(boxes)or boxes>p.PROPOSED_BOXES then fail('TRADE_TOPUP_ADJUST_OUT_OF_RANGE');end if;
   update RRL_TRADE_TOPUP_PROPOSAL set APPROVED_BOXES=boxes,STATUS='ADJUSTED',VERSION_NO=VERSION_NO+1,UPDATED_BY=p_actor,UPDATED_AT=systimestamp where PROPOSAL_ID=p.PROPOSAL_ID;
  else
   update RRL_TRADE_TOPUP_PROPOSAL set STATUS='REJECTED',VERSION_NO=VERSION_NO+1,UPDATED_BY=p_actor,UPDATED_AT=systimestamp where PROPOSAL_ID=p.PROPOSAL_ID;
  end if;
  r:=json_object_t.parse(RRL_TRADE_TOPUP_READ.card(p.PROPOSAL_ID));r.put('operation_id',op);r.put('replayed',false);r.put('warehouse_tasks_created',0);
  p_result:=r.to_clob;journal(op,p.WARE_ID,p.PROPOSAL_ID,action,boxes,hash_value,p_actor,p_result);
 end;

 procedure sap_accept(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);p RRL_TRADE_TOPUP_PROPOSAL%rowtype;r json_object_t;e RRL_TRADE_TOPUP_EVENT%rowtype;
  source_value varchar2(100):=d.get_string('source_id');event_value varchar2(100):=d.get_string('event_id');order_value varchar2(100):=d.get_string('sap_order_id');
  hash_value varchar2(64):=sha(p_request);site_source varchar2(100);
 begin
  if source_value is null or event_value is null or order_value is null then fail('TRADE_TOPUP_REQUEST_INVALID');end if;
  begin declare
   json_arg_1 number:=d.get_number('proposal_id');
  begin
   select*into p from RRL_TRADE_TOPUP_PROPOSAL where PROPOSAL_ID=json_arg_1;
  end;
  exception when no_data_found then fail('TRADE_TOPUP_PROPOSAL_NOT_FOUND');end;
  same_scope(p,d);lock_site(p.WARE_ID);
  require(p_actor,'tradecase_topup_result',p.WARE_ID);
  RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,p.WARE_ID,p.SOURCE_OWNER_ID,1);
  select SOURCE_ID into site_source from RRL_TRADE_SITE where WARE_ID=p.WARE_ID;
  if site_source<>source_value then fail('TRADE_TOPUP_SOURCE_MISMATCH');end if;
  begin
   select*into e from RRL_TRADE_TOPUP_EVENT where WARE_ID=p.WARE_ID and SOURCE_ID=source_value and EVENT_ID=event_value;
   if e.PAYLOAD_HASH<>hash_value then fail('TRADE_TOPUP_EVENT_CONFLICT');end if;
   r:=json_object_t.parse(e.RESULT_JSON);r.put('replayed',true);p_result:=r.to_clob;return;
  exception when no_data_found then null;end;
  select*into p from RRL_TRADE_TOPUP_PROPOSAL where PROPOSAL_ID=p.PROPOSAL_ID for update;
  if p.STATUS<>'CONFIRMED'then fail('TRADE_TOPUP_STATE_CONFLICT');end if;
  update RRL_TRADE_TOPUP_PROPOSAL set STATUS='SAP_ACCEPTED',SAP_ORDER_ID=order_value,VERSION_NO=VERSION_NO+1,UPDATED_BY=p_actor,UPDATED_AT=systimestamp
   where PROPOSAL_ID=p.PROPOSAL_ID;
  r:=json_object_t.parse(RRL_TRADE_TOPUP_READ.card(p.PROPOSAL_ID));r.put('replayed',false);
  -- The order itself arrives as an ordinary SAP ORDER document; WMS never fabricates it.
  p_result:=r.to_clob;
  insert into RRL_TRADE_TOPUP_EVENT(WARE_ID,SOURCE_ID,EVENT_ID,PROPOSAL_ID,PAYLOAD_HASH,BODY_JSON,RESULT_JSON)
   values(p.WARE_ID,source_value,event_value,p.PROPOSAL_ID,hash_value,p_request,p_result);
  journal('SAP:'||source_value||':'||event_value,p.WARE_ID,p.PROPOSAL_ID,'SAP_ACCEPT',p.APPROVED_BOXES,hash_value,p_actor,p_result);
 exception when dup_val_on_index then fail('TRADE_TOPUP_SAP_ORDER_ALREADY_LINKED');
 end;

 function list_trip(p_ware number,p_trip varchar2,p_actor varchar2)return clob is a json_array_t:=json_array_t();n number;
 begin
  select RRL_ACCESS_API.allowed(p_actor,'tradecase_view','WAREHOUSE',to_char(p_ware))into n from dual;
  if n<>1 then raise_application_error(-20882,'TRADE_TOPUP_ACCESS_DENIED');end if;
  for p in(select PROPOSAL_ID,SOURCE_OWNER_ID from RRL_TRADE_TOPUP_PROPOSAL where WARE_ID=p_ware and TRIP_ID=p_trip and STATUS<>'SUPERSEDED'
    and RRL_TRADE_STOCK_GUARD.owner_allowed(p_actor,p_ware,SOURCE_OWNER_ID,0)=1
    order by case when STATUS in('PROPOSED','ADJUSTED')then 0 else 1 end,PRIORITY,PROPOSAL_ID fetch first 200 rows only)loop
   a.append(json_object_t.parse(RRL_TRADE_TOPUP_READ.card(p.PROPOSAL_ID)));
  end loop;
  return a.to_clob;
 end;
end;
/
