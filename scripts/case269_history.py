exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.finance.infrastructure.day_reviews import DayReviews
from app.modules.finance.contracts import LogisticsCostError
from datetime import date
import httpx
data=json.loads(Path("tmp/context269.json").read_text(encoding="utf-8"));request=data["request"];svc=DayReviews(OracleGateway())
ware=request["warehouse_id"];day=date.fromisoformat(request["business_date"]);zone=request["timezone_region"];op=request["operation_id"]
items=svc.history(ware,day,zone,0,1,"admin");assert len(items["rows"])==1 and not items["has_more"]and items["rows"][0]["operation_id"]==op
assert svc.history(ware,day,zone,1,1,"admin")["rows"]==[]
detail=svc.get(op,"admin");assert detail["report"]==data["result"]["report"]and not detail["day_closed"]
try:svc.get(op,"SAP_FILE_GATEWAY")
except LogisticsCostError as e:assert e.status==403
else:raise AssertionError("Gateway report scope")
body={k:v for k,v in request.items()if k!="operation_id"};body.update(source_hash="0"*64,expected_version=1)
try:svc.record(op+".STALE",body,"admin")
except LogisticsCostError as e:assert e.status==409 and e.code=="DAY_REVIEW_SOURCE_CHANGED"
else:raise AssertionError("Stale capture")
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 r=client.get("http://127.0.0.1:8088/api/finance/day-reconciliation/reviews/"+op);assert r.status_code==200,r.text
 assert r.json()["report"]==detail["report"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from RRL_DAY_REVIEW");assert q.fetchone()==(1,)
 q.execute("""select SQL_ID,executions,round(elapsed_time/1000/nullif(executions,0),3),substr(SQL_TEXT,1,100)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and executions>0 and SQL_TEXT not like '%V$SQL%'
 and last_active_time>sysdate-10/1440 and (SQL_TEXT like '%RRL_DAY_REVIEW%'or SQL_TEXT like '%RRL_WAREHOUSE_TASK%'or SQL_TEXT like '%RRL_EVENT_OUTBOX%'or SQL_TEXT like '%RRL_SAP_RECEIPT_OUTBOX%')
 order by elapsed_time/nullif(executions,0)desc fetch first 8 rows only""")
 print("RECENT_SQL_MS",json.dumps(q.fetchall(),ensure_ascii=True))
print("PASS269 immutable history cursor/exact frozen report/current access/stale capture denied/HTTP/no new journal")
