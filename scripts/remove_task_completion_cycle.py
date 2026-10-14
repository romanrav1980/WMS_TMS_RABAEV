from pathlib import Path
base=Path("api/wms_api_server/app")
p=base/"modules/inventory/infrastructure/task_completion.py"
s=p.read_text(encoding="utf-8-sig")
s=s.replace("from decimal import Decimal","from decimal import Decimal\nfrom collections.abc import Callable\nfrom typing import Any, Protocol\nfrom ....oracle_gateway import OracleGateway\nfrom ....schemas import WarehouseTaskStatusRequest")
start=s.index('    if rows and rows[0]["state"] == "PREPARED":')
end=s.index('    metadata =',start)
s=s[:start]+'''    if not rows or rows[0]["state"] != "ACTIVE":
        raise HTTPException(503, detail="STOCK_RELEASE_NOT_ACTIVE")
'''+s[end:]
s=s.replace("def complete_existing_task(gateway, task_id: int, request, actor: str) -> dict:", "def complete_existing_task(gateway: OracleGateway | TransactionGateway, task_id: int, request: WarehouseTaskStatusRequest, actor: str) -> dict[str, Any]:")
s=s.replace("def lock_domain(gateway, task: dict) -> None:", "def lock_domain(gateway: OracleGateway | TransactionGateway, task: dict[str, Any]) -> None:")
s=s.replace('def run_existing_task_action(gateway, task_id: int, action: str, request) -> None:\n    from ....services.warehouse_task_service import WarehouseTaskService', '''class TaskActionHandler(Protocol):
    def get_task_or_404(self, task_id: int) -> dict[str, Any]: ...
    def assign_task(self, task_id: int, request: WarehouseTaskStatusRequest) -> None: ...
    def start_task(self, task_id: int, request: WarehouseTaskStatusRequest) -> None: ...
    def cancel_task(self, task_id: int, request: WarehouseTaskStatusRequest) -> None: ...


def run_existing_task_action(
    gateway: OracleGateway | TransactionGateway, task_id: int, action: str,
    request: WarehouseTaskStatusRequest,
    service_factory: Callable[[TransactionGateway], TaskActionHandler],
) -> None:''')
s=s.replace("service = WarehouseTaskService(bound)", "service = service_factory(bound)")
p.write_text(s,encoding="utf-8")
p=base/"modules/inventory/public.py";s=p.read_text(encoding="utf-8-sig")
s=s.replace("def run_existing_warehouse_task_action(gateway, task_id: int, action: str, request) -> None:", "def run_existing_warehouse_task_action(gateway, task_id: int, action: str, request, service_factory: Callable) -> None:")
s=s.replace("run_existing_task_action(gateway, task_id, action, request)","run_existing_task_action(gateway, task_id, action, request, service_factory)")
p.write_text(s,encoding="utf-8")
p=base/"services/warehouse_task_service.py";s=p.read_text(encoding="utf-8-sig")
for action in ("assign_task","start_task","cancel_task"):
 s=s.replace(f'run_existing_warehouse_task_action(self.gateway, task_id, "{action}", request)',f'run_existing_warehouse_task_action(self.gateway, task_id, "{action}", request, type(self))')
p.write_text(s,encoding="utf-8")
