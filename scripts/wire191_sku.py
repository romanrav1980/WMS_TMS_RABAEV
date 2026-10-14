from pathlib import Path
import json,hashlib
from decimal import Decimal
out={}
p=Path("api/wms_api_server/app/modules/master_data/contracts.py");t=p.read_text(encoding="utf-8").replace("from typing import Literal","from typing import Literal\nfrom decimal import Decimal")
t=t.replace("    serialized_weight_boxes: bool | None = None","    serialized_weight_boxes: bool | None = None\n    order_weight_tolerance_pct: Decimal | None = Field(default=None, ge=0, le=100, decimal_places=2)")
out[str(p)]=t
p=Path("api/wms_api_server/app/modules/master_data/infrastructure/receipt_policy.py");t=p.read_text(encoding="utf-8").replace("import json","import json\nfrom decimal import Decimal",1)
t=t.replace("p.SERIALIZED_WEIGHT_BOXES,","p.SERIALIZED_WEIGHT_BOXES,p.ORDER_WEIGHT_TOLERANCE_PCT,",1)
t=t.replace('"profiles": profiles,','"profiles": profiles,\n                "order_weight_tolerance_pct": format(Decimal(str(row["order_weight_tolerance_pct"] if configured else 15)), "f"),',1)
t=t.replace("select POLICY_VERSION,SERIALIZED_WEIGHT_BOXES from","select POLICY_VERSION,SERIALIZED_WEIGHT_BOXES,ORDER_WEIGHT_TOLERANCE_PCT from")
a="            if weighted:\n"
t=t.replace(a,'            tolerance = Decimal(str(old[2] if old else 15)) if request.order_weight_tolerance_pct is None else request.order_weight_tolerance_pct\n'+a,1)
t=t.replace('params = {"w": int(weighted),','params = {"pct": tolerance, "w": int(weighted),')
t=t.replace("MARKING_REQUIRED=:m,SERIALIZED_WEIGHT_BOXES=:w,","MARKING_REQUIRED=:m,SERIALIZED_WEIGHT_BOXES=:w,ORDER_WEIGHT_TOLERANCE_PCT=:pct,")
t=t.replace("MARKING_REQUIRED,SERIALIZED_WEIGHT_BOXES,UPDATED_AT","MARKING_REQUIRED,SERIALIZED_WEIGHT_BOXES,ORDER_WEIGHT_TOLERANCE_PCT,UPDATED_AT")
t=t.replace("values (:a,:v,:m,:w,systimestamp,:actor)","values (:a,:v,:m,:w,:pct,systimestamp,:actor)")
t=t.replace('"serialized_weight_boxes": weighted,','"serialized_weight_boxes": weighted,"order_weight_tolerance_pct": format(tolerance,"f"),')
out[str(p)]=t
p=Path("wiki-raw/wms_admin_ui_reference/finished-goods.html");t=p.read_text(encoding="utf-8");a='<label><input id="fgReceiptWeightedBoxes" type="checkbox" /> Серийные весовые коробки (KG, GS1)</label>'
assert a in t;t=t.replace(a,a+'\n            <label>Допуск массы заказа, % <input id="fgOrderWeightTolerance" type="number" min="0" max="100" step="0.01" value="15" /></label>')
out[str(p)]=t
p=Path("wiki-raw/wms_admin_ui_reference/sku-receiving-policy.js");t=p.read_text(encoding="utf-8")
t=t.replace('      el("fgReceiptWeightedBoxes").checked = Boolean(data.serialized_weight_boxes);','      el("fgReceiptWeightedBoxes").checked = Boolean(data.serialized_weight_boxes);\n      el("fgOrderWeightTolerance").value = data.order_weight_tolerance_pct ?? "15";')
t=t.replace('profiles }),','order_weight_tolerance_pct: el("fgOrderWeightTolerance").value, profiles }),')
out[str(p)]=t
f=Path("db/migrations/2026-10-11_ni042_order_weight_policy")
out[str(f/"checkpoint.json")]=json.dumps({"migration_id":"2026-10-11-191-order-weight-policy","sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in f.glob("*.sql")},"recovery":"Additive default15 metadata guarded rollback; existing optimistic SKU policy; no DB copy"},indent=2)
print(json.dumps(out,ensure_ascii=True))
