exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.st_deferral import StDeferral
import httpx
service=StDeferral(OracleGateway());new=json.loads(Path("tmp/context744.json").read_text(encoding="utf-8"));old=json.loads(Path("tmp/context276.json").read_text(encoding="utf-8"))
assert service.defer(new["defer_operation"],new["defer_body"],"admin")==new["defer_result"]
assert service.defer(old["operation"],old["body"],"admin")==old["result"]
v=service.context(new["st_uid"],"admin");assert v["source_trip_id"]==new["ids"][-1]and v["physical_preparation"]["members"][0]["cell"]==new["dst"]
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 r=client.get("http://127.0.0.1:8088/api/transport/st-deferrals/context",params={"st_number":new["st_uid"]});assert r.status_code==200 and r.json()["physical_preparation"]["state"]=="PREPARED_WHOLE_STOCK",r.text
 r=client.post("http://127.0.0.1:8088/api/transport/st-deferrals",json=dict(operation_id=new["defer_operation"],**new["defer_body"]));assert r.status_code==200 and r.json()==new["defer_result"],r.text
print("PASS748 after746 native/currentHTTP prepared context/exact saved745 + original unpicked276 replay; no new quantity or decision")
