create or replace package RRL_YARD_DOCK_PLAN_API authid definer as
 -- Planned interval [from,to) of one dock of the site for one yard visit (outbound trip or inbound supply): PLAN / MOVE / CANCEL.
 -- No dock may be planned for two visits at overlapping times; one vehicle is not planned at overlapping times on any site.
 -- A plan is not a fact and not a guarantee: arrival, dock assignment and work stay in RRL_YARD_VISIT_API; no stock effect.
 procedure command(p_ware number,p_request clob,p_actor varchar2,p_result out clob);
 -- ACTIVE plans touching [p_from,p_to) (<= 7 days) of visible visits, with the visit facts; times YYYY-MM-DDTHH:MI:SS+TZH:TZM in.
 function plans(p_ware number,p_actor varchar2,p_from varchar2,p_to varchar2)return clob;
end;
/
create or replace package body RRL_YARD_DOCK_PLAN_API as
 procedure fail(p_code varchar2)is begin raise_application_error(-20911,p_code);end;
 function sha(p_text clob)return varchar2 is begin return lower(rawtohex(sys.dbms_crypto.hash(p_text,sys.dbms_crypto.hash_sh256)));end;
 function stamp(p_value timestamp with time zone)return varchar2 is
 begin return case when p_value is null then null else to_char(p_value at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS"Z"')end;end;
 function moment(p_text varchar2)return timestamp with time zone is
 begin
  if p_text is null or not regexp_like(p_text,'^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[+-][0-9]{2}:[0-9]{2}$')then fail('YARD_PLAN_TIME_INVALID');end if;
  return to_timestamp_tz(p_text,'YYYY-MM-DD"T"HH24:MI:SSTZH:TZM');
 exception when others then if sqlcode=-20911 then raise;end if;fail('YARD_PLAN_TIME_INVALID');
 end;

 procedure require(p_actor varchar2,p_permission varchar2,p_ware number)is n number;
 begin
  select RRL_ACCESS_API.allowed(p_actor,p_permission,'WAREHOUSE',to_char(p_ware))into n from dual;
  if n<>1 then raise_application_error(-20882,'YARD_ACCESS_DENIED');end if;
 end;

 -- Same order as the yard visit writer: current access revision, then the site row (serializes every plan of this site's docks).
 procedure lock_site(p_ware number)is n number;
 begin
  lock table RRL_ACCESS_REV in share mode wait 5;
  select ENABLED into n from RRL_TRADE_SITE where WARE_ID=p_ware for update;
  if n<>1 then fail('TRADE_SITE_DISABLED');end if;
 exception when no_data_found then fail('TRADE_SITE_REQUIRED');
 end;

 -- One vehicle may visit several sites: its plans are serialized across sites by a lock on the vehicle number, taken after the
 -- site row (sites never wait on each other in reverse); released at commit/rollback.
 procedure lock_vehicle(p_vehicle varchar2)is n number;
 begin
  if p_vehicle is null then return;end if;
  n:=sys.dbms_lock.request(RRL_STOCK_LOCK_API.resource_lock_id(90,RRL_STOCK_LOCK_API.resource_key('YARD.PLAN.VEHICLE',p_vehicle)),
   sys.dbms_lock.x_mode,5,true);
  if n not in(0,4)then fail('YARD_PLAN_BUSY');end if;
 end;

 procedure assert_dock(p_ware number,p_dock varchar2)is n number;blocked number;
 begin
  select count(*),max(nvl(DOCK_IS_BLOCKED,0))into n,blocked from RRL_TT_DOCK where WARE_ID=p_ware and DOCK=p_dock;
  if n=0 then fail('YARD_DOCK_UNKNOWN');end if;  -- a dock of another site is unknown here
  if n>1 then fail('YARD_DOCK_AMBIGUOUS');end if;
  if blocked<>0 then fail('YARD_DOCK_BLOCKED');end if;
 end;

 -- Plans of visits already gone (DEPARTED/CANCELLED) no longer hold anything. The refusal names neither the other visit nor its site.
 procedure assert_free(p_ware number,p_visit number,p_vehicle varchar2,p_dock varchar2,p_from timestamp with time zone,p_to timestamp with time zone)is n number;
 begin
  select count(*)into n from RRL_YARD_DOCK_PLAN p join RRL_YARD_VISIT v on v.VISIT_ID=p.VISIT_ID
   where p.WARE_ID=p_ware and p.DOCK=p_dock and p.STATUS='ACTIVE'and p.VISIT_ID<>p_visit and v.STATE not in('DEPARTED','CANCELLED')
    and p.PLANNED_FROM<p_to and p.PLANNED_TO>p_from;
  if n>0 then fail('YARD_DOCK_PLAN_CONFLICT');end if;
  if p_vehicle is not null then
   select count(*)into n from RRL_YARD_DOCK_PLAN p join RRL_YARD_VISIT v on v.VISIT_ID=p.VISIT_ID
    where v.VEHICLE=p_vehicle and p.STATUS='ACTIVE'and p.VISIT_ID<>p_visit and v.STATE not in('DEPARTED','CANCELLED')
     and p.PLANNED_FROM<p_to and p.PLANNED_TO>p_from;
   if n>0 then fail('YARD_VEHICLE_PLAN_CONFLICT');end if;
  end if;
 end;

 function card(p RRL_YARD_DOCK_PLAN%rowtype,v RRL_YARD_VISIT%rowtype,p_op varchar2)return json_object_t is j json_object_t:=json_object_t();
 begin
  if p_op is not null then j.put('operation_id',p_op);end if;
  j.put('plan_id',p.PLAN_ID);j.put('warehouse_id',p.WARE_ID);j.put('visit_id',p.VISIT_ID);j.put('dock',p.DOCK);
  j.put('planned_from',stamp(p.PLANNED_FROM));j.put('planned_to',stamp(p.PLANNED_TO));j.put('status',p.STATUS);j.put('version',p.VERSION_NO);
  j.put('cancel_reason',p.CANCEL_REASON);j.put('updated_by',p.UPDATED_BY);
  -- Facts of the visit, read next to the plan; never derived from it.
  j.put('visit_kind',v.VISIT_KIND);j.put('trip_id',v.TRIP_ID);j.put('vehicle',v.VEHICLE);j.put('visit_state',v.STATE);j.put('fact_dock',v.DOCK);
  j.put('planned_arrival_at',stamp(v.PLANNED_ARRIVAL_AT));j.put('arrived_at',stamp(v.ARRIVED_AT));j.put('docked_at',stamp(v.DOCKED_AT));
  j.put('work_started_at',stamp(v.WORK_STARTED_AT));j.put('work_finished_at',stamp(v.WORK_FINISHED_AT));j.put('departed_at',stamp(v.DEPARTED_AT));
  j.put('cancelled_at',stamp(v.CANCELLED_AT));
  return j;
 end;

 procedure log_event(p RRL_YARD_DOCK_PLAN%rowtype,v RRL_YARD_VISIT%rowtype,p_op varchar2,p_action varchar2,p_hash varchar2,p_actor varchar2,p_result out clob)is
 begin
  p_result:=card(p,v,p_op).to_clob;
  insert into RRL_YARD_DOCK_PLAN_EVENT(OPERATION_ID,WARE_ID,PLAN_ID,VISIT_ID,ACTION,DOCK,PLANNED_FROM,PLANNED_TO,REQUEST_HASH,ACTOR,RESULT_JSON)
   values(p_op,p.WARE_ID,p.PLAN_ID,p.VISIT_ID,p_action,p.DOCK,p.PLANNED_FROM,p.PLANNED_TO,p_hash,p_actor,p_result);
 end;

 procedure lock_visit(p_ware number,p_visit number,p_actor varchar2,v out RRL_YARD_VISIT%rowtype)is
 begin
  begin select*into v from RRL_YARD_VISIT where VISIT_ID=p_visit and WARE_ID=p_ware for update;
  exception when no_data_found then fail('YARD_VISIT_NOT_FOUND');end;
  RRL_YARD_VISIT_API.assert_visit_owners(p_actor,p_ware,p_visit,1);
 end;

 procedure change(p_ware number,d json_object_t,p_op varchar2,p_hash varchar2,p_actor varchar2,p_result out clob)is
  action varchar2(10):=d.get_string('action');p RRL_YARD_DOCK_PLAN%rowtype;v RRL_YARD_VISIT%rowtype;visit_value number;n number;
  now timestamp with time zone:=systimestamp;dock varchar2(50);t_from timestamp with time zone;t_to timestamp with time zone;
 begin
  if action='PLAN'then visit_value:=d.get_number('visit_id');
  else
   begin select VISIT_ID into visit_value from RRL_YARD_DOCK_PLAN where PLAN_ID=d.get_number('plan_id')and WARE_ID=p_ware;
   exception when no_data_found then fail('YARD_PLAN_NOT_FOUND');end;
  end if;
  -- Visit before plan, as in every command. A plan of a hidden visit answers like a missing plan.
  begin lock_visit(p_ware,visit_value,p_actor,v);
  exception when others then if action<>'PLAN'and sqlerrm like '%YARD_VISIT_NOT_FOUND%'then fail('YARD_PLAN_NOT_FOUND');end if;raise;end;
  if action<>'PLAN'then
   select*into p from RRL_YARD_DOCK_PLAN where PLAN_ID=d.get_number('plan_id')for update;
   if p.STATUS<>'ACTIVE'then fail('YARD_PLAN_STATE_CONFLICT');end if;
   if d.get_number('expected_version')is null or d.get_number('expected_version')<>p.VERSION_NO then fail('VERSION_CONFLICT');end if;
  end if;
  if action='CANCEL'then
   if trim(d.get_string('reason'))is null then fail('YARD_PLAN_REASON_REQUIRED');end if;
   p.STATUS:='CANCELLED';p.CANCEL_REASON:=substr(d.get_string('reason'),1,500);
  else
   -- A plan is set or moved only before the truck stands at a dock; afterwards the yard facts rule.
   if v.STATE not in('EXPECTED','ARRIVED')then fail('YARD_PLAN_VISIT_STATE');end if;
   dock:=d.get_string('dock');t_from:=moment(d.get_string('planned_from'));t_to:=moment(d.get_string('planned_to'));
   if dock is null or lengthb(dock)>50 then fail('YARD_REQUEST_INVALID');end if;
   if t_to<=t_from then fail('YARD_PLAN_RANGE_INVALID');end if;
   if t_from<=now then fail('YARD_PLAN_IN_PAST');end if;  -- only future intervals; nothing is planned retroactively
   if action='MOVE'and dock=p.DOCK and t_from=p.PLANNED_FROM and t_to=p.PLANNED_TO then fail('YARD_REQUEST_INVALID');end if;
   if action='PLAN'then
    select count(*)into n from RRL_YARD_DOCK_PLAN where VISIT_ID=v.VISIT_ID and STATUS='ACTIVE';
    if n>0 then fail('YARD_PLAN_EXISTS');end if;
   end if;
   assert_dock(p_ware,dock);
   lock_vehicle(v.VEHICLE);
   assert_free(p_ware,v.VISIT_ID,v.VEHICLE,dock,t_from,t_to);
   p.DOCK:=dock;p.PLANNED_FROM:=t_from;p.PLANNED_TO:=t_to;
  end if;
  if action='PLAN'then
   p.PLAN_ID:=RRL_YARD_DOCK_PLAN_SQ.nextval;p.WARE_ID:=p_ware;p.VISIT_ID:=v.VISIT_ID;p.STATUS:='ACTIVE';p.VERSION_NO:=1;
   p.CREATED_BY:=p_actor;p.CREATED_AT:=now;p.UPDATED_BY:=p_actor;p.UPDATED_AT:=now;
   insert into RRL_YARD_DOCK_PLAN values p;
  else
   p.VERSION_NO:=p.VERSION_NO+1;p.UPDATED_BY:=p_actor;p.UPDATED_AT:=now;
   update RRL_YARD_DOCK_PLAN set row=p where PLAN_ID=p.PLAN_ID;
  end if;
  log_event(p,v,p_op,action,p_hash,p_actor,p_result);
 exception when dup_val_on_index then fail('YARD_PLAN_EXISTS');
 end;

 procedure command(p_ware number,p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');act varchar2(10):=d.get_string('action');
  hash_value varchar2(64):=sha(p_request);e RRL_YARD_DOCK_PLAN_EVENT%rowtype;j json_object_t;saved boolean:=false;
 begin
  if op is null or lengthb(op)>100 or not regexp_like(op,'^[A-Za-z0-9_.:-]+$')or act is null or act not in('PLAN','MOVE','CANCEL')then fail('YARD_REQUEST_INVALID');end if;
  -- Scope first: without the warehouse right nobody learns whether the site exists. Checked again under the locks.
  require(p_actor,'tradecase_yard_operate',p_ware);
  lock_site(p_ware);
  require(p_actor,'tradecase_yard_operate',p_ware);
  savepoint yard_dock_plan_command;saved:=true;
  begin
   select*into e from RRL_YARD_DOCK_PLAN_EVENT where OPERATION_ID=op;
   if e.WARE_ID<>p_ware then fail('YARD_OPERATION_CONFLICT');end if;
   -- Owner rights of today before anything about the stored operation is revealed; a receipt belongs to its own actor and body.
   RRL_YARD_VISIT_API.assert_visit_owners(p_actor,p_ware,e.VISIT_ID,1);
   if e.ACTOR<>p_actor or e.REQUEST_HASH<>hash_value then fail('YARD_OPERATION_CONFLICT');end if;
   j:=json_object_t.parse(e.RESULT_JSON);j.put('replayed',true);p_result:=j.to_clob;return;
  exception when no_data_found then null;end;
  change(p_ware,d,op,hash_value,p_actor,p_result);
  j:=json_object_t.parse(p_result);j.put('replayed',false);p_result:=j.to_clob;
 exception when others then if saved then rollback to yard_dock_plan_command;end if;raise;
 end;

 function plans(p_ware number,p_actor varchar2,p_from varchar2,p_to varchar2)return clob is
  a json_array_t:=json_array_t();r json_object_t:=json_object_t();n number:=0;p RRL_YARD_DOCK_PLAN%rowtype;v RRL_YARD_VISIT%rowtype;
  t_from timestamp with time zone:=moment(p_from);t_to timestamp with time zone:=moment(p_to);
 begin
  require(p_actor,'tradecase_view',p_ware);
  if t_to<=t_from or t_to-t_from>interval '7' day then fail('YARD_PLAN_WINDOW_INVALID');end if;
  -- Hidden owners are filtered before the bound, as in the yard lists; plans of gone visits are still shown with their visit state.
  for x in(select p.PLAN_ID from RRL_YARD_DOCK_PLAN p where p.WARE_ID=p_ware and p.STATUS='ACTIVE'and p.PLANNED_FROM<t_to and p.PLANNED_TO>t_from
    and RRL_YARD_VISIT_API.visit_visible(p_actor,p_ware,p.VISIT_ID)=1 order by p.PLANNED_FROM,p.PLAN_ID fetch first 501 rows only)loop
   n:=n+1;if n>500 then fail('YARD_PLAN_BOUND_NARROW_WINDOW');end if;
   select*into p from RRL_YARD_DOCK_PLAN where PLAN_ID=x.PLAN_ID;
   select*into v from RRL_YARD_VISIT where VISIT_ID=p.VISIT_ID;
   a.append(card(p,v,null));
  end loop;
  -- Lateness is judged against this server clock, not the browser's.
  r.put('observed_at',stamp(systimestamp));r.put('plans',a);
  return r.to_clob;
 end;
end;
/
