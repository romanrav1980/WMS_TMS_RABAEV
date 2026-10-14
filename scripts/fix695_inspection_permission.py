from pathlib import Path
import json,hashlib
root=Path("db/migrations/2026-10-12_ni072_shipping_inspection")
out={}
for p in [*root.glob("*.sql"),Path("scripts/checkpoint694_inspection.py"),Path("wiki/database/nicora_ni072_shipping_inspection_20261012.md")]:
 out[str(p)]=p.read_text(encoding="utf-8").replace("warehouse_day_inspection_confirm","warehouse_day_inspect").replace("WAREHOUSE_DAY_INSPECTION_CONFIRM","WAREHOUSE_DAY_INSPECT")
s=out[str(root/"001_schema.sql")]
out[str(root/"004_permission.sql")]=s[s.index("merge into RIGHTS"):]
out[str(root/"apply_resume695.sql")]="@004_permission.sql\n@002_api.sql\n@003_ledger.sql\n"
p=root/"checkpoint.json";d=json.loads(p.read_text());d["partial_apply"]="table created; initial permission name exceeded legacy RIGHT1(30); no rows/API written";d["permission"]="warehouse_day_inspect";d["current_sha256"]={Path(name).name:hashlib.sha256(value.encode()).hexdigest()for name,value in out.items()if name.endswith(".sql")}
out[str(p)]=json.dumps(d,indent=2)+"\n"
print(json.dumps(out))
