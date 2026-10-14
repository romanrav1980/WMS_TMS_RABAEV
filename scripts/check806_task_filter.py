from pathlib import Path
import json,httpx
with httpx.Client(auth=('admin','admin123'),timeout=30)as c:
 r=c.get('http://127.0.0.1:8088/api/warehouse-tasks',params={'task_type':'PUTAWAY','task_source':'MANUAL','source_doc_type':'ST_DEFER','limit':150});assert r.status_code==200,r.text
 rows=r.json();assert rows and all(x['source_doc_type']=='ST_DEFER' and x['task_type']=='PUTAWAY' for x in rows)
 task=next(x for x in rows if x['task_id']==1080);assert task['status']=='DONE' and str(task['qty']) in ('3','3.0')
 Path('tmp/context806.json').write_text(json.dumps({'rows':rows}),encoding='utf-8');print('806 PASS existing task filter',len(rows),'task1080',task['status'])
exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
ctx=json.loads(Path('tmp/context773.json').read_text(encoding='utf-8'))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as conn:
 q=conn.cursor();q.execute("select EVENT_OUTBOX_ID,EVENT_TYPE,AGGREGATE_TYPE,STATUS from RRL_EVENT_OUTBOX where CORRELATION_ID=:operation and EVENT_TYPE='STOCK_POSTED'",operation=ctx['move_operation']);print('WAIT_OUTBOX',q.fetchall())
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),1),substr(SQL_TEXT,1,80) from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and regexp_like(SQL_TEXT,'from[[:space:]]+RRL_WAREHOUSE_TASK','i')and upper(SQL_TEXT)not like '%V$SQL%' order by LAST_ACTIVE_TIME desc fetch first 3 rows only");print('TASK_SQL',q.fetchall())
