import json
from pathlib import Path
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json")
m=json.loads(p.read_text(encoding="utf-8"))
for name in ("LEGACY_SBORKA_PALLET_ID","SHIPPED_OPERATION"):
 if name not in m["required_columns"]["RRL_CASE_PICK_TASK"]:m["required_columns"]["RRL_CASE_PICK_TASK"].append(name)
out={str(p):json.dumps(m,indent=2)+"\n"}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/case_shipment_binding.py")
s=p.read_text(encoding="utf-8").replace("shipments = cur.fetchall()","shipments = cur.fetchmany(2)",1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/domain/carrier_shipment.py")
s=p.read_text(encoding="utf-8")
needle="        converted = convert_exact(quantity, int(numerator), int(denominator), int(scale))"
assert s.count(needle)==1
s=s.replace(needle,"        if any(value != int(value) for value in (numerator, denominator, scale)):\n            raise ValueError('Conversion policy requires integer factors and scale')\n"+needle,1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
