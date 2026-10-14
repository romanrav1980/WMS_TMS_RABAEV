from pathlib import Path
import json,re
d=Path("db/migrations/2026-10-08_stock_posting_core");m=json.loads((d/"current_runtime_manifest.json").read_text(encoding="utf-8"))
sources={name:(d/path).read_text(encoding="utf-8")for name,path in []}
root=Path("db/migrations/2026-10-11_ni061_marked_placement/002_root.sql").read_text(encoding="utf-8")
missing=[]
for p in m["components"]:
 text=(d/p).read_text(encoding="utf-8");match=re.search(r"create\s+or\s+replace\s+package\s+(\w+)",text,re.I)
 if match:
  name=match[1]
  if "procedure compile_command" in text.lower()and "procedure execute_command"in text.lower()and name+".compile_command"not in root:
   missing.append([name,p])
print(json.dumps(missing,indent=2))
