from pathlib import Path
import json
p=Path("admin/wms_admin_frontend/src/components/TransportRouteInput.tsx");s=p.read_text(encoding="utf-8")
s=s.replace('import {TransportRoadLegs} from "./TransportRoadLegs";','import {TransportRoadLegs} from "./TransportRoadLegs";\nimport {TransportDeliveryWindows} from "./TransportDeliveryWindows";')
needle="<TransportRoadLegs"
assert needle in s;s=s.replace(needle,"<TransportDeliveryWindows tripId={tripId} apiBase={apiBase} headers={headers} actor={actor}/><TransportRoadLegs",1)
print(json.dumps({p.as_posix():s},ensure_ascii=True))
