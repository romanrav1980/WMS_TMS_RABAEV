exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect')[0])
import time
sql='''with input as(select to_date(:wall,'YYYY-MM-DD HH24:MI')w,:zone z from dual), offsets as(
 select distinct cast(from_tz(cast(w+(level-49)/24 as timestamp),'UTC')at time zone(z)as date)-(w+(level-49)/24) d
 from input connect by level<=97), candidates as(select w-d candidate,z,w from input cross join offsets)
 select count(distinct candidate),to_char(min(candidate),'YYYY-MM-DD HH24:MI') from candidates
 where cast(from_tz(cast(candidate as timestamp),'UTC')at time zone(z)as date)=w'''
results=[]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for stops in [1,8,200]:
  start=time.perf_counter()
  for i in range(stops*17):q.execute(sql,wall='2026-10-14 09:00',zone='Europe/Moscow');assert q.fetchone()[0]==1
  results.append({'stops':stops,'conversions':stops*17,'milliseconds':round((time.perf_counter()-start)*1000,2)})
print(json.dumps(results));Path('reports/retailcase/2026-10-13/codex/STORE_WEEKLY/conversion_before.json').write_text(json.dumps(results,indent=2))
