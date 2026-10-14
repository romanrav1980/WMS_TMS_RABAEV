from pathlib import Path
import json
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json")
m=json.loads(p.read_text(encoding="utf-8"))
replacements={"../2026-10-10_ni063_tare_resolution/006_root.sql":"../2026-10-10_ni063_tare_assembly/006_root.sql","../2026-10-10_ni063_tare_resolution/005_tare_command.sql":"../2026-10-10_ni063_tare_assembly/004_tare_command.sql","../2026-10-10_ni063_tare_resolution/003_command.sql":"../2026-10-10_ni063_tare_assembly/005_resolution_command.sql"}
m["components"]=[replacements.get(x,x) for x in m["components"]]
for group,names in {"components":["002_planning.sql","003_command.sql"],"startup_scripts":["001_schema.sql"],"additional_scripts":["007_balance_guards.sql","008_book_guards.sql"]}.items():
 for name in names:
  item="../2026-10-10_ni063_tare_assembly/"+name
  if item not in m[group]:m[group].append(item)
print(json.dumps({str(p):json.dumps(m,indent=2)+"\n"},ensure_ascii=True))
