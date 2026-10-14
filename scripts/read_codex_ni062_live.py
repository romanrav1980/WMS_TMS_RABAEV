exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx,time
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");secret=q.fetchone()[0]
 q.execute("select r.WARE_ID,r.OPERATION_ID from RRL_STORE_RETURN_RECEIPT r where not exists(select 1 from RRL_STORE_RETURN_PLACEMENT p where p.RECEIPT_OPERATION_ID=r.OPERATION_ID) fetch first 1 rows only");pending=q.fetchone()
result={'sample_pending':pending,'reads':[]}
with httpx.Client(base_url='http://127.0.0.1:8088',auth=('admin',secret),timeout=30)as client:
 spec=client.get('/openapi.json').json();params=spec['paths']['/api/inventory/store-return-putaway/warehouses/{ware_id}/pending']['get']['parameters'];assert any(p['name']=='receipt_operation_id'for p in params)
 samples=[(14524201,'REUSE643.RECEIVE:dc1889623c',0),(14524201,'MISSING.LOCAL.RECEIPT',0)]+([(pending[0],pending[1],1)]if pending else [])
 for ware,receipt,count in samples:
  start=time.perf_counter();r=client.get(f'/api/inventory/store-return-putaway/warehouses/{ware}/pending',params={'receipt_operation_id':receipt});r.raise_for_status();data=r.json();assert len(data)==count and all(x['receipt_operation_id']==receipt for x in data);result['reads'].append({'ware':ware,'receipt':receipt,'count':len(data),'ms':round((time.perf_counter()-start)*1000,2)})
 if pending:
  r=client.get('/api/inventory/store-return-putaway/warehouses/14524201/pending',params={'receipt_operation_id':pending[1]});r.raise_for_status();assert pending[0]==14524201 or r.json()==[]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,100) from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%' and SQL_TEXT like '%select r.OPERATION_ID RECEIPT_OPERATION_ID%' and DBMS_LOB.INSTR(SQL_FULLTEXT,'r.OPERATION_ID=:receipt')>0 order by LAST_ACTIVE_TIME desc fetch first 4 rows only");result['sql']=q.fetchall()
Path('reports/nicora/2026-10-13/codex/NI062/live_read.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))