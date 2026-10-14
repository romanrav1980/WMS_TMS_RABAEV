from pathlib import Path
import json
d=Path("db/migrations/2026-10-08_stock_posting_core");m=json.loads((d/"current_runtime_manifest.json").read_text(encoding="utf-8"))
for category in ["startup_scripts","components","additional_scripts"]:
 for path in m.get(category,[]):
  if "RRL_RECEIPT_UNIT_PHYSICAL_UK" in (d/path).read_text(encoding="utf-8"):print(category,path)
