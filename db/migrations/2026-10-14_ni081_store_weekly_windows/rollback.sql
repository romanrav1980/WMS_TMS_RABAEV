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

create or replace PACKAGE BODY          "RRL_TT_TIME_API" as
 g_operation varchar2(100);g_tx varchar2(100);
 function write_allowed(p_operation varchar2)return number is begin
  if g_operation=p_operation and g_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;
 end;
 procedure scope(p_trip number,p_actor varchar2)is w RRL_TRANSPORT_TASK%rowtype;n number:=0;allowed number;begin
  select count(*)into allowed from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'transport_dispatch_edit')=1;
  if allowed!=1 then raise_application_error(-20882,'TT_TIME_ACTIVE_DISPATCHER_REQUIRED');end if;
  select *into w from RRL_TRANSPORT_TASK where ID=p_trip;
  for member in(select ID,WARE_ID from RRL_SBORKA_PALLETS where TRANSTASK_ID=p_trip order by ID fetch first 201 rows only)loop
   n:=n+1;if n>200 then raise_application_error(-20886,'TT_TIME_MEMBER_BOUND_200');end if;
   RRL_TRANSPORT_PLAN_RULES.assert_actor(p_actor,member.WARE_ID);
  end loop;
  if n=0 and nvl(w.USER_ID,'~')!=p_actor then
   select count(*)into allowed from RUSERS where ID=p_actor and upper(trim(USER_GROUP))='GLOBAL_ADMIN';
   if allowed!=1 then raise_application_error(-20882,'TT_TIME_EMPTY_TRIP_OWNER_REQUIRED');end if;
  end if;
 end;
 procedure snapshot(p_trip number,p_source out clob,p_hash out varchar2)is
  w RRL_TRANSPORT_TASK%rowtype;b json_object_t:=json_object_t();a json_array_t:=json_array_t();o json_object_t;n number:=0;
 begin
  select *into w from RRL_TRANSPORT_TASK where ID=p_trip;
  b.put('trip_id',p_trip);b.put('vehicle_num',w.TRANSPORT);b.put('driver_id',w.VODITEL_ID);b.put('dock',w.DOCK);
  b.put('source_contract_version',6);b.put('transport_type',w.TRANSTYPE);
  b.put('shipment_date',to_char(w.SHIPMENT_DATE,'YYYY-MM-DD HH24:MI:SS'));b.put('shipment_time',to_char(w.SHIPMENT_TIME,'YYYY-MM-DD HH24:MI:SS'));
  for member in(select ID,ST_NUMBER,WARE_ID,CONDITION,PALLET_UID,ADDR,STDATE,ORD,ZONE_TIME_PLAN_IN,ZONE_TIME_PLAN_OUT from RRL_SBORKA_PALLETS where TRANSTASK_ID=p_trip order by ID fetch first 201 rows only)loop
   n:=n+1;if n>200 then raise_application_error(-20886,'TT_TIME_MEMBER_BOUND_200');end if;
   o:=json_object_t();o.put('id',member.ID);o.put('st_number',member.ST_NUMBER);o.put('warehouse_id',member.WARE_ID);
   o.put('pallet_identifier',member.PALLET_UID);o.put('address',member.ADDR);o.put('st_date',to_char(member.STDATE,'YYYY-MM-DD HH24:MI:SS'));o.put('route_ordinal',member.ORD);o.put('delivery_window_from',to_char(member.ZONE_TIME_PLAN_IN,'YYYY-MM-DD HH24:MI:SS'));o.put('delivery_window_to',to_char(member.ZONE_TIME_PLAN_OUT,'YYYY-MM-DD HH24:MI:SS'));a.append(o);
  end loop;
  b.put('members',a);a:=json_array_t();n:=0;
  for warehouse in(select distinct WARE_ID from RRL_SBORKA_PALLETS where TRANSTASK_ID=p_trip order by WARE_ID)loop
   declare origin_wire clob;begin
    RRL_WARE_DEPOT_API.material(warehouse.WARE_ID,origin_wire);a.append(json_object_t.parse(origin_wire));
   end;
  end loop;
  b.put('warehouse_origins',a);a:=json_array_t();
  n:=0;
  for destination in(select ADDR,count(*) ADDRESS_COUNT,min(UNLOAD_NORM_MIN) UNLOAD_NORM_MIN,min(TW_STRICT) TW_STRICT,min(SHIROTA) LATITUDE,min(DOLGOTA) LONGITUDE
    from RRL_ADDR where nvl(DELETED3,0)=0 and ADDR in(select ADDR from RRL_SBORKA_PALLETS where TRANSTASK_ID=p_trip)
    group by ADDR order by ADDR fetch first 201 rows only)loop
   n:=n+1;if n>200 then raise_application_error(-20886,'TT_TIME_DESTINATION_BOUND_200');end if;
   o:=json_object_t();o.put('address',destination.ADDR);o.put('address_count',destination.ADDRESS_COUNT);
   o.put('unload_norm_min',destination.UNLOAD_NORM_MIN);o.put('window_strict',destination.TW_STRICT);
   o.put('latitude',destination.LATITUDE);o.put('longitude',destination.LONGITUDE);a.append(o);
  end loop;
  b.put('destination_rules',a);a:=json_array_t();n:=0;


  for line in(select r.ID,r.PALLET_UID,r.ARTICUL,r.QUANTITY,r.EI,r.ORDER_WEIGHT,r.TAREWEIGHT,r.TARESIZE,r.PACK_COUNT,r.DOCID,r.WARE_ID
   from RRL_SBORKA_PALLET_ROWS r where exists(select 1 from RRL_SBORKA_PALLETS member where member.TRANSTASK_ID=p_trip and member.PALLET_UID=r.PALLET_UID)
   order by r.ID fetch first 2001 rows only)loop
   n:=n+1;if n>2000 then raise_application_error(-20886,'TT_TIME_SOURCE_LINE_BOUND_2000');end if;
   o:=json_object_t();o.put('id',line.ID);o.put('pallet_identifier',line.PALLET_UID);o.put('article',line.ARTICUL);
   o.put('quantity',line.QUANTITY);o.put('unit',line.EI);o.put('order_weight',line.ORDER_WEIGHT);o.put('tare_weight',line.TAREWEIGHT);
   o.put('tare_size',line.TARESIZE);o.put('pack_count',line.PACK_COUNT);o.put('document_id',line.DOCID);o.put('warehouse_id',line.WARE_ID);a.append(o);
  end loop;
  b.put('source_lines',a);a:=json_array_t();n:=0;
  for op in(select *from RRL_TT_OPERATIONS where TT_ID=p_trip order by ORD,ID fetch first 201 rows only)loop
   n:=n+1;if n>200 then raise_application_error(-20886,'TT_TIME_OPERATION_BOUND_200');end if;
   o:=json_object_t();o.put('operation_id',op.ID);o.put('code',op.OPERATION_CODE);o.put('ordinal',op.ORD);o.put('duration_min',op.DURATION_MIN);
   o.put('plan_start',to_char(op.PLAN_START,'YYYY-MM-DD HH24:MI:SS'));o.put('plan_end',to_char(op.PLAN_END,'YYYY-MM-DD HH24:MI:SS'));
   a.append(o);
  end loop;
  b.put('operations',a);
  declare material_wire clob;begin RRL_TT_ROUTE_SCHEDULE.material(b.to_clob,material_wire);b.put('route_material',json_object_t.parse(material_wire));end;
  p_source:=b.to_clob;
  p_hash:=lower(rawtohex(sys.dbms_crypto.hash(p_source,sys.dbms_crypto.hash_sh256)));
 end;
 procedure assert_published_resources(p_trip RRL_TRANSPORT_TASK%rowtype,p_start date,p_finish date,p_zone varchar2,p_schedule clob)is
  v_start timestamp with time zone;v_finish timestamp with time zone;
  v_other_start timestamp with time zone;v_other_finish timestamp with time zone;v_a timestamp with time zone;v_b timestamp with time zone;
  v_source clob;v_hash varchar2(64);v_n number:=0;v_ops number:=0;b json_object_t;ops json_array_t;o json_object_t;chain json_array_t;peer json_object_t;peer_ops json_array_t;
  begin_chain json_object_t:=json_object_t.parse(p_schedule);
 begin
  select from_tz(cast(p_start as timestamp),p_zone),from_tz(cast(p_finish as timestamp),p_zone)into v_start,v_finish from dual;
  chain:=begin_chain.get_array('segments');
  for other in(select t.ID,t.VODITEL_ID,a.SOURCE_HASH,a.RESULT_JSON
   from RRL_TRANSPORT_TASK t join RRL_TT_TIME_APPROVAL a on a.TT_ID=t.ID
   where t.ID!=p_trip.ID and nvl(t.DELETED,0)=0 and t.CONDITION='Спланирован'and nvl(t.PAY_ORDER_ID,0)=0
   and(t.TRANSPORT=p_trip.TRANSPORT or t.VODITEL_ID=p_trip.VODITEL_ID)
   and a.VERSION_NO=(select max(latest.VERSION_NO)from RRL_TT_TIME_APPROVAL latest where latest.TT_ID=t.ID)
   order by t.ID fetch first 201 rows only)loop
   v_n:=v_n+1;if v_n>200 then raise_application_error(-20886,'TT_TIME_RESOURCE_PLAN_BOUND_200');end if;
   snapshot(other.ID,v_source,v_hash);
   if v_hash=other.SOURCE_HASH then
    b:=json_object_t.parse(other.RESULT_JSON);ops:=b.get_array('operations');v_other_start:=null;v_other_finish:=null;
    if ops is null or ops.get_size not between 1 and 200 then raise_application_error(-20886,'TT_TIME_RESOURCE_PLAN_OPERATIONS_INVALID');end if;
    v_ops:=v_ops+ops.get_size;if v_ops>2000 then raise_application_error(-20886,'TT_TIME_RESOURCE_OPERATION_BOUND_2000');end if;
    for i in 0..ops.get_size-1 loop
     o:=treat(ops.get(i)as json_object_t);
     v_a:=to_timestamp_tz(o.get_string('start_at'),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');
     v_b:=to_timestamp_tz(o.get_string('finish_at'),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');
     if v_a is null or v_b is null or v_b<v_a then raise_application_error(-20886,'TT_TIME_RESOURCE_PLAN_INTERVAL_INVALID');end if;
     if v_other_start is null or v_a<v_other_start then v_other_start:=v_a;end if;
     if v_other_finish is null or v_b>v_other_finish then v_other_finish:=v_b;end if;
    end loop;
    if v_start<v_other_finish and v_finish>v_other_start then raise_application_error(-20886,'TT_TIME_APPROVED_RESOURCE_OVERLAP');end if;
    if other.VODITEL_ID=p_trip.VODITEL_ID and v_other_start<v_finish+interval '7' day and v_other_finish>v_start-interval '7' day then
     peer:=b.get_object('route_schedule');
     if peer is null then raise_application_error(-20886,'TT_TIME_DRIVER_PEER_V6_APPROVAL_REQUIRED');end if;
     peer_ops:=peer.get_array('segments');
     for i in 0..peer_ops.get_size-1 loop chain.append(peer_ops.get(i));end loop;
    end if;
   end if;
  end loop;
  RRL_TT_ROUTE_SCHEDULE.assert_chain(chain.to_clob,p_zone);
 end;
 procedure context(p_trip number,p_actor varchar2,p_result out clob)is
  src clob;hash varchar2(64);v_version number;saved RRL_TT_TIME_APPROVAL%rowtype;b json_object_t:=json_object_t();
 begin
  scope(p_trip,p_actor);snapshot(p_trip,src,hash);
  select nvl(max(VERSION_NO),0)into v_version from RRL_TT_TIME_APPROVAL where TT_ID=p_trip;
  b.put('trip_id',p_trip);b.put('source_hash',hash);b.put('version',v_version);b.put('source',json_object_t.parse(src));
  b.put('approval_status','NO_APPROVAL');b.put('operational_admission',false);
  if v_version>0 then
   select *into saved from RRL_TT_TIME_APPROVAL where TT_ID=p_trip and VERSION_NO=v_version;
   if not json_object_t.parse(saved.RESULT_JSON).has('source_contract_version')then b.put('approval_status','LEGACY_SOURCE_CONTRACT');
   elsif saved.SOURCE_HASH=hash then b.put('approval_status','APPROVED');else b.put('approval_status','SOURCE_CHANGED');end if;
   b.put('last_approval',json_object_t.parse(saved.RESULT_JSON));
  end if;
  p_result:=b.to_clob;
 end;
 procedure approve(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob)is
  b json_object_t;w RRL_TRANSPORT_TASK%rowtype;saved RRL_TT_TIME_APPROVAL%rowtype;
  v_trip number;v_version number;v_req_hash varchar2(64);v_source clob;v_source_hash varchar2(64);v_zone varchar2(50);v_reason nvarchar2(500);v_phase varchar2(40);
  v_metadata boolean:=false;n number;v_start date;v_finish date;v_aware clob;v_schedule clob;route_result json_object_t;route_issue json_object_t;result json_object_t:=json_object_t();
 begin
  if p_operation is null or lengthb(p_operation)>100 or not regexp_like(p_operation,'^[A-Za-z0-9_.:-]+$')or p_body is null or dbms_lob.getlength(p_body)>2000 then raise_application_error(-20886,'TT_TIME_INPUT_BOUND');end if;
  b:=json_object_t.parse(p_body);v_trip:=b.get_number('trip_id');scope(v_trip,p_actor);
  v_req_hash:=lower(rawtohex(sys.dbms_crypto.hash(p_body,sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_METADATA_TX.begin_change(p_actor,'transport_dispatch_edit');v_metadata:=true;savepoint RRL_TT_TIME248;
  select *into w from RRL_TRANSPORT_TASK where ID=v_trip for update;scope(v_trip,p_actor);
  begin
   select *into saved from RRL_TT_TIME_APPROVAL where OPERATION_ID=p_operation;
   if saved.ACTOR!=p_actor or saved.TT_ID!=v_trip or saved.REQUEST_HASH!=v_req_hash then raise_application_error(-20886,'TT_TIME_OPERATION_PAYLOAD_CONFLICT');end if;
   p_result:=saved.RESULT_JSON;RRL_STOCK_METADATA_TX.end_change;return;
  exception when no_data_found then null;end;
  snapshot(v_trip,v_source,v_source_hash);
  RRL_TT_ROUTE_SCHEDULE.lock_material(v_source);
  snapshot(v_trip,v_source,v_source_hash);
  select nvl(max(VERSION_NO),0)into v_version from RRL_TT_TIME_APPROVAL where TT_ID=v_trip;
  if b.get_number('expected_version')is null or b.get_number('expected_version')!=v_version or b.get_string('source_hash')is null or b.get_string('source_hash')!=v_source_hash then raise_application_error(-20886,'TT_TIME_SOURCE_CHANGED');end if;
  if nvl(w.DELETED,0)!=0 or w.CONDITION is null or w.CONDITION!='Спланирован'or nvl(w.PAY_ORDER_ID,0)>0 or w.TRANSPORT is null or w.VODITEL_ID is null or w.VODITEL_ID<=0 then raise_application_error(-20886,'TT_TIME_CURRENT_PLANNED_VEHICLE_DRIVER_REQUIRED');end if;
  select count(*)into n from RRL_TT_HU_LOAD_FACT where TT_ID=v_trip and STATUS in('LOADED','DEPARTED');
  v_phase:=nvl(b.get_string('approval_phase'),'BEFORE_LOADING');
  if v_phase not in('BEFORE_LOADING','AFTER_LOADING_REVIEW')then raise_application_error(-20886,'TT_TIME_APPROVAL_PHASE_REQUIRED');end if;
  if n>0 then
   if v_phase!='AFTER_LOADING_REVIEW'then raise_application_error(-20886,'TT_TIME_PHYSICAL_EXECUTION_FROZEN');end if;
   select count(*)into n from RRL_SBORKA_PALLETS p where p.TRANSTASK_ID=v_trip
    and(nvl(p.CONDITION,-1)!=2 or(select count(*)from RRL_TT_HU_LOAD_ST m
      join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=m.LOAD_OPERATION_ID
      join RRL_STOCK_OPERATION op on op.OPERATION_ID=l.LOAD_OPERATION_ID
      join RRL_TR_VEHICLE vehicle on vehicle.ID=l.VEHICLE_ID and vehicle.NUM=w.TRANSPORT
      where m.SBORKA_PALLET_ID=p.ID and m.ACTIVE_FLAG=1 and l.TT_ID=v_trip
       and l.STATUS='LOADED'and l.VEHICLE_NUMBER=w.TRANSPORT and l.DOCK=w.DOCK
       and l.CUSTODY_RELEASED_AT is null and op.STATE='APPLIED')!=1);
   if n>0 then raise_application_error(-20886,'TT_TIME_ALL_CURRENT_MEMBERS_LOADED_PROOF_REQUIRED');end if;
   select count(*)into n from RRL_SBORKA_PALLETS where TRANSTASK_ID=v_trip;
   if n<1 then raise_application_error(-20886,'TT_TIME_CURRENT_MEMBERS_REQUIRED');end if;
  elsif v_phase='AFTER_LOADING_REVIEW'then raise_application_error(-20886,'TT_TIME_REVIEW_REQUIRES_ACTUAL_LOAD');end if;
  select count(*),min(PLAN_START),max(PLAN_END)into n,v_start,v_finish from RRL_TT_OPERATIONS where TT_ID=v_trip;
  if n<1 or n>200 or v_start is null or v_finish is null or v_finish<=v_start or v_finish-v_start>7 then raise_application_error(-20886,'TT_TIME_POSITIVE_BOUNDED_CHAIN_REQUIRED');end if;
  if w.SHIPMENT_DATE is null or w.SHIPMENT_TIME is null or v_start!=trunc(w.SHIPMENT_DATE)+(w.SHIPMENT_TIME-trunc(w.SHIPMENT_TIME))then raise_application_error(-20886,'TT_TIME_CHAIN_DEPARTURE_CHANGED');end if;
  select count(*)into n from RRL_TT_OPERATIONS where TT_ID=v_trip and(PLAN_START is null or PLAN_END is null or PLAN_END<PLAN_START or FACT_START is not null or FACT_END is not null);
  if n>0 then raise_application_error(-20886,'TT_TIME_VALID_UNSTARTED_CHAIN_REQUIRED');end if;
  v_zone:=b.get_string('time_zone');v_reason:=b.get_string('reason');
  if v_zone is null or v_zone not in('UTC','Europe/Moscow','Asia/Tbilisi')then raise_application_error(-20886,'TT_TIME_EXPLICIT_REGION_REQUIRED');end if;
  if v_reason is null or length(trim(v_reason))<8 then raise_application_error(-20886,'TT_TIME_REASON_REQUIRED');end if;
  RRL_TT_ROUTE_SCHEDULE.calculate(v_source,v_zone,v_schedule);route_result:=json_object_t.parse(v_schedule);
  if route_result.get_array('issues').get_size>0 then route_issue:=treat(route_result.get_array('issues').get(0)as json_object_t);raise_application_error(-20886,'TT_TIME_ROUTE_SCHEDULE_REJECTED:'||route_issue.get_string('code')||':'||route_issue.get_string('address'));end if;
  assert_published_resources(w,v_start,v_finish,v_zone,v_schedule);
  select json_arrayagg(json_object(
   'operation_id'value ID,'code'value OPERATION_CODE,'ordinal'value ORD,
   'start_at'value to_char(from_tz(cast(PLAN_START as timestamp),v_zone),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'),
   'finish_at'value to_char(from_tz(cast(PLAN_END as timestamp),v_zone),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')
   returning clob)order by ORD,ID returning clob)into v_aware from RRL_TT_OPERATIONS where TT_ID=v_trip;
  result.put('trip_id',v_trip);result.put('version',v_version+1);result.put('operation_id',p_operation);result.put('source_hash',v_source_hash);
  result.put('time_zone',v_zone);result.put('reason',v_reason);result.put('actor',p_actor);
  result.put('approval_phase',v_phase);
  result.put('source_contract_version',6);result.put('plan_source',json_object_t.parse(v_source));
  result.put('operations',json_array_t.parse(v_aware));result.put('approval_basis','NATIVE_ROUTE_REST_V6_WITHIN_ORIGINAL_RESOURCE_ENVELOPE');result.put('route_schedule',route_result);
  result.put('operational_admission',false);result.put('stock_changed',false);
  p_result:=result.to_clob;g_operation:=p_operation;g_tx:=dbms_transaction.local_transaction_id(false);
  insert into RRL_TT_TIME_APPROVAL(TT_ID,VERSION_NO,OPERATION_ID,ACTOR,REQUEST_HASH,SOURCE_HASH,TIME_ZONE,REASON,RESULT_JSON)
   values(v_trip,v_version+1,p_operation,p_actor,v_req_hash,v_source_hash,v_zone,v_reason,p_result);
  g_operation:=null;g_tx:=null;RRL_STOCK_METADATA_TX.end_change;
 exception when others then
  if v_metadata then rollback to RRL_TT_TIME248;end if;g_operation:=null;g_tx:=null;
  if v_metadata then RRL_STOCK_METADATA_TX.end_change;end if;raise;
 end;
end;

/

drop package RRL_STORE_WINDOW_RULES;
/
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-14-ni081-store-weekly-windows';
commit;
/
