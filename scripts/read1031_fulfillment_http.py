import json,httpx
from pathlib import Path
saved=json.loads(Path("tmp/read1027_fulfillment.json").read_text(encoding="utf-8"));oid=saved["current_order"]
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin","admin123"),timeout=25)as c:
 r=c.get(f"/api/customer-orders/{oid}/fulfillment");assert r.status_code==200,(r.status_code,r.text[:1000]);rows=r.json()
 assert rows[0]["case_place_current"]is True and rows[0]["case_current_version"]==10 and rows[0]["picked_content_version"]==10
 old=c.get("/api/customer-orders/1931/fulfillment");assert old.status_code==200 and old.json()[0]["status"]=="SHIPPED"and old.json()[0]["physical_composition"][0]["quantity"]=="3"and old.json()[0]["case_place_current"]is False
 missing=c.get("/api/customer-orders/999999999/fulfillment");assert missing.status_code==404
 Path("tmp/http1031_fulfillment.json").write_text(json.dumps({"current":rows,"historical":old.json(),"missing404":True,"current_order":oid},indent=2),encoding="utf-8")
 print("PASS1031 actualHTTP activeCASE10FF10/currentplace; historicalSHIPPED3 retained/no currentclaim; missing404")
