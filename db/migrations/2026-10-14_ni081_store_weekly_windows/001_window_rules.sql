-- MIGRATION_ID: 2026-10-14-ni081-store-weekly-windows
create or replace package RRL_STORE_WINDOW_RULES as
 procedure material(p_source clob,p_result out clob);
 procedure resolve(p_source clob,p_address varchar2,p_arrival date,p_zone varchar2,p_duration number,
  p_open out date,p_close out date,p_service out date,p_kind out varchar2,p_error out varchar2);
end;
/
create or replace package body RRL_STORE_WINDOW_RULES as
 -- Session-local bounded cache of timezone offsets by explicit zone/local date.
 -- It caches timezone rules only, never editable store configuration or resolved windows.
 type offsets_map is table of sys.odcinumberlist index by varchar2(100);
 g_offsets offsets_map;
 function instant(p_wall date,p_zone varchar2)return date is
  v_result date;v_count number;offsets sys.odcinumberlist;cache_key varchar2(100);
 begin
  cache_key:=p_zone||':'||to_char(trunc(p_wall),'YYYY-MM-DD');
  if not g_offsets.exists(cache_key)then
   if g_offsets.count>=256 then g_offsets.delete;end if;
   -- One set-based SQL (97 rows), once per zone/day, not 97 SQL calls per endpoint.
   select distinct cast(from_tz(cast(trunc(p_wall)+(level-49)/24 as timestamp),'UTC')at time zone(p_zone)as date)
    -(trunc(p_wall)+(level-49)/24) bulk collect into offsets from dual connect by level<=97;
   g_offsets(cache_key):=offsets;
  end if;
  offsets:=g_offsets(cache_key);
  select count(distinct candidate),min(candidate) into v_count,v_result from(
   select p_wall-column_value candidate from table(offsets))
   where cast(from_tz(cast(candidate as timestamp),'UTC')at time zone(p_zone)as date)=p_wall;
  if v_count!=1 then raise_application_error(-20886,'STORE_WINDOW_DST_AMBIGUOUS_OR_NONEXISTENT');end if;
  return v_result;
 end;
 procedure material(p_source clob,p_result out clob)is
  a json_array_t:=json_array_t();o json_object_t;rows_json json_array_t;item json_object_t;n number:=0;k number;
 begin
  for r in(select distinct address from json_table(p_source,'$.members[*]'columns(address varchar2(255)path '$.address'))order by address)loop
   n:=n+1;if n>200 then raise_application_error(-20886,'STORE_WINDOW_ADDRESS_BOUND_200');end if;
   o:=json_object_t();o.put('address',r.address);rows_json:=json_array_t();
   begin
    for h in(select PROFILE_VERSION,RECEIVING_WINDOW_MODE,TIMEZONE_REGION,MAX_VEHICLE_OUTER_HEIGHT_MM,MAX_VEHICLE_OUTER_LENGTH_MM
     from RRL_STORE_PROFILE where STORE_ADDR=r.address)loop
     o.put('profile_version',h.PROFILE_VERSION);o.put('mode',h.RECEIVING_WINDOW_MODE);o.put('time_zone',h.TIMEZONE_REGION);
     o.put('max_vehicle_outer_height_mm',h.MAX_VEHICLE_OUTER_HEIGHT_MM);o.put('max_vehicle_outer_length_mm',h.MAX_VEHICLE_OUTER_LENGTH_MM);
    end loop;
    if not o.has('profile_version')then o.put('profile_absent',true);o.put('mode','UNCONFIGURED');else o.put('profile_absent',false);end if;
    k:=0;for w in(select WEEKDAY,FROM_MINUTE,TO_MINUTE from RRL_STORE_RECEIVING_WINDOW where STORE_ADDR=r.address order by WEEKDAY,FROM_MINUTE,TO_MINUTE)loop
     k:=k+1;if k>56 then raise_application_error(-20886,'STORE_WEEKLY_INTERVAL_BOUND_56');end if;
     item:=json_object_t();item.put('weekday',w.WEEKDAY);item.put('from_minute',w.FROM_MINUTE);item.put('to_minute',w.TO_MINUTE);rows_json.append(item);
    end loop;
   end;
   o.put('windows',rows_json);a.append(o);
  end loop;p_result:=a.to_clob;
 end;
 procedure resolve(p_source clob,p_address varchar2,p_arrival date,p_zone varchar2,p_duration number,
  p_open out date,p_close out date,p_service out date,p_kind out varchar2,p_error out varchar2)is
  lo date;hi date;wf date;wt date;weekly_needed boolean:=false;members_count number:=0;
  b json_object_t:=json_object_t.parse(p_source);profiles json_array_t;profile json_object_t;found_count number:=0;
  zone_name varchar2(64);day_local date;arrival_utc date;opening_utc date;closing_utc date;candidate date;
  count_today number:=0;wire clob;weekday_no number;last_end number:=-1;interval_count number:=0;
 begin
  p_open:=null;p_close:=null;p_service:=null;p_error:=null;p_kind:='ST_MATERIALIZED';
  if p_arrival is null then p_error:='ROUTE_ARRIVAL_UNKNOWN';return;end if;
  if p_duration is null or p_duration<=0 or p_duration>1440 then p_error:='DESTINATION_RULE_INVALID';return;end if;
  for m in(select wf,wt from json_table(p_source,'$.members[*]'columns(a varchar2(255)path '$.address',wf varchar2(30)path '$.delivery_window_from',wt varchar2(30)path '$.delivery_window_to'))where a=p_address)loop
   members_count:=members_count+1;
   if m.wf is null and m.wt is null then weekly_needed:=true;
   elsif m.wf is null or m.wt is null then p_error:='DELIVERY_WINDOW_PARTIAL';return;
   else
    wf:=to_date(m.wf,'YYYY-MM-DD HH24:MI:SS');wt:=to_date(m.wt,'YYYY-MM-DD HH24:MI:SS');
    if wf>=wt then p_error:='DELIVERY_WINDOW_REVERSED_OR_EMPTY';return;end if;
    if lo is null or wf>lo then lo:=wf;end if;if hi is null or wt<hi then hi:=wt;end if;
   end if;
  end loop;
  if members_count=0 then p_error:='DELIVERY_MEMBERS_MISSING';return;end if;
  if lo is not null and lo>=hi then p_error:='DELIVERY_WINDOW_DISJOINT';return;end if;
  if not weekly_needed then p_open:=lo;p_close:=hi;p_service:=greatest(p_arrival,lo);return;end if;
  p_kind:=case when lo is null then 'STORE_WEEKLY'else 'ST_AND_STORE_WEEKLY'end;
  profiles:=b.get_array('store_window_profiles');
  if profiles is not null and profiles.get_size>0 then for i in 0..profiles.get_size-1 loop
   profile:=treat(profiles.get(i)as json_object_t);if profile.get_string('address')=p_address then found_count:=found_count+1;wire:=profile.to_clob;end if;
  end loop;end if;
  if found_count!=1 then p_error:='DELIVERY_WINDOW_UNCONFIGURED';return;end if;
  profile:=json_object_t.parse(wire);
  if profile.get_string('mode')!='WEEKLY' then p_error:='DELIVERY_WINDOW_UNCONFIGURED';return;end if;
  zone_name:=profile.get_string('time_zone');if zone_name is null then p_error:='STORE_TIMEZONE_REQUIRED';return;end if;
  arrival_utc:=instant(p_arrival,p_zone);
  select trunc(cast(from_tz(cast(arrival_utc as timestamp),'UTC')at time zone(zone_name)as date))into day_local from dual;
  weekday_no:=day_local-trunc(day_local,'IW')+1;
  -- Deliberately same service day: CLOSED is a refusal, never an implicit overnight reschedule.
  -- At most 8 intervals, one local day, no gap between intervals is treated as available.
  for w in(select f,t from json_table(wire,'$.windows[*]'columns(d number path '$.weekday',f number path '$.from_minute',t number path '$.to_minute'))where d=weekday_no order by f,t)loop
   count_today:=count_today+1;
   if count_today>8 or w.f is null or w.t is null or w.f<0 or w.t>1440 or w.f>=w.t or w.f!=trunc(w.f)or w.t!=trunc(w.t)or w.f<last_end then p_error:='STORE_WEEKLY_INTERVAL_INVALID';return;end if;
   last_end:=w.t;
   opening_utc:=instant(day_local+w.f/1440,zone_name);closing_utc:=instant(day_local+w.t/1440,zone_name);
   select cast(from_tz(cast(opening_utc as timestamp),'UTC')at time zone(p_zone)as date),cast(from_tz(cast(closing_utc as timestamp),'UTC')at time zone(p_zone)as date)into wf,wt from dual;
   if lo is not null then wf:=greatest(wf,lo);wt:=least(wt,hi);end if;
   candidate:=greatest(p_arrival,wf);
   if candidate+p_duration/1440<=wt and p_service is null then p_open:=wf;p_close:=wt;p_service:=candidate;end if;
  end loop;
  if count_today=0 then p_error:='STORE_CLOSED';elsif p_service is null then p_error:='STORE_NO_FEASIBLE_INTERVAL';end if;
 exception when others then
  if sqlcode=-20886 then p_error:=substr(sqlerrm,instr(sqlerrm,':')+2,150);return;end if;
  if sqlcode in(-1882,-1878,-1883,-1843,-1847,-1861,-1839)then p_error:='STORE_TIMEZONE_OR_WINDOW_INVALID';return;end if;
  raise;
 end;
end;
/
