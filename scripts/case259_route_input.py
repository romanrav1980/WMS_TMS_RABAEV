"""Reuse original own empty33564; no new trip/stock/driver/vehicle."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import TransportPreflight,TransportPlanError
from concurrent.futures import ThreadPoolExecutor
import httpx
ctx=json.loads(Path("tmp/context248.json").read_text(encoding="utf-8"));trip=ctx["trip_id"]
g=OracleGateway();svc=TransportPreflight(g);source=svc.route_context(trip,"admin")
assert source["route_status"]=="NO_INPUT"
tag=ctx["tag"] if "tag"in ctx else "33564"
body={"trip_id":trip,"expected_version":source["version"],"source_hash":source["source_hash"],
      "drive_min":45,"drive_back_min":50,"source_reference":"Own259 dispatcher route assumption with explicit reference",
      "reason":"Own259 specific route durations not legal or live routing proof"}
def native(c,operation,b):
 q=c.cursor();out=q.var(oracledb.DB_TYPE_CLOB);payload=q.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,json.dumps(b,sort_keys=True,separators=(",",":")))
 q.callproc("RRL_TT_ROUTE_API.apply_input",[operation,"admin",payload,out])
 return json.loads(out.getvalue().read())
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,DURATION_MIN,PLAN_START,PLAN_END from RRL_TT_OPERATIONS where TT_ID=:trip_id order by ID",trip_id=trip);before=q.fetchall()
 rolled=native(c,"ROUTE259.ROLL:"+tag,body);q.execute("select DURATION_MIN from RRL_TT_OPERATIONS where TT_ID=:trip_id and OPERATION_CODE='DRIVE'",trip_id=trip);assert q.fetchone()==(45,)
 c.rollback();q.execute("select ID,DURATION_MIN,PLAN_START,PLAN_END from RRL_TT_OPERATIONS where TT_ID=:trip_id order by ID",trip_id=trip);assert q.fetchall()==before
 q.execute("select count(*)from RRL_TT_ROUTE_INPUT where TT_ID=:trip_id",trip_id=trip);assert q.fetchone()==(0,)
def post(suffix):
 with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
  r=client.post("http://127.0.0.1:8088/api/transport/preflight/route-inputs",json={"operation_id":"ROUTE259:"+tag+"."+suffix,**body})
  return r.status_code,r.json()
with ThreadPoolExecutor(max_workers=2)as pool:outcomes=list(pool.map(post,["A","B"]))
assert sorted(x[0]for x in outcomes)==[200,409],outcomes
winner=next(b for status,b in outcomes if status==200)
assert svc.apply_route_input(winner["operation_id"],body,"admin")==winner
try:svc.apply_route_input(winner["operation_id"],{**body,"drive_min":46},"admin")
except TransportPlanError as e:assert e.status==409
else:raise AssertionError("Payload collision")
current=svc.route_context(trip,"admin");assert current["route_status"]=="CURRENT_DISPATCH_ESTIMATE"and current["version"]==1
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID from RRL_TT_OPERATIONS where TT_ID=:trip_id order by ID",trip_id=trip);assert [x[0]for x in q.fetchall()]==[x[0]for x in before]
 q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","transport_dispatch_edit"])
 q.execute("update RRL_TT_OPERATIONS set OPERATION_CODE='DRIVER_CHANGE'where ID=:op_id",op_id=before[0][0])
 try:native(c,"ROUTE259.FAIL:"+tag,{**body,"expected_version":1})
 except oracledb.DatabaseError as e:assert "OP_PLAN_CUSTOM_CHAIN_REVIEW_REQUIRED"in str(e)
 else:raise AssertionError("Custom chain bypass")
 q.execute("select count(*)from RRL_TT_ROUTE_INPUT where TT_ID=:trip_id",trip_id=trip);assert q.fetchone()==(1,)
 q.callproc("RRL_STOCK_METADATA_TX.end_change");c.rollback()
time=svc.time_context(trip,"admin");assert time["approval_status"]!="APPROVED"
approved=svc.approve_time("TIME259:"+tag,{"trip_id":trip,"expected_version":time["version"],"source_hash":time["source_hash"],
    "time_zone":"Asia/Tbilisi","reason":"Own259 current original route45 plus return50 explicit timezone"},"admin")
preview=svc.trip_time(trip,"UTC","admin");assert preview["time_zone"]=="Asia/Tbilisi"and preview["driver_rest"]["drive_min"]=="95.0"
assert not preview["driver_rest"]["unknown_intervals"]and not preview["operational_admission"]
try:svc.route_context(trip,"WR23413508027ed")
except TransportPlanError as e:assert e.status==403
else:raise AssertionError("Foreign emptytrip")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 try:q.execute("delete from RRL_TT_ROUTE_INPUT where TT_ID=:trip_id",trip_id=trip)
 except oracledb.DatabaseError as e:assert getattr(e.args[0],"code",0)==20863
 else:raise AssertionError("History deletion")
 c.rollback()
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("select executions,round(elapsed_time/1000/nullif(executions,0),3)from V$SQL where sql_text like '%FROM RRL_TT_ROUTE_INPUT WHERE TT_ID=%'and executions>0 order by last_active_time desc fetch first 3 rows only");print("SQL_MS",q.fetchall())
Path("tmp/context259.json").write_text(json.dumps({"trip_id":trip,"route_input":winner,"time":approved},ensure_ascii=True),encoding="utf-8")
print("PASS259 original33564/same12IDS/route45-50/outerrollback/customchainlatefailure onejournal/concurrentHTTP200-409/replay-collision/foreign403/historyguard/newawareapproval95min/protected20-20/no goods or birth")
