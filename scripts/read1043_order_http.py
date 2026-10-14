import httpx,json
from pathlib import Path
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin","admin123"),timeout=25) as c:
 old=c.get("/api/customer-orders/1931");assert old.status_code==200,(old.status_code,old.text[:500])
 assert old.json()["rows"][0]["order_qty_exact"]=="4"
 current=c.get("/api/customer-orders/2133");assert current.status_code==200
 assert current.json()["rows"][0]["order_qty_exact"]=="12"
 rows=c.get("/api/customer-orders",params={"limit":3});assert rows.status_code==200 and len(rows.json())<=3
 assert all("order_uom_count" in row for row in rows.json())
 missing=c.get("/api/customer-orders/999999999");assert missing.status_code==404
 invalid=c.get("/api/customer-orders/0");assert invalid.status_code==409
 Path("tmp/http1043_order_scope.json").write_text(json.dumps({"historical":old.json(),"current":current.json(),"list":rows.json(),"missing404":True,"invalid409":True},indent=2),encoding="utf-8")
print("PASS1043 actual API old4/current12/exactquantity/listbound/uommetadata/404/409")
