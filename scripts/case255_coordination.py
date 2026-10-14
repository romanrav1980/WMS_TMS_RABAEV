exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import TransportPreflight,update_existing_trip,generate_existing_operations
from datetime import datetime,timezone,timedelta
import httpx
ctx=json.loads(Path("tmp/context254.json").read_text(encoding="utf-8"));trip=ctx["target_trip"];tag=ctx["tag"];g=OracleGateway();svc=TransportPreflight(g)
# Explicit UTC date+clock before declared ready due; original empty TT/vehicle/driver unchanged.
clock=datetime.now(timezone.utc)+timedelta(minutes=45)
update_existing_trip(g,trip,{"shipment_date":clock.date().isoformat(),"shipment_time":clock.strftime("%H:%M")},"admin")
generate_existing_operations(g,trip,"admin")
source=svc.time_context(trip,"admin")
approved=svc.approve_time("TIME255:"+tag,{"trip_id":trip,"expected_version":source["version"],"source_hash":source["source_hash"],"time_zone":"UTC","reason":"Own255 original warehouse receiving loading cutoff"},"admin")
before=svc.coordination(trip,"admin")
assert before["warehouse_placed_deliveries"]==0 and before["incoming"]["expected_deliveries"]==1
assert any(x["code"]=="COORDINATION_READY_PROMISE_AFTER_LOADING"for x in before["blockers"]),before
assert not before["operational_admission"]and before["read_only"]and before["consistent_snapshot"]
ctx["time255"]=approved;Path("tmp/context254.json").write_text(json.dumps(ctx,ensure_ascii=True),encoding="utf-8")
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 r=client.get(f"http://127.0.0.1:8088/api/transport/preflight/trips/{trip}/coordination")
 assert r.status_code==200,(r.status_code,r.text[:500])
 assert r.json()["warehouse_placed_deliveries"]==0
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS255 original254 TT approved UTC cutoff before expected warehouse ready; same snapshot incoming1/place0/noST/explicit latepromise/loadingmissing/noadmission/API200/no quantity changes")
