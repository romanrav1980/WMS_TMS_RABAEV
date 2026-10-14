from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/transport/public.py");s=p.read_text(encoding="utf-8")
s+="\nfrom .contracts_depot import WarehouseDepotPort,warehouse_depot_service\nfrom .infrastructure.warehouse_depot import WarehouseDepot\nfrom .api.warehouse_depot_routes import router as warehouse_depot_router\n\ndef build_warehouse_depot(gateway: Any) -> WarehouseDepotPort:\n    return WarehouseDepot(gateway)\n";out[str(p)]=s
p=Path("api/wms_api_server/app/main.py");s=p.read_text(encoding="utf-8")
s+="\nfrom .modules.transport.public import warehouse_depot_router,warehouse_depot_service\nfrom .warehouse_depot_composition import build_warehouse_depot_service\napp.include_router(warehouse_depot_router)\napp.dependency_overrides[warehouse_depot_service]=build_warehouse_depot_service\n";out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
