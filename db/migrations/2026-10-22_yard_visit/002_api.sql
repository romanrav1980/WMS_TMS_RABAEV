create or replace package RRL_YARD_VISIT_API authid definer as
 -- Yard visit of one TRADECASE site: EXPECTED -> ARRIVED (queue) -> AT_DOCK -> WORKING -> WORK_DONE -> DEPARTED, CANCELLED before work.
 -- No stock, reservation or loading effect: the loading/departure facts stay in their own commands.
 procedure command(p_ware number,p_request clob,p_actor varchar2,p_result out clob);
 function visits(p_ware number,p_actor varchar2,p_active number)return clob;
end;
/
create or replace package body RRL_YARD_VISIT_API as
 procedure fail(p_code varchar2)is begin raise_application_error(-20911,p_code);end;
 function sha(p_text clob)return varchar2 is begin return lower(rawtohex(sys.dbms_crypto.hash(p_text,sys.dbms_crypto.hash_sh256)));end;
 function stamp(p_value timestamp with time zone)return varchar2 is
 begin return case when p_value is null then null else to_char(p_value at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS"Z"')end;end;

 -- Same order as the other TRADECASE writers: current access revision, then the site row, then the visit.
 procedure lock_site(p_ware number)is n number;
 begin
  lock table RRL_ACCESS_REV in share mode wait 5;
  select ENABLED into n from RRL_TRADE_SITE where WARE_ID=p_ware for update;
  if n<>1 then fail('TRADE_SITE_DISABLED');end if;
 exception when no_data_found then fail('TRADE_SITE_REQUIRED');
 end;

 procedure require(p_actor varchar2,p_permission varchar2,p_ware number)is n number;
 begin
  select RRL_ACCESS_API.allowed(p_actor,p_permission,'WAREHOUSE',to_char(p_ware))into n from dual;
  if n<>1 then raise_application_error(-20882,'YARD_ACCESS_DENIED');end if;
 end;

 -- An outbound visit carries the trip's goods: every owner of its orders must be operable by the actor.
 -- An actor who may not even read an owner gets p_hidden, the same answer as for a missing trip/visit: nothing about it leaks.
 procedure require_owners(p_actor varchar2,p_ware number,p_trip varchar2,p_write number,p_hidden varchar2)is body clob;
 begin
  if p_trip is null then return;end if;
  begin select BODY_JSON into body from RRL_TRADE_DOCUMENT where WARE_ID=p_ware and ENTITY_TYPE='TRIP'and EXTERNAL_ID=p_trip and STATUS='ACCEPTED';
  exception when no_data_found then fail(p_hidden);end;
  for o in(select distinct ol.SOURCE_OWNER_ID OWNER from json_table(body,'$.orders[*]'columns(ORDER_ID varchar2(100)path'$.order_id'))t
    join RRL_TRADE_ORDER_LINK l on l.WARE_ID=p_ware and l.EXTERNAL_ID=t.ORDER_ID join RRL_TRADE_ORDER_LINE ol on ol.CUSTOMER_ORDER_ID=l.CUSTOMER_ORDER_ID)loop
   if RRL_TRADE_STOCK_GUARD.owner_allowed(p_actor,p_ware,o.OWNER,0)<>1 then fail(p_hidden);end if;
   if p_write=1 then RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,p_ware,o.OWNER,1);end if;
  end loop;
 end;

 function card(v RRL_YARD_VISIT%rowtype)return json_object_t is j json_object_t:=json_object_t();planned_dock varchar2(50);
 begin
  if v.NATIVE_TASK_ID is not null then
   begin select DOCK into planned_dock from RRL_TRANSPORT_TASK where ID=v.NATIVE_TASK_ID;exception when no_data_found then null;end;
  end if;
  j.put('planned_dock',planned_dock);
  j.put('visit_id',v.VISIT_ID);j.put('warehouse_id',v.WARE_ID);j.put('visit_kind',v.VISIT_KIND);j.put('trip_id',v.TRIP_ID);
  j.put('native_task_id',v.NATIVE_TASK_ID);j.put('vehicle',v.VEHICLE);j.put('dock',v.DOCK);j.put('state',v.STATE);j.put('version',v.VERSION_NO);
  j.put('planned_arrival_at',stamp(v.PLANNED_ARRIVAL_AT));j.put('arrived_at',stamp(v.ARRIVED_AT));j.put('docked_at',stamp(v.DOCKED_AT));
  j.put('work_started_at',stamp(v.WORK_STARTED_AT));j.put('work_finished_at',stamp(v.WORK_FINISHED_AT));j.put('departed_at',stamp(v.DEPARTED_AT));
  j.put('cancelled_at',stamp(v.CANCELLED_AT));j.put('cancel_reason',v.CANCEL_REASON);j.put('updated_by',v.UPDATED_BY);
  return j;
 end;

 procedure assert_dock(p_ware number,p_dock varchar2,p_visit number)is n number;blocked number;
 begin
  select count(*),max(nvl(DOCK_IS_BLOCKED,0))into n,blocked from RRL_TT_DOCK where WARE_ID=p_ware and DOCK=p_dock;
  if n=0 then fail('YARD_DOCK_UNKNOWN');end if;
  if n>1 then fail('YARD_DOCK_AMBIGUOUS');end if;
  if blocked<>0 then fail('YARD_DOCK_BLOCKED');end if;  -- a broken/blocked dock is never assigned
  select count(*)into n from RRL_YARD_VISIT where WARE_ID=p_ware and DOCK=p_dock and STATE in('AT_DOCK','WORKING','WORK_DONE')and VISIT_ID<>p_visit;
  if n>0 then fail('YARD_DOCK_OCCUPIED');end if;
 end;

 procedure expect(p_ware number,d json_object_t,p_op varchar2,p_hash varchar2,p_actor varchar2,p_result out clob)is
  v RRL_YARD_VISIT%rowtype;trip varchar2(100):=d.get_string('trip_id');kind varchar2(12):=nvl(d.get_string('visit_kind'),'OUTBOUND');
  planned varchar2(40):=d.get_string('planned_arrival_at');n number;
 begin
  if kind not in('OUTBOUND','INBOUND')or(kind='OUTBOUND'and trip is null)then fail('YARD_REQUEST_INVALID');end if;
  require_owners(p_actor,p_ware,trip,1,'YARD_TRIP_REQUIRED');
  select count(*)into n from RRL_YARD_VISIT where WARE_ID=p_ware and TRIP_ID=trip and STATE not in('DEPARTED','CANCELLED');
  if n>0 then fail('YARD_TRIP_VISIT_ACTIVE');end if;
  v.VISIT_ID:=RRL_YARD_VISIT_SQ.nextval;v.WARE_ID:=p_ware;v.VISIT_KIND:=kind;v.TRIP_ID:=trip;v.STATE:='EXPECTED';v.VERSION_NO:=1;
  begin select NATIVE_TASK_ID into v.NATIVE_TASK_ID from RRL_TRADE_TRIP_LINK where WARE_ID=p_ware and TRIP_ID=trip;
  exception when no_data_found then null;end;
  -- The vehicle is the trip's own; it is never typed in to fit the yard.
  if v.NATIVE_TASK_ID is not null then select TRANSPORT into v.VEHICLE from RRL_TRANSPORT_TASK where ID=v.NATIVE_TASK_ID;end if;
  if planned is not null then v.PLANNED_ARRIVAL_AT:=to_timestamp_tz(planned,'YYYY-MM-DD"T"HH24:MI:SSTZH:TZM');end if;
  v.CREATED_BY:=p_actor;v.UPDATED_BY:=p_actor;v.CREATED_AT:=systimestamp;v.UPDATED_AT:=systimestamp;
  insert into RRL_YARD_VISIT values v;
  p_result:=card(v).to_clob;
  insert into RRL_YARD_VISIT_EVENT(OPERATION_ID,WARE_ID,VISIT_ID,ACTION,FROM_STATE,TO_STATE,REQUEST_HASH,ACTOR,RESULT_JSON)
   values(p_op,p_ware,v.VISIT_ID,'EXPECT',null,'EXPECTED',p_hash,p_actor,p_result);
 exception when dup_val_on_index then fail('YARD_TRIP_VISIT_ACTIVE');
 end;

 procedure transition(p_ware number,d json_object_t,p_op varchar2,p_hash varchar2,p_actor varchar2,p_result out clob)is
  v RRL_YARD_VISIT%rowtype;action varchar2(20):=d.get_string('action');id_value number:=d.get_number('visit_id');
  expected number:=d.get_number('expected_version');dock varchar2(50):=d.get_string('dock');reason varchar2(500):=d.get_string('reason');from_state varchar2(12);n number;
 begin
  begin select*into v from RRL_YARD_VISIT where VISIT_ID=id_value and WARE_ID=p_ware for update;
  exception when no_data_found then fail('YARD_VISIT_NOT_FOUND');end;
  require_owners(p_actor,p_ware,v.TRIP_ID,1,'YARD_VISIT_NOT_FOUND');
  if expected is null or expected<>v.VERSION_NO then fail('VERSION_CONFLICT');end if;
  from_state:=v.STATE;
  if action='ARRIVE'and v.STATE='EXPECTED'then
   -- Checked before the update under the site lock (all writers of this warehouse are serialized); the unique index stays the last guard.
   select count(*)into n from RRL_YARD_VISIT where WARE_ID=p_ware and VEHICLE=v.VEHICLE and STATE in('ARRIVED','AT_DOCK','WORKING','WORK_DONE');
   if n>0 then fail('YARD_VEHICLE_OCCUPIED');end if;
   v.STATE:='ARRIVED';v.ARRIVED_AT:=systimestamp;
  elsif action='ASSIGN_DOCK'and v.STATE='ARRIVED'or action='REASSIGN_DOCK'and v.STATE='AT_DOCK'then
   if dock is null or dock=v.DOCK then fail('YARD_REQUEST_INVALID');end if;
   assert_dock(p_ware,dock,v.VISIT_ID);v.DOCK:=dock;v.STATE:='AT_DOCK';v.DOCKED_AT:=systimestamp;
  elsif action='START'and v.STATE='AT_DOCK'then v.STATE:='WORKING';v.WORK_STARTED_AT:=systimestamp;
  elsif action='FINISH'and v.STATE='WORKING'then v.STATE:='WORK_DONE';v.WORK_FINISHED_AT:=systimestamp;
  elsif action='DEPART'and v.STATE='WORK_DONE'then v.STATE:='DEPARTED';v.DEPARTED_AT:=systimestamp;  -- releases the dock
  elsif action='CANCEL'and v.STATE in('EXPECTED','ARRIVED','AT_DOCK')then
   if reason is null then fail('YARD_CANCEL_REASON_REQUIRED');end if;
   v.STATE:='CANCELLED';v.CANCELLED_AT:=systimestamp;v.CANCEL_REASON:=substr(reason,1,500);
  else fail('YARD_STATE_CONFLICT');end if;
  v.VERSION_NO:=v.VERSION_NO+1;v.UPDATED_BY:=p_actor;v.UPDATED_AT:=systimestamp;
  update RRL_YARD_VISIT set row=v where VISIT_ID=v.VISIT_ID;
  p_result:=card(v).to_clob;
  insert into RRL_YARD_VISIT_EVENT(OPERATION_ID,WARE_ID,VISIT_ID,ACTION,FROM_STATE,TO_STATE,DOCK,REQUEST_HASH,ACTOR,RESULT_JSON)
   values(p_op,p_ware,v.VISIT_ID,action,from_state,v.STATE,v.DOCK,p_hash,p_actor,p_result);
 exception when dup_val_on_index then fail('YARD_DOCK_OR_VEHICLE_OCCUPIED');  -- concurrent dispatcher lost the race
 end;

 procedure command(p_ware number,p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');hash_value varchar2(64):=sha(p_request);
  e RRL_YARD_VISIT_EVENT%rowtype;j json_object_t;v RRL_YARD_VISIT%rowtype;
 begin
  if op is null or lengthb(op)>100 or not regexp_like(op,'^[A-Za-z0-9_.:-]+$')then fail('YARD_REQUEST_INVALID');end if;
  lock_site(p_ware);
  -- Current rights are checked before any cached answer: a revoked user does not get the old result back.
  require(p_actor,'tradecase_yard_operate',p_ware);
  begin
   select*into e from RRL_YARD_VISIT_EVENT where OPERATION_ID=op;
   if e.WARE_ID<>p_ware then fail('YARD_OPERATION_CONFLICT');end if;
   select*into v from RRL_YARD_VISIT where VISIT_ID=e.VISIT_ID;
   -- Owner rights of today, before anything about the stored operation is revealed.
   require_owners(p_actor,p_ware,v.TRIP_ID,1,'YARD_VISIT_NOT_FOUND');
   if e.REQUEST_HASH<>hash_value then fail('YARD_OPERATION_CONFLICT');end if;
   j:=json_object_t.parse(e.RESULT_JSON);j.put('replayed',true);p_result:=j.to_clob;return;
  exception when no_data_found then null;end;
  if d.get_string('action')='EXPECT'then expect(p_ware,d,op,hash_value,p_actor,p_result);
  else transition(p_ware,d,op,hash_value,p_actor,p_result);end if;
  j:=json_object_t.parse(p_result);j.put('replayed',false);p_result:=j.to_clob;
 end;

 function visits(p_ware number,p_actor varchar2,p_active number)return clob is a json_array_t:=json_array_t();j json_object_t;n number;visible boolean;r json_object_t:=json_object_t();
  v RRL_YARD_VISIT%rowtype;
 begin
  select RRL_ACCESS_API.allowed(p_actor,'tradecase_view','WAREHOUSE',to_char(p_ware))into n from dual;
  if n<>1 then raise_application_error(-20882,'YARD_ACCESS_DENIED');end if;
  for x in(select VISIT_ID from RRL_YARD_VISIT where WARE_ID=p_ware and(p_active=0 or STATE not in('DEPARTED','CANCELLED'))
    order by case STATE when 'WORKING'then 1 when 'AT_DOCK'then 2 when 'WORK_DONE'then 3 when 'ARRIVED'then 4 when 'EXPECTED'then 5 else 6 end,
     nvl(ARRIVED_AT,PLANNED_ARRIVAL_AT),VISIT_ID fetch first 200 rows only)loop
   select*into v from RRL_YARD_VISIT where VISIT_ID=x.VISIT_ID;
   visible:=true;
   begin require_owners(p_actor,p_ware,v.TRIP_ID,0,'YARD_VISIT_NOT_FOUND');
   exception when others then if sqlcode in(-20882,-20911)then visible:=false;else raise;end if;end;
   -- Visits of hidden owners are omitted entirely, not counted.
   if visible then j:=card(v);a.append(j);end if;
  end loop;
  -- Overdue/queue age is judged by the server clock of this snapshot, not the browser's.
  r.put('observed_at',stamp(systimestamp));r.put('visits',a);
  return r.to_clob;
 end;
end;
/
