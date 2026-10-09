import json
from pathlib import Path
d=Path("db/migrations/2026-10-08_stock_posting_core");out={}
p=d/"125_inventory_birth.sql";s=p.read_text(encoding="utf-8")
s=s.replace("RRL_STOCK_UNIT_CORE.assert_composition(uid,cell);","RRL_STOCK_UNIT_CORE.admit_captured(uid,cell);",1)
out[str(p)]=s
p=d/"055_mes_movement_core.sql";s=p.read_text(encoding="utf-8")
s=s.replace("RRL_STOCK_UNIT_CORE.assert_composition(v_uid,m.TARGET_LOCATION);","RRL_STOCK_UNIT_CORE.admit_captured(v_uid,m.TARGET_LOCATION);",1)
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/birth_capture.py");s=p.read_text(encoding="utf-8")
needle='        captures[uid]=marks'
s=s.replace(needle,needle+'\n        if sum(len(b["unit_bindings"]) for b in births)>10000:raise ValueError("At most 10000 physical units per birth command")',1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
