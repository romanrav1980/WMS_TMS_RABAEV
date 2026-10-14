exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.transport.infrastructure.coordination_preflight import coordination,read_coordination
from app.modules.transport.infrastructure.time_preflight import trip_time_preview
from app.modules.transport.infrastructure.trip_time_approval import read_time_context
from app.modules.platform.public import read_oracle_json
from app.oracle_gateway import OracleGateway
import httpx,uuid
g=OracleGateway();before=coordination(g,33564,"admin")
assert before["delivery_windows"]["status"]=="CURRENT_APPROVED_REGION_REQUIRED"and not before["departure_authorized"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();context=read_time_context(q,33564,"admin");c.rollback()
 body={"trip_id":33564,"expected_version":context["version"],"source_hash":context["source_hash"],"time_zone":"Asia/Tbilisi","reason":"Изолированное согласование часового пояса для снимка готовности; транзакция отменяется"}
 payload=q.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False))
 out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  try:q.callproc("RRL_TT_TIME_API.approve",["QA288."+uuid.uuid4().hex[:12],"admin",payload,out])
  except oracledb.DatabaseError as e:
   assert e.args[0].code==20886 and "TT_TIME_CHAIN_DEPARTURE_CHANGED"in str(e)
   from app.modules.transport.infrastructure.time_preflight import read_trip_time
   from app.modules.transport.infrastructure.delivery_window_preview import read_delivery_windows
   temporal=read_trip_time(q,33564,"Asia/Tbilisi","admin")
   windows=read_delivery_windows(q,33564,"",24,"Asia/Tbilisi","admin")
   assert "driver_days"in temporal and windows["status"]=="INSUFFICIENT_EVIDENCE"
   print("BOUND288 own current chain departure mismatch: native refuses approval; approved coordinator branch not evidenced")
  else:
   snapshot=read_coordination(q,33564,"admin")
   assert snapshot["time"]["approval_status"]=="APPROVED"and "driver_days"in snapshot["temporal"]
   assert snapshot["delivery_windows"]["status"]=="INSUFFICIENT_EVIDENCE"and not snapshot["departure_authorized"]
 finally:c.rollback()
 assert read_time_context(q,33564,"admin")["version"]==context["version"];c.rollback()
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3),buffer_gets
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and executions>0 and SQL_TEXT not like '%V$SQL%'
 and(SQL_TEXT like '%select distinct t.ID,t.TRANSPORT,t.VODITEL_ID%'or SQL_TEXT like '%select distinct t.ID from RRL_TRANSPORT_TASK t%')
 order by last_active_time desc fetch first 4 rows only""");print("SQL288_MS",q.fetchall())
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 r=client.get("http://127.0.0.1:8088/api/transport/preflight/trips/33564/coordination")
 assert r.status_code==200 and "delivery_windows"in r.json()and not r.json()["departure_authorized"],r.text
print("PASS288 approvedregion samecursor coordinator underouterrollback, currentblockedHTTP; oldapproval preserved/noqty. Historicalstalechain fixed byoriginalsame12ID generator; missingrealwindows remainblocked")
