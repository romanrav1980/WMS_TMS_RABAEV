from pathlib import Path
import json
files={}
p=Path("api/wms_api_server/app/modules/fulfillment/public.py");s=p.read_text(encoding="utf-8")
s+="""
from .contracts_prepared_layout import PreparedLayoutPort, prepared_layout_service
from .api.prepared_layout_routes import router as prepared_layout_router
from .infrastructure.prepared_layout import PreparedLayout


def build_prepared_layout(gateway: Any, posting: Any) -> PreparedLayoutPort:
    return PreparedLayout(gateway, posting)
"""
files[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_stock.py");s=p.read_text(encoding="utf-8")
old='self.command_type in {"CASE_PALLET_TYPE_CHANGE"'
assert s.count(old)==1;files[str(p)]=s.replace(old,'self.command_type in {"ST_PREPARED_ROW_MOVE","CASE_PALLET_TYPE_CHANGE"',1)
p=Path("api/wms_api_server/app/main.py");s=p.read_text(encoding="utf-8");start=s.index("from .modules.inventory.public import pallet_floor_router,pallet_floor_service")
old=s[start:]
assert "from .case_type_composition import build_case_type_service" in old
# Extract carrier/layout registrations from the oversized composition root.
files["api/wms_api_server/app/prepared_carrier_routes.py"]='''"""Registration of existing carrier metadata and prepared-layout workspaces."""
from fastapi import FastAPI
from .modules.inventory.public import pallet_floor_router, pallet_floor_service, case_type_router, case_type_service
from .pallet_floor_composition import build_pallet_floor_service
from .case_type_composition import build_case_type_service
from .modules.fulfillment.public import prepared_layout_router, prepared_layout_service
from .prepared_layout_composition import build_prepared_layout_service


def register_prepared_carrier_routes(app: FastAPI) -> None:
    for router, dependency, factory in (
        (pallet_floor_router, pallet_floor_service, build_pallet_floor_service),
        (case_type_router, case_type_service, build_case_type_service),
        (prepared_layout_router, prepared_layout_service, build_prepared_layout_service),
    ):
        app.include_router(router)
        app.dependency_overrides[dependency] = factory
'''
files[str(p)]=s[:start]+"from .prepared_carrier_routes import register_prepared_carrier_routes\nregister_prepared_carrier_routes(app)\n"
print(json.dumps(files))
