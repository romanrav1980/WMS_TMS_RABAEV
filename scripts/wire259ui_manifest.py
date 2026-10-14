from pathlib import Path
import json
out={}
p=Path("admin/wms_admin_frontend/src/components/TransportTimePreflight.tsx");s=p.read_text(encoding="utf-8").replace('import { TransportCoordination } from "./TransportCoordination";','import { TransportCoordination } from "./TransportCoordination";\nimport { TransportRouteInput } from "./TransportRouteInput";')
s=s.replace('    <TransportTimeApproval tripId=', '    <TransportRouteInput tripId={tripId} apiBase={apiBase} headers={headers} actor={actor}/>\n    <TransportTimeApproval tripId=');out[str(p)]=s
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"))
j["packages"].extend(["RRL_TT_ROUTE_SOURCE","RRL_TT_ROUTE_API"])
j["components"]=[x.replace("../2026-10-10_ni081_operation_plan/001_api.sql","../2026-10-11_ni081_route_input/003_operation_api.sql")for x in j["components"]]
# Source package must precede generator in generated compilation order.
pos=j["components"].index("../2026-10-11_ni081_route_input/003_operation_api.sql")
j["components"].insert(pos,"../2026-10-11_ni081_route_input/002_source.sql")
j["components"].insert(pos+2,"../2026-10-11_ni081_route_input/004_api.sql")

j["startup_scripts"].append("../2026-10-11_ni081_route_input/001_schema.sql")
out[str(p)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
