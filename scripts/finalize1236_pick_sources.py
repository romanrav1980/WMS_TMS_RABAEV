from pathlib import Path
import json
d=Path("db/migrations/2026-10-14_ni033_pick_create_idempotency");files={}
s=(d/"001_api.sql").read_text(encoding="utf-8")
files[str(d/"001_schema.sql")]=s[:s.index("create or replace package")]
files[str(d/"006_guard.sql")]=s[s.index("create or replace trigger"):]
files[str(d/"apply.sql")]="@@001_schema.sql\n@@003_command.sql\n@@004_admission.sql\n@@005_picking.sql\n@@006_guard.sql\n@@002_ledger.sql\n"
files[str(d/"rollback.sql")]="-- Disable operation-id UI/API integration before rollback; retained receipts must not be deleted.\n@@000_before_rrl_pick_plan_admission.sql\n@@000_before_rrl_picking_api.sql\n"
base=Path("db/migrations/2026-10-08_stock_posting_core");mp=base/"current_runtime_manifest.json";m=json.loads(mp.read_text(encoding="utf-8"))
prefix="../2026-10-14_ni033_pick_create_idempotency/"
for key,values in {"packages":["RRL_PICK_PLAN_CREATE_API"],"components":[prefix+"003_command.sql",prefix+"004_admission.sql",prefix+"005_picking.sql"],"additional_scripts":[prefix+"006_guard.sql"],"startup_scripts":[prefix+"001_schema.sql"]}.items():
 for v in values:
  if v not in m[key]:m[key].append(v)
files[str(mp)]=json.dumps(m,indent=2)+"\n"
print(json.dumps(files,ensure_ascii=True))
