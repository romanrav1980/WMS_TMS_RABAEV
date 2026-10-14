import httpx,json
from pathlib import Path
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin","admin123"),timeout=25)as c:
 first=c.get("/api/customer-orders",params={"limit":3});assert first.status_code==200
 cursor=first.json()[-1]["customer_order_id"]
 second=c.get("/api/customer-orders",params={"limit":3,"before_id":cursor});assert second.status_code==200
 a=[x["customer_order_id"] for x in first.json()];b=[x["customer_order_id"] for x in second.json()]
 assert len(a)==len(b)==3 and max(b)<min(a)
 old=c.get("/api/customer-orders/-980711");assert old.status_code==200 and old.json()["customer_order_id"]==-980711
 invalid=c.get("/api/customer-orders",params={"before_id":0});assert invalid.status_code==422
 negative=c.get("/api/customer-orders",params={"before_id":-980711,"limit":3});assert negative.status_code==200
 assert all(x["customer_order_id"] < -980711 for x in negative.json())
 Path("tmp/http1049_order_paging.json").write_text(json.dumps({"first":a,"second":b,"negative_legacy_id":-980711,"legacy200":True,"invalid422":True},indent=2),encoding="utf-8")
print("PASS1049 actual HTTP keyset/negative legacy keys/422/listbounded; no writes")
