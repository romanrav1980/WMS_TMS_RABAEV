import json,httpx
from pathlib import Path
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin","admin123"),timeout=20)as c:
 r=c.post("/api/transport/preflight/trips/33571",json={"additional_st_numbers":["SAP_2135"]})
 assert r.status_code==200,r.text
 body=r.json();t=body["routes"][0]["temperature_requirements"]
 assert len(t["items"])==2 and not t["all_ranges_configured"] and not t["vehicle_temperature_verified"]
 assert body["operational_admission"]is False
 Path("tmp/http1144_thermal.json").write_text(json.dumps(body,indent=2),encoding="utf-8")
print("PASS1144 current HTTP native capacity+existing warehouse temperature ranges; missing config is not temperature admission")
