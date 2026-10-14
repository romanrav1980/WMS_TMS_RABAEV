create or replace package RRL_SAP_STORE_ADMISSION_API authid definer as
 function write_allowed return number;
 procedure context(p_order number,p_actor varchar2,p_result out clob);
 procedure apply_decision(p_actor varchar2,p_body clob,p_result out clob);
end;
/
create or replace package body RRL_SAP_STORE_ADMISSION_API as
 g_tx varchar2(100);
 function write_allowed return number is begin
  if g_tx is not null and g_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;
 end;
 procedure context(p_order number,p_actor varchar2,p_result out clob)is
  v_ware number;v_version number;saved RRL_SAP_STORE_DECISION%rowtype;b json_object_t:=json_object_t();
 begin
  select WARE_ID into v_ware from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=p_order;
  RRL_STORE_ORDER_SCOPE.assert_scope(p_actor,'customer_order_view',v_ware);
  select nvl(max(VERSION_NO),0)into v_version from RRL_SAP_STORE_DECISION where CUSTOMER_ORDER_ID=p_order;
  b.put('customer_order_id',p_order);b.put('version',v_version);
  if v_version>0 then
   select *into saved from RRL_SAP_STORE_DECISION where CUSTOMER_ORDER_ID=p_order and VERSION_NO=v_version;
   b.put('last_decision',json_object_t.parse(saved.RESULT_JSON));
  end if;p_result:=b.to_clob;
 end;
 procedure apply_decision(p_actor varchar2,p_body clob,p_result out clob)is
  b json_object_t;src RRL_SAP_STORE_ORDER%rowtype;co RRL_CUSTOMER_ORDER%rowtype;
  saved RRL_SAP_STORE_DECISION%rowtype;v_meta boolean:=false;
  v_sender varchar2(100);v_message varchar2(100);v_decision varchar2(100);v_order varchar2(100);v_hash varchar2(64);v_original varchar2(64);v_code varchar2(10);
  v_id number;v_ware number;own_ware number;v_global number;v_version number;n number;v_status varchar2(30);v_co_status varchar2(30);
  v_reason nvarchar2(500);v_ref nvarchar2(500);v_raw clob;v_offset number;v_allowed number;v_rule clob;v_zone varchar2(10);v_finish timestamp with time zone;cached json_object_t;r json_object_t:=json_object_t();
 begin
  RRL_STORE_ORDER_SCOPE.actor_scope(p_actor,'sap_store_decision_import',own_ware,v_global);
  if p_body is null or dbms_lob.getlength(p_body)>8*1024*1024 then raise_application_error(-20886,'STORE_ADMISSION_BODY_BOUND');end if;
  b:=json_object_t.parse(p_body);
  if b.get_size!=11 or b.get_number('expected_version')is null or b.get_number('expected_version')<0 or trunc(b.get_number('expected_version'))!=b.get_number('expected_version')then raise_application_error(-20886,'STORE_ADMISSION_INPUT_FIELDS_INVALID');end if;
  v_sender:=b.get_string('sender');v_message:=b.get_string('message_id');v_decision:=b.get_string('decision_id');
  v_order:=b.get_string('order_number');v_hash:=b.get_string('payload_hash');v_original:=b.get_string('original_content_hash');v_code:=b.get_string('decision');
  v_reason:=b.get_string('reason');v_ref:=b.get_string('reference');v_raw:=b.get_clob('raw_xml');
  if v_sender is null or v_message is null or v_decision is null or v_order is null or v_hash is null or not regexp_like(v_hash,'^[a-f0-9]{64}$','c')
   or v_original is null or not regexp_like(v_original,'^[a-f0-9]{64}$','c')or v_code is null or v_code not in('ACCEPT','REJECT')
   or v_reason is null or length(trim(v_reason))<8 or v_ref is null or length(trim(v_ref))<8 or v_raw is null then raise_application_error(-20886,'STORE_ADMISSION_EXPLICIT_SOURCE_REQUIRED');end if;
  select s.CUSTOMER_ORDER_ID,c.WARE_ID into v_id,v_ware from RRL_SAP_STORE_ORDER s join RRL_CUSTOMER_ORDER c on c.CUSTOMER_ORDER_ID=s.CUSTOMER_ORDER_ID where s.SENDER=v_sender and s.ORDER_NUMBER=v_order;
  RRL_STORE_ORDER_SCOPE.assert_scope(p_actor,'sap_store_decision_import',v_ware);
  RRL_STOCK_METADATA_TX.begin_change(p_actor,'sap_store_decision_import');v_meta:=true;savepoint RRL_ADMISSION267;
  select *into co from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=v_id for update;
  select *into src from RRL_SAP_STORE_ORDER where CUSTOMER_ORDER_ID=v_id for update;
  RRL_STORE_ORDER_SCOPE.assert_scope(p_actor,'sap_store_decision_import',co.WARE_ID);
  begin select *into saved from RRL_SAP_STORE_DECISION where SENDER=v_sender and MESSAGE_ID=v_message;
   cached:=json_object_t.parse(saved.RESULT_JSON);
   if saved.PAYLOAD_HASH!=v_hash or saved.CUSTOMER_ORDER_ID!=v_id
    or saved.DECISION_ID!=v_decision or saved.DECISION_CODE!=v_code or saved.ORIGINAL_CONTENT_HASH!=v_original
    or saved.VERSION_NO!=b.get_number('expected_version')+1 or dbms_lob.compare(saved.RAW_XML,v_raw)!=0
    or cached.get_string('reason')!=v_reason
    or cached.get_string('reference')!=v_ref then raise_application_error(-20886,'STORE_ADMISSION_MESSAGE_PAYLOAD_CONFLICT');end if;
   p_result:=saved.RESULT_JSON;RRL_STOCK_METADATA_TX.end_change;return;
  exception when no_data_found then null;end;
  select count(*)into n from RRL_SAP_STORE_DECISION where SENDER=v_sender and DECISION_ID=v_decision;
  if n>0 then raise_application_error(-20886,'STORE_ADMISSION_DECISION_USE_ORIGINAL_MESSAGE');end if;
  select nvl(max(VERSION_NO),0)into v_version from RRL_SAP_STORE_DECISION where CUSTOMER_ORDER_ID=v_id;
  if b.get_number('expected_version')is null or b.get_number('expected_version')!=v_version or src.CONTENT_HASH!=v_original then raise_application_error(-20886,'STORE_ADMISSION_SOURCE_VERSION_CHANGED');end if;
  if src.PREPARATION_HASH is not null or co.STATUS not in('DRAFT','IMPORTED','OPEN')then raise_application_error(-20886,'STORE_ADMISSION_OPERATIONAL_SOURCE_FROZEN');end if;
  select(select count(*)from RRL_PICK_PLAN where CUSTOMER_ORDER_ID=v_id and STATUS!='CANCELLED')
   +(select count(*)from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=v_id and STATUS!='CANCELLED')
   +(select count(*)from RRL_STOCK_RESERVATION where(CUSTOMER_ORDER_ID=v_id or(SOURCE_DOC_TYPE='CUSTOMER_ORDER'and SOURCE_DOC_ID=v_id))and STATUS in('ACTIVE','ALLOCATED','PICKING'))into n from dual;
  if n>0 then raise_application_error(-20886,'STORE_ADMISSION_PLANNING_ALREADY_STARTED');end if;
  if v_code='ACCEPT'then
   if src.ADMISSION_STATUS not in('PENDING_LATE','PENDING_CALENDAR')then raise_application_error(-20886,'STORE_ADMISSION_PENDING_SOURCE_REQUIRED');end if;
   RRL_STORE_CALENDAR_API.delivery_rule(co.WARE_ID,co.CUSTOMER_STORE_MAP_ID,src.DELIVERY_DATE,v_offset,v_allowed,v_rule);
   if v_allowed!=1 then raise_application_error(-20886,'STORE_ADMISSION_CALENDAR_CLOSED');end if;
   if v_offset!=src.UTC_OFFSET_MINUTES then raise_application_error(-20886,'STORE_ADMISSION_CALENDAR_ZONE_CHANGED');end if;
   v_zone:=case when src.UTC_OFFSET_MINUTES<0 then '-'else '+'end||lpad(trunc(abs(src.UTC_OFFSET_MINUTES)/60),2,'0')||':'||lpad(mod(abs(src.UTC_OFFSET_MINUTES),60),2,'0');
   select from_tz(cast(src.PICKING_FINISH_AT as timestamp),v_zone)into v_finish from dual;
   if v_finish<=systimestamp then raise_application_error(-20886,'STORE_ADMISSION_PICKING_DEADLINE_PASSED');end if;
   v_status:='ACCEPTED';v_co_status:='IMPORTED';
  else
   if src.ADMISSION_STATUS='REJECTED'then raise_application_error(-20886,'STORE_ADMISSION_ALREADY_REJECTED');end if;
   v_status:='REJECTED';v_co_status:='CANCELLED';
  end if;
  r.put('sender',v_sender);r.put('message_id',v_message);r.put('decision_id',v_decision);r.put('customer_order_id',v_id);
  r.put('version',v_version+1);r.put('original_content_hash',src.CONTENT_HASH);r.put('previous_admission_status',src.ADMISSION_STATUS);
  r.put('admission_status',v_status);r.put('customer_order_status',v_co_status);r.put('reason',v_reason);r.put('reference',v_ref);r.put('actor',p_actor);
  r.put('stock_changed',false);r.put('original_demand_changed',false);r.put('original_schedule_changed',false);
  if v_rule is not null then r.put('calendar_proof',json_object_t.parse(v_rule));end if;
  p_result:=r.to_clob;g_tx:=dbms_transaction.local_transaction_id(false);
  update RRL_SAP_STORE_ORDER set ADMISSION_STATUS=v_status where CUSTOMER_ORDER_ID=v_id;
  update RRL_CUSTOMER_ORDER set STATUS=v_co_status,UPDATED_AT=sysdate,UPDATED_BY=p_actor where CUSTOMER_ORDER_ID=v_id;
  insert into RRL_SAP_STORE_DECISION(SENDER,MESSAGE_ID,DECISION_ID,CUSTOMER_ORDER_ID,VERSION_NO,PAYLOAD_HASH,ORIGINAL_CONTENT_HASH,DECISION_CODE,ACTOR,RAW_XML,RESULT_JSON)
   values(v_sender,v_message,v_decision,v_id,v_version+1,v_hash,v_original,v_code,p_actor,v_raw,p_result);
  g_tx:=null;RRL_STOCK_METADATA_TX.end_change;
 exception when others then
  if v_meta then rollback to RRL_ADMISSION267;end if;g_tx:=null;
  if v_meta then RRL_STOCK_METADATA_TX.end_change;end if;raise;
 end;
end;
/
