"""149 unchanged ARM URI/DTO/current native refusal, original retired141 fact preserved."""
import httpx
base="http://127.0.0.1:8088"
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 schema=client.get(base+"/openapi.json");assert schema.status_code==200
 assert "/api/admin/transport/operations/{op_id}/fact"in schema.json()["paths"]
 rows=client.get(base+"/api/admin/transport/tasks/33530/operations")
 assert rows.status_code==200,(rows.status_code,rows.text[:1400])
 before=rows.json();fact=next(row for row in before if row.get("fact_start"))
 identity=fact["op_id"]
 path=base+f"/api/admin/transport/operations/{identity}/fact"
 empty=client.patch(path,json={});assert empty.status_code==400,(empty.status_code,empty.text[:1000])
 denied=client.patch(path,json={"fact_start":fact["fact_start"],"fact_end":fact["fact_end"]})
 assert denied.status_code==409,(denied.status_code,denied.text[:1400])
 after=client.get(base+"/api/admin/transport/tasks/33530/operations")
 assert after.status_code==200 and after.json()==before
 print("PASS149 original ARM URI/schema/empty400/current cancelled trip409, original141 recorded operations/facts unchanged; no new trip or quantity",flush=True)
