create or replace package body RRL_TT_ROUTE_SCHEDULE as
 procedure material(p_source clob,p_result out clob)is
  b json_object_t:=json_object_t.parse(p_source);r json_object_t:=json_object_t();origins json_array_t;
  stops json_array_t:=json_array_t();pairs json_array_t:=json_array_t();legs json_array_t:=json_array_t();o json_object_t;
  depot varchar2(200);prev varchar2(200);n number:=0;wire clob;last_ord number;valid boolean:=true;
 begin
  origins:=b.get_array('warehouse_origins');
  if origins is not null and origins.get_size=1 then
   o:=treat(origins.get(0)as json_object_t);
   if o.get_boolean('configured')then depot:=o.get_string('depot_address');end if;
  end if;
  prev:=depot;
  for s in(select address,min(route_ord)ord,count(*)cnt,count(route_ord)ord_count,min(route_ord)lo,max(route_ord)hi
   from json_table(p_source,'$.members[*]'columns(address varchar2(200)path '$.address',route_ord number path '$.route_ordinal'))
   group by address order by min(route_ord),address)loop
   n:=n+1;if n>200 then raise_application_error(-20886,'TT_ROUTE_STOP_BOUND_200');end if;
   if s.address is null or s.ord_count!=s.cnt or s.lo<0 or s.lo!=trunc(s.lo)or last_ord=s.ord then valid:=false;end if;
   last_ord:=s.ord;stops.append(s.address);o:=json_object_t();o.put('from_address',prev);o.put('to_address',s.address);pairs.append(o);prev:=s.address;
  end loop;
  o:=json_object_t();o.put('from_address',prev);o.put('to_address',depot);pairs.append(o);wire:=pairs.to_clob;
  for leg in(select /*+ leading(p m) use_nl(m) index(m PK_DIST_MATRIX) */ /* NI081_ROUTE_LEGS */ p.pos,p.a,p.b,m.DURATION_MIN,m.DURATION_BASIS,m.SOURCE,m.UPDATED_AT,
   case when m.UPDATED_AT>=sysdate-1 then 1 else 0 end fresh
   from json_table(wire,'$[*]'columns(pos for ordinality,a varchar2(200)path '$.from_address',b varchar2(200)path '$.to_address'))p
   left join RRL_ADDR_DISTANCE_MATRIX m on m.FROM_ADDR=p.a and m.TO_ADDR=p.b order by p.pos)loop
   o:=json_object_t();o.put('from_address',leg.a);o.put('to_address',leg.b);o.put('duration_min',leg.DURATION_MIN);
   o.put('duration_basis',leg.DURATION_BASIS);o.put('provider',leg.SOURCE);o.put('updated_at',to_char(leg.UPDATED_AT,'YYYY-MM-DD HH24:MI:SS'));o.put('fresh',leg.fresh=1);
   legs.append(o);
  end loop;
  r.put('policy_id','REV55_ROUTE_V6_120_15_540_ROAD24H');r.put('continuous_limit_min',120);r.put('minimum_break_min',15);r.put('drive_limit_min',540);
  r.put('maximum_cache_age_hours',24);r.put('depot_address',depot);r.put('stops',stops);r.put('legs',legs);r.put('order_valid',valid and n>0);p_result:=r.to_clob;
 end;
 procedure lock_material(p_source clob)is
  b json_object_t:=json_object_t.parse(p_source);m json_object_t;wire clob;dummy number;
 begin
  m:=b.get_object('route_material');wire:=m.to_clob;
  -- Same order for every approval; no lock in a rank earlier than CONFIG/TT.
  for r in(select a.rowid rid from RRL_ADDR a where nvl(a.DELETED3,0)=0 and a.ADDR in
   (select address from json_table(p_source,'$.members[*]'columns(address varchar2(200)path '$.address')))order by a.ADDR,a.rowid)loop
   select 1 into dummy from RRL_ADDR where rowid=r.rid for update wait 5;
  end loop;
  for r in(select distinct a,b from json_table(wire,'$.legs[*]'columns(a varchar2(200)path '$.from_address',b varchar2(200)path '$.to_address'))order by a,b)loop
   begin select 1 into dummy from RRL_ADDR_DISTANCE_MATRIX where FROM_ADDR=r.a and TO_ADDR=r.b for update wait 5;
   exception when no_data_found then raise_application_error(-20886,'TT_ROUTE_ROAD_MISSING');end;
  end loop;
 end;
 procedure assert_chain(p_segments clob,p_zone varchar2)is
  continuous number:=0;total number:=0;minutes number;a date;z date;part_end date;previous_end date;count_ops number:=0;
  type totals_t is table of number index by varchar2(10);totals totals_t;day_key varchar2(10);
 begin
  for op in(select code,a,z from json_table(p_segments,'$[*]'columns(code varchar2(50)path '$.code',a varchar2(60)path '$.start_at',z varchar2(60)path '$.finish_at'))order by to_timestamp_tz(a,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'),to_timestamp_tz(z,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'))loop
   count_ops:=count_ops+1;if count_ops>2000 then raise_application_error(-20886,'TT_TIME_DRIVER_OPERATION_BOUND_2000');end if;
   select cast(to_timestamp_tz(op.a,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')at time zone (p_zone) as date),
    cast(to_timestamp_tz(op.z,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')at time zone (p_zone) as date)into a,z from dual;
   if a is null or z is null or z<a or(previous_end is not null and a<previous_end)then raise_application_error(-20886,'TT_TIME_DRIVER_CHAIN_OVERLAP_OR_INVALID');end if;
   previous_end:=z;minutes:=(z-a)*1440;
   if op.code in('DRIVE','DRIVE_BACK','DRIVE_TO_CLIENT')then
    continuous:=continuous+minutes;
    if continuous>120.000001 then raise_application_error(-20886,'TT_TIME_DRIVER_CONTINUOUS_LIMIT');end if;
    while a<z loop
     part_end:=least(z,trunc(a)+1);day_key:=to_char(a,'YYYY-MM-DD');
     if not totals.exists(day_key)then totals(day_key):=0;end if;
     totals(day_key):=totals(day_key)+(part_end-a)*1440;
     if totals(day_key)>540.000001 then raise_application_error(-20886,'TT_TIME_DRIVER_DAY_LIMIT');end if;a:=part_end;
    end loop;
   elsif op.code='REST'and minutes>=15 then continuous:=0;end if;
  end loop;
 end;
 procedure calculate(p_source clob,p_zone varchar2,p_result out clob)is
  b json_object_t:=json_object_t.parse(p_source);m json_object_t;r json_object_t:=json_object_t();legs json_array_t;addresses json_array_t;
  segments json_array_t:=json_array_t();stops json_array_t:=json_array_t();issues json_array_t:=json_array_t();warnings json_array_t:=json_array_t();errors json_array_t;
  leg json_object_t;o json_object_t;clock_at date;departure date;finish_bound date;arrival date;service_at date;opening date;closing date;return_at date;
  address varchar2(200);norm number;strict number;cnt number;missing number;n number;continuous number:=0;total number:=0;late number;stnums json_array_t;
  function iso(p_date date)return varchar2 is begin
   return to_char(from_tz(cast(p_date as timestamp),p_zone),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');end;
  procedure issue(p_code varchar2)is x json_object_t:=json_object_t();begin x.put('code',p_code);x.put('address',address);issues.append(x);end;
  procedure segment(p_code varchar2,p_min number)is x json_object_t:=json_object_t();begin
   if p_min<=0 then return;end if;
   x.put('code',p_code);x.put('start_at',iso(clock_at));clock_at:=clock_at+p_min/1440;x.put('finish_at',iso(clock_at));
   x.put('duration_min',RRL_STOCK_PLAN_HELPER.decimal_text(p_min));x.put('address',address);segments.append(x);
  end;
  procedure drive(p_leg json_object_t)is remaining number;piece number;begin
   if p_leg.get_string('from_address')is null or p_leg.get_string('to_address')is null or p_leg.get_string('from_address')=p_leg.get_string('to_address')
    or nvl(p_leg.get_string('duration_basis'),'~')!='ROAD_PROFILE_ESTIMATE' or not p_leg.get_boolean('fresh')
    or p_leg.get_number('duration_min')is null or p_leg.get_number('duration_min')<=0 then
    issue('ROUTE_ROAD_MISSING_STALE_OR_UNSUPPORTED');clock_at:=null;return;end if;
   remaining:=p_leg.get_number('duration_min');total:=total+remaining;
   if total>540 then issue('DRIVER_TRIP_DRIVE_LIMIT');clock_at:=null;return;end if;
   if clock_at is null then return;end if;
   while remaining>0 loop
    if continuous>=120 then segment('REST',15);continuous:=0;end if;
    piece:=least(remaining,120-continuous);segment('DRIVE',piece);continuous:=continuous+piece;remaining:=remaining-piece;
   end loop;
  end;
 begin
  if p_zone is null or p_zone not in('UTC','Europe/Moscow','Asia/Tbilisi')then raise_application_error(-20886,'TT_TIME_EXPLICIT_REGION_REQUIRED');end if;
  m:=b.get_object('route_material');legs:=m.get_array('legs');addresses:=m.get_array('stops');
  if not m.get_boolean('order_valid')then issue('ROUTE_ORDER_INVALID');end if;
  if m.get_string('depot_address')is null then issue('WAREHOUSE_DEPOT_NOT_CONFIGURED');end if;
  select count(*),min(to_date(start_at,'YYYY-MM-DD HH24:MI:SS'))into n,departure
   from json_table(p_source,'$.operations[*]'columns(code varchar2(50)path '$.code',start_at varchar2(30)path '$.plan_start'))where code='DRIVE';
  select max(to_date(end_at,'YYYY-MM-DD HH24:MI:SS'))into finish_bound
   from json_table(p_source,'$.operations[*]'columns(code varchar2(50)path '$.code',end_at varchar2(30)path '$.plan_end'))where code='DRIVE_BACK';
  clock_at:=departure;if n!=1 or departure is null then issue('ROUTE_DEPARTURE_STAGE_UNKNOWN');clock_at:=null;end if;
  -- Preserve explicit pre-route duties/rest; no unknown gap is treated as rest.
  for op in(select code,a,z from json_table(p_source,'$.operations[*]'columns(code varchar2(50)path '$.code',a varchar2(30)path '$.plan_start',z varchar2(30)path '$.plan_end'))
   where to_date(z,'YYYY-MM-DD HH24:MI:SS')<=departure order by a,z)loop
   o:=json_object_t();o.put('code',op.code);o.put('start_at',iso(to_date(op.a,'YYYY-MM-DD HH24:MI:SS')));o.put('finish_at',iso(to_date(op.z,'YYYY-MM-DD HH24:MI:SS')));segments.append(o);
  end loop;
  if addresses.get_size>0 then for i in 0..addresses.get_size-1 loop
   address:=addresses.get_string(i);drive(treat(legs.get(i)as json_object_t));arrival:=clock_at;errors:=json_array_t();
   select count(*),count(case when wf is null or wt is null then 1 end),max(to_date(wf,'YYYY-MM-DD HH24:MI:SS')),min(to_date(wt,'YYYY-MM-DD HH24:MI:SS'))
    into cnt,missing,opening,closing from json_table(p_source,'$.members[*]'columns(a varchar2(200)path '$.address',wf varchar2(30)path '$.delivery_window_from',wt varchar2(30)path '$.delivery_window_to'))where a=address;
   select count(*),min(norm),min(strict),min(address_count)into n,norm,strict,cnt
    from json_table(p_source,'$.destination_rules[*]'columns(a varchar2(200)path '$.address',norm number path '$.unload_norm_min',strict number path '$.window_strict',address_count number path '$.address_count'))where a=address;
   if missing>0 or opening is null or closing is null or opening>closing then issue('DELIVERY_WINDOW_MISSING_OR_DISJOINT');errors.append('DELIVERY_WINDOW_MISSING_OR_DISJOINT');clock_at:=null;end if;
   if n!=1 or cnt!=1 or norm is null or norm<=0 or norm>1440 or strict is null or strict not in(0,1)then issue('DESTINATION_RULE_INVALID');errors.append('DESTINATION_RULE_INVALID');clock_at:=null;end if;
   if clock_at is not null and clock_at<opening then segment('WAIT',(opening-clock_at)*1440);end if;
   service_at:=clock_at;if clock_at is not null then segment('UNLOAD',norm);end if;late:=greatest(0,(clock_at-closing)*1440);
   if late>0 then
    if strict=1 then issue('DELIVERY_HARD_WINDOW_MISSED');errors.append('DELIVERY_HARD_WINDOW_MISSED');
    else o:=json_object_t();o.put('code','DELIVERY_SOFT_WINDOW_MISSED');o.put('address',address);warnings.append(o);errors.append('DELIVERY_SOFT_WINDOW_MISSED');end if;
   end if;
   stnums:=json_array_t();for st in(select distinct sn from json_table(p_source,'$.members[*]'columns(a varchar2(200)path '$.address',sn varchar2(200)path '$.st_number'))where a=address order by sn)loop stnums.append(st.sn);end loop;
   o:=json_object_t();o.put('address',address);o.put('st_numbers',stnums);o.put('window_from',iso(opening));o.put('window_to',iso(closing));o.put('arrival_at',iso(arrival));o.put('service_start_at',iso(service_at));o.put('service_finish_at',iso(clock_at));
   o.put('wait_min',RRL_STOCK_PLAN_HELPER.decimal_text((service_at-arrival)*1440));o.put('late_min',RRL_STOCK_PLAN_HELPER.decimal_text(late));o.put('unload_norm_min',RRL_STOCK_PLAN_HELPER.decimal_text(norm));o.put('window_strict',strict);o.put('issues',errors);stops.append(o);
  end loop;end if;
  -- Retain the existing return-loading duty between last delivery and return drive.
  for op in(select code,duration_min from json_table(p_source,'$.operations[*]'columns(code varchar2(50)path '$.code',duration_min number path '$.duration_min',a varchar2(30)path '$.plan_start'))
   where to_date(a,'YYYY-MM-DD HH24:MI:SS')>=departure and to_date(a,'YYYY-MM-DD HH24:MI:SS')<finish_bound
   and code not in('DRIVE','UNLOAD','DRIVE_BACK')order by a)loop
   if op.code='LOAD_RETURNS'and op.duration_min>=0 then
    if clock_at is not null then segment(op.code,op.duration_min);end if;
   elsif op.code!='DEPART'then issue('ROUTE_OPERATION_MAPPING_REQUIRED');end if;
  end loop;
  address:=m.get_string('depot_address');drive(treat(legs.get(legs.get_size-1)as json_object_t));
  if clock_at is null then issue('ROUTE_RETURN_TIME_UNKNOWN');elsif finish_bound is null or clock_at>finish_bound then issue('ROUTE_EXCEEDS_PLANNED_RESOURCE_ENVELOPE');end if;
  return_at:=clock_at;
  if clock_at is not null and finish_bound>=clock_at then segment('WAIT',(finish_bound-clock_at)*1440);end if;
  for op in(select code,a,z from json_table(p_source,'$.operations[*]'columns(code varchar2(50)path '$.code',a varchar2(30)path '$.plan_start',z varchar2(30)path '$.plan_end'))
   where to_date(a,'YYYY-MM-DD HH24:MI:SS')>=finish_bound order by a,z)loop
   o:=json_object_t();o.put('code',op.code);o.put('start_at',iso(to_date(op.a,'YYYY-MM-DD HH24:MI:SS')));o.put('finish_at',iso(to_date(op.z,'YYYY-MM-DD HH24:MI:SS')));segments.append(o);
  end loop;
  r.put('segments',segments);r.put('stops',stops);r.put('return_at',iso(return_at));r.put('departure_at',iso(departure));r.put('issues',issues);r.put('warnings',warnings);r.put('drive_min',RRL_STOCK_PLAN_HELPER.decimal_text(total));
  r.put('status',case when issues.get_size=0 then 'NO_EARLIEST_WINDOW_VIOLATION'else 'INSUFFICIENT_EVIDENCE'end);r.put('policy_id',m.get_string('policy_id'));r.put('time_zone',p_zone);
  r.put('estimate_basis','NATIVE_DRIVE_REST_WAIT_UNLOAD');r.put('driver_breaks_included',true);r.put('legal_compliance_verified',false);r.put('operational_admission',false);r.put('destination_time_zones_verified',false);
  r.put('depot_address',m.get_string('depot_address'));r.put('depot_basis','CONFIGURED_WAREHOUSE_REFERENCE');r.put('read_only',true);r.put('stock_changed',false);p_result:=r.to_clob;
 end;
end;

/
