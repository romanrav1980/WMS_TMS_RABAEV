import sys,json
from pathlib import Path
sys.path.insert(0,str(Path("api/wms_api_server").resolve()))
import httpx
with httpx.Client(auth=("admin","admin123"),timeout=30)as c:
 base="http://127.0.0.1:8088/api/finance/logistics-costs"
 r=c.get(base+"/warehouses/35944973/period-policy");assert r.status_code==200 and r.json()["version"]==3,(r.status_code,r.text[:500])
 r=c.get(base+"/trips/33534/assembly-period",params={"warehouse_id":38542432,"timezone_region":"Asia/Tbilisi"});assert r.status_code==200 and r.json()["state"]=="INCOMPLETE",(r.status_code,r.text[:500])
 r=c.get("http://127.0.0.1:8088/api/case-pick/tasks/1112");assert r.status_code==200 and "started_at_instant"in r.json()and r.json()["started_at_instant"]is None,(r.status_code,r.text[:500])
print("PASS366 restartedHTTP policyv3/assembly INCOMPLETE/legacyCASE exactclock nullable")
