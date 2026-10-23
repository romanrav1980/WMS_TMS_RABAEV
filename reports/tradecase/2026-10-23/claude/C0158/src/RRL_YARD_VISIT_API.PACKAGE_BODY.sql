package body RRL_YARD_VISIT_API as
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

 -- RRL_ACCESS_API.allowed returns 0 for a deleted RUSERS row first (alive), GLOBAL_ADMIN included.
 procedure require(p_actor varchar2,p_permission varchar2,p_ware number)is n number;
 begin
  select RRL_ACCESS_API.allowed(p_actor,p_permission,'WAREHOUSE',to_char(p_ware))into n from dual;
  if n<>1 then raise_application_error(-20882,'YARD_ACCESS_DENIED');end if;
 end;

 -- Owners come from the accepted source documents, not from native bindings: every TRIP order line must resolve to exactly one
 -- SOURCE_OWNER_ID in the latest accepted ORDER. A missing basis, line or owner fails closed. An actor who may not even read an owner
 -- gets p_hidden, the same answer as for a missing trip/visit; a read-only owner gets TRADE_OWNER_ACCESS_DENIED on a write.
 procedure require_owners(p_actor varchar2,p_ware number,p_trip varchar2,p_write number,p_hidden varchar2)is body clob;lines number:=0;
 begin
  if p_trip is null then fail(p_hidden);end if;
  begin select BODY_JSON into body from RRL_TRADE_DOCUMENT where WARE_ID=p_ware and ENTITY_TYPE='TRIP'and EXTERNAL_ID=p_trip and STATUS='ACCEPTED'
    order by VERSION_NO desc fetch first 1 rows only;
  exception when no_data_found then fail(p_hidden);end;
  for o in(select t.ORDER_ID,t.LINE_ID,(select case when count(*)>0 and count(*)=count(ol.OWNER)and count(distinct ol.OWNER)=1 then max(ol.OWNER)end
      from RRL_TRADE_DOCUMENT d,json_table(d.BODY_JSON,'$.lines[*]'columns(LINE_ID varchar2(100)path'$.line_id',OWNER varchar2(100)path'$.source_owner_id'))ol
      where d.WARE_ID=p_ware and d.ENTITY_TYPE='ORDER'and d.EXTERNAL_ID=t.ORDER_ID and d.STATUS='ACCEPTED'and ol.LINE_ID=t.LINE_ID
      and d.VERSION_NO=(select max(x.VERSION_NO)from RRL_TRADE_DOCUMENT x where x.WARE_ID=d.WARE_ID and x.ENTITY_TYPE='ORDER'and x.EXTERNAL_ID=d.EXTERNAL_ID and x.STATUS='ACCEPTED'))OWNER
    from json_table(body,'$.orders[*]'columns(ORDER_ID varchar2(100)path'$.order_id',LINE_ID varchar2(100)path'$.line_id'))t)loop
   lines:=lines+1;
   if o.ORDER_ID is null or o.LINE_ID is null or trim(o.OWNER)is null then fail(p_hidden);end if;
   if RRL_TRADE_STOCK_GUARD.owner_allowed(p_actor,p_ware,o.OWNER,0)<>1 then fail(p_hidden);end if;
   if p_write=1 then RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,p_ware,o.OWNER,1);end if;
  end loop;
  if lines=0 then fail(p_hidden);end if;
 end;

 function trip_visible(p_actor varchar2,p_ware number,p_trip varchar2)return number is
 begin require_owners(p_actor,p_ware,p_trip,0,'YARD_VISIT_NOT_FOUND');return 1;
 exception when others then if sqlcode in(-20882,-20911)then return 0;end if;raise;
 end;

 procedure require_visit_owners(v RRL_YARD_VISIT%rowtype,p_actor varchar2,p_write number)is
 begin
  if v.VISIT_KIND='INBOUND'then RRL_YARD_SUPPLY_API.assert_visit(v.WARE_ID,v.VISIT_ID,p_actor,p_write);
  else require_owners(p_actor,v.WARE_ID,v.TRIP_ID,p_write,'YARD_VISIT_NOT_FOUND');end if;
 end;
 function visit_visible(p_actor varchar2,p_ware number,p_visit number)return number is v RRL_YARD_VISIT%rowtype;
 begin
  select*into v from RRL_YARD_VISIT where VISIT_ID=p_visit and WARE_ID=p_ware;
  require_visit_owners(v,p_actor,0);return 1;
 exception when no_data_found then return 0;
  when others then if sqlcode in(-20882,-20911)then return 0;end if;raise;
 end;
 function card(v RRL_YARD_VISIT%rowtype,p_op varchar2)return json_object_t is j json_object_t:=json_object_t();planned_dock varchar2(50);
 begin
  if v.NATIVE_TASK_ID is not null then
   begin select DOCK into planned_dock from RRL_TRANSPORT_TASK where ID=v.NATIVE_TASK_ID;exception when no_data_found then null;end;
  end if;
  if p_op is not null then j.put('operation_id',p_op);end if;  -- every command receipt names its own operation
  j.put('planned_dock',planned_dock);
  if v.VISIT_KIND='INBOUND'then j.put('supply_ids',json_array_t.parse(RRL_YARD_SUPPLY_API.supply_ids(v.VISIT_ID)));end if;
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

 -- Outbound arrival re-reads its native trip; inbound arrival validates its accepted supply versions and recorded vehicle.
 procedure bind_vehicle(v in out RRL_YARD_VISIT%rowtype,p_actor varchar2)is n number;
 begin
  if v.VISIT_KIND='INBOUND'then
   RRL_YARD_SUPPLY_API.assert_visit(v.WARE_ID,v.VISIT_ID,p_actor,1,1);
  else
  begin select NATIVE_TASK_ID into v.NATIVE_TASK_ID from RRL_TRADE_TRIP_LINK where WARE_ID=v.WARE_ID and TRIP_ID=v.TRIP_ID;
  exception when no_data_found then fail('YARD_TRIP_BINDING_REQUIRED');end;
  begin select upper(trim(TRANSPORT))into v.VEHICLE from RRL_TRANSPORT_TASK where ID=v.NATIVE_TASK_ID;
  exception when no_data_found then fail('YARD_TRIP_BINDING_REQUIRED');end;
  end if;
  if v.VEHICLE is null then fail('YARD_VEHICLE_REQUIRED');end if;
  -- Global: one truck cannot stand in two yards. Checked before the update; the unique index is the last guard across warehouses.
  -- The refusal names neither the other warehouse nor its trip.
  select count(*)into n from RRL_YARD_VISIT where VEHICLE=v.VEHICLE and STATE in('ARRIVED','AT_DOCK','WORKING','WORK_DONE')and VISIT_ID<>v.VISIT_ID;
  if n>0 then fail('YARD_VEHICLE_OCCUPIED');end if;
 end;

 procedure log_event(v RRL_YARD_VISIT%rowtype,p_op varchar2,p_action varchar2,p_from varchar2,p_at timestamp with time zone,
                  p_hash varchar2,p_actor varchar2,p_result out clob)is
 begin
  p_result:=card(v,p_op).to_clob;
  insert into RRL_YARD_VISIT_EVENT(OPERATION_ID,WARE_ID,VISIT_ID,ACTION,FROM_STATE,TO_STATE,DOCK,VEHICLE,REQUEST_HASH,ACTOR,EVENT_AT,RESULT_JSON)
   values(p_op,v.WARE_ID,v.VISIT_ID,p_action,p_from,v.STATE,v.DOCK,v.VEHICLE,p_hash,p_actor,p_at,p_result);
 end;

 procedure expect(p_ware number,d json_object_t,p_op varchar2,p_hash varchar2,p_actor varchar2,p_result out clob)is
  v RRL_YARD_VISIT%rowtype;trip varchar2(100):=d.get_string('trip_id');kind varchar2(12):=nvl(d.get_string('visit_kind'),'OUTBOUND');
  planned varchar2(40):=d.get_string('planned_arrival_at');n number;now timestamp with time zone:=systimestamp;sources clob;vehicle varchar2(50);
 begin
  -- Inbound vehicle is entered by the operator; no vehicle field is assumed in the ERP supply contract.
  if kind='INBOUND'then
   if trip is not null or not d.has('supply_ids')then fail('YARD_SUPPLIES_REQUIRED');end if;
   sources:=d.get_array('supply_ids').to_clob;vehicle:=upper(trim(d.get_string('vehicle')));
   if vehicle is null then fail('YARD_VEHICLE_REQUIRED');end if;
   RRL_YARD_SUPPLY_API.check_request(p_ware,sources,p_actor);
  elsif kind='OUTBOUND'and trip is not null then
   if d.has('supply_ids')or d.has('vehicle')then fail('YARD_REQUEST_INVALID');end if;
   require_owners(p_actor,p_ware,trip,1,'YARD_TRIP_REQUIRED');
  else fail('YARD_REQUEST_INVALID');end if;
  select count(*)into n from RRL_YARD_VISIT where WARE_ID=p_ware and TRIP_ID=trip and STATE not in('DEPARTED','CANCELLED');
  if n>0 then fail('YARD_TRIP_VISIT_ACTIVE');end if;
  v.VISIT_ID:=RRL_YARD_VISIT_SQ.nextval;v.WARE_ID:=p_ware;v.VISIT_KIND:=kind;v.TRIP_ID:=trip;v.STATE:='EXPECTED';v.VERSION_NO:=1;
  -- An expectation may wait for data: the planned vehicle is informative only and holds nothing until ARRIVE re-reads it.
  if kind='INBOUND'then v.VEHICLE:=vehicle;else
  begin select l.NATIVE_TASK_ID,upper(trim(t.TRANSPORT))into v.NATIVE_TASK_ID,v.VEHICLE from RRL_TRADE_TRIP_LINK l
    join RRL_TRANSPORT_TASK t on t.ID=l.NATIVE_TASK_ID where l.WARE_ID=p_ware and l.TRIP_ID=trip;
  exception when no_data_found then null;end;
  end if;
  if planned is not null then v.PLANNED_ARRIVAL_AT:=to_timestamp_tz(planned,'YYYY-MM-DD"T"HH24:MI:SSTZH:TZM');end if;
  v.CREATED_BY:=p_actor;v.UPDATED_BY:=p_actor;v.CREATED_AT:=now;v.UPDATED_AT:=now;
  insert into RRL_YARD_VISIT values v;
  if kind='INBOUND'then RRL_YARD_SUPPLY_API.create_links(p_ware,v.VISIT_ID,sources,p_actor);end if;
  log_event(v,p_op,'EXPECT',null,now,p_hash,p_actor,p_result);
 exception when dup_val_on_index then fail('YARD_TRIP_VISIT_ACTIVE');
 end;

 procedure transition(p_ware number,d json_object_t,p_op varchar2,p_hash varchar2,p_actor varchar2,p_result out clob)is
  v RRL_YARD_VISIT%rowtype;action varchar2(20):=d.get_string('action');id_value number:=d.get_number('visit_id');
  expected number:=d.get_number('expected_version');dock varchar2(50):=d.get_string('dock');reason varchar2(500):=d.get_string('reason');
  from_state varchar2(12);now timestamp with time zone:=systimestamp;
 begin
  begin select*into v from RRL_YARD_VISIT where VISIT_ID=id_value and WARE_ID=p_ware for update;
  exception when no_data_found then fail('YARD_VISIT_NOT_FOUND');end;
  require_visit_owners(v,p_actor,1);
  if expected is null or expected<>v.VERSION_NO then fail('VERSION_CONFLICT');end if;
  from_state:=v.STATE;
  if action='ARRIVE'and v.STATE='EXPECTED'then bind_vehicle(v,p_actor);v.STATE:='ARRIVED';v.ARRIVED_AT:=now;
  elsif action='ASSIGN_DOCK'and v.STATE='ARRIVED'or action='REASSIGN_DOCK'and v.STATE='AT_DOCK'then
   if dock is null or dock=v.DOCK then fail('YARD_REQUEST_INVALID');end if;
   assert_dock(p_ware,dock,v.VISIT_ID);v.DOCK:=dock;v.STATE:='AT_DOCK';v.DOCKED_AT:=now;
  elsif action='START'and v.STATE='AT_DOCK'then v.STATE:='WORKING';v.WORK_STARTED_AT:=now;
  elsif action='FINISH'and v.STATE='WORKING'then v.STATE:='WORK_DONE';v.WORK_FINISHED_AT:=now;
  elsif action='DEPART'and v.STATE='WORK_DONE'then v.STATE:='DEPARTED';v.DEPARTED_AT:=now;  -- releases the dock and the vehicle
  elsif action='CANCEL'and v.STATE in('EXPECTED','ARRIVED','AT_DOCK')then
   if reason is null then fail('YARD_CANCEL_REASON_REQUIRED');end if;
   v.STATE:='CANCELLED';v.CANCELLED_AT:=now;v.CANCEL_REASON:=substr(reason,1,500);
  else fail('YARD_STATE_CONFLICT');end if;
  v.VERSION_NO:=v.VERSION_NO+1;v.UPDATED_BY:=p_actor;v.UPDATED_AT:=now;
  update RRL_YARD_VISIT set row=v where VISIT_ID=v.VISIT_ID;
  log_event(v,p_op,action,from_state,now,p_hash,p_actor,p_result);
 exception when dup_val_on_index then fail('YARD_DOCK_OR_VEHICLE_OCCUPIED');  -- concurrent dispatcher lost the race
 end;

 procedure command(p_ware number,p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');act varchar2(20):=d.get_string('action');
  hash_value varchar2(64):=sha(p_request);e RRL_YARD_VISIT_EVENT%rowtype;j json_object_t;v RRL_YARD_VISIT%rowtype;saved boolean:=false;
 begin
  if op is null or lengthb(op)>100 or not regexp_like(op,'^[A-Za-z0-9_.:-]+$')then fail('YARD_REQUEST_INVALID');end if;
  -- Scope first: without the warehouse right nobody learns whether the site exists. Checked again under the locks.
  require(p_actor,'tradecase_yard_operate',p_ware);
  lock_site(p_ware);
  require(p_actor,'tradecase_yard_operate',p_ware);
  savepoint yard_visit_command;saved:=true;
  begin
   select*into e from RRL_YARD_VISIT_EVENT where OPERATION_ID=op;
   if e.WARE_ID<>p_ware then fail('YARD_OPERATION_CONFLICT');end if;
   select*into v from RRL_YARD_VISIT where VISIT_ID=e.VISIT_ID;
   -- Owner rights of today, before anything about the stored operation is revealed; a receipt belongs to its own actor and body.
   require_visit_owners(v,p_actor,1);
   if e.ACTOR<>p_actor or e.REQUEST_HASH<>hash_value then fail('YARD_OPERATION_CONFLICT');end if;
   j:=json_object_t.parse(e.RESULT_JSON);j.put('replayed',true);p_result:=j.to_clob;return;
  exception when no_data_found then null;end;
  if act='EXPECT'then expect(p_ware,d,op,hash_value,p_actor,p_result);
  else transition(p_ware,d,op,hash_value,p_actor,p_result);end if;
  j:=json_object_t.parse(p_result);j.put('replayed',false);p_result:=j.to_clob;
 exception when others then if saved then rollback to yard_visit_command;end if;raise;
 end;

 function visits(p_ware number,p_actor varchar2,p_active number)return clob is a json_array_t:=json_array_t();r json_object_t:=json_object_t();
  v RRL_YARD_VISIT%rowtype;
 begin
  require(p_actor,'tradecase_view',p_ware);
  -- Hidden owners are filtered before the limit: foreign visits can neither push out a visible one nor be counted.
  for x in(select VISIT_ID from RRL_YARD_VISIT where WARE_ID=p_ware and(p_active=0 or STATE not in('DEPARTED','CANCELLED'))
    and visit_visible(p_actor,p_ware,VISIT_ID)=1
    order by case STATE when 'WORKING'then 1 when 'AT_DOCK'then 2 when 'WORK_DONE'then 3 when 'ARRIVED'then 4 when 'EXPECTED'then 5 else 6 end,
     nvl(ARRIVED_AT,PLANNED_ARRIVAL_AT),VISIT_ID fetch first 200 rows only)loop
   select*into v from RRL_YARD_VISIT where VISIT_ID=x.VISIT_ID;
   a.append(card(v,null));
  end loop;
  -- Overdue/queue age is judged by the server clock of this snapshot, not the browser's.
  r.put('observed_at',stamp(systimestamp));r.put('visits',a);
  return r.to_clob;
 end;

 function history(p_ware number,p_actor varchar2,p_from varchar2,p_to varchar2)return clob is
  a json_array_t:=json_array_t();ev json_array_t;j json_object_t;e json_object_t;r json_object_t:=json_object_t();n number:=0;
  t_from timestamp with time zone:=to_timestamp_tz(p_from,'YYYY-MM-DD"T"HH24:MI:SSTZH:TZM');
  t_to timestamp with time zone:=to_timestamp_tz(p_to,'YYYY-MM-DD"T"HH24:MI:SSTZH:TZM');
 begin
  require(p_actor,'tradecase_view',p_ware);
  if t_to<=t_from or t_to-t_from>interval '7' day then fail('YARD_HISTORY_INVALID_WINDOW');end if;
  -- Bounded by the window and by visible owners (filtered before the bound, so hidden visits are never counted).
  for x in(select VISIT_ID,VISIT_KIND,TRIP_ID,VEHICLE,STATE,PLANNED_ARRIVAL_AT from RRL_YARD_VISIT where WARE_ID=p_ware
    and((ARRIVED_AT<t_to and nvl(DEPARTED_AT,nvl(CANCELLED_AT,t_to))>=t_from)
     or(STATE='EXPECTED'and PLANNED_ARRIVAL_AT>=t_from and PLANNED_ARRIVAL_AT<t_to))
    and visit_visible(p_actor,p_ware,VISIT_ID)=1 order by VISIT_ID fetch first 501 rows only)loop
   n:=n+1;if n>500 then fail('YARD_HISTORY_BOUND_NARROW_WINDOW');end if;
   j:=json_object_t();j.put('visit_id',x.VISIT_ID);j.put('trip_id',x.TRIP_ID);j.put('vehicle',x.VEHICLE);j.put('state',x.STATE);
   j.put('visit_kind',x.VISIT_KIND);
   if x.VISIT_KIND='INBOUND'then j.put('supply_ids',json_array_t.parse(RRL_YARD_SUPPLY_API.supply_ids(x.VISIT_ID)));end if;
   j.put('planned_arrival_at',stamp(x.PLANNED_ARRIVAL_AT));ev:=json_array_t();
   for y in(select ACTION,DOCK,EVENT_AT from RRL_YARD_VISIT_EVENT where VISIT_ID=x.VISIT_ID order by EVENT_AT,CREATED_AT)loop
    e:=json_object_t();e.put('action',y.ACTION);e.put('dock',y.DOCK);e.put('at',stamp(y.EVENT_AT));ev.append(e);
   end loop;
   j.put('events',ev);a.append(j);
  end loop;
  r.put('observed_at',stamp(systimestamp));r.put('visits',a);
  return r.to_clob;
 end;
end;