from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni081_trip_time")
p=Path("admin/wms_admin_frontend/src/components/TransportGanttPage.tsx")
s=p.read_text(encoding="utf-8")
needle='apiBase={API_BASE} headers={apiHeaders()} />'
assert s.count(needle)==1
out={str(p):s.replace(needle,'apiBase={API_BASE} headers={apiHeaders()} actor={API_BASIC_AUTH.split(":")[0]} />')}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json")
m=json.loads(p.read_text(encoding="utf-8"))
out[str(f/"000_before_manifest.json")]=p.read_text(encoding="utf-8")
base="../2026-10-11_ni081_trip_time/"
m["packages"].append("RRL_TT_TIME_API")
m["components"].append(base+"002_api.sql")
for i,path in enumerate(m["components"]):
 if "transport_edit" in path and path.endswith("001_api.sql"):m["components"][i]=base+"004_create_status.sql"
m["additional_scripts"].append(base+"003_guard.sql")
m["startup_scripts"].append(base+"001_schema.sql")
m["required_columns"]["RRL_TT_TIME_APPROVAL"]=["TT_ID","VERSION_NO","OPERATION_ID","SOURCE_HASH","TIME_ZONE"]
out[str(p)]=json.dumps(m,indent=2)+"\n"
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@004_create_status.sql\n"
out[str(f/"rollback.sql")]=(f/"rollback.sql").read_text(encoding="utf-8")+"@000_before_rrl_transport_edit_api.sql\n"
print(json.dumps(out,ensure_ascii=True))
