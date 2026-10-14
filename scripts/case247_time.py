"""Original ARM rows only, explicit wall-time interpretation, no metadata creation."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import TransportPreflight,TransportPlanError
from datetime import datetime
import httpx
service=TransportPreflight(OracleGateway())
a=service.trip_time(33530,"Asia/Tbilisi","admin")
b=service.trip_time(33530,"UTC","admin")
assert len(a["operations"])==len(b["operations"])==12
assert a["read_only"] and not a["operational_admission"] and a["status"]=="BLOCKED"
assert a["start_at"].startswith("2026-10-10T08:00:00") and a["start_at"].endswith("+04:00"),a
assert b["start_at"].endswith("+00:00")
assert (datetime.fromisoformat(b["start_at"])-datetime.fromisoformat(a["start_at"])).total_seconds()==14400
assert any(i["code"]=="TIME_DRIVER_REQUIRED"for i in a["issues"])
empty=service.trip_time(33531,"Europe/Moscow","admin")
assert any(i["code"]=="TIME_ORIGINAL_OPERATIONS_REQUIRED"for i in empty["issues"])
try:service.trip_time(33530,"UTC","WR23413508027ed")
except TransportPlanError as exc: assert exc.status==403
else:raise AssertionError("Foreign actor leak")
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 url="http://127.0.0.1:8088/api/transport/preflight/trips/33530/time"
 r=client.post(url,json={"time_zone":"Asia/Tbilisi"})
 assert r.status_code==200,(r.status_code,r.text[:600])
 assert len(r.json()["operations"])==12
 assert client.post(url,json={"time_zone":"Automatic"}).status_code==422
 assert client.post(url,json={"time_zone":"UTC","actor":"admin"}).status_code==422
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491")
 assert q.fetchone()==(20,20)
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3) from V$SQL
 where sql_text like 'select distinct t.ID,t.TRANSPORT,t.VODITEL_ID%from RRL_TRANSPORT_TASK%'
 and executions>0 order by last_active_time desc fetch first 3 rows only""")
 print("SQL_MS",q.fetchall())
print("PASS247 original12 ARM operations explicit+04/UTC instants/empty chain and missing driver blocked/foreign403/real HTTP200 and strict422/protected20-20/no writes. No seeded overlap/driver legality/operational admission claim.")
