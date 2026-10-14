from pathlib import Path
base=Path("api/wms_api_server/app/modules/inventory/infrastructure")
p=base/"receiving.py";s=p.read_text(encoding="utf-8-sig")
start=s.index("    def _book_pallet(");end=s.index("    def complete(",start)
booking=s[start:end]
booking=booking.replace("emit_event: bool = True, ","")
booking=booking.replace("        if emit_event:\n            self._event(cur, sscc, qty, order[0], None, order[2], 1, actor)\n","")
booking=booking.replace("stock_quantity if stock_quantity is not None else qty","stock_quantity if stock_quantity is not None else qty")
leaf='''"""Receipt metadata staging only; quantities are posted by the stock coordinator."""
from datetime import date
from decimal import Decimal
from typing import Any
import json
import oracledb
from .receiving_marks import ReceivingMarks

class ReceiptBooking:
'''+booking+'''    @staticmethod
    def _text(value: Any) -> str:
        return value.read() if hasattr(value,"read") else value
'''
(base/"receipt_booking.py").write_text(leaf,encoding="utf-8")
s=s[:start]+s[end:]
start=s.index("        from .receipt_commands import receive_command")
end=s.index("    def complete(",start)
s=s[:start]+'''        from .receipt_posting import receive_command
        return receive_command(self.gateway,order_id,payload,actor)

'''+s[end:]
start=s.index('        rows = self.gateway.fetch_all(',s.index("    def complete("))
end=s.index("    def replan(",start)
s=s[:start]+'''        from .task_completion import complete_existing_task
        from ....schemas import WarehouseTaskStatusRequest
        return complete_existing_task(self.gateway,task_id,WarehouseTaskStatusRequest(**scans),actor)

'''+s[end:]
start=s.index("    def _event(");end=s.index("    def _outbox(",start)
s=s[:start]+s[end:]
s=s.replace("    def _text(value) -> str:","    def _text(value: object) -> str:")
p.write_text(s,encoding="utf-8")
p=base/"receipt_commands.py";s=p.read_text(encoding="utf-8-sig")
start=s.index("def receive_command(")
command=s[start:].replace('''    if rows and rows[0]["state"] == "PREPARED":
        return None''','''    if not rows or rows[0]["state"] != "ACTIVE":
        raise StockPostingError("STOCK_RELEASE_NOT_ACTIVE",payload["operation_id"])''')
command=command.replace("def receive_command(gateway, order_id: str, payload: dict, actor: str):","def receive_command(gateway: Any, order_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:")
(base/"receipt_posting.py").write_text('''"""SAP receipt entry point for the sole stock posting coordinator."""
from decimal import Decimal
from typing import Any
from ..contracts_stock import StockCommand,StockPostingError
from .stock_posting_uow import StockPosting

'''+command,encoding="utf-8")
s=s[:start].replace("from ..contracts_stock import StockCommand, StockPostingError\n","").replace("from .stock_posting_uow import StockPosting\n","")
s=s.replace("    from .receiving import Receiving","    from .receipt_booking import ReceiptBooking")
s=s.replace("Receiving(None)._book_pallet","ReceiptBooking()._book_pallet").replace("emit_event=False, bindings=","bindings=")
s=s.replace("from datetime import date","from datetime import date\nfrom typing import Any\nimport oracledb")
s=s.replace("def _text(value):","def _text(value: Any) -> str:")
s=s.replace("def plan_receipt(cursor, document: dict) -> tuple[dict, dict]:","def plan_receipt(cursor: oracledb.Cursor, document: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:")
s=s.replace("def stage_receipt(cursor, document: dict, marks: dict) -> None:","def stage_receipt(cursor: oracledb.Cursor, document: dict[str, Any], marks: dict[str, Any]) -> None:")
p.write_text(s,encoding="utf-8")
