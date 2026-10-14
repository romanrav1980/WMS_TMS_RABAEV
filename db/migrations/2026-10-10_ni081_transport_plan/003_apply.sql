create or replace package RRL_TRANSPORT_PLAN_API authid definer as
 function apply_write_allowed(p_plan number)return number;
 procedure apply_plan(p_plan number,p_day date,p_dock varchar2,p_actor varchar2,p_result out clob);
 procedure assign_sts(p_tt number,p_sts clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_TRANSPORT_PLAN_API as
 g_plan number;g_tx varchar2(100);
 function apply_write_allowed(p_plan number)return number is begin
  if g_plan=p_plan and g_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;end;
 procedure basic_actor(p_actor varchar2)is n number;begin
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'transport_dispatch_edit')=1;
  if n!=1 then raise_application_error(-20882,'PLAN_ACTIVE_DISPATCHER_REQUIRED');end if;
 end;
 procedure lock_vehicle(p_id number)is v_id number;begin
  select ID into v_id from RRL_TR_VEHICLE where ID=p_id for update;
 end;
 procedure lock_trip(p_tt number,p_expected_vehicle varchar2)is v RRL_TRANSPORT_TASK%rowtype;begin
  select *into v from RRL_TRANSPORT_TASK where ID=p_tt for update;
  if nvl(v.DELETED,0)!=0 or v.CONDITION='Отгружен'or nvl(v.PAY_ORDER_ID,0)>0 then raise_application_error(-20886,'PLAN_ACTIVE_UNBILLED_TRIP_REQUIRED');end if;
  if nvl(v.TRANSPORT,'~')!=nvl(p_expected_vehicle,'~')then raise_application_error(-20886,'PLAN_VEHICLE_CHANGED_RETRY');end if;
 end;
 procedure write_members(p_tt number,p_sts json_array_t)is v_answer varchar2(4000);v_order number;v_number varchar2(100);begin
  for i in 0..p_sts.get_size-1 loop
   v_number:=p_sts.get_string(i);v_answer:=RRL_TT_ADD_PALL(p_tt,v_number);
   if lower(substr(nvl(v_answer,'OK'),1,3))='err'then raise_application_error(-20886,'PLAN_NATIVE_ST_WRITER_FAILED');end if;
  end loop;
  v_order:=RRL_TT_REORDER_ADR(p_tt);
 end;
 procedure assign_sts(p_tt number,p_sts clob,p_actor varchar2,p_result out clob)is
  v_num varchar2(100);v_vehicle number;v_requested json_array_t:=json_array_t.parse(p_sts);
  v_prospective json_array_t:=json_array_t();v_seen json_object_t:=json_object_t();v_count number:=0;v_old number;v_state number;v_check clob;v_out json_object_t;
 begin
  basic_actor(p_actor);
  if v_requested.get_size not between 1 and 200 then raise_application_error(-20886,'PLAN_SELECT_1_200_STS');end if;
  select TRANSPORT into v_num from RRL_TRANSPORT_TASK where ID=p_tt;
  if v_num is not null then select ID into v_vehicle from RRL_TR_VEHICLE where NUM=v_num;lock_vehicle(v_vehicle);end if;
  lock_trip(p_tt,v_num);
  for item in(select ID,ST_NUMBER from(
   select ID,ST_NUMBER from RRL_SBORKA_PALLETS where TRANSTASK_ID=p_tt
   union
   select p.ID,p.ST_NUMBER from RRL_SBORKA_PALLETS p join
    json_table(p_sts,'$[*]'columns(ST_NUMBER varchar2(100)path '$'))j on j.ST_NUMBER=p.ST_NUMBER)
   order by ID fetch first 201 rows only)loop
   v_count:=v_count+1;if v_count>200 then raise_application_error(-20886,'PLAN_ROUTE_ACTUAL_ROW_BOUND_200');end if;
   select TRANSTASK_ID,CONDITION into v_old,v_state from RRL_SBORKA_PALLETS where ID=item.ID for update;
   if nvl(v_old,0)not in(0,p_tt)or v_state=2 then raise_application_error(-20886,'PLAN_ST_FOREIGN_OR_SHIPPED');end if;
   for ware in(select WARE_ID from RRL_SBORKA_PALLETS where ID=item.ID)loop RRL_TRANSPORT_PLAN_RULES.assert_actor(p_actor,ware.WARE_ID);end loop;
   if not v_seen.has(item.ST_NUMBER)then v_prospective.append(item.ST_NUMBER);v_seen.put(item.ST_NUMBER,true);end if;
  end loop;
  for i in 0..v_requested.get_size-1 loop if not v_seen.has(v_requested.get_string(i))then raise_application_error(-20886,'PLAN_ST_NOT_FOUND');end if;end loop;
  RRL_TRANSPORT_PLAN_RULES.check_vehicle(v_vehicle,v_prospective.to_clob,0,v_check);
  write_members(p_tt,v_requested);v_out:=json_object_t.parse(v_check);v_out.put('assigned',v_requested.get_size);p_result:=v_out.to_clob;
 end;
 procedure apply_plan(p_plan number,p_day date,p_dock varchar2,p_actor varchar2,p_result out clob)is
  v_saved RRL_PLANNER_APPLY_RESULT%rowtype;v_raw clob;v_hash varchar2(64);v_applied date;v_doc json_object_t;
  v_routes json_array_t;v_route json_object_t;v_stops json_array_t;v_all json_array_t:=json_array_t();
  v_vehicles json_array_t:=json_array_t();v_wares json_array_t:=json_array_t();v_seen_st json_object_t:=json_object_t();v_seen_vehicle json_object_t:=json_object_t();v_seen_ware json_object_t:=json_object_t();
  type ids is table of number index by pls_integer;v_trips ids;v_vehicle_ids ids;
  v_vehicle RRL_TR_VEHICLE%rowtype;v_number varchar2(100);v_actual_ware number;v_current number;v_state number;v_found json_object_t:=json_object_t();v_row_count number:=0;v_check clob;v_all_text clob;v_vehicle_text clob;v_row_text clob;v_rows json_array_t:=json_array_t();v_found_keys json_key_list;
  v_result json_object_t:=json_object_t();v_created json_array_t:=json_array_t();v_key varchar2(100);v_declared_num varchar2(100);
 begin
  g_plan:=null;g_tx:=null;basic_actor(p_actor);
  if p_day is null or p_day!=trunc(p_day)then raise_application_error(-20886,'PLAN_SHIPMENT_DAY_REQUIRED');end if;
  select PAYLOAD,APPLIED_AT into v_raw,v_applied from RRL_PLANNER_PLANS where ID=p_plan for update;
  if dbms_lob.getlength(v_raw)>4194304 then raise_application_error(-20886,'PLAN_SOURCE_BOUND_4MB');end if;
  v_hash:=lower(rawtohex(sys.dbms_crypto.hash(v_raw,sys.dbms_crypto.hash_sh256)));
  begin select *into v_saved from RRL_PLANNER_APPLY_RESULT where PLAN_ID=p_plan;
   if v_saved.SOURCE_HASH!=v_hash or v_saved.SHIPMENT_DATE!=p_day or nvl(v_saved.DOCK,'~')!=nvl(p_dock,'~')or v_saved.ACTOR!=p_actor then raise_application_error(-20886,'PLAN_APPLY_PAYLOAD_CONFLICT');end if;
   v_doc:=json_object_t.parse(v_saved.RESULT_JSON);v_wares:=v_doc.get_array('warehouse_ids');
   for i in 0..v_wares.get_size-1 loop RRL_TRANSPORT_PLAN_RULES.assert_actor(p_actor,v_wares.get_number(i));end loop;
   p_result:=v_saved.RESULT_JSON;return;
  exception when no_data_found then null;end;
  if v_applied is not null then raise_application_error(-20886,'PLAN_LEGACY_APPLY_RECONCILIATION_REQUIRED');end if;
  v_doc:=json_object_t.parse(v_raw);v_routes:=v_doc.get_array('routes');
  if v_routes is null or v_routes.get_size not between 1 and 100 then raise_application_error(-20886,'PLAN_ROUTE_BOUND_1_100');end if;
  for i in 0..v_routes.get_size-1 loop
   v_route:=treat(v_routes.get(i)as json_object_t);v_vehicle_ids(i):=v_route.get_number('vehicle_id');v_key:=to_char(v_vehicle_ids(i),'TM9');
   if v_vehicle_ids(i)is null or v_vehicle_ids(i)<=0 or v_seen_vehicle.has(v_key)then raise_application_error(-20886,'PLAN_DISTINCT_CURRENT_VEHICLES_REQUIRED');end if;
   v_seen_vehicle.put(v_key,true);v_vehicles.append(v_vehicle_ids(i));v_stops:=v_route.get_array('stops');
   if v_stops is null or v_stops.get_size not between 1 and 200 then raise_application_error(-20886,'PLAN_ROUTE_ST_BOUND_1_200');end if;
   for j in 0..v_stops.get_size-1 loop
    v_number:=v_stops.get_string(j);
    if v_number is null or length(v_number)>100 or v_seen_st.has(v_number)then raise_application_error(-20886,'PLAN_DUPLICATE_OR_INVALID_ST');end if;
    v_seen_st.put(v_number,true);v_all.append(v_number);
   end loop;
  end loop;
  if v_all.get_size>2000 then raise_application_error(-20886,'PLAN_ST_BOUND_2000');end if;
  v_all_text:=v_all.to_clob;v_vehicle_text:=v_vehicles.to_clob;
  for item in(select ID from json_table(v_vehicle_text,'$[*]'columns(ID number path '$'))order by ID)loop lock_vehicle(item.ID);end loop;
  for item in(select ID,ST_NUMBER,WARE_ID from RRL_SBORKA_PALLETS where ST_NUMBER in
   (select ST_NUMBER from json_table(v_all_text,'$[*]'columns(ST_NUMBER varchar2(100)path '$')))order by ID fetch first 5001 rows only)loop
   v_row_count:=v_row_count+1;v_rows.append(item.ID);if v_row_count>5000 then raise_application_error(-20886,'PLAN_ACTUAL_ROWS_BOUND_5000');end if;
   -- Source discovery/recheck before creating TT; actual row locking happens below after new TT.
   select TRANSTASK_ID,CONDITION into v_current,v_state from RRL_SBORKA_PALLETS where ID=item.ID;
   if nvl(v_current,0)!=0 or v_state=2 then raise_application_error(-20886,'PLAN_ST_ALREADY_ASSIGNED_OR_SHIPPED');end if;
   RRL_TRANSPORT_PLAN_RULES.assert_actor(p_actor,item.WARE_ID);v_found.put(item.ST_NUMBER,true);
   v_key:=to_char(item.WARE_ID,'TM9');if not v_seen_ware.has(v_key)then v_seen_ware.put(v_key,true);v_wares.append(item.WARE_ID);end if;
  end loop;
  v_found_keys:=v_found.get_keys;
  if v_found_keys.count!=v_all.get_size then raise_application_error(-20886,'PLAN_CURRENT_ST_SET_CHANGED');end if;
  for i in 0..v_routes.get_size-1 loop
   v_route:=treat(v_routes.get(i)as json_object_t);v_stops:=v_route.get_array('stops');
   select *into v_vehicle from RRL_TR_VEHICLE where ID=v_vehicle_ids(i);
   v_declared_num:=v_route.get_string('vehicle_num');
   if v_declared_num!=v_vehicle.NUM or v_declared_num is null then raise_application_error(-20886,'PLAN_VEHICLE_ID_PLATE_CONFLICT');end if;
   RRL_TRANSPORT_PLAN_RULES.check_vehicle(v_vehicle.ID,v_stops.to_clob,1,v_check);
   v_trips(i):=RRL_TRASPORT_TASK_ADD(v_vehicle.TR_TYPE,p_day,p_actor);
   update RRL_TRANSPORT_TASK set TRANSPORT=v_vehicle.NUM,DOCK=p_dock,USER_ID=p_actor where ID=v_trips(i);
   lock_trip(v_trips(i),v_vehicle.NUM);v_created.append(v_trips(i));
  end loop;
  v_row_text:=v_rows.to_clob;
  for item in(select ID from json_table(v_row_text,'$[*]'columns(ID number path '$'))order by ID)loop
   select TRANSTASK_ID,CONDITION,WARE_ID into v_current,v_state,v_actual_ware from RRL_SBORKA_PALLETS where ID=item.ID for update;
   RRL_TRANSPORT_PLAN_RULES.assert_actor(p_actor,v_actual_ware);
   if nvl(v_current,0)!=0 or v_state=2 then raise_application_error(-20886,'PLAN_ST_CHANGED_DURING_APPLY');end if;
  end loop;
  for i in 0..v_routes.get_size-1 loop
   v_route:=treat(v_routes.get(i)as json_object_t);v_stops:=v_route.get_array('stops');
   RRL_TRANSPORT_PLAN_RULES.check_vehicle(v_vehicle_ids(i),v_stops.to_clob,1,v_check);write_members(v_trips(i),v_stops);
   for j in 0..v_stops.get_size-1 loop v_number:=v_stops.get_string(j);update RRL_SBORKA_PALLETS set ORD=j+1 where ST_NUMBER=v_number and TRANSTASK_ID=v_trips(i);end loop;
  end loop;
  select count(*)into v_current from RRL_SBORKA_PALLETS where ST_NUMBER in
   (select ST_NUMBER from json_table(v_all_text,'$[*]'columns(ST_NUMBER varchar2(100)path '$')));
  if v_current!=v_row_count then raise_application_error(-20886,'PLAN_SOURCE_ROWS_CHANGED_RETRY');end if;
  v_result.put('source_member_ids',v_rows);
  v_result.put('plan_id',p_plan);v_result.put('tasks_created',v_routes.get_size);v_result.put('created_task_ids',v_created);v_result.put('warehouse_ids',v_wares);
  v_result.put('validation_scope','DECLARED_CAPACITY_TYPE_HYDRO');v_result.put('physical_load_admission',false);
  v_result.put('stock_changed',false);v_result.put('driver_inferred_from_vehicle',false);v_result.put('application_status','APPLIED');p_result:=v_result.to_clob;
  g_plan:=p_plan;g_tx:=dbms_transaction.local_transaction_id(true);
  insert into RRL_PLANNER_APPLY_RESULT(PLAN_ID,SOURCE_HASH,SHIPMENT_DATE,DOCK,ACTOR,RESULT_JSON)values(p_plan,v_hash,p_day,p_dock,p_actor,p_result);
  update RRL_PLANNER_PLANS set APPLIED_AT=sysdate,STATUS='APPLIED'where ID=p_plan;g_plan:=null;g_tx:=null;
 exception when others then g_plan:=null;g_tx:=null;raise;
 end;
end;
/
