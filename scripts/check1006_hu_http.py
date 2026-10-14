import json,httpx
from pathlib import Path
v=json.loads(Path("tmp/context1002.json").read_text(encoding="utf-8"));old=json.loads(Path("tmp/context987.json").read_text(encoding="utf-8"));case=old["cases"][0][0]
body={**v["relocate_body"],"identifier":"CASE:"+str(case),"operation_id":"HU1002.RELOCATE:"+old["tag"]}
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin","admin123"),timeout=25)as c:
 r=c.post("/api/warehouse-hus/relocate-slot",json=body);assert r.status_code==200,(r.status_code,r.text[:1200]);data=r.json()
 assert data==v["relocate"],"HTTP must replay original result"
 r=c.get("/api/warehouse-hus/composition",params={"identifier":old["cases"][0][2]});assert r.status_code==200;current=r.json()
 assert current["nodes"][0]["version"]==10 and current["quantities"][0]["quantity"]=="12"
 Path("tmp/http1006_hu.json").write_text(json.dumps({"cached_relocation":data,"current_case":current,"original_operation_replayed":True},indent=2),encoding="utf-8")
 print("PASS1006 existingHTTP cached HU_RELOCATE_SLOT/same receipt/currentCASEversion10/12EA")
