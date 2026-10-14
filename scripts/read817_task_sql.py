from pathlib import Path
import json,httpx
with httpx.Client(auth=('admin','admin123'),timeout=30)as c:
 r=c.get('http://127.0.0.1:8088/api/admin/slow-sql',params={'path_like':'%/api/warehouse-tasks%','limit':5});print('SLOW_API',r.status_code,[(x['log_id'],x['elapsed_ms'],x['api_path'])for x in r.json()] if r.status_code==200 else 'unavailable')
exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),1) from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and upper(SQL_TEXT)not like '%V\u0024SQL%' and upper(SQL_TEXT)like '%SELECT TASK_ID, TASK_TYPE, TASK_SOURCE%' order by LAST_ACTIVE_TIME desc fetch first 4 rows only");print('TASK_LIST_SQL',q.fetchall())
