import json
from pathlib import Path
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json")
m=json.loads(p.read_text(encoding="utf-8"))
replacements={"../2026-10-10_ni062_return_receiving/005_root.sql":"../2026-10-10_ni062_return_putaway/006_root.sql"}
for old,new in [("RRL_STOCK_TASK_PLAN","003_task_plan.sql"),("RRL_STOCK_TASK_CORE","004_task_core.sql"),("RRL_STOCK_TASK_DOMAIN","005_task_domain.sql")]:
 for item in m["components"]:
  text=(p.parent/item).read_text(encoding="utf-8-sig")
  if text.lower().startswith("create or replace package "+old.lower()+" "):
   replacements[item]="../2026-10-10_ni062_return_putaway/"+new
m["components"]=[replacements.get(item,item) for item in m["components"]]
helper="../2026-10-10_ni062_return_putaway/002_helper.sql"
if helper not in m["components"]:m["components"].append(helper)
for name in ["001_schema.sql","007_guards.sql"]:
 item="../2026-10-10_ni062_return_putaway/"+name
 key="startup_scripts" if name.startswith("001") else "additional_scripts"
 if item not in m[key]:m[key].append(item)
print(json.dumps({str(p):json.dumps(m,indent=2)+"\n"},ensure_ascii=True))
