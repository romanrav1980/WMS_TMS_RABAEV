import json
from pathlib import Path
p=Path("db/migrations/2026-10-12_ni071_vehicle_source/apply.sql");v=p.read_text(encoding="utf-8")
for name in ("008_source_hash.sql","009_source_hash_ledger.sql","010_config_fleet.sql","011_config_fleet_ledger.sql"):
 if "@@"+name not in v:v+="@@"+name+"\n"
p.write_text(v,encoding="utf-8")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for name in ("../2026-10-12_ni071_vehicle_source/apply.sql","../2026-10-12_ni071_unload_norm_basis/apply.sql"):
 if name not in m["additional_scripts"]:m["additional_scripts"].append(name)
p.write_text(json.dumps(m,indent=2)+"\n",encoding="utf-8")
exec(Path("scripts/stock_posting_current_bundle.py").read_text(encoding="utf-8"))
