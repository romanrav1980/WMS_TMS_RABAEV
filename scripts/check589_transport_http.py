import json,sys
from pathlib import Path
import httpx
d=json.loads(Path("tmp/context586.json").read_text(encoding="utf-8"));assert d["done"]
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin","admin123"),timeout=25)as client:
 r=client.get("/api/finance/logistics-costs/trips/"+str(d["trip"])+"/transport-costs",params={"warehouse_id":d["warehouse"]})
 assert r.status_code==200,(r.status_code,r.text[:1000]);assert r.json()["recognized"]==d["winner"]["result"]
 r=client.post("/api/finance/logistics-costs/transport-costs/conduct",json=d["winner"]["body"])
 assert r.status_code==200,(r.status_code,r.text[:1000]);assert r.json()==d["winner"]["result"]
print("PASS589 actual HTTP current actor read + exact monetary command replay returns retained original result; no new recognition.")
