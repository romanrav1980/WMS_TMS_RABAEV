import json,hashlib
from pathlib import Path
p=Path("db/migrations/2026-10-12_ni071_normative_correction/checkpoint.json");d=json.loads(p.read_text(encoding="utf-8"))
d["status"]="APPLIED_VALID";d["current_sha256"]={q.name:hashlib.sha256(q.read_bytes()).hexdigest()for q in p.parent.glob("*.sql")if not q.name.startswith("000_")}
d["evidence"]="603 independent concurrent credit approval one winner/one stale refusal;609/610 existing signed allocation and stale FINANCE rejection; original107.25 immutable/current0."
p.write_text(json.dumps(d,indent=2)+"\n",encoding="utf-8")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));name="../2026-10-12_ni071_normative_correction/apply.sql"
if name not in m["additional_scripts"]:m["additional_scripts"].append(name)
p.write_text(json.dumps(m,indent=2)+"\n",encoding="utf-8")
exec(Path("scripts/stock_posting_current_bundle.py").read_text(encoding="utf-8"))
