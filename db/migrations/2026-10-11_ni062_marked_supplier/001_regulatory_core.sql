create or replace package RRL_REGULATORY_STOCK_OUTBOX authid definer accessible by(package RRL_REGULATORY_API)as
 procedure declare_events(p_operation varchar2,p_event varchar2,p_profiles clob,p_resources in out nocopy json_array_t);
 function enqueue_events(p_operation varchar2,p_event varchar2,p_domain clob,p_units clob,p_profiles clob)return clob;
end;
/
create or replace package body RRL_REGULATORY_STOCK_OUTBOX as
 function event_key(p_operation varchar2,p_event varchar2,p_system varchar2)return varchar2 is
 begin
  if p_event not in('MARKED_GOODS_DISPOSED','MARKED_SUPPLIER_RETURN_DISPATCHED')then raise_application_error(-20871,'REGULATORY_STOCK_EVENT_KIND_REQUIRED');end if;
  return case p_event when 'MARKED_GOODS_DISPOSED'then 'RETURN.DISPOSAL.GOV:'else 'RETURN.SUPPLIER.GOV:'end||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation||chr(0)||p_system,'AL32UTF8'),sys.dbms_crypto.hash_sh256));
 end;
 procedure declare_events(p_operation varchar2,p_event varchar2,p_profiles clob,p_resources in out nocopy json_array_t)is k varchar2(100);
 begin
  for x in(select distinct S from json_table(p_profiles,'$[*]'columns(S varchar2(40)path '$.system_code'))order by S)loop
   if x.S is null or lengthb(x.S)>30 then raise_application_error(-20871,'REGULATORY_TARGET_SYSTEM_BOUND');end if;
   k:=event_key(p_operation,p_event,x.S);RRL_STOCK_PLAN_HELPER.anchor(p_resources,70,'UNIQUE',k);
  end loop;
 end;
 function enqueue_events(p_operation varchar2,p_event varchar2,p_domain clob,p_units clob,p_profiles clob)return clob is
  frozen clob;kind_text varchar2(80);domain json_object_t;source json_object_t;gov json_object_t;code_wire clob;gov_id number;k varchar2(100);ids json_array_t:=json_array_t();units_count number;n number;
 begin
  if p_operation!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'REGULATORY_STOCK_FACT_ROOT_CONTEXT_REQUIRED');end if;
  select COMMAND_TYPE,RESOLVED_PLAN_JSON into kind_text,frozen from RRL_STOCK_OPERATION where OPERATION_ID=p_operation and STATE='IN_FLIGHT';
  domain:=json_object_t.parse(frozen).get_object('domain');
  if p_event='MARKED_GOODS_DISPOSED'and kind_text='STORE_RETURN_DISPOSE'then source:=domain;
   if dbms_lob.compare(source.get_array('disposal_units').to_clob,p_units)!=0 or dbms_lob.compare(source.get_array('disposal_profiles').to_clob,p_profiles)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: disposal regulatory source');end if;
  elsif p_event='MARKED_SUPPLIER_RETURN_DISPATCHED'and kind_text='LOAD_SHIPMENT'then source:=domain.get_object('shipment').get_object('domain').get_object('supplier_return_source');
   if dbms_lob.compare(source.get_array('units').to_clob,p_units)!=0 or dbms_lob.compare(source.get_array('profiles').to_clob,p_profiles)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: supplier regulatory source');end if;
  else raise_application_error(-20863,'REGULATORY_STOCK_FACT_MATCHING_COMMAND_REQUIRED');end if;
  if dbms_lob.compare(source.to_clob,p_domain)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: regulatory frozen domain');end if;
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',source.get_string('uid')));
  select count(*),count(distinct K)into units_count,n from json_table(p_units,'$[*]'columns(K varchar2(64)path '$.key'));
  if units_count<1 or units_count>10000 or units_count!=n then raise_application_error(-20881,'REGULATORY_STOCK_UNIT_BOUND');end if;
  for x in(select K from json_table(p_units,'$[*]'columns(K varchar2(64)path '$.key'))order by K)loop RRL_STOCK_LOCK_API.assert_held(60,RRL_STOCK_LOCK_API.resource_key('UNIT',x.K));end loop;
  for target in(select distinct S from json_table(p_profiles,'$[*]'columns(S varchar2(30)path '$.system_code'))order by S)loop
   select json_arrayagg(json_object('physical_unit_key'value u.PHYSICAL_UNIT_KEY,'origin_uid'value u.UID_PALLET,'unit_id'value u.UNIT_ID,'code_hash'value c.CODE_HASH,'canonical_code'value c.CANONICAL_CODE,'profiles'value c.PROFILES_JSON format json)order by u.PHYSICAL_UNIT_KEY,c.CODE_HASH returning clob)into code_wire
    from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID
    where c.SYSTEM_CODE=target.S and u.PHYSICAL_UNIT_KEY in(select K from json_table(p_units,'$[*]'columns(K varchar2(64)path '$.key')));
   if code_wire is null then raise_application_error(-20886,'REGULATORY_STOCK_CANONICAL_CODES_REQUIRED');end if;
   gov:=json_object_t.parse(p_domain);gov.put('contract_version',1);gov.put('operation_id',p_operation);gov.put('operation_type',case p_event when 'MARKED_GOODS_DISPOSED'then 'DISPOSAL'else 'SUPPLIER_RETURN_DISPATCH'end);gov.put('system_code',target.S);gov.put('codes',json_array_t.parse(code_wire));gov.put('physical_disposal_recorded',p_event='MARKED_GOODS_DISPOSED');gov.put('external_ack_verified',false);
   k:=event_key(p_operation,p_event,target.S);RRL_STOCK_LOCK_API.assert_held(70,RRL_STOCK_LOCK_API.resource_key('UNIQUE',k));
   gov_id:=RRL_TRACEABILITY_API.enqueue_event(p_event,'STOCK_OPERATION',p_operation,k,gov.to_clob,target.S,p_operation);ids.append(gov_id);
  end loop;
  return ids.to_clob;
 end;
end;
/
