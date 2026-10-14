exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import TransportPreflight,create_existing_trip,update_existing_trip,generate_existing_operations,cancel_trip
from datetime import date
from uuid import uuid4
data=json.loads(Path("tmp/context248.json").read_text(encoding="utf-8"));parent=data["trip_id"];g=OracleGateway();svc=TransportPreflight(g)
ctx=svc.time_context(parent,"admin");assert ctx["approval_status"]=="APPROVED" and ctx["last_approval"]["time_zone"]=="Asia/Tbilisi"
p=Path("tmp/context249.json")
assert not p.exists(),"Resume current fixture; don't duplicate it"
peer=create_existing_trip(g,"20",date(2026,10,12),"admin");tag=uuid4().hex[:10]
data={"peer_trip_id":peer,"parent_trip_id":parent,"tag":tag};p.write_text(json.dumps(data),encoding="utf-8")
update_existing_trip(g,peer,{"transport":ctx["source"]["vehicle_num"],"voditel_id":1,"shipment_time":"05:00"},"admin")
generate_existing_operations(g,peer,"admin")
def approve(suffix):
 source=svc.time_context(peer,"admin")
 return svc.approve_time("TIME249:"+tag+"."+suffix,{"trip_id":peer,"expected_version":source["version"],"source_hash":source["source_hash"],"time_zone":"UTC","reason":"Own249 cross region same original vehicle driver"},"admin")
approve("UTC05")
result=svc.trip_time(parent,"UTC","admin")
assert result["time_zone"]=="Asia/Tbilisi" and result["requested_time_zone"]=="UTC"
hit=[x for x in result["conflicts"]if x["trip_id"]==peer]
assert hit and all(x["time_zone"]=="UTC" and x["time_approval_status"]=="APPROVED" for x in hit)
update_existing_trip(g,peer,{"shipment_time":"09:00"},"admin");generate_existing_operations(g,peer,"admin")
changed=svc.trip_time(parent,"UTC","admin")
assert any(x["code"]=="TIME_OTHER_APPROVAL_CHANGED"and x["trip_id"]==peer for x in changed["issues"])
approve("UTC09")
final=svc.trip_time(parent,"UTC","admin")
assert not any(x["trip_id"]==peer for x in final["conflicts"])
assert not any(x.get("trip_id")==peer for x in final["issues"])
cancel_trip(g,peer,"admin")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491")
 assert q.fetchone()==(20,20)
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3) from V$SQL
 where sql_text like 'select distinct t.ID,t.TRANSPORT,t.VODITEL_ID%'
 and executions>0 order by last_active_time desc fetch first 3 rows only""")
 print("SQL_MS",q.fetchall())
print("PASS249 approved Tbilisi09 and UTC05 share real instant and conflict; UTC09 same wall differs4h/no peer conflict; caller UTC cannot override approved parentregion; stale peer approval conservatively blocked; same readonly snapshot/current native context/own empty peer cancelled/protected20-20/no stock.")
