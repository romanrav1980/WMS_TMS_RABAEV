create or replace package body RRL_STOCK_TRIP_DEPART_CMD as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t:=json_object_t();f json_array_t:=json_array_t();r json_array_t:=json_array_t();members json_array_t:=json_array_t();loads json_array_t:=json_array_t();
  trip_no number:=d.get_object('source').get_number('task_id');tt RRL_TRANSPORT_TASK%rowtype;vehicle_no number;ware_no number;n number:=0;promise_wire clob;thermal_value json_object_t;floor_wire clob;
 begin
  promise_wire:=RRL_INTERWARE_DEPART_GATE.promises(trip_no);RRL_INTERWARE_DEPART_GATE.assert_ready(promise_wire);
  select * into tt from RRL_TRANSPORT_TASK where ID=trip_no;
  select ID into vehicle_no from RRL_TR_VEHICLE where NUM=tt.TRANSPORT and nvl(DELETED,0)=0;
  select WARE_ID into ware_no from RRL_TT_DOCK where DOCK=tt.DOCK;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TRANSPORT_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(trip_no));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TR_VEHICLE',RRL_STOCK_PLAN_HELPER.decimal_text(vehicle_no));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TR_VODITEL',RRL_STOCK_PLAN_HELPER.decimal_text(tt.VODITEL_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_VEHICLE_SOURCE',RRL_STOCK_PLAN_HELPER.decimal_text(trip_no));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_DOCK',tt.DOCK);
  for sp in(select ID from RRL_SBORKA_PALLETS where TRANSTASK_ID=trip_no order by ID fetch first 201 rows only) loop
   n:=n+1;if n>200 then raise_application_error(-20881,'DEPART_MEMBER_ST_BOUND_200');end if;
   members.append(sp.ID);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(sp.ID));
  end loop;
  if n=0 then raise_application_error(-20886,'DEPART_ASSIGNED_ST_REQUIRED');end if;
  n:=0;
  for ld in(select LOAD_OPERATION_ID from RRL_TT_HU_LOAD_FACT where TT_ID=trip_no and STATUS='LOADED' order by LOAD_OPERATION_ID fetch first 201 rows only) loop
   n:=n+1;if n>200 then raise_application_error(-20881,'DEPART_PLACE_BOUND_200');end if;
   loads.append(ld.LOAD_OPERATION_ID);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_HU_LOAD_FACT',ld.LOAD_OPERATION_ID);
  end loop;
  if n=0 then raise_application_error(-20886,'DEPART_PHYSICAL_LOAD_REQUIRED');end if;
  floor_wire:=RRL_STOCK_LOAD_FLOOR.checked_trip(trip_no,vehicle_no);
  if floor_wire is null then v.put_null('floor_at_departure');else v.put('floor_at_departure',json_object_t.parse(floor_wire));end if;
  RRL_STOCK_LOAD_THERMAL.compile_confirmation(members.to_clob,vehicle_no,d.get_object('metadata').to_clob,thermal_value,'MANUAL_AT_DEPARTURE');
  if thermal_value is null then v.put_null('temperature_at_departure');else v.put('temperature_at_departure',thermal_value);end if;
  v.put('incoming_promises',json_array_t.parse(promise_wire));
  v.put('trip',trip_no);v.put('vehicle_id',vehicle_no);v.put('vehicle',tt.TRANSPORT);v.put('dock',tt.DOCK);v.put('warehouse',ware_no);v.put('driver_id',tt.VODITEL_ID);v.put('members',members);v.put('loads',loads);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 exception when no_data_found then raise_application_error(-20886,'DEPART_TRIP_VEHICLE_DOCK_CONFIGURATION_REQUIRED');
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);plan clob;v json_object_t;j json_object_t:=json_object_t();tt RRL_TRANSPORT_TASK%rowtype;veh RRL_TR_VEHICLE%rowtype;
  trip_no number;vehicle_no number;ware_no number;blocked_no number;places number;mass_no number;minimum_no number;member_ids clob;load_ids clob;n number;op varchar2(100):=d.get_string('operation_id');dock_name varchar2(50);promise_wire clob;depart_instant timestamp with time zone;thermal_element json_element_t;thermal_wire clob;floor_wire clob;floor_element json_element_t;
 begin
  if RRL_HAS_WRIGHT(p_actor,'transport_dispatch_close')!=1 then raise_application_error(-20882,'TRIP_DEPART_FORBIDDEN');end if;
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');
  trip_no:=v.get_number('trip');vehicle_no:=v.get_number('vehicle_id');dock_name:=v.get_string('dock');member_ids:=v.get_array('members').to_clob;load_ids:=v.get_array('loads').to_clob;
  select * into veh from RRL_TR_VEHICLE where ID=vehicle_no for update;
  select * into tt from RRL_TRANSPORT_TASK where ID=trip_no for update;
  select WARE_ID,nvl(DOCK_IS_BLOCKED,0) into ware_no,blocked_no from RRL_TT_DOCK where DOCK=dock_name for update;
  if tt.CONDITION is null or tt.CONDITION!=unistr('\0421\043F\043B\0430\043D\0438\0440\043E\0432\0430\043D') or nvl(tt.DELETED,0)!=0 or tt.TRANSPORT!=v.get_string('vehicle') or tt.DOCK!=dock_name or tt.VODITEL_ID is null
   or nvl(tt.VODITEL_ID,-1)!=nvl(v.get_number('driver_id'),-1) or veh.NUM!=tt.TRANSPORT or nvl(veh.BLOCKED,0)!=0 or nvl(veh.WORKING_NOW,0)!=1 or nvl(veh.DELETED,0)!=0 or ware_no!=v.get_number('warehouse') or blocked_no!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: departure assignment');end if;
  begin select ID into n from RRL_TR_VODITEL where ID=tt.VODITEL_ID and nvl(DELETED,0)=0 for update;
  exception when no_data_found then raise_application_error(-20886,'DEPART_ACTUAL_DRIVER_REQUIRED');end;
  n:=1;
  if n!=1 then raise_application_error(-20886,'DEPART_ACTUAL_DRIVER_REQUIRED');end if;
  promise_wire:=RRL_INTERWARE_DEPART_GATE.promises(trip_no);RRL_INTERWARE_DEPART_GATE.assert_ready(promise_wire);
  if dbms_lob.compare(promise_wire,v.get_array('incoming_promises').to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: expected incoming cargo');end if;
  for sp in(select ID from RRL_SBORKA_PALLETS where ID in(select ID from json_table(member_ids,'$[*]' columns(ID number path '$'))) order by ID) loop
   select ID into n from RRL_SBORKA_PALLETS where ID=sp.ID for update;
  end loop;
  select count(*) into n from RRL_SBORKA_PALLETS where TRANSTASK_ID=trip_no;
  if n!=v.get_array('members').get_size then raise_application_error(-20890,'CLOSURE_CHANGED: departure ST membership');end if;
  select count(*) into n from RRL_SBORKA_PALLETS sp where sp.TRANSTASK_ID=trip_no and(sp.CONDITION is null or sp.CONDITION!=2 or not exists(
   select 1 from RRL_TT_HU_LOAD_ST ls join RRL_TT_HU_LOAD_FACT lf on lf.LOAD_OPERATION_ID=ls.LOAD_OPERATION_ID
    join RRL_STOCK_OPERATION operation_record on operation_record.OPERATION_ID=lf.LOAD_OPERATION_ID and operation_record.STATE='APPLIED'
   where ls.SBORKA_PALLET_ID=sp.ID and lf.TT_ID=trip_no and lf.VEHICLE_ID=vehicle_no and lf.VEHICLE_NUMBER=tt.TRANSPORT and lf.DOCK=dock_name and lf.STATUS='LOADED'));
  if n>0 then raise_application_error(-20886,'DEPART_WAITING_FOR_ACTUAL_LOADED_STS');end if;
  select count(*),nvl(sum(GROSS_WEIGHT_KG),0) into places,mass_no from RRL_TT_HU_LOAD_FACT where TT_ID=trip_no and STATUS='LOADED';
  if places!=v.get_array('loads').get_size then raise_application_error(-20890,'CLOSURE_CHANGED: departure physical places');end if;
  if v.has('floor_at_departure')then floor_element:=v.get('floor_at_departure');if not floor_element.is_null then floor_wire:=floor_element.to_clob;end if;end if;
  RRL_STOCK_LOAD_FLOOR.assert_departure(trip_no,vehicle_no,floor_wire);
  select nvl(MIN_PALLET_LOAD,0) into minimum_no from RRL_TRANSPORT_TYPE where TRANSPORTTYPE=veh.TR_TYPE;
  if veh.PALLETS is null or veh.MAX_WEIGHT_KG is null or(floor_wire is null and places>veh.PALLETS)or mass_no>veh.MAX_WEIGHT_KG then raise_application_error(-20886,'DEPART_PHYSICAL_CAPACITY_EXCEEDED');end if;
  if places<minimum_no and RRL_HAS_WRIGHT(p_actor,'SEND_EMPTY_TRUCK')!=1 then raise_application_error(-20886,'DEPART_BELOW_MINIMUM_PHYSICAL_LOAD');end if;
  if v.has('temperature_at_departure')then thermal_element:=v.get('temperature_at_departure');if not thermal_element.is_null then thermal_wire:=thermal_element.to_clob;end if;end if;
  RRL_STOCK_LOAD_THERMAL.assert_current(member_ids,vehicle_no,thermal_wire,'MANUAL_AT_DEPARTURE');
  depart_instant:=systimestamp;
  for ld in(select ID from json_table(load_ids,'$[*]' columns(ID varchar2(100) path '$')) order by ID) loop
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TT_HU_LOAD_FACT',ld.ID));
   update RRL_TT_HU_LOAD_FACT set STATUS='DEPARTED',DEPARTURE_OPERATION_ID=op,DEPARTED_AT=depart_instant where LOAD_OPERATION_ID=ld.ID and TT_ID=trip_no and STATUS='LOADED';
   if sql%rowcount!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: departure load fact');end if;
  end loop;
  update RRL_TRANSPORT_TASK set CONDITION=unistr('\041E\0442\0433\0440\0443\0436\0435\043D'),USER_ID=p_actor where ID=trip_no;
  RRL_VEH_DEPART_SOURCE.capture_source(op,trip_no,vehicle_no,depart_instant);
  if floor_wire is not null then j.put('floor_at_departure',json_object_t.parse(floor_wire));end if;
  if thermal_wire is not null then j.put('temperature_at_departure',json_object_t.parse(thermal_wire));j.put('temperature_confirmed_at',to_char(depart_instant,'YYYY-MM-DD"T"HH24:MI:SS.FF3TZH:TZM'));end if;
  j.put('operation_id',op);j.put('task_id',trip_no);j.put('status','DEPARTED');j.put('physical_places',places);j.put('gross_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(mass_no));j.put('stock_consumed_again',false);p_result:=j.to_clob;
 exception when no_data_found then raise_application_error(-20886,'DEPART_CONFIGURATION_REQUIRED');
 end;
end;
/
