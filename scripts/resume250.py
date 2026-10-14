exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import TransportPreflight,update_existing_trip,generate_existing_operations,cancel_trip
from concurrent.futures import ThreadPoolExecutor
import httpx
p=Path("tmp/context250.json");data=json.loads(p.read_text(encoding="utf-8"))
Path("tmp/context250_first.json").write_text(json.dumps(data),encoding="utf-8")
parent=data["parent_trip_id"];peer=data["peer_trip_id"];tag=data["tag"];g=OracleGateway();svc=TransportPreflight(g)
for trip,clock in[(parent,"09:00"),(peer,"05:00")]:
 update_existing_trip(g,trip,{"shipment_date":"2026-10-14","shipment_time":clock},"admin")
 generate_existing_operations(g,trip,"admin")
tail=Path("scripts/case250_time_resource.py").read_text(encoding="utf-8").split("def body(trip,zone):",1)[1]
tail="def body(trip,zone):"+tail
tail=tail.replace("TIME250.RACE:","TIME250.RACE2:").replace("TIME250.ROLLBACK:","TIME250.ROLLBACK2:").replace("TIME250.BOUNDARY:","TIME250.BOUNDARY2:")
exec(tail)
