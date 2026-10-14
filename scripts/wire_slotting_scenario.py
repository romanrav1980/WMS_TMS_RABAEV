from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/public.py")
out[str(p)]=p.read_text(encoding="utf-8-sig")+'''
from .contracts_slotting import SlottingDemandPort,slotting_demand_service
from .api.slotting_routes import router as slotting_router
from .infrastructure.slotting_demand_reader import SlottingDemand

def build_slotting_demand(gateway: Any) -> SlottingDemandPort:
    return SlottingDemand(gateway)
'''
p=Path("api/wms_api_server/app/main.py")
out[str(p)]=p.read_text(encoding="utf-8-sig")+'''
from .modules.inventory.public import slotting_router,slotting_demand_service
from .slotting_composition import slotting_demand
app.include_router(slotting_router)
app.dependency_overrides[slotting_demand_service]=slotting_demand
'''
print(json.dumps(out,ensure_ascii=True))
