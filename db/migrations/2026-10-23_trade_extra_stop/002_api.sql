create or replace package RRL_TRADE_EXTRA_STOP_API authid definer as
 -- Decision on an extra stop outside the main route (TRADECASE program, section 12). The stop is proposed for approval only if the
 -- route recalculated by the existing native calculator with the stop still keeps every strict window and the planned resource end;
 -- the slack comes from that recalculation, not from a fixed number. Unknown inputs never promise feasibility.
 function evaluate(p_trip number,p_actor varchar2,p_request clob)return clob;           -- READ ONLY
 procedure command(p_request clob,p_actor varchar2,p_result out clob);                   -- APPROVE / DECLINE / SET_POLICY
 function decisions(p_trip number,p_actor varchar2)return clob;                          -- READ ONLY
 -- Pure part: the route source of RRL_TT_TIME_API.context in, the decision out. p_legs (synthetic legs) only for controlled checks.
 function evaluate_source(p_source clob,p_request clob,p_legs clob default null)return clob;
end;
/
create or replace package body RRL_TRADE_EXTRA_STOP_API as
 -- PURE BEGIN (depends only on RRL_TT_ROUTE_SCHEDULE, RRL_STORE_WINDOW_RULES, RRL_STOCK_PLAN_HELPER; checked in a read-only block)
 function minutes_between(p_from varchar2,p_to varchar2)return number is
 begin
  if p_from is null or p_to is null then return null;end if;
  return round((cast(to_timestamp_tz(p_to,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')as date)-cast(to_timestamp_tz(p_from,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')as date))*1440,1);
 end;

 function calc(p_source json_object_t,p_zone varchar2)return json_object_t is r clob;
 begin RRL_TT_ROUTE_SCHEDULE.calculate(p_source.to_clob,p_zone,r);return json_object_t.parse(r);end;

 -- Classification of a calculated variant: FEASIBLE, VIOLATION (complete data, broken strict window / resource end / drive limit), UNKNOWN.
 function verdict(r json_object_t)return varchar2 is issues json_array_t:=r.get_array('issues');code varchar2(80);violation boolean:=false;
 begin
  if issues.get_size=0 then return 'FEASIBLE';end if;
  for i in 0..issues.get_size-1 loop
   code:=treat(issues.get(i)as json_object_t).get_string('code');
   if code in('DELIVERY_HARD_WINDOW_MISSED','ROUTE_EXCEEDS_PLANNED_RESOURCE_ENVELOPE','DRIVER_TRIP_DRIVE_LIMIT')then violation:=true;
   else return 'UNKNOWN';end if;  -- any missing input makes the variant unknown, even if something else is also broken
  end loop;
  return case when violation then 'VIOLATION'else 'FEASIBLE'end;
 end;

 -- Slack until the binding deadline: minutes between the service end and the window end of every strict stop, and the return before
 -- the planned resource end. The smallest value is "the time left before the main delivery deadline".
 function slack(p_source json_object_t,r json_object_t)return number is stops json_array_t:=r.get_array('stops');s json_object_t;v number;best number;
  bound varchar2(30);wire clob:=p_source.to_clob;
 begin
  for i in 0..stops.get_size-1 loop
   s:=treat(stops.get(i)as json_object_t);
   if s.get_number('window_strict')=1 then v:=minutes_between(s.get_string('service_finish_at'),s.get_string('window_to'));
    if v is not null and(best is null or v<best)then best:=v;end if;
   end if;
  end loop;
  select max(z)into bound from json_table(wire,'$.operations[*]'columns(c varchar2(50)path '$.code',z varchar2(30)path '$.plan_end'))where c='DRIVE_BACK';
  if bound is not null and r.get_string('return_at')is not null then
   v:=round((to_date(bound,'YYYY-MM-DD HH24:MI:SS')-cast(to_timestamp_tz(r.get_string('return_at'),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')as date))*1440,1);
   if best is null or v<best then best:=v;end if;
  end if;
  return best;
 end;

 -- The route with the extra address inserted at position p_pos (0 = first stop), rebuilt by the native material owners.
 function variant(p_source json_object_t,p_stops json_array_t,p_pos number,p_address varchar2,p_rule json_object_t,p_legs clob)return json_object_t is
  b json_object_t:=json_object_t.parse(p_source.to_clob);members json_array_t:=b.get_array('members');m json_object_t;rules json_array_t;
  ord json_array_t:=json_array_t();x json_object_t;wire clob;mat json_object_t;legs json_array_t:=json_array_t();prev varchar2(255);
  leg_from varchar2(255);leg_to varchar2(255);
 begin
  for i in 0..p_stops.get_size loop
   if i=p_pos then ord.append(p_address);end if;
   if i<p_stops.get_size then ord.append(p_stops.get_string(i));end if;
  end loop;
  for i in 0..members.get_size-1 loop
   m:=treat(members.get(i)as json_object_t);
   for j in 0..ord.get_size-1 loop if ord.get_string(j)=m.get_string('address')then m.put('route_ordinal',(j+1)*10);end if;end loop;
  end loop;
  x:=json_object_t();x.put('address',p_address);x.put('st_number','EXTRA');x.put_null('delivery_window_from');x.put_null('delivery_window_to');
  if p_rule.has('synthetic_window_from')then x.put('delivery_window_from',p_rule.get_string('synthetic_window_from'));x.put('delivery_window_to',p_rule.get_string('synthetic_window_to'));end if;
  for j in 0..ord.get_size-1 loop if ord.get_string(j)=p_address then x.put('route_ordinal',(j+1)*10);end if;end loop;
  members.append(x);b.put('members',members);
  rules:=b.get_array('destination_rules');x:=json_object_t();x.put('address',p_address);x.put('address_count',p_rule.get_number('address_count'));
  x.put('unload_norm_min',p_rule.get_number('unload_norm_min'));x.put('window_strict',p_rule.get_number('window_strict'));rules.append(x);b.put('destination_rules',rules);
  if p_legs is null then
   RRL_STORE_WINDOW_RULES.material(b.to_clob,wire);b.put('store_window_profiles',json_array_t.parse(wire));
   RRL_TT_ROUTE_SCHEDULE.material(b.to_clob,wire);b.put('route_material',json_object_t.parse(wire));
  else  -- controlled check: legs given explicitly, same policy fields as the native material
   mat:=json_object_t.parse(b.get_object('route_material').to_clob);prev:=mat.get_string('depot_address');
   for j in 0..ord.get_size loop
    leg_from:=prev;leg_to:=case when j<ord.get_size then ord.get_string(j)else mat.get_string('depot_address')end;
    x:=json_object_t();x.put('from_address',leg_from);x.put('to_address',leg_to);
    for l in(select d from json_table(p_legs,'$[*]'columns(a varchar2(255)path '$.from_address',z varchar2(255)path '$.to_address',d number path '$.duration_min'))
      where a=leg_from and z=leg_to)loop
     x.put('duration_min',l.d);x.put('duration_basis','ROAD_PROFILE_ESTIMATE');x.put('fresh',true);
    end loop;
    if not x.has('duration_min')then x.put_null('duration_min');x.put('fresh',false);end if;
    legs.append(x);if j<ord.get_size then prev:=ord.get_string(j);end if;
   end loop;
   mat.put('stops',ord);mat.put('legs',legs);b.put('route_material',mat);
  end if;
  return b;
 end;

 function brief(r json_object_t)return json_object_t is o json_object_t:=json_object_t();stops json_array_t:=r.get_array('stops');
 begin
  o.put('status',r.get_string('status'));o.put('return_at',r.get_string('return_at'));o.put('departure_at',r.get_string('departure_at'));
  o.put('drive_min',r.get_string('drive_min'));o.put('stops',stops);o.put('issues',r.get_array('issues'));
  return o;
 end;

 function evaluate_source(p_source clob,p_request clob,p_legs clob default null)return clob is
  src json_object_t:=json_object_t.parse(p_source);q json_object_t:=json_object_t.parse(p_request);res json_object_t:=json_object_t();
  zone varchar2(30):=nvl(q.get_string('zone'),'UTC');address varchar2(255):=q.get_string('address');rule json_object_t:=q.get_object('extra_rule');
  before json_object_t;after json_object_t;best json_object_t;best_pos number;stops json_array_t;v json_object_t;kind varchar2(20);
  variants json_array_t:=json_array_t();unknown boolean:=false;row_v json_object_t;
 begin
  res.put('address',address);res.put('rule_source','TRADECASE program section 12: propose if it fits the slack before the main delivery deadline');
  if q.get_boolean('new_stops_forbidden')then res.put('decision','FORBIDDEN');res.put('reason','NEW_STOPS_FORBIDDEN');return res.to_clob;end if;
  before:=calc(src,zone);res.put('before',brief(before));res.put('before_slack_min',slack(src,before));
  if verdict(before)<>'FEASIBLE'then res.put('decision','UNKNOWN');res.put('reason','BASE_ROUTE_NOT_CONFIRMED');return res.to_clob;end if;
  stops:=src.get_object('route_material').get_array('stops');
  for i in 0..stops.get_size-1 loop if stops.get_string(i)=address then res.put('decision','ALREADY_ON_ROUTE');return res.to_clob;end if;end loop;
  if rule is null or rule.get_number('address_count')is null or rule.get_number('address_count')<>1 then
   res.put('decision','UNKNOWN');res.put('reason','EXTRA_ADDRESS_NOT_UNIQUE');return res.to_clob;end if;
  for pos in 0..stops.get_size loop
   v:=variant(src,stops,pos,address,rule,p_legs);after:=calc(v,zone);kind:=verdict(after);
   row_v:=json_object_t();row_v.put('position',pos);row_v.put('verdict',kind);row_v.put('return_at',after.get_string('return_at'));
   row_v.put('issues',after.get_array('issues'));variants.append(row_v);
   if kind='UNKNOWN'then unknown:=true;end if;
   if kind='FEASIBLE'and(best is null or after.get_string('return_at')<best.get_string('return_at'))then best:=after;best_pos:=pos;
    res.put('after_slack_min',slack(v,after));end if;
  end loop;
  res.put('variants',variants);
  if best is not null then
   res.put('decision','PROPOSE');res.put('position',best_pos);res.put('after',brief(best));
   res.put('added_min',minutes_between(before.get_string('return_at'),best.get_string('return_at')));
   res.put('added_drive_min',to_number(best.get_string('drive_min'))-to_number(before.get_string('drive_min')));
  elsif unknown then res.put('decision','UNKNOWN');res.put('reason','EXTRA_STOP_INPUTS_MISSING');
  else res.put('decision','REJECT');res.put('reason','EXTRA_STOP_BREAKS_DEADLINE');end if;
  return res.to_clob;
 end;
 -- PURE END

 procedure fail(p_code varchar2)is begin raise_application_error(-20911,p_code);end;
 function sha(p_text clob)return varchar2 is begin return lower(rawtohex(sys.dbms_crypto.hash(p_text,sys.dbms_crypto.hash_sh256)));end;
 function stamp(p_value timestamp with time zone)return varchar2 is
 begin return case when p_value is null then null else to_char(p_value at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS"Z"')end;end;

 -- Every warehouse of the trip must allow the dispatcher's edit right (the same right as the existing route commands).
 procedure require_edit(p_trip number,p_actor varchar2)is n number;k number:=0;
 begin
  for w in(select distinct WARE_ID from RRL_SBORKA_PALLETS where TRANSTASK_ID=p_trip and WARE_ID is not null)loop
   k:=k+1;select RRL_ACCESS_API.allowed(p_actor,'transport_dispatch_edit','WAREHOUSE',to_char(w.WARE_ID))into n from dual;
   if n<>1 then raise_application_error(-20882,'EXTRA_STOP_ACCESS_DENIED');end if;
  end loop;
  if k=0 then fail('EXTRA_STOP_TRIP_NOT_FOUND');end if;
 end;

 function policy(p_trip number)return RRL_TRADE_ROUTE_STOP_POLICY%rowtype is p RRL_TRADE_ROUTE_STOP_POLICY%rowtype;
 begin
  begin select*into p from RRL_TRADE_ROUTE_STOP_POLICY where TRIP_ID=p_trip;
  exception when no_data_found then p.TRIP_ID:=p_trip;p.NEW_STOPS_FORBIDDEN:=0;p.VERSION_NO:=0;end;
  return p;
 end;

 -- Road distance of an ordered route depot -> stops -> depot from the same road cache the legs come from; null when any pair is unknown.
 function distance_km(p_depot varchar2,p_order json_array_t)return number is total number:=0;km number;a varchar2(255);z varchar2(255);
 begin
  if p_depot is null then return null;end if;
  a:=p_depot;
  for i in 0..p_order.get_size loop
   z:=case when i<p_order.get_size then p_order.get_string(i)else p_depot end;
   begin select DISTANCE_KM into km from RRL_ADDR_DISTANCE_MATRIX where FROM_ADDR=a and TO_ADDR=z;
   exception when no_data_found then return null;end;
   if km is null then return null;end if;
   total:=total+km;a:=z;
  end loop;
  return total;
 end;

 -- Real evaluation: current native time context (it checks the view right), the extra address rule as RRL_TT_TIME_API builds it.
 function evaluate(p_trip number,p_actor varchar2,p_request clob)return clob is ctx clob;c json_object_t;q json_object_t:=json_object_t.parse(p_request);
  rule json_object_t:=json_object_t();n number;norm number;strict number;v_address varchar2(255):=q.get_string('address');r json_object_t;p RRL_TRADE_ROUTE_STOP_POLICY%rowtype;
 begin
  if v_address is null or length(v_address)>255 then fail('EXTRA_STOP_REQUEST_INVALID');end if;
  RRL_TT_TIME_API.context(p_trip,p_actor,ctx);c:=json_object_t.parse(ctx);
  select count(*),min(UNLOAD_NORM_MIN),min(TW_STRICT)into n,norm,strict from RRL_ADDR where nvl(DELETED3,0)=0 and ADDR=v_address;
  rule.put('address_count',n);rule.put('unload_norm_min',norm);rule.put('window_strict',strict);
  p:=policy(p_trip);q.put('extra_rule',rule);q.put('new_stops_forbidden',p.NEW_STOPS_FORBIDDEN=1);
  r:=json_object_t.parse(evaluate_source(c.get_object('source').to_clob,q.to_clob));
  -- Mileage change (program: show the change of time and mileage) from cached road distances, never estimated.
  declare m json_object_t:=c.get_object('source').get_object('route_material');stops json_array_t:=m.get_array('stops');ord json_array_t:=json_array_t();
   before_km number;after_km number;
  begin
   before_km:=distance_km(m.get_string('depot_address'),stops);r.put('distance_km_before',before_km);
   if r.get_string('decision')='PROPOSE'then
    for i in 0..stops.get_size loop
     if i=r.get_number('position')then ord.append(v_address);end if;
     if i<stops.get_size then ord.append(stops.get_string(i));end if;
    end loop;
    after_km:=distance_km(m.get_string('depot_address'),ord);r.put('distance_km_after',after_km);
    if before_km is not null and after_km is not null then r.put('added_km',after_km-before_km);end if;
   end if;
  end;
  r.put('trip_id',p_trip);r.put('source_hash',c.get_string('source_hash'));r.put('time_version',c.get_number('version'));
  r.put('policy_version',p.VERSION_NO);r.put('new_stops_forbidden',p.NEW_STOPS_FORBIDDEN=1);
  r.put('external_sap_order','NOT_CREATED');  -- the SAP order is created by SAP after approval; not simulated here
  return r.to_clob;
 end;

 procedure command(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');act varchar2(20):=d.get_string('action');
  v_trip number:=d.get_number('trip_id');hash_value varchar2(64):=sha(p_request);e RRL_TRADE_EXTRA_STOP_EVENT%rowtype;j json_object_t;dummy number;
  ev json_object_t;p RRL_TRADE_ROUTE_STOP_POLICY%rowtype;v_decision varchar2(20);now timestamp with time zone:=systimestamp;
  v_address varchar2(255):=d.get_string('address');expected number:=d.get_number('expected_version');given_hash varchar2(64):=d.get_string('source_hash');
  v_position number:=d.get_number('position');v_reason varchar2(500):=d.get_string('reason');forbid number:=case when d.get_boolean('new_stops_forbidden')then 1 else 0 end;result_text clob;
 begin
  if op is null or lengthb(op)>100 or not regexp_like(op,'^[A-Za-z0-9_.:-]+$')or v_trip is null or act not in('APPROVE','DECLINE','SET_POLICY')then fail('EXTRA_STOP_REQUEST_INVALID');end if;
  require_edit(v_trip,p_actor);
  -- One writer per trip at a time: the trip row is the same anchor the route commands use for this trip.
  begin select 1 into dummy from RRL_TRANSPORT_TASK where ID=v_trip for update wait 5;
  exception when no_data_found then fail('EXTRA_STOP_TRIP_NOT_FOUND');end;
  require_edit(v_trip,p_actor);
  begin
   select*into e from RRL_TRADE_EXTRA_STOP_EVENT where OPERATION_ID=op;
   if e.TRIP_ID<>v_trip or e.ACTOR<>p_actor or e.REQUEST_HASH<>hash_value then fail('EXTRA_STOP_OPERATION_CONFLICT');end if;
   j:=json_object_t.parse(e.RESULT_JSON);j.put('replayed',true);p_result:=j.to_clob;return;
  exception when no_data_found then null;end;
  if v_reason is null or length(trim(v_reason))<3 then fail('EXTRA_STOP_REASON_REQUIRED');end if;
  p:=policy(v_trip);
  if act='SET_POLICY'then
   if d.get_number('expected_policy_version')is null or d.get_number('expected_policy_version')<>p.VERSION_NO then fail('VERSION_CONFLICT');end if;
   if p.VERSION_NO=0 then insert into RRL_TRADE_ROUTE_STOP_POLICY(TRIP_ID,NEW_STOPS_FORBIDDEN,VERSION_NO,UPDATED_BY,UPDATED_AT)values(v_trip,forbid,1,p_actor,now);
   else update RRL_TRADE_ROUTE_STOP_POLICY set NEW_STOPS_FORBIDDEN=forbid,VERSION_NO=VERSION_NO+1,UPDATED_BY=p_actor,UPDATED_AT=now where TRIP_ID=v_trip;end if;
   j:=json_object_t();j.put('operation_id',op);j.put('trip_id',v_trip);j.put('action',act);j.put('new_stops_forbidden',forbid=1);j.put('policy_version',p.VERSION_NO+1);
   v_decision:='POLICY';
  else
   -- Re-evaluated now, inside this transaction, on the same route source the dispatcher saw; a changed route needs a new v_decision.
   ev:=json_object_t.parse(evaluate(v_trip,p_actor,p_request));
   if expected is null or given_hash is null or ev.get_number('time_version')<>expected or ev.get_string('source_hash')<>given_hash then fail('EXTRA_STOP_SOURCE_CHANGED');end if;
   if act='APPROVE'and(ev.get_string('decision')<>'PROPOSE'or ev.get_number('position')<>v_position)then fail('EXTRA_STOP_NOT_PROPOSED');end if;
   v_decision:=case when act='APPROVE'then 'APPROVED'else 'DECLINED'end;
   j:=ev;j.put('operation_id',op);j.put('action',act);j.put('decision_state',v_decision);j.put('decided_by',p_actor);j.put('decided_at',stamp(now));j.put('reason',trim(v_reason));
   if v_decision='APPROVED'then j.put('next_stage','WAITING_SAP_ORDER');end if;  -- the new stop appears with the SAP order, not before
  end if;
  result_text:=j.to_clob;  -- JSON methods never inside SQL
  insert into RRL_TRADE_EXTRA_STOP_EVENT(OPERATION_ID,TRIP_ID,ACTION,ADDRESS,POSITION_NO,DECISION,SOURCE_HASH,TIME_VERSION,REQUEST_HASH,ACTOR,EVENT_AT,RESULT_JSON)
   values(op,v_trip,act,v_address,v_position,v_decision,given_hash,expected,hash_value,p_actor,now,result_text);
  j.put('replayed',false);p_result:=j.to_clob;
 end;

 function decisions(p_trip number,p_actor varchar2)return clob is ctx clob;c json_object_t;r json_object_t:=json_object_t();a json_array_t:=json_array_t();
  o json_object_t;p RRL_TRADE_ROUTE_STOP_POLICY%rowtype;current_hash varchar2(64);
 begin
  RRL_TT_TIME_API.context(p_trip,p_actor,ctx);c:=json_object_t.parse(ctx);current_hash:=c.get_string('source_hash');
  for x in(select OPERATION_ID,ACTION,ADDRESS,POSITION_NO,DECISION,SOURCE_HASH,ACTOR,EVENT_AT from RRL_TRADE_EXTRA_STOP_EVENT
    where TRIP_ID=p_trip and ACTION in('APPROVE','DECLINE')order by EVENT_AT desc fetch first 50 rows only)loop
   o:=json_object_t();o.put('operation_id',x.OPERATION_ID);o.put('address',x.ADDRESS);o.put('position',x.POSITION_NO);o.put('decision_state',x.DECISION);
   o.put('decided_by',x.ACTOR);o.put('decided_at',stamp(x.EVENT_AT));
   -- A decision is bound to the route it was made on.
   o.put('validity',case when x.SOURCE_HASH=current_hash then 'CURRENT'else 'STALE_ROUTE_CHANGED'end);a.append(o);
  end loop;
  p:=policy(p_trip);r.put('trip_id',p_trip);r.put('source_hash',current_hash);r.put('time_version',c.get_number('version'));
  r.put('new_stops_forbidden',p.NEW_STOPS_FORBIDDEN=1);r.put('policy_version',p.VERSION_NO);r.put('decisions',a);
  return r.to_clob;
 end;
end;
/
