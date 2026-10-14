import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/transport/public.py");v=p.read_text(encoding="utf-8");assert "build_vehicle_profiles"not in v
out[str(p)]=v+"""
from .contracts_vehicle_profile import VehicleProfilePort,vehicle_profile_service
from .infrastructure.vehicle_profile import VehicleProfiles
from .api.vehicle_profile_routes import router as vehicle_profile_router

def build_vehicle_profiles(gateway: Any)->VehicleProfilePort:
    return VehicleProfiles(gateway)
"""
p=Path("api/wms_api_server/app/main.py");v=p.read_text(encoding="utf-8");assert "vehicle_profile_router"not in v
out[str(p)]=v+"""
from .modules.transport.public import vehicle_profile_router,vehicle_profile_service
from .vehicle_profile_composition import build_vehicle_profile_service
app.include_router(vehicle_profile_router)
app.dependency_overrides[vehicle_profile_service]=build_vehicle_profile_service
"""
print(json.dumps(out))
