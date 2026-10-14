from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/public.py");t=p.read_text(encoding="utf-8")
assert "waiting_task_router" not in t
out[str(p)]=t+"""
from .api.waiting_task_routes import router as waiting_task_router
from .contracts_waiting_tasks import waiting_task_dependency,WaitingTaskPort
from .infrastructure.st_defer_waiting import StDeferWaiting

def waiting_task_service() -> WaitingTaskPort:
    return StDeferWaiting(OracleGateway())
"""
p=Path("api/wms_api_server/app/main.py");t=p.read_text(encoding="utf-8")
assert "waiting_task_router" not in t
out[str(p)]=t+"""
from .modules.inventory.public import waiting_task_router,waiting_task_dependency,waiting_task_service
app.include_router(waiting_task_router)
app.dependency_overrides[waiting_task_dependency]=waiting_task_service
"""
print(json.dumps(out,ensure_ascii=True))
