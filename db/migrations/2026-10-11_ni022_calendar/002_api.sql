create or replace package RRL_STORE_CALENDAR_API authid definer as
 function write_allowed(p_operation varchar2)return number;
 function config_write_allowed return number;
 procedure configure(p_ware number,p_store varchar2,p_body clob,p_actor varchar2,p_result out clob);
 procedure context(p_ware number,p_store varchar2,p_day varchar2,p_actor varchar2,p_result out clob);
 procedure set_exception(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob);
end;
/
create or replace package body RRL_STORE_CALENDAR_API as
 g_operation varchar2(100);g_tx varchar2(100);g_config boolean:=false;
 function write_allowed(p_operation varchar2)return number is begin
  if g_operation=p_operation and g_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;
 end;
 function config_write_allowed return number is begin
  if g_config and g_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;
 end;
 procedure scope(p_ware number,p_actor varchar2)is n number;begin
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0
   and RRL_HAS_WRIGHT(ID,'customer_rule_edit')=1
   and(WARE_ID=p_ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN');
  if n!=1 then raise_application_error(-20882,'STORE_CAL_CURRENT_WARE_ACTOR_REQUIRED');end if;
  select count(*)into n from RRL_WARES where ID=p_ware;
  if n!=1 then raise_application_error(-20886,'STORE_CAL_WARE_NOT_FOUND');end if;
 end;
 function store_id(p_store varchar2)return number is n number;v_id number;begin
  select count(*),max(CUSTOMER_STORE_MAP_ID)into n,v_id from RRL_CUSTOMER_STORE_MAP where STORE_CODE=p_store and ACTIVE=1;
  if n!=1 then raise_application_error(-20886,'STORE_CAL_UNIQUE_ACTIVE_STORE_REQUIRED');end if;return v_id;
 end;
 function local_date(p_day varchar2)return date is d date;begin
  d:=to_date(p_day,'FXYYYY-MM-DD');
  if p_day is null or to_char(d,'YYYY-MM-DD')!=p_day then raise_application_error(-20886,'STORE_CAL_EXPLICIT_LOCAL_DATE_REQUIRED');end if;return d;
 end;
 procedure context(p_ware number,p_store varchar2,p_day varchar2,p_actor varchar2,p_result out clob)is
  v_store number;v_day date;v_version number;src RRL_SAP_STORE_CALENDAR%rowtype;saved RRL_SAP_STORE_CAL_EXCEPTION%rowtype;b json_object_t:=json_object_t();
 begin
  scope(p_ware,p_actor);v_store:=store_id(p_store);v_day:=local_date(p_day);
  b.put('warehouse_id',p_ware);b.put('store_code',p_store);b.put('delivery_date',p_day);
  select nvl(max(VERSION_NO),0)into v_version from RRL_SAP_STORE_CAL_EXCEPTION where WARE_ID=p_ware and CUSTOMER_STORE_MAP_ID=v_store and DELIVERY_DATE=v_day;
  b.put('version',v_version);b.put('exception_status','NO_EXCEPTION');b.put('stock_changed',false);
  begin select *into src from RRL_SAP_STORE_CALENDAR where WARE_ID=p_ware and CUSTOMER_STORE_MAP_ID=v_store;
   b.put('configured',true);b.put('utc_offset_minutes',src.UTC_OFFSET_MINUTES);b.put('delivery_weekdays',src.DELIVERY_WEEKDAYS);b.put('allow_same_day',src.ALLOW_SAME_DAY=1);
  exception when no_data_found then b.put('configured',false);end;
  if v_version>0 then
   select *into saved from RRL_SAP_STORE_CAL_EXCEPTION where WARE_ID=p_ware and CUSTOMER_STORE_MAP_ID=v_store and DELIVERY_DATE=v_day and VERSION_NO=v_version;
   b.put('exception_status',saved.DAY_STATE);b.put('last_exception',json_object_t.parse(saved.RESULT_JSON));
  end if;p_result:=b.to_clob;
 end;
 procedure configure(p_ware number,p_store varchar2,p_body clob,p_actor varchar2,p_result out clob)is
  b json_object_t:=json_object_t.parse(p_body);a json_array_t:=b.get_array('delivery_weekdays');v_store number;v_offset number;v_same number;v_days varchar2(20);v_day number;v_meta boolean:=false;
 begin
  scope(p_ware,p_actor);RRL_STOCK_METADATA_TX.begin_change(p_actor,'customer_rule_edit');v_meta:=true;savepoint RRL_STORE_CAL264;
  scope(p_ware,p_actor);v_store:=store_id(p_store);v_offset:=b.get_number('utc_offset_minutes');
  if v_offset is null or v_offset not between -720 and 840 or trunc(v_offset)!=v_offset or a is null or a.get_size not between 1 and 7 or not b.has('allow_same_day')then raise_application_error(-20886,'STORE_CAL_CONFIG_INVALID');end if;
  if b.get_boolean('allow_same_day')then v_same:=1;else v_same:=0;end if;
  for i in 0..a.get_size-1 loop v_day:=a.get_number(i);
   if v_day is null or v_day not between 1 and 7 or trunc(v_day)!=v_day then raise_application_error(-20886,'STORE_CAL_WEEKDAY_INVALID');end if;
   if instr(','||v_days||',',','||v_day||',')=0 then v_days:=v_days||case when v_days is null then null else ','end||v_day;end if;
  end loop;
  g_config:=true;g_tx:=dbms_transaction.local_transaction_id(false);
  merge into RRL_SAP_STORE_CALENDAR d using(select p_ware WARE_ID,v_store CUSTOMER_STORE_MAP_ID from dual)s on(d.WARE_ID=s.WARE_ID and d.CUSTOMER_STORE_MAP_ID=s.CUSTOMER_STORE_MAP_ID)
  when matched then update set UTC_OFFSET_MINUTES=v_offset,DELIVERY_WEEKDAYS=v_days,ALLOW_SAME_DAY=v_same,UPDATED_BY=p_actor,UPDATED_AT=systimestamp
  when not matched then insert(WARE_ID,CUSTOMER_STORE_MAP_ID,UTC_OFFSET_MINUTES,DELIVERY_WEEKDAYS,ALLOW_SAME_DAY,UPDATED_BY)values(p_ware,v_store,v_offset,v_days,v_same,p_actor);
  g_config:=false;g_tx:=null;RRL_STOCK_METADATA_TX.end_change;
  b.put('warehouse_id',p_ware);b.put('store_code',p_store);p_result:=b.to_clob;
 exception when others then
  if v_meta then rollback to RRL_STORE_CAL264;end if;g_config:=false;g_tx:=null;
  if v_meta then RRL_STOCK_METADATA_TX.end_change;end if;raise;
 end;
 procedure set_exception(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob)is
  b json_object_t;v_ware number;v_store_code varchar2(100);v_store number;v_day date;v_version number;
  v_req_hash varchar2(64);v_state varchar2(10);v_ref nvarchar2(500);v_reason nvarchar2(500);v_meta boolean:=false;n number;
  saved RRL_SAP_STORE_CAL_EXCEPTION%rowtype;r json_object_t:=json_object_t();
 begin
  if p_operation is null or lengthb(p_operation)>100 or not regexp_like(p_operation,'^[A-Za-z0-9_.:-]+$')or p_body is null or dbms_lob.getlength(p_body)>4000 then raise_application_error(-20886,'STORE_CAL_EXCEPTION_INPUT_BOUND');end if;
  b:=json_object_t.parse(p_body);v_ware:=b.get_number('warehouse_id');v_store_code:=b.get_string('store_code');v_day:=local_date(b.get_string('delivery_date'));
  scope(v_ware,p_actor);v_req_hash:=lower(rawtohex(sys.dbms_crypto.hash(p_body,sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_METADATA_TX.begin_change(p_actor,'customer_rule_edit');v_meta:=true;savepoint RRL_CAL_EX264;
  scope(v_ware,p_actor);v_store:=store_id(v_store_code);
  begin select *into saved from RRL_SAP_STORE_CAL_EXCEPTION where OPERATION_ID=p_operation;
   if saved.ACTOR!=p_actor or saved.WARE_ID!=v_ware or saved.CUSTOMER_STORE_MAP_ID!=v_store or saved.REQUEST_HASH!=v_req_hash then raise_application_error(-20886,'STORE_CAL_EXCEPTION_PAYLOAD_CONFLICT');end if;
   p_result:=saved.RESULT_JSON;RRL_STOCK_METADATA_TX.end_change;return;
  exception when no_data_found then null;end;
  select count(*)into n from RRL_SAP_STORE_CALENDAR where WARE_ID=v_ware and CUSTOMER_STORE_MAP_ID=v_store;
  if n!=1 then raise_application_error(-20886,'STORE_CAL_CONFIGURE_SOURCE_BOOK_REQUIRED');end if;
  select nvl(max(VERSION_NO),0)into v_version from RRL_SAP_STORE_CAL_EXCEPTION where WARE_ID=v_ware and CUSTOMER_STORE_MAP_ID=v_store and DELIVERY_DATE=v_day;
  if b.get_number('expected_version')is null or b.get_number('expected_version')!=v_version then raise_application_error(-20886,'STORE_CAL_EXCEPTION_VERSION_CHANGED');end if;
  v_state:=b.get_string('day_state');v_ref:=b.get_string('source_reference');v_reason:=b.get_string('reason');
  if v_state is null or v_state not in('OPEN','CLOSED')or v_ref is null or length(trim(v_ref))<8 or v_reason is null or length(trim(v_reason))<8 then raise_application_error(-20886,'STORE_CAL_EXCEPTION_REASON_REQUIRED');end if;
  r.put('operation_id',p_operation);r.put('warehouse_id',v_ware);r.put('store_code',v_store_code);r.put('delivery_date',to_char(v_day,'YYYY-MM-DD'));
  r.put('version',v_version+1);r.put('day_state',v_state);r.put('source_reference',v_ref);r.put('reason',v_reason);r.put('actor',p_actor);r.put('stock_changed',false);
  p_result:=r.to_clob;g_operation:=p_operation;g_tx:=dbms_transaction.local_transaction_id(false);
  insert into RRL_SAP_STORE_CAL_EXCEPTION(WARE_ID,CUSTOMER_STORE_MAP_ID,DELIVERY_DATE,VERSION_NO,OPERATION_ID,ACTOR,REQUEST_HASH,DAY_STATE,SOURCE_REFERENCE,REASON,RESULT_JSON)
   values(v_ware,v_store,v_day,v_version+1,p_operation,p_actor,v_req_hash,v_state,v_ref,v_reason,p_result);
  g_operation:=null;g_tx:=null;RRL_STOCK_METADATA_TX.end_change;
 exception when others then
  if v_meta then rollback to RRL_CAL_EX264;end if;g_operation:=null;g_tx:=null;
  if v_meta then RRL_STOCK_METADATA_TX.end_change;end if;raise;
 end;
end;
/
