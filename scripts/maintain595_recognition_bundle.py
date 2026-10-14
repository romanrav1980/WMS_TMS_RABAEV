import json
from pathlib import Path
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for name in("../2026-10-12_ni071_transport_recognition/apply.sql","../2026-10-12_ni071_transport_rounding/apply.sql"):
 if name not in m["additional_scripts"]:m["additional_scripts"].append(name)
p.write_text(json.dumps(m,indent=2)+"\n",encoding="utf-8")
exec(Path("scripts/stock_posting_current_bundle.py").read_text(encoding="utf-8"))
