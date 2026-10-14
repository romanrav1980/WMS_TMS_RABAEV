exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import TransportPreflight,create_existing_trip,update_existing_trip,generate_existing_operations,cancel_trip,TransportPlanError
from datetime import date
from concurrent.futures import ThreadPoolExecutor
import httpx
data=json.loads(Path("tmp/context248.json").read_text(encoding="utf-8"));trip=data["trip_id"];tag=data["tag"];g=OracleGateway();svc=TransportPreflight(g)
ctx=svc.time_context(trip,"admin");assert ctx["approval_status"]=="SOURCE_CHANGED"
body={"trip_id":trip,"expected_version":ctx["version"],"source_hash":ctx["source_hash"],"time_zone":"Asia/Tbilisi","reason":"Own248 reapprove regenerated planned chain"}
try:svc.approve_time("TIME248.MISMATCH:"+tag,body,"admin")
except TransportPlanError as exc:assert "TT_TIME_CHAIN_DEPARTURE_CHANGED"in str(exc),str(exc)
else:raise AssertionError("TT date and ARM chain mismatch approved")
generate_existing_operations(g,trip,"admin")
ctx=svc.time_context(trip,"admin");body.update(expected_version=ctx["version"],source_hash=ctx["source_hash"])
def approve(i):
 with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
  r=client.post("http://127.0.0.1:8088/api/transport/preflight/time-approvals",json={**body,"operation_id":f"TIME248.RACE:{tag}.{i}"})
  return r.status_code,r.json()
with ThreadPoolExecutor(max_workers=2)as pool:out=list(pool.map(approve,(0,1)))
assert sorted(x[0]for x in out)==[200,409],out
winner=next(x[1]for x in out if x[0]==200)
assert svc.time_context(trip,"admin")["approval_status"]=="APPROVED"
assert svc.approve_time(winner["operation_id"],body,"admin")==winner
try:svc.approve_time(winner["operation_id"],{**body,"reason":"different contents same original operation"},"admin")
except TransportPlanError as exc:assert exc.status==409
else:raise AssertionError("Changed payload replay allowed")
try:svc.approve_time(winner["operation_id"],body,"WR23413508027ed")
except TransportPlanError as exc:assert exc.status==403
else:raise AssertionError("Foreign replay allowed")
peer=create_existing_trip(g,"20",date(2026,10,12),"admin")
data["peer_trip_id"]=peer;data["approval2"]=winner;Path("tmp/context248.json").write_text(json.dumps(data,ensure_ascii=True),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select CONDITION from RRL_TRANSPORT_TASK where ID=:trip_id",trip_id=peer)
 assert q.fetchone()[0]=="Спланирован"
update_existing_trip(g,peer,{"transport":ctx["source"]["vehicle_num"],"voditel_id":1,"shipment_time":"12:00"},"admin")
peerops=generate_existing_operations(g,peer,"admin")
assert not any(x["trip_id"]==peer for x in svc.trip_time(trip,"Asia/Tbilisi","admin")["conflicts"])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 def fact(op,values):
  output=q.var(oracledb.DB_TYPE_CLOB);arg=q.var(oracledb.DB_TYPE_CLOB);arg.setvalue(0,json.dumps(values))
  q.callproc("RRL_TT_OPERATION_PLAN_API.write_fact",[op,"admin",arg,output]);c.commit()
 fact(peerops[0]["op_id"],{"fact_start":"2026-10-12 08:00","fact_end":"2026-10-12 09:00"})
 assert not any(x["trip_id"]==peer for x in svc.trip_time(trip,"Asia/Tbilisi","admin")["conflicts"])
 fact(peerops[1]["op_id"],{"fact_start":"2026-10-12 08:00"})
 hit=[x for x in svc.trip_time(trip,"Asia/Tbilisi","admin")["conflicts"]if x["trip_id"]==peer]
 assert len(hit)==1 and hit[0]["occupancy_basis"]=="RECORDED_OPEN_FACT" and hit[0]["driver_conflict"] and hit[0]["vehicle_conflict"],hit
cancel_trip(g,peer,"admin")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491")
 assert q.fetchone()==(20,20)
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3) from V$SQL
 where sql_text like '%RRL_TT_TIME_APPROVAL%' and executions>0 and command_type=3
 order by last_active_time desc fetch first 5 rows only""");print("SQL_MS",q.fetchall())
print("PASS248 real HTTP concurrent one approval/version/immutable replay/payload conflict/foreign403/stale original chain refused/native regeneration/new peer correct Cyrillic status. PASS247 same vehicle+driver overlap actual start without end/half-open endpoint/no planned release; synthetic own peer cancelled/history retained/no stock/protected20-20.")
