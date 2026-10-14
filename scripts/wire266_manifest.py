from pathlib import Path
import json
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"));j["components"]=[x.replace("../2026-10-11_ni022_source_scope/001_api.sql","../2026-10-11_sap_gateway_actor/001_scope.sql")for x in j["components"]];j["startup_scripts"].append("../2026-10-11_sap_gateway_actor/002_account.sql");print(json.dumps({str(p):json.dumps(j,ensure_ascii=True,indent=2)+"\n"},ensure_ascii=True))
