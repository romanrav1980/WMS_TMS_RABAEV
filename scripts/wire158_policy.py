import json,re
from pathlib import Path
out={}
base="db/migrations/2026-10-10_ni081_range_apply/"
p=Path(base+"002_policy.sql");s=p.read_text(encoding="utf-8");s=re.sub(r"\bmode\b","v_mode",s);out[str(p)]=s
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for name in ("RRL_PICK_RANGE_POLICY","RRL_PICK_TOPOLOGY_API"):
 if name not in m["packages"]:m["packages"].append(name)
indices=[]
d=p.parent
for i,relative in enumerate(m["components"]):
 if re.search(r"create\s+or\s+replace\s+package\s+RRL_STOCK_REPL_CAPACITY\b",(d/relative).read_text(encoding="utf-8"),re.I):indices.append(i)
if len(indices)!=1:raise ValueError("Expected one current native capacity contract:"+str(indices))
m["components"][indices[0]]="../2026-10-10_ni081_range_apply/004_capacity_contract.sql"
m["components"].insert(indices[0],"../2026-10-10_ni081_range_apply/002_policy.sql")
m["components"].append("../2026-10-10_ni081_range_apply/005_topology_contract.sql")
m["startup_scripts"].append("../2026-10-10_ni081_range_apply/001_schema.sql")
m["additional_scripts"].append("../2026-10-10_ni081_range_apply/003_guards.sql")
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
print(json.dumps(out))
