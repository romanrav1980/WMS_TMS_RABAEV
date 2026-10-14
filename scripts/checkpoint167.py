import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parents[1];f=r/"db/migrations/2026-10-10_ni033_case_close"
paths=list(f.glob("*.sql"))+[r/"api/wms_api_server/app/modules/inventory/infrastructure/case_carrier_close.py",r/"api/wms_api_server/app/modules/inventory/infrastructure/case_close_journal.py"]
(f/"checkpoint.json").write_text(json.dumps({"migration_id":"2026-10-10-167-case-carrier-close","source_sha256":{str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},"recovery":"drop additive guard only; original journal remains; no database copy"},indent=2)+"\n",encoding="utf-8")
p=r/"db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json";m=json.loads(p.read_text(encoding="utf-8-sig"))
name="../2026-10-10_ni033_case_close/001_journal_guard.sql"
if name not in m["additional_scripts"]:m["additional_scripts"].append(name)
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
