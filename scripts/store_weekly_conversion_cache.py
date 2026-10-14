from pathlib import Path
p=Path('db/migrations/2026-10-14_ni081_store_weekly_windows/001_window_rules.sql')
s=p.read_text(encoding='utf-8-sig');Path('reports/nicora/2026-10-13/codex/STORE_WEEKLY/instant_before.sql').write_text(s[s.index(' function instant'):s.index(' procedure material',s.index(' function instant'))],encoding='utf-8')
a=s.index(' -- Map a local');z=s.index(' procedure material',a)
s=s[:a]+''' -- Session-local bounded cache of timezone offsets by explicit zone/local date.
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
''' +s[z:]
p.write_text(s,encoding='utf-8')
