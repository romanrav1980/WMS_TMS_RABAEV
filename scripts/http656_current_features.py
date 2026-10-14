import httpx,json
from pathlib import Path
ctx=json.loads(Path("tmp/context641.json").read_text())
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 r=client.get("http://127.0.0.1:8088/api/finance/day-reconciliation/warehouses/"+str(ctx["warehouse"])+"/shipping-register",params={"business_date":"2026-10-12"})
 assert r.status_code==200,(r.status_code,r.text[:500])
 value=r.json();assert "classification_coverage"in value and value["classification_coverage"]["scope"]=="CURRENT_WMS_CELL_CATALOG"
 assert not value["all_shipping_zone_coverage_verified"]and not value["shipping_zone_empty_confirmed"]
 r=client.post("http://127.0.0.1:8088/api/transport/preflight/trips/33570/time",json={"time_zone":"UTC"})
 assert r.status_code==200,(r.status_code,r.text[:500])
 value=r.json();assert value["driver_days"]["days"];assert all("continuity"in day for day in value["driver_days"]["days"])
 assert not value["operational_admission"]
 print("PASS656 loaded API current published-catalog diagnostics/driver-day continuity/read-only/no operational admission")
