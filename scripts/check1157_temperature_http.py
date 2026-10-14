from pathlib import Path
import json,httpx
d=json.loads(Path("tmp/context1152.json").read_text(encoding="utf-8"))
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin","admin123"),timeout=15)as c:
 r=c.get("/api/admin/transport/vehicles/"+str(d["vehicle_id"])+"/profile");assert r.status_code==200,r.text
 profile=r.json();assert profile["profile"]["temperature_capability"]["temp_min_c"]=="-20.125"
 r=c.post("/api/admin/transport/vehicle-profiles",json=d["body"]);assert r.status_code==200,r.text
 assert r.json()==d["result"],"Original same-operation result changed"
 r=c.post("/api/transport/preflight/trips/33571",json={"additional_st_numbers":["SAP_2135"]});assert r.status_code==200,r.text
 thermal=r.json()["routes"][0]["temperature_requirements"]
 assert thermal["planning"]["status"]=="SKU_REQUIREMENTS_UNCONFIRMED" and not thermal["operational_admission"]
 evidence={"profile":profile,"same_operation_original_result":True,"trip_temperature":thermal}
 Path("tmp/http1157_temperature.json").write_text(json.dumps(evidence,indent=2),encoding="utf-8")
print("PASS1157 HTTP numeric current profile, exact replay, unknown SKU preserved; no new operation")
