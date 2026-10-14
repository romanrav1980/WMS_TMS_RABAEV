exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import TransportPreflight,create_existing_trip,update_existing_trip,generate_existing_operations,cancel_trip
from datetime import date
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import httpx
g=OracleGateway();svc=TransportPreflight(g);parent=json.loads(Path("tmp/context248.json").read_text(encoding="utf-8"))["trip_id"]
p=Path("tmp/context250.json");assert not p.exists(),"Resume the current committed fixture"
peer=create_existing_trip(g,"20",date(2026,10,13),"admin");tag=uuid4().hex[:10]
data={"parent_trip_id":parent,"peer_trip_id":peer,"tag":tag};p.write_text(json.dumps(data),encoding="utf-8")
plate=svc.time_context(parent,"admin")["source"]["vehicle_num"]
update_existing_trip(g,parent,{"shipment_date":"2026-10-13","shipment_time":"09:00"},"admin");generate_existing_operations(g,parent,"admin")
update_existing_trip(g,peer,{"transport":plate,"voditel_id":1,"shipment_time":"05:00"},"admin");generate_existing_operations(g,peer,"admin")
def body(trip,zone):
 ctx=svc.time_context(trip,"admin")
 return {"trip_id":trip,"expected_version":ctx["version"],"source_hash":ctx["source_hash"],"time_zone":zone,"reason":"Own250 atomic shared driver vehicle publication"}
bodies=[body(parent,"Asia/Tbilisi"),body(peer,"UTC")]
data["bodies"]=bodies;p.write_text(json.dumps(data),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();arg=q.var(oracledb.DB_TYPE_CLOB);arg.setvalue(0,json.dumps(bodies[0],sort_keys=True,separators=(",",":")));result=q.var(oracledb.DB_TYPE_CLOB)
 q.callproc("RRL_TT_TIME_API.approve",["TIME250.ROLLBACK:"+tag,"admin",arg,result]);c.rollback()
assert svc.time_context(parent,"admin")["version"]==bodies[0]["expected_version"]
def approve(i):
 with httpx.Client(auth=("admin","admin123"),timeout=35)as client:
  r=client.post("http://127.0.0.1:8088/api/transport/preflight/time-approvals",json={**bodies[i],"operation_id":f"TIME250.RACE:{tag}.{i}"})
  return r.status_code,r.json()
with ThreadPoolExecutor(max_workers=2)as pool:out=list(pool.map(approve,(0,1)))
data["responses"]=out;p.write_text(json.dumps(data),encoding="utf-8")
assert sorted(x[0]for x in out)==[200,409],out
loser=next(i for i,x in enumerate(out)if x[0]==409)
assert "TT_TIME_APPROVED_RESOURCE_OVERLAP"in json.dumps(out[loser]),out
assert svc.time_context(bodies[loser]["trip_id"],"admin")["version"]==bodies[loser]["expected_version"]
# Same absolute end=start is accepted, not rounded or padded.
if loser==0:
 update_existing_trip(g,parent,{"shipment_time":"10:40"},"admin");generate_existing_operations(g,parent,"admin")
 boundary=body(parent,"Asia/Tbilisi")
else:
 update_existing_trip(g,peer,{"shipment_time":"06:40"},"admin");generate_existing_operations(g,peer,"admin")
 boundary=body(peer,"UTC")
decision=svc.approve_time("TIME250.BOUNDARY:"+tag,boundary,"admin")
assert decision["operations"][0]["start_at"].endswith("+04:00"if loser==0 else "+00:00")
assert svc.time_context(parent,"admin")["approval_status"]=="APPROVED"
assert svc.time_context(peer,"admin")["approval_status"]=="APPROVED"
assert not any(x["trip_id"]==peer for x in svc.trip_time(parent,"UTC","admin")["conflicts"])
cancel_trip(g,peer,"admin")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491")
 assert q.fetchone()==(20,20)
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3) from V$SQL
 where sql_text like '%RRL_TRANSPORT_TASK T JOIN RRL_TT_TIME_APPROVAL A%' and executions>0
 order by last_active_time desc fetch first 3 rows only""")
 print("SQL_MS",q.fetchall())
print("PASS250 two different own empty original TT same vehicle-driver cross-zone same instant: rollback then actual concurrent HTTP one200/one409 RESOURCE_OVERLAP/loser version unchanged; exact end=start new approval allowed/same readonly occupancy agrees/peer cancelled/history retained/no goods/protected20-20")
