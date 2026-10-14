exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
from time import perf_counter
import httpx
folder=Path('reports/retailcase/2026-10-13/codex/NI081');trip=json.loads((folder/'fixture.json').read_text(encoding='utf-8'))['trip_id'];evidence={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");secret=q.fetchone()[0]
 with httpx.Client(auth=('admin',secret),timeout=20)as client:
  start=perf_counter();r=client.get(f'http://127.0.0.1:8088/api/transport/preflight/trips/{trip}/delivery-windows',params={'time_zone':'Asia/Tbilisi'});assert r.status_code==200,r.text;evidence['http']={'status':r.status_code,'ms':round((perf_counter()-start)*1000,2),'issues':r.json()['issues'],'policy_id':r.json()['policy_id']}
 q.execute("select INDEX_NAME,COLUMN_NAME,COLUMN_POSITION from USER_IND_COLUMNS where TABLE_NAME='RRL_ADDR_DISTANCE_MATRIX'order by INDEX_NAME,COLUMN_POSITION");evidence['road_indexes']=q.fetchall()
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3)AVG_MS,BUFFER_GETS,substr(SQL_TEXT,1,600)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'
 and (SQL_TEXT like '%GROUP BY ADDRESS ORDER BY MIN%'or SQL_TEXT like '%RRL_ADDR_DISTANCE_MATRIX M ON%'or SQL_TEXT like '%RRL_TT_TIME_APPROVAL A ON A.TT_ID%')
 order by LAST_ACTIVE_TIME desc fetch first 10 rows only""");evidence['sql']=q.fetchall()
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%'");evidence['invalid']=q.fetchall()
 q.execute("select MIGRATION_ID,STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-14-ni081-route-rest-approval'");evidence['ledger']=q.fetchall()
(folder/'runtime_sql.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(evidence,ensure_ascii=True))
