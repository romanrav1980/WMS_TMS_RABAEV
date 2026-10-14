create or replace package body RRL_STOCK_LOAD_FLOOR as
 g_writing boolean:=false;g_operation varchar2(100);g_tx varchar2(100);
 function current_matrix(p_vehicle number)return json_object_t is
  profile_value json_object_t:=json_object_t.parse(RRL_VEHICLE_PROFILE_API.describe_profile(p_vehicle));configured json_object_t;
 begin
  if not profile_value.has('profile')then return null;end if;
  configured:=profile_value.get_object('profile');
  if not configured.has('floor_capacity')then return null;end if;
  if profile_value.get_string('state')!='READY'then raise_application_error(-20886,'LOAD_FLOOR_CURRENT_PROFILE_REQUIRED');end if;
  return profile_value;
 end;
 function compile_load(p_snapshot clob,p_vehicle number,p_rows in out nocopy json_array_t)return json_object_t is
  profile_value json_object_t:=current_matrix(p_vehicle);tree json_object_t;node_value json_object_t;nodes json_array_t;
  result json_object_t:=json_object_t();type_no number;case_no number;n number;book_id varchar2(100);
  root_id varchar2(200);ware_no number;origin_value varchar2(24);reference_value varchar2(200);
 begin
  if profile_value is null then return null;end if;
  tree:=json_object_t.parse(p_snapshot);root_id:=tree.get_string('root');ware_no:=tree.get_number('warehouse');
  nodes:=tree.get_array('nodes');
  if nodes.get_size<1 or nodes.get_size>200 then raise_application_error(-20886,'LOAD_FLOOR_TOP_SOURCE_REQUIRED');end if;
  node_value:=treat(nodes.get(0) as json_object_t);
  if node_value.get_number('depth')!=0 or node_value.get_string('uid')!=root_id then raise_application_error(-20886,'LOAD_FLOOR_SINGLE_TOP_REQUIRED');end if;
  if node_value.get_string('kind')='CASE'then
   case_no:=node_value.get_number('case_task_id');
   select PALLET_TYPE_ID into type_no from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=case_no and WARE_ID=ware_no and STATUS!='CANCELLED';
   if type_no is null then raise_application_error(-20886,'LOAD_FLOOR_CASE_TYPE_REQUIRED');end if;
   RRL_STOCK_PLAN_HELPER.row_key(p_rows,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(case_no));
   origin_value:='CASE_TYPE';reference_value:=RRL_STOCK_PLAN_HELPER.decimal_text(case_no);
  elsif node_value.get_string('kind')='CONTAINER'then
   select count(*),min(PALLET_TYPE_ID),min(OPERATION_ID)into n,type_no,book_id from RRL_TARE_BOOK
    where PLACE_KIND='HU'and PLACE_ID=root_id and OWNER_WARE_ID=ware_no and STATUS='HELD';
   if n!=1 then raise_application_error(-20886,'LOAD_FLOOR_SINGLE_HELD_HU_TARE_REQUIRED');end if;
   RRL_STOCK_PLAN_HELPER.row_key(p_rows,'RRL_TARE_BOOK',book_id);
   origin_value:='HELD_HU_TARE_BOOK';reference_value:=book_id;
  else raise_application_error(-20886,'LOAD_FLOOR_CONFIRMED_TOP_TYPE_REQUIRED');end if;
  select count(*)into n from RRL_PALLET_TYPE where PALLET_TYPE_ID=type_no and ACTIVE=1;
  if n!=1 then raise_application_error(-20886,'LOAD_FLOOR_ACTIVE_TOP_TYPE_REQUIRED');end if;
  result.put('vehicle_id',p_vehicle);result.put('profile_version',profile_value.get_number('version'));
  result.put('profile_base_hash',profile_value.get_string('base_hash'));result.put('pallet_type_id',type_no);
  result.put('type_origin',origin_value);result.put('source_reference',reference_value);
  result.put('root',root_id);result.put('warehouse',ware_no);result.put('top_place_count',1);
  return result;
 exception when no_data_found then raise_application_error(-20886,'LOAD_FLOOR_CURRENT_TOP_SOURCE_REQUIRED');
 end;
 function checked_trip(p_trip number,p_vehicle number,p_extra_type number default null)return clob is
  profile_value json_object_t:=current_matrix(p_vehicle);counts json_array_t:=json_array_t();entry_value json_object_t;result json_object_t;
  type count_map is table of number index by varchar2(100);type_counts count_map;key_value varchar2(100);unknown_no number:=0;load_count number:=0;
 begin
  if profile_value is null then return null;end if;
  for item in(select l.LOAD_OPERATION_ID,l.VEHICLE_ID,l.VEHICLE_NUMBER,f.PALLET_TYPE_ID,f.VEHICLE_ID FLOOR_VEHICLE,o.STATE
   from RRL_TT_HU_LOAD_FACT l left join RRL_TT_LOAD_FLOOR_FACT f on f.LOAD_OPERATION_ID=l.LOAD_OPERATION_ID
   left join RRL_STOCK_OPERATION o on o.OPERATION_ID=l.LOAD_OPERATION_ID
   where l.TT_ID=p_trip and l.STATUS='LOADED'order by l.LOAD_OPERATION_ID fetch first 201 rows only)loop
   load_count:=load_count+1;
   if load_count>200 then raise_application_error(-20881,'LOAD_FLOOR_PLACES_BOUND_200');end if;
   if item.VEHICLE_ID!=p_vehicle or item.STATE is null or item.STATE!='APPLIED'then raise_application_error(-20886,'LOAD_FLOOR_CURRENT_LOAD_PROOF_REQUIRED');end if;
   if item.PALLET_TYPE_ID is null or item.FLOOR_VEHICLE!=p_vehicle then unknown_no:=unknown_no+1;
   else
    key_value:=to_char(item.PALLET_TYPE_ID,'TM9');
    if type_counts.exists(key_value)then type_counts(key_value):=type_counts(key_value)+1;else type_counts(key_value):=1;end if;
   end if;
  end loop;
  if p_extra_type is not null then
   key_value:=to_char(p_extra_type,'TM9');
   if type_counts.exists(key_value)then type_counts(key_value):=type_counts(key_value)+1;else type_counts(key_value):=1;end if;
  end if;
  key_value:=type_counts.first;
  while key_value is not null loop
   entry_value:=json_object_t();entry_value.put('pallet_type_id',to_number(key_value));entry_value.put('places',type_counts(key_value));counts.append(entry_value);
   key_value:=type_counts.next(key_value);
  end loop;
  result:=json_object_t.parse(RRL_VEHICLE_PROFILE_API.check_floor_capacity(p_vehicle,counts.to_clob,unknown_no));
  if result.get_string('status')!='COMPATIBLE'then raise_application_error(-20886,'LOAD_FLOOR_PHYSICAL_VARIANT_NOT_CONFIRMED');end if;
  result.put('loaded_top_places',load_count);result.put('prospective_top_places',load_count+case when p_extra_type is null then 0 else 1 end);
  result.put('profile_base_hash',profile_value.get_string('base_hash'));
  return result.to_clob;
 end;
 function planning_counts(p_vehicle number,p_sts clob,p_base_counts clob,p_unknown number)return clob is
  numbers json_array_t:=json_array_t.parse(p_sts);base_counts json_array_t:=json_array_t.parse(p_base_counts);wire_counts json_array_t:=json_array_t();
  entry_value json_object_t;result json_object_t:=json_object_t();el json_element_t;
  query_value varchar2(32767);cursor_no integer;ran integer;rc sys_refcursor;load_id varchar2(100);type_id number;vehicle_id number;floor_vehicle number;
  unknown_no number:=p_unknown;load_count number:=0;st_value varchar2(100);key_value varchar2(100);
  type count_map is table of number index by varchar2(100);counts count_map;
 begin
  if numbers.get_size<1 or numbers.get_size>200 or base_counts.get_size>200 then raise_application_error(-20881,'PLAN_FLOOR_SOURCE_BOUND_200');end if;
  for i in 0..base_counts.get_size-1 loop
   entry_value:=treat(base_counts.get(i) as json_object_t);key_value:=to_char(entry_value.get_number('pallet_type_id'),'TM9');
   counts(key_value):=entry_value.get_number('places');
  end loop;
  query_value:='select /* PLAN_LOADED_TOP_BOUND1197 */ l.LOAD_OPERATION_ID,f.PALLET_TYPE_ID,l.VEHICLE_ID,f.VEHICLE_ID from RRL_TT_HU_LOAD_FACT l left join RRL_TT_LOAD_FLOOR_FACT f on f.LOAD_OPERATION_ID=l.LOAD_OPERATION_ID where l.STATUS=''LOADED''and l.LOAD_OPERATION_ID in(select m.LOAD_OPERATION_ID from RRL_TT_HU_LOAD_ST m join RRL_SBORKA_PALLETS p on p.ID=m.SBORKA_PALLET_ID where m.ACTIVE_FLAG=1 and p.ST_NUMBER in(';
  for i in 0..numbers.get_size-1 loop
   if i>0 then query_value:=query_value||',';end if;query_value:=query_value||':st'||to_char(i,'FM999');
  end loop;
  query_value:=query_value||'))order by l.LOAD_OPERATION_ID fetch first 201 rows only';
  cursor_no:=dbms_sql.open_cursor;dbms_sql.parse(cursor_no,query_value,dbms_sql.native);
  for i in 0..numbers.get_size-1 loop
   el:=numbers.get(i);
   if not el.is_string then raise_application_error(-20886,'PLAN_FLOOR_ST_REQUIRED');end if;
   st_value:=numbers.get_string(i);
   if st_value is null then raise_application_error(-20886,'PLAN_FLOOR_ST_REQUIRED');end if;
   dbms_sql.bind_variable(cursor_no,':st'||to_char(i,'FM999'),st_value);
  end loop;
  ran:=dbms_sql.execute(cursor_no);rc:=dbms_sql.to_refcursor(cursor_no);cursor_no:=null;
  loop
   fetch rc into load_id,type_id,vehicle_id,floor_vehicle;exit when rc%notfound;
   load_count:=load_count+1;
   if load_count>200 then raise_application_error(-20881,'PLAN_FLOOR_LOADED_BOUND_200');end if;
   if vehicle_id!=p_vehicle then raise_application_error(-20886,'PLAN_FLOOR_LOADED_VEHICLE_CONFLICT');end if;
   if type_id is null or floor_vehicle!=p_vehicle then unknown_no:=unknown_no+1;
   else
    key_value:=to_char(type_id,'TM9');
    if counts.exists(key_value)then counts(key_value):=counts(key_value)+1;else counts(key_value):=1;end if;
   end if;
  end loop;close rc;
  key_value:=counts.first;
  while key_value is not null loop
   entry_value:=json_object_t();entry_value.put('pallet_type_id',to_number(key_value));entry_value.put('places',counts(key_value));wire_counts.append(entry_value);
   key_value:=counts.next(key_value);
  end loop;
  result.put('counts',wire_counts);result.put('unconfirmed_places',unknown_no);return result.to_clob;
 exception when others then
  if cursor_no is not null then if dbms_sql.is_open(cursor_no)then dbms_sql.close_cursor(cursor_no);end if;end if;
  if rc%isopen then close rc;end if;raise;
 end;
 procedure assert_load(p_vehicle number,p_trip number,p_frozen clob)is
  rows_value json_array_t:=json_array_t();current_value json_object_t;current_wire clob;n number;capacity_wire clob;frozen json_object_t;tree json_object_t:=json_object_t();node_value json_object_t:=json_object_t();nodes json_array_t:=json_array_t();
 begin
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),4);
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TR_VEHICLE',RRL_STOCK_PLAN_HELPER.decimal_text(p_vehicle)));
  if p_frozen is null then
   current_value:=current_matrix(p_vehicle);
   if current_value is not null then raise_application_error(-20890,'CLOSURE_CHANGED: new load floor profile');end if;
   return;
  end if;
  frozen:=json_object_t.parse(p_frozen);tree.put('root',frozen.get_string('root'));tree.put('warehouse',frozen.get_number('warehouse'));
  node_value.put('uid',frozen.get_string('root'));node_value.put('depth',0);
  if frozen.get_string('type_origin')='CASE_TYPE'then
   node_value.put('kind','CASE');node_value.put('case_task_id',to_number(frozen.get_string('source_reference')));
  else node_value.put('kind','CONTAINER');end if;
  nodes.append(node_value);tree.put('nodes',nodes);
  current_value:=compile_load(tree.to_clob,p_vehicle,rows_value);
  if p_frozen is null and current_value is null then return;end if;
  if p_frozen is null or current_value is null then raise_application_error(-20890,'CLOSURE_CHANGED: load floor profile');end if;
  current_wire:=current_value.to_clob;select count(*)into n from dual where json_equal(p_frozen,current_wire);
  if n!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: load top type/profile');end if;
  capacity_wire:=checked_trip(p_trip,p_vehicle,current_value.get_number('pallet_type_id'));
 end;
 procedure assert_departure(p_trip number,p_vehicle number,p_frozen clob)is current_wire clob;n number;
 begin
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),4);
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TR_VEHICLE',RRL_STOCK_PLAN_HELPER.decimal_text(p_vehicle)));
  current_wire:=checked_trip(p_trip,p_vehicle);
  if p_frozen is null and current_wire is null then return;end if;
  if p_frozen is null or current_wire is null then raise_application_error(-20890,'CLOSURE_CHANGED: depart floor profile');end if;
  select count(*)into n from dual where json_equal(p_frozen,current_wire);
  if n!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: depart floor cargo/profile');end if;
 end;
 procedure assert_writing(p_operation varchar2)is
 begin
  if not g_writing or g_operation is null or g_operation!=p_operation or g_tx is null
   or g_tx!=dbms_transaction.local_transaction_id(false)
   or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null
   or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')!=p_operation then raise_application_error(-20863,'LOAD_FLOOR_ROOT_OWNER_REQUIRED');end if;
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TT_HU_LOAD_FACT',p_operation));
 end;
 procedure persist_confirmation(p_operation varchar2,p_domain clob,p_actor varchar2)is
  d json_object_t;vehicle_no number;version_no number;type_no number;origin_value varchar2(24);reference_value varchar2(200);n number;
 begin
  if p_domain is null then return;end if;
  d:=json_object_t.parse(p_domain);vehicle_no:=d.get_number('vehicle_id');version_no:=d.get_number('profile_version');
  type_no:=d.get_number('pallet_type_id');origin_value:=d.get_string('type_origin');reference_value:=d.get_string('source_reference');
  select count(*)into n from RRL_TT_HU_LOAD_FACT l join RRL_STOCK_OPERATION o on o.OPERATION_ID=l.LOAD_OPERATION_ID
   where l.LOAD_OPERATION_ID=p_operation and l.VEHICLE_ID=vehicle_no and l.LOADED_BY=p_actor and l.STATUS='LOADED'and o.STATE='IN_FLIGHT';
  if n!=1 then raise_application_error(-20863,'LOAD_FLOOR_CURRENT_FACT_REQUIRED');end if;
  g_writing:=true;g_operation:=p_operation;g_tx:=dbms_transaction.local_transaction_id(false);
  insert into RRL_TT_LOAD_FLOOR_FACT(LOAD_OPERATION_ID,VEHICLE_ID,PROFILE_VERSION,PALLET_TYPE_ID,TYPE_ORIGIN,SOURCE_REFERENCE,ACTOR,CONFIRMATION_JSON)
   values(p_operation,vehicle_no,version_no,type_no,origin_value,reference_value,p_actor,p_domain);
  g_writing:=false;g_operation:=null;g_tx:=null;
 exception when others then g_writing:=false;g_operation:=null;g_tx:=null;raise;
 end;
end;
/
