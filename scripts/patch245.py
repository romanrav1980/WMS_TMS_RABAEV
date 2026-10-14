from pathlib import Path
import json
root=Path("api/wms_api_server/app");out={};f=Path("db/migrations/2026-10-11_ni081_cancel_resource")
for name in["services/warehouse_task_service.py","routers/warehouse_tasks.py","modules/resources/public.py","wiki_dummy"]:
 if name=="wiki_dummy":continue
 p=root/name;out[str(f/("000_before_"+p.name))]=p.read_text(encoding="utf-8")
p=root/"modules/resources/public.py";s=p.read_text(encoding="utf-8");s+='\nfrom .infrastructure.task_cancellation import release_cancelled_task as release_cancelled_warehouse_task_resource\n';out[str(p)]=s
p=root/"services/warehouse_task_service.py";s=p.read_text(encoding="utf-8").replace("from ..oracle_gateway import OracleGateway","from ..oracle_gateway import OracleGateway\nfrom ..transaction_gateway import TransactionGateway",1).replace("def __init__(self, gateway: OracleGateway | None = None)","def __init__(self, gateway: OracleGateway | TransactionGateway | None = None)",1)
old='''        if task.get("status") == "DONE":
            raise HTTPException(status_code=409, detail="Completed task cannot be cancelled.")
        if not getattr(self.gateway, "transaction_bound", False):
            from ..modules.inventory.public import run_existing_warehouse_task_action
            return run_existing_warehouse_task_action(self.gateway, task_id, "cancel_task", request, type(self))
'''
new='''        if not getattr(self.gateway, "transaction_bound", False):
            from ..modules.inventory.public import run_existing_warehouse_task_action
            return run_existing_warehouse_task_action(self.gateway, task_id, "cancel_task", request, type(self))
        if task.get("status") == "DONE":
            raise HTTPException(status_code=409, detail="Completed task cannot be cancelled.")
        if task.get("status") == "CANCELLED":
            return
'''
assert old in s;s=s.replace(old,new,1)
start=s.index("    def cancel_task(");anchor=s.index("        self._sync_wave_replenishment_status(",start)
s=s[:anchor]+'''        from ..modules.resources.public import release_cancelled_warehouse_task_resource
        release_cancelled_warehouse_task_resource(self.gateway,task,request.updated_by or request.assigned_to or "API",request.reason)
'''+s[anchor:];out[str(p)]=s
p=root/"routers/warehouse_tasks.py";s=p.read_text(encoding="utf-8")
start=s.index('def cancel_warehouse_task(');prefix=s[:start];tail=s[start:].replace('require_permission(WAREHOUSE_TASK_EXECUTE_PERMISSION)','require_permission("warehouse_task_edit")',1);out[str(p)]=prefix+tail
print(json.dumps(out,ensure_ascii=True))
