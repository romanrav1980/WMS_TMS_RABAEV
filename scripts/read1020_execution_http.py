import httpx,json
from pathlib import Path
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin","admin123"),timeout=25)as c:
 r=c.get("/api/customer-orders/1931/execution");assert r.status_code==200,(r.status_code,r.text[:700]);v=r.json()
 assert v["execution_status"]=="PARTIAL"and v["active_line_count"]==1 and v["lines"][0]["picked_quantity"]=="3"and v["lines"][0]["remaining_quantity"]=="1"
 a=c.get("/api/warehouse-hus/composition",params={"identifier":"CASE:1131"});assert a.status_code==200,(a.status_code,a.text[:700])
 b=c.get("/api/warehouse-hus/composition",params={"identifier":"CP553000000001131"});assert a.json()==b.json()
 Path("tmp/http1020_execution.json").write_text(json.dumps({"order":v,"canonical_case":a.json()},indent=2),encoding="utf-8")
 print("PASS1020 actualHTTP originalorder partial3/remain1/active1/newunits; internalCASE=scan/currentphysicalslot")
