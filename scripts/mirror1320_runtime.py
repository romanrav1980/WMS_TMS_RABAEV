from pathlib import Path
import json
base=Path("db/migrations/2026-10-08_stock_posting_core");p=base/"current_runtime_manifest.json";m=json.loads(p.read_text(encoding="utf-8"))
old="../2026-10-11_ni081_route_input/003_operation_api.sql";new="../2026-10-14_ni053_driver_workspace/001_api.sql"
assert old in m["components"]or new in m["components"];m["components"]=[new if x==old else x for x in m["components"]]
for x in ["../2026-10-14_ni053_driver_workspace/apply.sql","../2026-10-14_ni053_stock_pallet_unload/apply.sql"]:
 if x not in m["additional_scripts"]:m["additional_scripts"].append(x)
files={str(p):json.dumps(m,indent=2)+"\n"}
print(json.dumps(files,ensure_ascii=True))
