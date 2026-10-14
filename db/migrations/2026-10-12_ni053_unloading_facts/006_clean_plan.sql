create or replace package RRL_STORE_UNLOAD_API authid definer as
 procedure start_unloading(p_request clob,p_actor varchar2,p_result out clob);
 function writing return boolean;
end;
/
create or replace package body RRL_STORE_UNLOAD_API as
 g_writing boolean:=false;
 function writing return boolean is begin return g_writing;end;
 procedure start_unloading(p_request clob,p_actor varchar2,p_result out clob)is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;j json_object_t:=json_object_t();
 op varchar2(100):=d.get_string('operation_id');load_op varchar2(100):=d.get_string('load_operation_id');addr_text varchar2(255):=d.get_string('store_address');
 expected varchar2(64):=d.get_string('expected_composition_signature');raw_domain clob;old_request clob;old_actor nvarchar2(50);n number;trip number;started timestamp with time zone;
 f json_array_t:=json_array_t();r json_array_t:=json_array_t();state varchar2(20);root_node json_object_t;scan_text varchar2(200):=d.get_string('scan_place');root_text varchar2(200);signature varchar2(64);savepoint_ready boolean:=false;plan_started boolean:=false;keys json_key_list:=d.get_keys;
 begin
  if op is null or not regexp_like(op,'^[A-Za-z0-9_.:-]+$')or length(op)>100 or load_op is null or addr_text is null or keys.count!=6
   or expected is null or not regexp_like(expected,'^[A-F0-9]{64}$')
   or d.get_boolean('before_cameras')is null or not d.get_boolean('before_cameras')
   then raise_application_error(-20886,'UNLOAD_START_INPUT_REQUIRED');end if;
  for i in 1..keys.count loop
   if keys(i)not in('operation_id','load_operation_id','store_address','expected_composition_signature','scan_place','before_cameras')
    then raise_application_error(-20886,'UNLOAD_START_UNKNOWN_FIELD');end if;
  end loop;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',op);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_HU_LOAD_FACT',load_op);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STORE.RECEIPT.LOAD:'||load_op);
  RRL_STOCK_LOCK_API.begin_plan;plan_started:=true;RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  savepoint store_unload_start;savepoint_ready:=true;
  select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if state!='ACTIVE'then raise_application_error(-20860,'UNLOAD_START_RELEASE_CLOSED');end if;
  RRL_STOCK_STORE_RECEIPT_READ.describe_load(load_op,p_actor,addr_text,raw_domain);v:=json_object_t.parse(raw_domain);
  begin
   select REQUEST_JSON,ACTOR,RESULT_JSON into old_request,old_actor,p_result from RRL_STORE_UNLOAD_START where OPERATION_ID=op;
   select count(*)into n from dual where json_equal(old_request,p_request);
   if n!=1 or old_actor!=p_actor then raise_application_error(-20864,'UNLOAD_START_OPERATION_CONFLICT');end if;
   RRL_STOCK_LOCK_API.clear_plan;return;
  exception when no_data_found then null;end;
  if v.get_boolean('already_received')then raise_application_error(-20886,'UNLOAD_START_RECEIPT_ALREADY_COMPLETED');end if;
  if expected!=v.get_string('composition_signature')then raise_application_error(-20890,'CLOSURE_CHANGED: unload manifest');end if;
  root_node:=treat(v.get_object('snapshot').get_array('nodes').get(0)as json_object_t);
  if scan_text is null or(scan_text!=v.get_string('root_scan_identifier')and
    (root_node.get_string('kind')='CASE'or v.get_string('root_sscc')is null or scan_text!=v.get_string('root_sscc')))
   then raise_application_error(-20886,'UNLOAD_START_PHYSICAL_PLACE_SCAN_REQUIRED');end if;
  select count(*)into n from RRL_STORE_UNLOAD_START where LOAD_OPERATION_ID=load_op;
  if n!=0 then raise_application_error(-20886,'UNLOAD_START_EXISTS');end if;
  select TT_ID into trip from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=load_op for update;
  started:=systimestamp;root_text:=v.get_string('root');signature:=v.get_string('composition_signature');
  j.put('operation_id',op);j.put('load_operation_id',load_op);j.put('store_address',addr_text);j.put('root',root_text);j.put('trip_id',trip);
  j.put('started_at_instant',to_char(started,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));
  j.put('time_source','SYSTEM_CAPTURED');j.put('status','STARTED');j.put('stock_changed',false);j.put('cost_posted',false);p_result:=j.to_clob;
  g_writing:=true;
  insert into RRL_STORE_UNLOAD_START(OPERATION_ID,LOAD_OPERATION_ID,STORE_ADDR,ROOT_KEY,COMPOSITION_SIGNATURE,ACTOR,STARTED_AT_INSTANT,REQUEST_JSON,RESULT_JSON)
   values(op,load_op,addr_text,root_text,signature,p_actor,started,p_request,p_result);
  g_writing:=false;RRL_STOCK_LOCK_API.clear_plan;
 exception when others then g_writing:=false;if savepoint_ready then rollback to store_unload_start;end if;if plan_started then RRL_STOCK_LOCK_API.clear_plan;end if;raise;
 end;
end;
/
create or replace trigger RRL_STORE_UNLOAD_START_G before insert or update or delete on RRL_STORE_UNLOAD_START for each row
begin if not inserting or not RRL_STORE_UNLOAD_API.writing then raise_application_error(-20863,'UNLOAD_START_HISTORY_IMMUTABLE');end if;end;
/
