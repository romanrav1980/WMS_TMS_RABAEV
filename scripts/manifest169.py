import json
from pathlib import Path
r=Path(__file__).resolve().parents[1];p=r/"db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json";m=json.loads(p.read_text(encoding="utf-8-sig"))
if "RRL_WAVE_EXEC_ACCESS"not in m["packages"]:m["packages"].insert(0,"RRL_WAVE_EXEC_ACCESS")
for k,items in m.items():
 if not isinstance(items,list):continue
 for i,x in enumerate(items):
  if x=="../2026-10-10_owner_hu_closure/002_finish.sql":
   items[i:i+1]=["../2026-10-10_ni033_wave_defer/001_access.sql","../2026-10-10_ni033_wave_defer/002_finish_contract.sql"];break
 for i,x in enumerate(items):
  if x=="../2026-10-10_ni033_case_scope/003_root_contract.sql":items[i]="../2026-10-10_ni033_wave_defer/003_root_contract.sql"
print(json.dumps({str(p.relative_to(r)):json.dumps(m,ensure_ascii=False,indent=2)+"\n"}))
