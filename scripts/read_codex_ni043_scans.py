exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx,time
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");secret=q.fetchone()[0]
 q.execute("select t.TASK_ID from RRL_WAREHOUSE_TASK t join RRL_REMAINS r on r.UID_POLETA=nvl(t.UID_PALLET,t.SSCC)and r.CELL=t.FROM_CELL where t.STATUS in('PLANNED','ASSIGNED','IN_PROGRESS')order by t.TASK_ID desc fetch first 1 row only");task=q.fetchone()[0]
result={'task_id':task,'reads':[]}
with httpx.Client(base_url='http://127.0.0.1:8088',auth=('admin',secret),timeout=30)as client:
 for suffix in ['scan-context','scan-draft']:
  start=time.perf_counter();r=client.get('/api/warehouse-tasks/'+str(task)+'/'+suffix);r.raise_for_status();data=r.json();result['reads'].append({'suffix':suffix,'status':r.status_code,'seconds':round(time.perf_counter()-start,3),'task_id':data.get('task_id')if data else None,'draft_exists':bool(data)if suffix=='scan-draft'else None})
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and EXECUTIONS>0 and (SQL_TEXT like 'select t.TASK_ID,t.STATUS,t.ASSIGNED_TO,t.FROM_CELL CELL,%' or SQL_TEXT like 'select DRAFT_ID,TASK_ID,ACTOR,REQUEST_JSON,UNIT_KEYS_JSON,%') order by LAST_ACTIVE_TIME desc fetch first 6 rows only");result['sql']=q.fetchall()
Path('reports/nicora/2026-10-13/codex/NI043/live_reads.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))