create or replace package RRL_CLUSTER_CREATE_API authid definer as
 function write_allowed(p_operation varchar2)return number;
 procedure create_cluster(p_operation varchar2,p_actor varchar2,p_request clob,p_sts clob,p_result out clob);
end;
/
create or replace package body RRL_CLUSTER_CREATE_API as
 g_operation varchar2(100);g_tx varchar2(100);
 function write_allowed(p_operation varchar2)return number is begin
  if p_operation=g_operation and g_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;
 end;
 procedure actor_allowed(p_actor varchar2)is n number;begin
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'transport_dispatch_edit')=1;
  if n!=1 then raise_application_error(-20882,'CLUSTER_ACTIVE_DISPATCHER_REQUIRED');end if;
 end;
 procedure check_saved_scope(p_result clob,p_actor varchar2)is b json_object_t;wares json_array_t;begin
  b:=json_object_t.parse(p_result);wares:=b.get_array('warehouse_ids');
  for i in 0..wares.get_size-1 loop RRL_TRANSPORT_PLAN_RULES.assert_actor(p_actor,wares.get_number(i));end loop;
 end;
 procedure create_cluster(p_operation varchar2,p_actor varchar2,p_request clob,p_sts clob,p_result out clob)is
  request_text varchar2(4000);request_hash varchar2(64);saved RRL_CLUSTER_CREATE_RESULT%rowtype;
  b json_object_t;fields json_object_t:=json_object_t();numbers json_array_t;wares json_array_t:=json_array_t();
  seen json_object_t:=json_object_t();v_trip number;v_day date;v_count number:=0;v_ware number;v_check clob;
  result json_object_t;assigned json_object_t;
 begin
  savepoint RRL_CLUSTER139;
  actor_allowed(p_actor);
  if p_operation is null or lengthb(p_operation)>100 then raise_application_error(-20886,'CLUSTER_OPERATION_ID_REQUIRED');end if;
  if p_request is null or dbms_lob.getlength(p_request)>2000 then raise_application_error(-20886,'CLUSTER_REQUEST_BOUND_2000');end if;
  request_text:=dbms_lob.substr(p_request,2000,1);
  select lower(rawtohex(standard_hash(request_text,'SHA256')))into request_hash from dual;
  g_operation:=p_operation;g_tx:=dbms_transaction.local_transaction_id(true);
  begin
   insert into RRL_CLUSTER_CREATE_RESULT(OPERATION_ID,ACTOR,REQUEST_HASH,REQUEST_JSON)
    values(p_operation,p_actor,request_hash,p_request);
  exception when dup_val_on_index then
   select *into saved from RRL_CLUSTER_CREATE_RESULT where OPERATION_ID=p_operation;
   if saved.ACTOR!=p_actor or saved.REQUEST_HASH!=request_hash then raise_application_error(-20886,'CLUSTER_OPERATION_PAYLOAD_CONFLICT');end if;
   if saved.RESULT_JSON is null then raise_application_error(-20886,'CLUSTER_RESULT_INCOMPLETE');end if;
   check_saved_scope(saved.RESULT_JSON,p_actor);p_result:=saved.RESULT_JSON;g_operation:=null;g_tx:=null;return;
  end;
  if p_sts is null or dbms_lob.getlength(p_sts)>65536 then raise_application_error(-20886,'CLUSTER_SOURCE_JSON_BOUND');end if;
  b:=json_object_t.parse(p_request);numbers:=json_array_t.parse(p_sts);
  if numbers.get_size<1 or numbers.get_size>200 then raise_application_error(-20886,'CLUSTER_SELECT_1_200_STS');end if;
  -- Store the first selected source snapshot. Native assignment rechecks each locked source.
  for item in(select distinct WARE_ID from RRL_SBORKA_PALLETS sp where ST_NUMBER in(
    select ST_NUMBER from json_table(p_sts,'$[*]'columns(ST_NUMBER varchar2(100)path '$')))order by WARE_ID)loop
   RRL_TRANSPORT_PLAN_RULES.assert_actor(p_actor,item.WARE_ID);wares.append(item.WARE_ID);
  end loop;
  if wares.get_size=0 then raise_application_error(-20886,'CLUSTER_CURRENT_SOURCE_REQUIRED');end if;
  v_day:=to_date(b.get_string('stdate'),'FXYYYY-MM-DD');
  RRL_TRANSPORT_EDIT_API.create_trip(b.get_string('transtype'),v_day,p_actor,v_trip);
  if b.has('vehicle')and not b.get('vehicle').is_null then fields.put('transport',b.get_string('vehicle'));end if;
  if b.has('driver_id')and not b.get('driver_id').is_null then fields.put('voditel_id',b.get_number('driver_id'));end if;
  if b.has('dock')and not b.get('dock').is_null then fields.put('dock',b.get_string('dock'));end if;
  if fields.get_size>0 then RRL_TRANSPORT_EDIT_API.update_trip(v_trip,p_actor,fields.to_clob,v_check);end if;
  RRL_TRANSPORT_PLAN_API.assign_sts(v_trip,p_sts,p_actor,v_check);assigned:=json_object_t.parse(v_check);
  -- Capture warehouse scope after assignment, not the unlocked discovery.
  wares:=json_array_t();
  for item in(select distinct WARE_ID from RRL_SBORKA_PALLETS where TRANSTASK_ID=v_trip order by WARE_ID)loop
   RRL_TRANSPORT_PLAN_RULES.assert_actor(p_actor,item.WARE_ID);wares.append(item.WARE_ID);
  end loop;
  result:=json_object_t();result.put('task_id',v_trip);result.put('raion',b.get_string('raion'));
  v_count:=numbers.get_size;result.put('st_count',v_count);result.put('warnings',assigned.get('warnings'));
  result.put('operation_id',p_operation);result.put('warehouse_ids',wares);result.put('source_st_numbers',numbers);
  result.put('stock_changed',false);p_result:=result.to_clob;
  update RRL_CLUSTER_CREATE_RESULT set TRIP_ID=v_trip,RESULT_JSON=p_result where OPERATION_ID=p_operation;
  g_operation:=null;g_tx:=null;
 exception when others then rollback to RRL_CLUSTER139;g_operation:=null;g_tx:=null;raise;
 end;
end;
/
