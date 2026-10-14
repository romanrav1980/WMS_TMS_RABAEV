from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/transport/api/vehicle_profile_routes.py")
s=p.read_text(encoding="utf-8").replace('def temperature_pair(self):','def temperature_pair(self) -> "VehicleProfileRequest":')
print(json.dumps({str(p):s}))
