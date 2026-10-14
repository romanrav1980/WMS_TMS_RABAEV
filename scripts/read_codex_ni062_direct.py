exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.inventory.infrastructure.return_putaway import ReturnPutaway
import time
result={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute('set transaction read only')
 class Gateway:
  def fetch_all(self,sql,binds):
   q.execute(sql,binds);names=[d[0].lower()for d in q.description];return [dict(zip(names,row))for row in q.fetchall()]
 service=ReturnPutaway(Gateway(),None)
 q.execute("select r.WARE_ID,r.OPERATION_ID from RRL_STORE_RETURN_RECEIPT r where not exists(select 1 from RRL_STORE_RETURN_PLACEMENT p where p.RECEIPT_OPERATION_ID=r.OPERATION_ID) fetch first 1 rows only");sample=q.fetchone();result['sample']=sample
 samples=[(14524201,'REUSE643.RECEIVE:dc1889623c',0),(14524201,'MISSING.LOCAL.RECEIPT',0)]+([(sample[0],sample[1],1)]if sample else [])
 result['reads']=[]
 for ware,receipt,count in samples:
  start=time.perf_counter();rows=service.pending(ware,'admin',receipt);assert len(rows)==count and all(r['receipt_operation_id']==receipt for r in rows);result['reads'].append({'receipt':receipt,'count':len(rows),'ms':round((time.perf_counter()-start)*1000,3)})
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and SQL_TEXT not like '%V$SQL%' and SQL_TEXT like '%select r.OPERATION_ID RECEIPT_OPERATION_ID%' and DBMS_LOB.INSTR(SQL_FULLTEXT,'r.OPERATION_ID=:receipt')>0 order by LAST_ACTIVE_TIME desc fetch first 2 rows only");result['sql']=q.fetchall()
 if result['sql']:
  try:
   q.execute("select OPERATION,OPTIONS,OBJECT_NAME,CARDINALITY from V$SQL_PLAN where SQL_ID=:id and CHILD_NUMBER=0 order by ID fetch first 30 rows only",id=result['sql'][0][0]);result['plan']=q.fetchall()
  except oracledb.DatabaseError:result['plan']='unavailable'
Path('reports/retailcase/2026-10-13/codex/NI062/direct_read.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))