import httpx
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 r=client.get("http://127.0.0.1:8088/api/inventory/store-returns/warehouses/13583852/pending-page",params={"limit":1});assert r.status_code==200 and r.json()["items"]==[],r.text
 r=client.get("http://127.0.0.1:8088/api/inventory/store-returns/warehouses/13583852/policy");assert r.status_code==200,r.text
 r=client.get("http://127.0.0.1:8088/api/transport/preflight/trips/33564/road-legs",params={"depot_address":"QA.HTTP283","max_age_hours":24});assert r.status_code==200 and r.json()["drive_min"]is None and r.json()["status"]=="ROAD_DURATION_UNKNOWN",r.text
print("PASS283 HTTP currentpagedemptyqueue/policy/currentNativeV3roadlegsunknown/no mutation")
