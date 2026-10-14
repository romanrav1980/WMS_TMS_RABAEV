from pathlib import Path
import json,httpx
ctx=json.loads(Path("tmp/context744.json").read_text(encoding="utf-8"))
probe=json.loads(Path("tmp/context753.json").read_text(encoding="utf-8"))
url="http://127.0.0.1:8088/api/receiving/warehouses/"+str(ctx["ware"])+"/settings"
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 r=client.get(url);assert r.status_code==200,r.text
 current=r.json();assert current["defer_wait_cell"]==probe["cell"]
 keys=("company_prefix","extension_digit","coordinate_unit_m","reachtruck_mps","lift_mps","placement_metric","hu_cell_height_unit","outgoing_qc_mode","outgoing_qc_independent","outgoing_qc_sample_percent")
 body={k:current[k] for k in keys if k in current}
 r=client.put(url,json=body);assert r.status_code==200,r.text
 assert r.json()["defer_wait_cell"]==probe["cell"]
print("769 PASS currentHTTP setting GET and omitted optional field preserves designation")
