from pathlib import Path
import json,httpx
ctx=json.loads(Path("tmp/context671.json").read_text(encoding="utf-8"))
trip=ctx["group_plan"]["target_trip_id"];address=ctx["group_onward"]["members"][0]["final_address"]
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 url="http://127.0.0.1:8088/api/delivery/store-receipts/trips/"+str(trip)+"/places"
 r=client.get(url,params={"store_address":address,"limit":1});assert r.status_code==200,r.text
 rows=r.json();assert len(rows)==1 and rows[0]["load_operation_id"]==ctx["group_second_load_operation_id"]
 r=client.get(url,params={"store_address":address,"limit":1,"after":rows[0]["load_operation_id"]});assert r.status_code==200 and r.json()==[],r.text
 r=client.get(url,params={"store_address":address,"limit":1,"after":ctx["load_operation_id"]});assert r.status_code==422,r.text
 body=dict(operation_id=ctx["group_store_operation_id"],load_operation_id=ctx["group_second_load_operation_id"],store_address=address,**ctx["group_store_metadata"])
 r=client.post("http://127.0.0.1:8088/api/delivery/store-receipts/confirm",json=body);assert r.status_code==409 and r.json()["detail"]["outcome_confirmed"]is False,r.text
print("PASS738 latestHTTP pages/empty/foreign422/canonical conflict keeps original intent")
