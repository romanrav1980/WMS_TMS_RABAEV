from pathlib import Path
p=Path("api/wms_api_server/app/modules/inventory/contracts_stock.py");s=p.read_text(encoding="utf-8")
if '"INTERWARE_UNLOAD"' not in s:s=s.replace('{"STORE_RETURN_DISPOSE",','{"INTERWARE_UNLOAD", "INTERWARE_RECEIVE", "STORE_RETURN_DISPOSE",',1);p.write_text(s,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");s=p.read_text(encoding="utf-8")
if "from ..contracts_stock import StockCommand" not in s:
 s=s.replace("from .metadata_transactions import receipt_task_metadata","from .metadata_transactions import receipt_task_metadata\nfrom ..contracts_stock import StockCommand\nfrom .stock_posting_uow import StockPosting")
 s=s.replace("def __init__(self, gateway: Any) -> None:","def __init__(self, gateway: Any, posting: StockPosting) -> None:")
 s=s.replace("        self.gateway = gateway","        self.gateway = gateway\n        self.posting = posting",1)
 marker="    def queue(self, ware_id:"
 pos=s.index(marker)
 s=s[:pos]+"""    def receive_action(self, kind: str, operation_id: str, plan_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]:
        if kind not in ("INTERWARE_UNLOAD","INTERWARE_RECEIVE"):
            raise ValueError("Unknown physical interwarehouse action")
        return self.posting.post(StockCommand(operation_id=operation_id,command_type=kind,actor=actor,source={"plan_operation_id":plan_id},lines=(),metadata=metadata))

"""+s[pos:]
 s=s.replace("DECISION_REFERENCE,ACTOR from RRL_INTERWARE_PLAN","DECISION_REFERENCE,p.ACTOR,(select u.OPERATION_ID from RRL_INTERWARE_UNLOAD u where u.PLAN_OPERATION_ID=p.OPERATION_ID) UNLOAD_OPERATION_ID,(select r.OPERATION_ID from RRL_INTERWARE_RECEIPT r where r.PLAN_OPERATION_ID=p.OPERATION_ID) RECEIPT_OPERATION_ID from RRL_INTERWARE_PLAN p")
 p.write_text(s,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py");s=p.read_text(encoding="utf-8")
if "def receive_action(" not in s:s=s.replace("    def queue(","    def receive_action(self, kind: str, operation_id: str, plan_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]: ...\n    def queue(",1);p.write_text(s,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/inventory/public.py");s=p.read_text(encoding="utf-8").replace("return Interwarehouse(gateway)","return Interwarehouse(gateway,StockPosting())");p.write_text(s,encoding="utf-8")
p=Path("db/migrations/2026-10-10_ni061_receiving/002_command.sql");s=p.read_text(encoding="utf-8").replace("where CELL=v_cell and WARE_ID=plan.TARGET_WARE_ID and nvl(BLOCKED_FOR_ACCEPT,0)=0;","where CELL=v_cell and WARE_ID=plan.TARGET_WARE_ID and nvl(BLOCKED_FOR_ACCEPT,0)=0 and BLOCKED_FOR_REMAINS=1 and BLOCKED_FOR_POPOLNENIE=1;")
p.write_text(s,encoding="utf-8")
