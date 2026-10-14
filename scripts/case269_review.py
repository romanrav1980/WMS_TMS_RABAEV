exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.finance.infrastructure.day_reviews import DayReviews,canonical,material
from app.modules.platform.public import read_oracle_json
from datetime import date
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
import httpx
svc=DayReviews(OracleGateway());ware=5265051;day=date(2026,10,11);zone="Asia/Tbilisi"
context=svc.context(ware,day,zone,"admin");assert context["version"]==0,"Resume context269 existing journal"
body={"warehouse_id":ware,"business_date":day.isoformat(),"timezone_region":zone,"expected_version":0,"source_hash":context["source_hash"],"reason":"Own269 review captured current facts, external obligations kept open"}
tag=uuid4().hex[:10]
report=svc.reconciliation.report(ware,day,zone,"admin");raw,hash_value,captured=material(report)
assert hash_value==body["source_hash"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();p=q.var(oracledb.DB_TYPE_CLOB);p.setvalue(0,canonical(body));m=q.var(oracledb.DB_TYPE_CLOB);m.setvalue(0,raw);r=q.var(oracledb.DB_TYPE_CLOB)
 q.callproc("RRL_DAY_REVIEW_API.append_review",["admin","DR269.ROLL:"+tag,p,m,captured,r])
 result=read_oracle_json(r.getvalue());assert not result["day_closed"]and not result["external_obligations_closed"]
 c.rollback();q.execute("select count(*)from RRL_DAY_REVIEW");assert q.fetchone()==(0,)
def send(suffix):
 payload={**body,"operation_id":"DR269:"+tag+suffix}
 with httpx.Client(auth=("admin","admin123"),timeout=60)as client:
  r=client.post("http://127.0.0.1:8088/api/finance/day-reconciliation/reviews",json=payload)
 return r.status_code,r.json(),payload
with ThreadPoolExecutor(2)as pool:responses=list(pool.map(send,[".A",".B"]))
assert sorted(x[0]for x in responses)==[201,409],responses
winner=next(x for x in responses if x[0]==201);saved=winner[1];request=winner[2]
assert saved["state"]=="REVIEW_RECORDED"and saved["version"]==1 and not saved["stock_changed"]
op=request["operation_id"];native_body={k:v for k,v in request.items()if k!="operation_id"}
assert svc.record(op,native_body,"admin")==saved
from app.modules.finance.contracts import LogisticsCostError
try:svc.record(op,{**native_body,"reason":"Changed reason same existing operation identifier"},"admin")
except LogisticsCostError as e:assert e.status==409
else:raise AssertionError("Payload collision")
try:svc.record(op,native_body,"SAP_FILE_GATEWAY")
except LogisticsCostError as e:assert e.status==403
else:raise AssertionError("Service edit denied")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 try:q.execute("delete from RRL_DAY_REVIEW where OPERATION_ID=:op",op=op)
 except oracledb.DatabaseError as e:assert getattr(e.args[0],"code",0)==20863
 else:raise AssertionError("History deletion")
 c.rollback()
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("select executions,round(elapsed_time/1000/nullif(executions,0),3)from V$SQL where sql_text like '%FROM RRL_DAY_REVIEW WHERE%'and executions>0 order by last_active_time desc fetch first 3 rows only");print("SQL_MS",q.fetchall())
Path("tmp/context269.json").write_text(json.dumps({"request":request,"result":saved},ensure_ascii=True),encoding="utf-8")
print("PASS269 native outer rollback/concurrentHTTP201-409/version1/saved exact replay/body collision/current service edit denied/immutable journal/P20H20/no closure or quantity effect")
