from pathlib import Path
import json
out={}
p=Path('api/wms_api_server/app/modules/inventory/api/stock_command_routes.py');s=p.read_text(encoding='utf-8-sig')
s=s.replace('from ..contracts_stock import StockLine, StockPostingError','from ..contracts_stock import StockLine, StockPostingError\nfrom ..contracts_stock_settings import StockCompatibilityPort,StockSettingError,stock_compatibility_service')
start=s.index('    from ....oracle_gateway import OracleGateway');end=s.index('\n\n\n@router.post("/compatibility/manual-moves")',start)
s=s[:start]+"""    try:return service.set_compatibility(request.enabled,request.reason,user.username)
    except StockSettingError as exc:raise HTTPException(exc.status,detail=str(exc)) from exc
"""+s[end:]
s=s.replace('user: AdminUser = Depends(require_permission("stock_compatibility_admin")),\n)', 'user: AdminUser = Depends(require_permission("stock_compatibility_admin")),\n    service: StockCompatibilityPort = Depends(stock_compatibility_service),\n)')
out[str(p)]=s
p=Path('api/wms_api_server/app/modules/inventory/public.py');s=p.read_text(encoding='utf-8-sig')
s+='''
from .contracts_stock_settings import StockCompatibilityPort,stock_compatibility_service
from .infrastructure.stock_settings import StockCompatibility

def build_stock_compatibility(gateway: Any) -> StockCompatibilityPort:
    return StockCompatibility(gateway)
'''
out[str(p)]=s
p=Path('api/wms_api_server/app/main.py');s=p.read_text(encoding='utf-8-sig')
s+='''
from .modules.inventory.public import stock_compatibility_service
from .stock_settings_composition import stock_settings_service
app.dependency_overrides[stock_compatibility_service]=stock_settings_service
'''
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
