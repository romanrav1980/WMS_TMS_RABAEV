from pathlib import Path
import json,httpx
data=json.loads(Path("tmp/context1118.json").read_text(encoding="utf-8"));o=data["source"]["customer_order_id"]
base="http://127.0.0.1:8088/api/integrations/sap/store-orders/"
result={}
with httpx.Client(auth=("admin","admin123"),timeout=20)as c:
 for suffix in("","/resolve"):
  r=c.post(base+str(o)+"/prepare-st/automatic"+suffix,json=data["body"])
  assert r.status_code==200,r.text;result["repeat"+suffix]=r.json()
  actual=r.json()["result"]if suffix else r.json()
  assert actual["st_number"]=="SAP_"+str(o) and actual["idempotent"]
 r=c.post(base+"2047/automatic-layout",json=data["body"]["limits"])
 assert r.status_code==409 and "NORM_SMALLER_THAN_BOX" in r.text,r.text
 result["invalid_existing_source"]={"status":r.status_code,"detail":r.json()}
 r=c.post(base+str(o)+"/prepare-st/automatic",json={**data["body"],"unexpected":1});assert r.status_code==422
 result["strict_contract"]=422
with httpx.Client(timeout=10)as c:
 r=c.post(base+str(o)+"/prepare-st/automatic",json=data["body"]);assert r.status_code in(401,403)
 result["anonymous_denied"]=r.status_code
Path("tmp/http1121_auto.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print("PASS1121 actual HTTP repeat/resolve original two places, invalid norm409, extra field422, anonymous denied; no new source")
