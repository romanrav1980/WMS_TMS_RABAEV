import httpx
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 r=client.post("http://127.0.0.1:8088/api/transport/preflight/trips/33570/time",json={"time_zone":"UTC"})
 assert r.status_code==200,(r.status_code,r.text[:500])
 b=r.json();assert "driver_days"in b and "driver_rest"in b
 assert b["driver_days"]["days"][0]["unresolved_trip_ids"]and not b["operational_admission"]
 print("PASS258 HTTP200 currentUIpayload/localday unresolved/sourceV2/no admission")
