from pathlib import Path
import json
p=Path("admin/wms_admin_frontend/src/components/TransportTimePreflight.tsx")
s=p.read_text(encoding="utf-8").replace('import { TransportDriverRest, type DriverRestResult } from "./TransportDriverRest";','import { TransportDriverRest, type DriverRestResult } from "./TransportDriverRest";\nimport { TransportDriverDay, type DriverDayResult } from "./TransportDriverDay";')
s=s.replace('driver_rest: DriverRestResult;','driver_rest: DriverRestResult; driver_days: DriverDayResult;')
s=s.replace('<TransportDriverRest value={result.driver_rest}/>','<TransportDriverRest value={result.driver_rest}/>\n      <TransportDriverDay value={result.driver_days}/>')
p2=Path("api/wms_api_server/app/modules/transport/infrastructure/driver_day.py")
d=p2.read_text(encoding="utf-8").replace('if trip not in ids:\n            ids.append(trip)','if trip not in ids:\n            if len(ids) >= 200:\n                raise TransportPlanError("DRIVER_DAY_TRIP_BOUND_200", "Сузьте окно рейсов водителя")\n            ids.append(trip)')
print(json.dumps({str(p):s,str(p2):d},ensure_ascii=True))
