exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
import httpx
from app.oracle_gateway import OracleGateway
from app.modules.fulfillment.infrastructure.legacy_preparation import LegacyPreparation
from app.modules.fulfillment.api.store_order_routes import PreparationRequest
g=OracleGateway();service=LegacyPreparation(g);d=json.loads(Path("tmp/context277.json").read_text(encoding="utf-8"))
canonical=PreparationRequest.model_validate(d["body"]).model_dump(mode="json")
r=service.resolve(d["source"]["customer_order_id"],canonical,"admin");assert r["state"]=="ST_PREPARED"and len(r["result"]["pallet_identifiers"])==3
pending=json.loads(Path("tmp/context273.json").read_text(encoding="utf-8"));order=pending["store"]["customer_order_id"];article=pending["article"]
b={"operation_id":"LAY278.READONLY:"+pending["tag"],"pallets":[{"lines":[{"articul":article,"quantity":"48"}]}]}
r=service.resolve(order,PreparationRequest.model_validate(b).model_dump(mode="json"),"admin");assert r["state"]=="NOT_PREPARED"
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 r=client.post(f"http://127.0.0.1:8088/api/integrations/sap/store-orders/{order}/preparation-layout",json={"article_pallet_counts":{article:2}})
 assert r.status_code==200 and len(r.json()["pallets"])==2,r.text
 r=client.post(f"http://127.0.0.1:8088/api/integrations/sap/store-orders/{order}/prepare-st/resolve",json=b)
 assert r.status_code==200 and r.json()["state"]=="NOT_PREPARED",r.text
 r=client.post(f"http://127.0.0.1:8088/api/integrations/sap/store-orders/{d['source']['customer_order_id']}/prepare-st/resolve",json=d["body"])
 assert r.status_code==200 and r.json()["state"]=="ST_PREPARED",r.text
 h=json.loads(Path("tmp/context276.json").read_text(encoding="utf-8"))
 r=client.get("http://127.0.0.1:8088/api/transport/st-deferrals/history",params={"st_number":h["st"]});assert r.status_code==200 and len(r.json()["rows"])==1,r.text
print("PASS278 HTTP current2wholeboxproposal/noST creation/resolve existing3pal and awaited absence; original276 history HTTP valid")
