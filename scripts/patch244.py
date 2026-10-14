from pathlib import Path
out={}
root=Path("api/wms_api_server/app")
# Capture application sources before editing.
paths=["services/warehouse_task_service.py","services/warehouse_task_domain_sync_service.py","routers/warehouse_tasks.py","modules/inventory/public.py"]
f=Path("db/migrations/2026-10-11_ni081_task_read")
for name in paths:
 p=root/name;out[str(f/("000_before_"+p.name))]=p.read_text(encoding="utf-8")
p=root/"services/warehouse_task_service.py";s=p.read_text(encoding="utf-8").replace("        limit: int = 100,\n    ) -> list[dict[str, Any]]:","        limit: int = 100,\n        scope_warehouse_id: int | None = None,\n        scope_global: bool = True,\n    ) -> list[dict[str, Any]]:",1)
s=s.replace('        conditions = []\n        params:', '        conditions = []\n        params:',1)
s=s.replace('        if status:\n','''        if not scope_global:
            conditions.append("(FROM_WARE_ID=:scope_ware or TO_WARE_ID=:scope_ware)")
            params["scope_ware"]=scope_warehouse_id
        if status:
''',1);out[str(p)]=s
p=root/"services/warehouse_task_domain_sync_service.py";s=p.read_text(encoding="utf-8")
start=s.index("    def list_sync(");prefix=s[:start];tail=s[start:]
tail=tail.replace("        limit: int = 100,\n    ) -> list[dict[str, Any]]:","        limit: int = 100,\n        scope_warehouse_id: int | None = None,\n        scope_global: bool = True,\n    ) -> list[dict[str, Any]]:",1)
tail=tail.replace("        if status:\n",'''        if not scope_global:
            conditions.append("exists(select 1 from RRL_WAREHOUSE_TASK task_scope where task_scope.TASK_ID=RRL_WAREHOUSE_TASK_SYNC.TASK_ID and(task_scope.FROM_WARE_ID=:scope_ware or task_scope.TO_WARE_ID=:scope_ware))")
            params["scope_ware"]=scope_warehouse_id
        if status:
''',1);out[str(p)]=prefix+tail
p=root/"modules/inventory/public.py";s=p.read_text(encoding="utf-8");s+='''

from .contracts_task_read import TaskReadError,TaskViewScope
from .infrastructure.task_read_scope import read_task_snapshot
__all__ += ["TaskReadError","TaskViewScope","read_task_snapshot"]
''';out[str(p)]=s
p=root/"routers/warehouse_tasks.py";s=p.read_text(encoding="utf-8").replace("from fastapi import APIRouter, Depends","from fastapi import APIRouter, Depends, HTTPException",1)
s=s.replace('router = APIRouter(prefix="/api/warehouse-tasks", tags=["warehouse-tasks"])','''from collections.abc import Callable
from typing import TypeVar
from ..transaction_gateway import TransactionGateway
from ..modules.inventory.public import TaskReadError,TaskViewScope,read_task_snapshot

router = APIRouter(prefix="/api/warehouse-tasks", tags=["warehouse-tasks"])
ReadResult=TypeVar("ReadResult")

def _read(user: AdminUser,loader: Callable[[TransactionGateway,TaskViewScope],ReadResult],task_id: int | None=None) -> ReadResult:
    try:
        return read_task_snapshot(WarehouseTaskService().gateway,user.username,loader,task_id)
    except TaskReadError as exc:
        raise HTTPException(exc.status,detail=exc.code) from exc
''',1)
s=s.replace("    return WarehouseTaskService().list_tasks(","    return _read(_user,lambda gateway,scope: WarehouseTaskService(gateway).list_tasks(",1)
anchor="        limit=limit,\n    )";replacement="        limit=limit,scope_warehouse_id=scope.warehouse_id,scope_global=scope.global_admin,\n    ))"
assert anchor in s;s=s.replace(anchor,replacement,1)
s=s.replace("    return WarehouseTaskDomainSyncService().list_sync(","    return _read(_user,lambda gateway,scope: WarehouseTaskDomainSyncService(gateway).list_sync(",1)
assert anchor in s;s=s.replace(anchor,replacement,1)
s=s.replace("return WarehouseTaskService().get_task_or_404(task_id)","return _read(_user,lambda gateway,scope: WarehouseTaskService(gateway).get_task_or_404(task_id),task_id)",1)
s=s.replace("return get_existing_task_progress(WarehouseTaskService().gateway, task_id)","return _read(_user,lambda gateway,scope: get_existing_task_progress(gateway,task_id),task_id)",1)
s=s.replace("sync = WarehouseTaskDomainSyncService().get_task_sync(task_id)","sync = _read(_user,lambda gateway,scope: WarehouseTaskDomainSyncService(gateway).get_task_sync(task_id),task_id)",1)
out[str(p)]=s
import json
print(json.dumps(out,ensure_ascii=True))
