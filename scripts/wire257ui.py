from pathlib import Path
import json
p=Path("admin/wms_admin_frontend/src/components/TransportTimePreflight.tsx")
s=p.read_text(encoding="utf-8").replace('import { TransportCoordination } from "./TransportCoordination";','import { TransportCoordination } from "./TransportCoordination";\nimport { TransportDriverRest, type DriverRestResult } from "./TransportDriverRest";')
s=s.replace('type Result = {','type Result = {\n  driver_rest: DriverRestResult;')
s=s.replace('    {result && <div>','    {result && <div>\n      <TransportDriverRest value={result.driver_rest}/>')
print(json.dumps({str(p):s},ensure_ascii=True))
