exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
import httpx
source=json.loads(Path("tmp/replay262_source.json").read_text(encoding="utf-8"));operation=source["operation_id"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select RESULT_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:operation",operation=operation);saved=read_oracle_json(q.fetchone()[0])
 q.execute("select count(*)from RRL_EVENTS");events_before=q.fetchone()[0]
 with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
  r=client.post("http://127.0.0.1:8088/api/receiving/supply-orders/"+source["source"]["order_id"]+"/pallets",
     json={"operation_id":operation,**source["metadata"]})
  assert r.status_code==201,(r.status_code,r.text[:800]);assert r.json()==saved
 q.execute("select count(*)from RRL_EVENTS");assert q.fetchone()[0]==events_before
 q.execute("select count(*)from RRL_SAP_PALLET_RECEIPT where OPERATION_ID=:operation",operation=operation);assert q.fetchone()==(1,)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("select executions,round(elapsed_time/1000/nullif(executions,0),3)from V$SQL where sql_text like '%FROM RRL_STOCK_OPERATION%WHERE OPERATION_ID=%'and executions>0 order by last_active_time desc fetch first 3 rows only");print("SQL_MS",q.fetchall())
print("PASS262 actual existingSAPreceipt canonicalmetadata/sameoriginalOPID/HTTP201 exactsavedresult/oneimmutable receipt/eventsunchanged/protected20-20/no newstock or sourcebirth")
