exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import TransportPreflight,TransportPlanError
from app.modules.platform.public import read_oracle_json
import httpx
svc=TransportPreflight(OracleGateway());trip=33564
original=svc.route_context(trip,"admin");assert original["route_status"]=="CURRENT_DISPATCH_ESTIMATE"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","transport_dispatch_edit"])
 q.execute("update RRL_TRANSPORT_TASK set SHIPMENT_TIME=SHIPMENT_TIME+1/24 where ID=:trip_id",trip_id=trip)
 out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_TT_ROUTE_API.context",[trip,"admin",out])
 assert read_oracle_json(out.getvalue())["route_status"]=="SOURCE_CHANGED"
 q.callproc("RRL_TT_OPERATION_PLAN_API.generate",[trip,"admin",out])
 rows=read_oracle_json(out.getvalue());assert all(x["duration_min"]==0 for x in rows if x["operation_code"]in{"DRIVE","DRIVE_BACK"})
 q.callproc("RRL_STOCK_METADATA_TX.end_change");c.rollback()
assert svc.route_context(trip,"admin")==original
ctx=json.loads(Path("tmp/context254.json").read_text(encoding="utf-8"));frozen=svc.route_context(ctx["target_trip"],"admin")
try:svc.apply_route_input("ROUTE259.FROZEN:33570",{"trip_id":ctx["target_trip"],"expected_version":frozen["version"],"source_hash":frozen["source_hash"],
 "drive_min":10,"drive_back_min":10,"source_reference":"Own259 frozen phase proof","reason":"Own259 cannot regenerate departed original"},"admin")
except TransportPlanError as e:assert e.status==409 and "PLANNED_UNBILLED_REQUIRED"in str(e)
else:raise AssertionError("Departed mutation")
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 r=client.get("http://127.0.0.1:8088/api/transport/preflight/trips/33564/route-context");assert r.status_code==200 and r.json()["route_status"]=="CURRENT_DISPATCH_ESTIMATE"
 b={"operation_id":"ROUTE259.INVALID","trip_id":trip,"expected_version":1,"source_hash":original["source_hash"],"drive_min":2.5,"drive_back_min":1,"source_reference":"Own259 invalid input","reason":"Own259 exact integer contract"}
 assert client.post("http://127.0.0.1:8088/api/transport/preflight/route-inputs",json=b).status_code==422
 assert client.post("http://127.0.0.1:8088/api/transport/preflight/route-inputs",json={**b,"drive_min":1,"actor":"admin"}).status_code==422
print("PASS259 source clockchange invalidates/noOPS delete/staleestimate fallback notreatreal/outerrollback exactcurrent/departedblocked/currentHTTP200 strict422/no writes retained")
