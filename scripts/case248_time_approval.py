"""Own metadata-only original TT, no stock or source data creation."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import TransportPreflight,create_existing_trip,update_existing_trip,generate_existing_operations
from datetime import date
from uuid import uuid4
g=OracleGateway();service=TransportPreflight(g)
p=Path("tmp/context248.json")
if p.exists():data=json.loads(p.read_text(encoding="utf-8"))
else:
 trip=create_existing_trip(g,"20",date(2026,10,12),"admin")
 data={"trip_id":trip,"tag":uuid4().hex[:10]}
 p.write_text(json.dumps(data),encoding="utf-8")
trip=data["trip_id"];tag=data["tag"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select NUM from RRL_TR_VEHICLE where ID=10059")
 plate=q.fetchone()[0]
update_existing_trip(g,trip,{"transport":plate,"voditel_id":1,"shipment_time":"08:00"},"admin")
ops=generate_existing_operations(g,trip,"admin")
context=service.time_context(trip,"admin")
data["context"]=context;p.write_text(json.dumps(data,ensure_ascii=True),encoding="utf-8")
print("OWN248",trip,"OPS",len(ops),"VERSION",context["version"],"STATUS",context["approval_status"],flush=True)
body={"trip_id":trip,"expected_version":context["version"],"source_hash":context["source_hash"],"time_zone":"Asia/Tbilisi","reason":"Own248 approve original planned wall region"}
serialized=json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();result=q.var(oracledb.DB_TYPE_CLOB);request=q.var(oracledb.DB_TYPE_CLOB);request.setvalue(0,serialized)
 q.callproc("RRL_TT_TIME_API.approve",["TIME248.ROLLBACK:"+tag,"admin",request,result])
 c.rollback()
assert service.time_context(trip,"admin")["version"]==context["version"]
a=service.approve_time("TIME248.APPROVE:"+tag,body,"admin")
b=service.approve_time("TIME248.APPROVE:"+tag,body,"admin")
assert a==b and not a["operational_admission"] and len(a["operations"])==12
assert service.time_context(trip,"admin")["approval_status"]=="APPROVED"
update_existing_trip(g,trip,{"shipment_time":"09:00"},"admin")
assert service.time_context(trip,"admin")["approval_status"]=="SOURCE_CHANGED"
assert service.approve_time("TIME248.APPROVE:"+tag,body,"admin")==a
data["approval"]=a;p.write_text(json.dumps(data,ensure_ascii=True),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 try:q.execute("delete from RRL_TT_TIME_APPROVAL where TT_ID=:trip_id",trip_id=trip)
 except oracledb.DatabaseError as exc:assert exc.args[0].code==20863;c.rollback()
 else:raise AssertionError("Approval journal mutable")
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491")
 assert q.fetchone()==(20,20)
print("PASS248 own empty TT existing native edit/generator12 /late rollback/immutable region approval/replay/current source changed/old historical repeat/no stock/protected20-20")
