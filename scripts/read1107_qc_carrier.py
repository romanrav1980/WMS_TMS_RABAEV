import json,httpx
from pathlib import Path
r={}
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin","admin123"),timeout=20)as c:
 for identifier in("CP553000000001131","CASE:1131","CASE.QC.ST:4bb85f1f15:1131"):
  response=c.get("/api/outgoing-quality/"+identifier)
  r[identifier]={"status":response.status_code,"body":response.json()if response.headers.get("content-type","").startswith("application/json")else response.text[:300]}
Path("tmp/read1107_qc_carrier.json").write_text(json.dumps(r,indent=2),encoding="utf-8")
print(json.dumps(r,ensure_ascii=True))
