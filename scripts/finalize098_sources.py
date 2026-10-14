from pathlib import Path
import json
folder=Path("db/migrations/2026-10-10_ni063_tare_ledger")
p=folder/"004_package.sql";s=p.read_text(encoding="utf-8-sig")
key,package=s.split("\n/\n",1)
apply=(folder/"apply.sql").read_text(encoding="utf-8-sig").replace("@@004_package.sql","@@002_key.sql\n@@004_package.sql")
manifest=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json")
m=json.loads(manifest.read_text(encoding="utf-8"))
m["components"]=["../2026-10-10_ni063_tare_ledger/005_root.sql" if x=="../2026-10-10_ni062_return_putaway/006_root.sql" else x for x in m["components"]]
for key_name,names in {"components":["004_package.sql"],"startup_scripts":["001_schema.sql","002_key.sql"],"additional_scripts":["006_guards.sql"]}.items():
 for name in names:
  item="../2026-10-10_ni063_tare_ledger/"+name
  if item not in m[key_name]:m[key_name].append(item)
print(json.dumps({str(p):package,str(folder/"002_key.sql"):key+"\n/\n",str(folder/"apply.sql"):apply,str(manifest):json.dumps(m,indent=2)+"\n"},ensure_ascii=True))
