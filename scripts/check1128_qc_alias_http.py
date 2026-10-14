import json,httpx
from pathlib import Path
r={}
canonical="CASE.QC.ST:4bb85f1f15:1131"
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin","admin123"),timeout=20)as c:
 for identifier in("CP553000000001131","CASE:1131",canonical):
  response=c.get("/api/outgoing-quality/"+identifier);assert response.status_code==200,response.text
  body=response.json();assert body["shipment_identifier"]==canonical and body["case_content_version"]==20
  r[identifier]={"status":200,"canonical":body["shipment_identifier"],"version":body["case_content_version"],"ready":body["ready"],"requested_identifier":body.get("requested_identifier")}
 response=c.get("/api/outgoing-quality/CASE:999999999999999999");assert response.status_code==403,response.text
 r["unknown_source"]=403
Path("tmp/http1128_qc_alias.json").write_text(json.dumps(r,indent=2),encoding="utf-8")
print("PASS1128 physical CASE barcode/CASE:ID/canonical same current QC v20; unknown source denied; no QC POST")
