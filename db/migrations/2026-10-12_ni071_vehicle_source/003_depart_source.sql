create or replace package RRL_VEH_DEPART_SOURCE authid definer accessible by(
 package RRL_STOCK_TRIP_DEPART_CMD,trigger RRL_TT_VEH_SOURCE_GUARD)as
 procedure capture_source(p_operation varchar2,p_trip number,p_vehicle number,p_instant timestamp with time zone);
 procedure assert_writing;
end;
/
create or replace package body RRL_VEH_DEPART_SOURCE as
 g_writing boolean:=false;
 procedure assert_writing is op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');k varchar2(80);state varchar2(20);
 begin
  if not g_writing or op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null
   or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
   then raise_application_error(-20863,'VEHICLE_SOURCE_ROOT_REQUIRED');end if;
  select COMMAND_TYPE,STATE into k,state from RRL_STOCK_OPERATION where OPERATION_ID=op;
  if k!='TRIP_DEPART'or state!='IN_FLIGHT'then raise_application_error(-20863,'VEHICLE_SOURCE_DEPART_REQUIRED');end if;
 end;
 procedure capture_source(p_operation varchar2,p_trip number,p_vehicle number,p_instant timestamp with time zone)is
  tt RRL_TRANSPORT_TASK%rowtype;veh RRL_TR_VEHICLE%rowtype;wire clob;domain_value json_object_t;
  profile json_object_t;j json_object_t:=json_object_t();source_state varchar2(24);profile_version number;
  source_wire clob;carrier varchar2(255);region_value varchar2(4000);n number;
 begin
  if p_operation!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')then raise_application_error(-20863,'VEHICLE_SOURCE_OPERATION_REQUIRED');end if;
  g_writing:=true;assert_writing;
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TT_VEHICLE_SOURCE',RRL_STOCK_PLAN_HELPER.decimal_text(p_trip)));
  select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=p_operation;
  domain_value:=json_object_t.parse(wire).get_object('domain');
  if domain_value.get_number('trip')!=p_trip or domain_value.get_number('vehicle_id')!=p_vehicle
   then raise_application_error(-20863,'VEHICLE_SOURCE_ORIGINAL_PLAN_REQUIRED');end if;
  select *into tt from RRL_TRANSPORT_TASK where ID=p_trip;select *into veh from RRL_TR_VEHICLE where ID=p_vehicle;
  select DOVERENNOST_OT into carrier from RRL_TR_VODITEL where ID=tt.VODITEL_ID and nvl(DELETED,0)=0;
  select count(*)into n from RRL_TT_HU_LOAD_FACT where TT_ID=p_trip and DEPARTURE_OPERATION_ID=p_operation
   and STATUS='DEPARTED'and DEPARTED_AT=p_instant;
  if n!=domain_value.get_array('loads').get_size or n<1 then raise_application_error(-20863,'VEHICLE_SOURCE_ORIGINAL_DEPARTURE_CLOCK');end if;
  profile:=json_object_t.parse(RRL_VEHICLE_PROFILE_API.describe_profile(p_vehicle));
  source_state:=profile.get_string('state');profile_version:=profile.get_number('version');if profile_version=0 then profile_version:=null;end if;
  region_value:=RRL_GET_TT_PRICE_ID(p_trip);
  j.put('departure_operation_id',p_operation);j.put('trip_id',p_trip);j.put('warehouse_id',domain_value.get_number('warehouse'));
  j.put('vehicle_id',p_vehicle);j.put('vehicle_number',veh.NUM);j.put('task_vehicle_type',tt.TRANSTYPE);
  j.put('driver_id',tt.VODITEL_ID);j.put('carrier_company',carrier);j.put('legacy_region_key',region_value);
  j.put('profile_state',source_state);j.put('vehicle_profile',profile);
  j.put('departed_at_instant',to_char(p_instant,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));
  source_wire:=j.to_clob;
  insert into RRL_TT_VEHICLE_SOURCE(TT_ID,DEPARTURE_OPERATION_ID,VEHICLE_ID,PROFILE_VERSION,SOURCE_STATE,SOURCE_JSON,CAPTURED_AT)
   values(p_trip,p_operation,p_vehicle,profile_version,source_state,source_wire,p_instant);
  g_writing:=false;
 exception when others then g_writing:=false;raise;end;
end;
/
