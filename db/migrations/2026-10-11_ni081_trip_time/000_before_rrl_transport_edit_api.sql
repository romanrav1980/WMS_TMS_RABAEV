create or replace package RRL_TRANSPORT_EDIT_API authid definer as
 procedure create_trip(p_type varchar2,p_day date,p_actor varchar2,p_trip out number);
 procedure update_trip(p_trip number,p_actor varchar2,p_body clob,p_result out clob);
end;
/

create or replace package body RRL_TRANSPORT_EDIT_API as
 procedure actor_allowed(p_actor varchar2)is n number;begin
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'transport_dispatch_edit')=1;
  if n!=1 then raise_application_error(-20882,'TRANSPORT_CURRENT_DISPATCHER_REQUIRED');end if;
 end;
 procedure create_trip(p_type varchar2,p_day date,p_actor varchar2,p_trip out number)is begin
  actor_allowed(p_actor);
  if p_type is null or lengthb(p_type)>10 or p_day is null or p_day!=trunc(p_day)then raise_application_error(-20886,'TRANSPORT_TYPE_DAY_REQUIRED');end if;
  p_trip:=RRL_TRASPORT_TASK_ADD(p_type,p_day,p_actor);update RRL_TRANSPORT_TASK set USER_ID=p_actor where ID=p_trip;
 end;
 procedure update_trip(p_trip number,p_actor varchar2,p_body clob,p_result out clob)is
  b json_object_t:=json_object_t.parse(p_body);old_trip RRL_TRANSPORT_TASK%rowtype;requested RRL_TRANSPORT_TASK%rowtype;
  before_num varchar2(50);new_num varchar2(50);old_vehicle number;new_vehicle number;v_id number;
  vehicle_ids json_array_t:=json_array_t();vehicles_text clob;sts json_array_t:=json_array_t();seen json_object_t:=json_object_t();
  v_count number:=0;v_actual_ware number;v_actual_st varchar2(100);v_global number;v_critical boolean;v_check clob;result json_object_t;
 begin
  actor_allowed(p_actor);
  select TRANSPORT into before_num from RRL_TRANSPORT_TASK where ID=p_trip;
  new_num:=case when b.has('transport')then b.get_string('transport')else before_num end;
  if before_num is not null then
   begin select ID into old_vehicle from RRL_TR_VEHICLE where NUM=before_num;exception when no_data_found then old_vehicle:=null;end;
  end if;
  if new_num is not null and b.has('transport')then select ID into new_vehicle from RRL_TR_VEHICLE where NUM=new_num;else new_vehicle:=old_vehicle;end if;
  if old_vehicle is not null then vehicle_ids.append(old_vehicle);end if;
  if new_vehicle is not null and nvl(old_vehicle,-1)!=new_vehicle then vehicle_ids.append(new_vehicle);end if;
  vehicles_text:=vehicle_ids.to_clob;
  for item in(select ID from json_table(vehicles_text,'$[*]'columns(ID number path '$'))order by ID)loop
   select ID into v_id from RRL_TR_VEHICLE where ID=item.ID for update;
  end loop;
  select *into old_trip from RRL_TRANSPORT_TASK where ID=p_trip for update;requested:=old_trip;
  if nvl(old_trip.TRANSPORT,'~')!=nvl(before_num,'~')then raise_application_error(-20886,'TRANSPORT_VEHICLE_CHANGED_RETRY');end if;
  if nvl(old_trip.DELETED,0)!=0 then raise_application_error(-20886,'TRANSPORT_ACTIVE_TRIP_REQUIRED');end if;
  requested.TRANSPORT:=new_num;
  if b.has('voditel_id')then
   requested.VODITEL_ID:=b.get_number('voditel_id');
   if requested.VODITEL_ID=0 then requested.VODITEL_ID:=null;end if;
   if requested.VODITEL_ID is not null then
    select count(*)into v_count from RRL_TR_VODITEL where ID=requested.VODITEL_ID and nvl(DELETED,0)=0;
    if v_count!=1 then raise_application_error(-20886,'TRANSPORT_CURRENT_DRIVER_REQUIRED');end if;
   end if;
  end if;
  if b.has('dock')then requested.DOCK:=b.get_string('dock');end if;
  if b.has('transtype')then requested.TRANSTYPE:=b.get_string('transtype');end if;
  if b.has('shipment_date')then requested.SHIPMENT_DATE:=to_date(b.get_string('shipment_date'),'YYYY-MM-DD');end if;
  if b.has('shipment_time')then requested.SHIPMENT_TIME:=to_date(b.get_string('shipment_time'),'HH24:MI');end if;
  if b.has('primechanie')then requested.PRIMECHANIE:=b.get_string('primechanie');end if;
  v_critical:=nvl(requested.TRANSPORT,'~')!=nvl(old_trip.TRANSPORT,'~')or nvl(requested.VODITEL_ID,-1)!=nvl(old_trip.VODITEL_ID,-1)
   or nvl(requested.DOCK,'~')!=nvl(old_trip.DOCK,'~')or nvl(requested.TRANSTYPE,'~')!=nvl(old_trip.TRANSTYPE,'~')
   or nvl(requested.SHIPMENT_DATE,date '1900-01-01')!=nvl(old_trip.SHIPMENT_DATE,date '1900-01-01')
   or nvl(requested.SHIPMENT_TIME,date '1900-01-01')!=nvl(old_trip.SHIPMENT_TIME,date '1900-01-01');
  if v_critical then
   if old_trip.CONDITION='Отгружен'or nvl(old_trip.PAY_ORDER_ID,0)>0 then raise_application_error(-20886,'TRANSPORT_PLAN_FROZEN');end if;
   select count(*)into v_count from RRL_TT_HU_LOAD_FACT where TT_ID=p_trip and STATUS in('LOADED','DEPARTED');
   if v_count>0 then raise_application_error(-20886,'TRIP_CONFIRMED_UNLOADING_REQUIRED_BEFORE_REASSIGNMENT');end if;
  end if;
  v_count:=0;
  for item in(select ID,ST_NUMBER,WARE_ID from RRL_SBORKA_PALLETS where TRANSTASK_ID=p_trip order by ID fetch first 201 rows only)loop
   v_count:=v_count+1;if v_count>200 then raise_application_error(-20886,'TRANSPORT_EDIT_SOURCE_BOUND_200');end if;
   select ID,WARE_ID,ST_NUMBER into v_id,v_actual_ware,v_actual_st from RRL_SBORKA_PALLETS where ID=item.ID for update;
   if v_actual_st!=item.ST_NUMBER then raise_application_error(-20886,'TRANSPORT_SOURCE_ST_CHANGED_RETRY');end if;
   RRL_TRANSPORT_PLAN_RULES.assert_actor(p_actor,v_actual_ware);
   if not seen.has(item.ST_NUMBER)then seen.put(item.ST_NUMBER,true);sts.append(item.ST_NUMBER);end if;
  end loop;
  if v_count=0 and nvl(old_trip.USER_ID,'~')!=p_actor then
   select count(*)into v_global from RUSERS where ID=p_actor and upper(trim(USER_GROUP))='GLOBAL_ADMIN';
   if v_global!=1 then raise_application_error(-20882,'TRANSPORT_EMPTY_TRIP_OWNER_REQUIRED');end if;
  end if;
  if v_critical then
   RRL_TRANSPORT_PLAN_RULES.check_vehicle(new_vehicle,sts.to_clob,0,v_check);result:=json_object_t.parse(v_check);
  else result:=json_object_t();result.put('validation_status','UNCHANGED_PLAN');end if;
  update RRL_TRANSPORT_TASK set TRANSPORT=requested.TRANSPORT,VODITEL_ID=requested.VODITEL_ID,DOCK=requested.DOCK,
   TRANSTYPE=requested.TRANSTYPE,SHIPMENT_DATE=requested.SHIPMENT_DATE,SHIPMENT_TIME=requested.SHIPMENT_TIME,
   PRIMECHANIE=requested.PRIMECHANIE,USER_ID=p_actor where ID=p_trip;
  result.put('task_id',p_trip);result.put('stock_changed',false);p_result:=result.to_clob;
 end;
end;
/
