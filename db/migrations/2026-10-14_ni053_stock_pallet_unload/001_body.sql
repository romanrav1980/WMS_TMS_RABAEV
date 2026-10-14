create or replace package body RRL_STORE_UNLOAD_CORE as
 g_writing boolean:=false;
 function writing return boolean is begin return g_writing;end;
 procedure validate_input(p_metadata json_object_t,p_domain json_object_t)is
 m json_object_t;s RRL_STORE_UNLOAD_START%rowtype;n number;root_node json_object_t;keys json_key_list;load_op varchar2(100):=p_domain.get_string('load_operation_id');
 method_value varchar2(20);difficulty boolean;loader boolean;start_op varchar2(100);
 begin
  select count(*)into n from RRL_STORE_UNLOAD_START where LOAD_OPERATION_ID=load_op;
  if not p_metadata.has('unloading')or p_metadata.get('unloading').is_null then
   if n!=0 then raise_application_error(-20886,'UNLOAD_FINISH_DETAILS_REQUIRED');end if;return;
  end if;
  m:=p_metadata.get_object('unloading');keys:=m.get_keys;
  if keys.count!=5 then raise_application_error(-20886,'UNLOAD_FINISH_FIELDS_REQUIRED');end if;
  for i in 1..keys.count loop
   if keys(i)not in('start_operation_id','method','rolling_difficult','loader_present','evidence_reference')
    then raise_application_error(-20886,'UNLOAD_FINISH_UNKNOWN_FIELD');end if;
  end loop;
  start_op:=m.get_string('start_operation_id');
  begin select *into s from RRL_STORE_UNLOAD_START where OPERATION_ID=start_op;
  exception when no_data_found then raise_application_error(-20886,'UNLOAD_SYSTEM_START_REQUIRED');end;
  if s.LOAD_OPERATION_ID!=load_op or s.STORE_ADDR!=p_domain.get_string('store_address')or s.ROOT_KEY!=p_domain.get_string('root')
   or s.COMPOSITION_SIGNATURE!=p_domain.get_string('composition_signature')
   then raise_application_error(-20886,'UNLOAD_ORIGINAL_SOURCE_REQUIRED');end if;
  method_value:=m.get_string('method');difficulty:=m.get_boolean('rolling_difficult');loader:=m.get_boolean('loader_present');
  if method_value is null or method_value not in('ROLL_CAGE','PALLET','MANUAL')or difficulty is null or loader is null
   or trim(m.get_string('evidence_reference'))is null or lengthb(m.get_string('evidence_reference'))>255
   then raise_application_error(-20886,'UNLOAD_ACTUAL_DETAILS_REQUIRED');end if;
  root_node:=treat(p_domain.get_object('snapshot').get_array('nodes').get(0)as json_object_t);
  if method_value='ROLL_CAGE'and(root_node.get_string('kind')!='CONTAINER'or root_node.get_string('type')!='ROLL_CAGE')
   then raise_application_error(-20886,'UNLOAD_ROLL_CAGE_SOURCE_REQUIRED');end if;
  if method_value='PALLET' then
   if nvl(root_node.get_string('kind'),'~')='CONTAINER'and nvl(root_node.get_string('type'),'~')='PALLET' then null;
   elsif nvl(root_node.get_string('kind'),'~')='STOCK' then
    -- Frozen physical loading proof, never infer pallet type from current SKU/store settings.
    select count(*)into n from RRL_TT_LOAD_FLOOR_FACT f
     join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=f.LOAD_OPERATION_ID
     join RRL_STOCK_OPERATION o on o.OPERATION_ID=l.LOAD_OPERATION_ID
     where f.LOAD_OPERATION_ID=load_op and f.TYPE_ORIGIN='ROOT_STOCK_TYPE'
      and l.ROOT_UID=s.ROOT_KEY and l.STATUS='DEPARTED'and o.STATE='APPLIED'
      and json_value(f.CONFIRMATION_JSON,'$.root')=l.ROOT_UID
      and json_value(f.CONFIRMATION_JSON,'$.type_origin')='ROOT_STOCK_TYPE'
      and json_value(f.CONFIRMATION_JSON,'$.pallet_type_id' returning number)=f.PALLET_TYPE_ID;
    if n!=1 then raise_application_error(-20886,'UNLOAD_PALLET_LOADING_PROOF_REQUIRED');end if;
   else raise_application_error(-20886,'UNLOAD_PALLET_SOURCE_REQUIRED');end if;
  end if;
  if difficulty and(method_value!='ROLL_CAGE'or not loader)then raise_application_error(-20886,'UNLOAD_DIFFICULT_ROLL_REQUIRES_LOADER');end if;
 end;
 procedure capture(p_request clob,p_actor varchar2)is
 d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');u json_object_t;
 op varchar2(100):=d.get_string('operation_id');source_op varchar2(100);method_value varchar2(20);reference_value varchar2(255);difficulty number;loader number;
 s RRL_STORE_UNLOAD_START%rowtype;receipt RRL_STORE_RECEIPT_FACT%rowtype;body clob;kind varchar2(80);state varchar2(20);
 begin
  if not m.has('unloading')or m.get('unloading').is_null then return;end if;
  if nvl(sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID'),'~')!=op or
   sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
   then raise_application_error(-20863,'UNLOAD_FINISH_ROOT_REQUIRED');end if;
  select COMMAND_TYPE,STATE into kind,state from RRL_STOCK_OPERATION where OPERATION_ID=op;
  if kind!='STORE_RECEIPT'or state!='IN_FLIGHT'then raise_application_error(-20863,'UNLOAD_FINISH_RECEIPT_OWNER_REQUIRED');end if;
  u:=m.get_object('unloading');source_op:=u.get_string('start_operation_id');
  select *into s from RRL_STORE_UNLOAD_START where OPERATION_ID=source_op;
  select *into receipt from RRL_STORE_RECEIPT_FACT where OPERATION_ID=op;
  if receipt.LOAD_OPERATION_ID!=s.LOAD_OPERATION_ID or receipt.STORE_ADDR!=s.STORE_ADDR or receipt.RECEIVED_BY!=p_actor
   or receipt.RECEIVED_AT<s.STARTED_AT_INSTANT then raise_application_error(-20886,'UNLOAD_FINISH_ORIGINAL_RECEIPT_REQUIRED');end if;
  method_value:=u.get_string('method');reference_value:=u.get_string('evidence_reference');
  difficulty:=case when u.get_boolean('rolling_difficult')then 1 else 0 end;loader:=case when u.get_boolean('loader_present')then 1 else 0 end;
  body:=u.to_clob;g_writing:=true;
  insert into RRL_STORE_UNLOAD_FACT(RECEIPT_OPERATION_ID,START_OPERATION_ID,LOAD_OPERATION_ID,STORE_ADDR,METHOD,ROLLING_DIFFICULT,LOADER_PRESENT,EVIDENCE_REFERENCE,ACTOR,FINISHED_AT_INSTANT,PAYLOAD_JSON)
  values(op,source_op,s.LOAD_OPERATION_ID,s.STORE_ADDR,method_value,difficulty,loader,reference_value,p_actor,receipt.RECEIVED_AT,body);
  g_writing:=false;
 exception when others then g_writing:=false;raise;
 end;
end;

/
