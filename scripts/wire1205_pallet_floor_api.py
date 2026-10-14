from pathlib import Path
import json
f={}
p=Path("api/wms_api_server/app/modules/inventory/public.py");s=p.read_text(encoding="utf-8")
s+='''

from .contracts_pallet_floor import PalletFloorPort,pallet_floor_service
from .api.pallet_floor_routes import router as pallet_floor_router
from .infrastructure.pallet_floor_type import PalletFloorType

def build_pallet_floor_type(gateway: Any,posting: Any)->PalletFloorPort:
    return PalletFloorType(gateway,posting)
'''
f[str(p)]=s
p=Path("api/wms_api_server/app/main.py");s=p.read_text(encoding="utf-8")
s+='''

from .modules.inventory.public import pallet_floor_router,pallet_floor_service
from .pallet_floor_composition import build_pallet_floor_service
app.include_router(pallet_floor_router)
app.dependency_overrides[pallet_floor_service]=build_pallet_floor_service
'''
f[str(p)]=s
print(json.dumps(f))
