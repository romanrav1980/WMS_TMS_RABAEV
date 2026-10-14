import json
from pathlib import Path
r=Path(__file__).resolve().parents[1];p=r/"db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json";m=json.loads(p.read_text(encoding="utf-8-sig"))
for k,items in m.items():
 if isinstance(items,list):
  for i,x in enumerate(items):
   if x=="../2026-10-10_ni033_empty_case/002_wave_access_contract.sql":items[i]="../2026-10-11_ni033_mixed_wave/001_access.sql"
   elif x=="../2026-10-10_ni033_wave_defer/002_finish_contract.sql":items[i]="../2026-10-11_ni033_mixed_wave/002_finish_contract.sql"
print(json.dumps({str(p.relative_to(r)):json.dumps(m,ensure_ascii=False,indent=2)+"\n"}))
