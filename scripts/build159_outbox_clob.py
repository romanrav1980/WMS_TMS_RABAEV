import json
from pathlib import Path
out={};base="db/migrations/2026-10-10_outbox_clob_response/"
s=Path("db/migrations/2026-10-10_outbox_lease/002_api.sql").read_text(encoding="utf-8")
needle="RRL_TRACEABILITY_API.update_adapter_request(p_request_id,b.get_string('response_json')"
if s.count(needle)!=1:raise ValueError("Native response anchor missing")
s=s.replace(needle,"RRL_TRACEABILITY_API.update_adapter_request(p_request_id,b.get_clob('response_json')",1)
out[base+"001_contract.sql"]=s
out[base+"002_body.sql"]="create or replace "+s.split("create or replace ",2)[2]
out[base+"apply.sql"]="@@002_body.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
idx=m["components"].index("../2026-10-10_outbox_lease/002_api.sql")
m["components"][idx]="../2026-10-10_outbox_clob_response/001_contract.sql"
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
p=Path("api/wms_api_server/app/services/traceability_service.py");t=p.read_text(encoding="utf-8")
t=t.replace("                       LEASE_UNTIL,","                       to_char(LEASE_UNTIL at time zone 'UTC','YYYY-MM-DD\"T\"HH24:MI:SS.FF6TZH:TZM')LEASE_UNTIL,")
t=t.replace("                   LEASE_UNTIL,","                   to_char(LEASE_UNTIL at time zone 'UTC','YYYY-MM-DD\"T\"HH24:MI:SS.FF6TZH:TZM')LEASE_UNTIL,")
out[str(p)]=t
print(json.dumps(out))
