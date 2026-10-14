exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx,time
from datetime import datetime,timezone
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");secret=q.fetchone()[0]
 q.execute("select a.PLAN_OPERATION_ID from RRL_WORKLOAD_ATTENDANCE a where a.WARE_ID=:ware and a.SITE_CODE=:site and a.START_AT<:finish and a.FINISH_AT>:start_at and not exists(select 1 from RRL_WORKLOAD_ATTEND_CANCEL c where c.PLAN_OPERATION_ID=a.PLAN_OPERATION_ID) order by a.START_AT,a.PLAN_OPERATION_ID",ware=6667491,site='QA134',start_at=datetime(2026,10,1,tzinfo=timezone.utc),finish=datetime(2026,11,1,tzinfo=timezone.utc));expected=[r[0]for r in q.fetchall()]
result={}
with httpx.Client(base_url='http://127.0.0.1:8088',auth=('admin',secret),timeout=30)as client:
 path='/api/resources/workload/warehouses/6667491'
 t=time.perf_counter();old=client.get(path);old.raise_for_status();old=old.json();result['unfiltered_seconds']=round(time.perf_counter()-t,3)
 params={'site_code':'QA134','start_at':'2026-10-01T00:00:00Z','finish_at':'2026-11-01T00:00:00Z'}
 t=time.perf_counter();r=client.get(path,params=params);r.raise_for_status();data=r.json();result['filtered_seconds']=round(time.perf_counter()-t,3)
 assert data['norms']==[row for row in old['norms']if row['site_code']=='QA134']
 assert [row['plan_operation_id']for row in data['planned_attendance']]==expected
 assert not data['stock_changed'] and not data['actual_presence_created']
 result['norm_count']=len(data['norms']);result['attendance_ids']=expected
 result['one_bound']=client.get(path,params={'start_at':params['start_at']}).status_code
 result['over31days']=client.get(path,params={**params,'finish_at':'2026-11-02T00:00:00Z'}).status_code
 assert result['one_bound']==result['over31days']==422
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and EXECUTIONS>0 and (SQL_TEXT like 'select n.WARE_ID,n.SITE_CODE,n.ARTICLE%' or SQL_TEXT like 'select a.PLAN_OPERATION_ID,a.WARE_ID,a.SITE_CODE%') order by LAST_ACTIVE_TIME desc fetch first 8 rows only");result['sql']=q.fetchall()
print(json.dumps(result));Path('tmp/result1397.json').write_text(json.dumps(result,indent=2),encoding='utf-8')