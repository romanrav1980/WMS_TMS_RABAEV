exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect')[0])
import time
p=Path('db/migrations/2026-10-14_ni081_store_weekly_windows/001_window_rules.sql')
src=p.read_text(encoding='utf-8');new=src[src.index(' type offsets_map'):src.index(' procedure material',src.index(' type offsets_map'))]
old=Path('reports/nicora/2026-10-13/codex/STORE_WEEKLY/instant_before.sql').read_text()
results=[]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=120000;q=c.cursor()
 for variant,code in [('original',old),('cached',new)]:
  for stops in [1,8,200]:
   start=time.perf_counter()
   q.execute('declare v_result date;'+code+''' begin
    for i in 1..:n loop v_result:=instant(to_date('2026-10-14 09:00','YYYY-MM-DD HH24:MI'),'Europe/Moscow');end loop;
    if v_result!=to_date('2026-10-14 06:00','YYYY-MM-DD HH24:MI')then raise_application_error(-20999,'WRONG_UTC');end if;end;''',n=stops*17)
   results.append({'variant':variant,'stops':stops,'conversions':stops*17,'milliseconds':round((time.perf_counter()-start)*1000,3)})
  for wall,expected in [('2026-10-25 02:30','AMBIGUOUS'),('2026-03-29 02:30','AMBIGUOUS')]:
   q.execute('declare v_result date;failed boolean:=false;'+code+''' begin
    begin v_result:=instant(to_date(:wall,'YYYY-MM-DD HH24:MI'),'Europe/Berlin');exception when others then if sqlcode=-20886 then failed:=true;else raise;end if;end;
    if not failed then raise_application_error(-20999,'DST_NOT_REJECTED');end if;end;''',wall=wall)
print(json.dumps(results));Path('reports/nicora/2026-10-13/codex/STORE_WEEKLY/conversion_native.json').write_text(json.dumps({'measurements':results,'dst_fold_gap_both_variants':'PASS','writes':False},indent=2))
