from pathlib import Path
import json
p=Path("scripts/ni042_warehouse_scale_archive_case.py");t=p.read_text(encoding="utf-8").replace("187","188")
a='"weighted_box_barcode":labels[0]}'
assert a in t
t=t.replace(a,'"weighted_box_barcode":labels[0],"warehouse_scale_capture":capture["capture_key"]}')
a='  q.execute("select count(*),sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:id",id=operation);journal=q.fetchone();assert journal[0]>0'
t=t.replace(a,a+'\n  q.execute("select STOCK_OPERATION_ID from RRL_WH_SCALE_USE where CAPTURE_KEY=:p_key",p_key=capture["capture_key"]);assert q.fetchone()==(operation,)\n  reused=api.post(base+f"/tasks/{case}/lines/{line}/weighted-box",json={**body,"operation_id":operation+":SECOND"});assert reused.status_code==409,(reused.status_code,reused.text)')
print(json.dumps({"scripts/ni042_warehouse_scale_use_case.py":t},ensure_ascii=True))
