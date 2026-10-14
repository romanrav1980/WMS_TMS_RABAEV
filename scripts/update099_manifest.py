from pathlib import Path
import json
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json")
m=json.loads(p.read_text(encoding="utf-8"))
m["components"]=["../2026-10-10_ni063_tare_deadlines/003_tare_command.sql" if x=="../2026-10-10_ni063_tare_ledger/004_package.sql" else x for x in m["components"]]
for group,names in {"components":["002_policy_helper.sql"],"startup_scripts":["001_schema.sql"],"additional_scripts":["004_debt_view.sql","005_guards.sql"]}.items():
 for name in names:
  item="../2026-10-10_ni063_tare_deadlines/"+name
  if item not in m[group]:m[group].append(item)
print(json.dumps({str(p):json.dumps(m,indent=2)+"\n"},ensure_ascii=True))
