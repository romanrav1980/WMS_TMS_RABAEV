exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx,time
case='STORE383.RECEIPT:c09bc5c0'
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");secret=q.fetchone()[0]
with httpx.Client(base_url='http://127.0.0.1:8088',auth=('admin',secret),timeout=30)as client:
 start=time.perf_counter();r=client.get('/api/delivery/store-receipts/cases/'+case);r.raise_for_status();data=r.json();result={'case_id':data['case_id'],'status':r.status_code,'seconds':round(time.perf_counter()-start,3),'lines':data['lines'],'obligations':data['obligations']}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,90) from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and EXECUTIONS>0 and(SQL_TEXT like '%from RRL_STORE_DISCREPANCY_CASE where CASE_ID=:case_id%' or SQL_TEXT like '%from RRL_STORE_RECEIPT_LINE where OPERATION_ID=:case_id%' or SQL_TEXT like '%from RRL_STORE_DELIVERY_OBLIGATION where CASE_ID=:case_id%') and SQL_TEXT not like 'select SQL_ID,%' order by LAST_ACTIVE_TIME desc fetch first 5 rows only");result['sql']=q.fetchall()
Path('reports/retailcase/2026-10-13/codex/C0023/live_read.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({'status':result['status'],'seconds':result['seconds'],'lines':len(result['lines']),'sql':result['sql']}))