"""Keep receipt reversal API behind an application port and composition-root factory."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];files={}
def edit(path,old,new):
 text=files.get(path,(ROOT/path).read_text(encoding="utf-8"))
 if text.count(old)!=1:raise RuntimeError("Missing unique anchor: "+path)
 files[path]=text.replace(old,new,1)
path="api/wms_api_server/app/modules/inventory/application/stock_commands.py"
text=(ROOT/path).read_text(encoding="utf-8")
files[path]=text+"""

class ReceiptReverse:
    def __init__(self, posting: StockPostingPort) -> None:
        self.posting = posting

    def execute(self, operation_id: str, actor: str, document_id: int, reason: str) -> dict[str, Any]:
        if document_id < 1 or not reason.strip() or len(reason) > 1000:
            raise ValueError("Receipt document and explicit reversal reason required")
        return self.posting.post(StockCommand(
            operation_id=operation_id, command_type="RECEIPT_REVERSE", actor=actor,
            lines=(), source={"receipt_document_id": document_id}, metadata={"reason": reason},
        ))
"""
path="api/wms_api_server/app/modules/inventory/api/stock_command_routes.py"
edit(path,"from ..application.stock_commands import ManualStockMove","from ..application.stock_commands import ManualStockMove, ReceiptReverse")
edit(path,"class ReceiptReverseRequest(BaseModel):","""def receipt_reverse_service() -> ReceiptReverse:
    raise RuntimeError("Receipt reversal service not wired")


class ReceiptReverseRequest(BaseModel):""")
edit(path,"""    user: AdminUser = Depends(require_permission("stock_receipt_reverse")),
) -> dict[str, Any]:
    from ..contracts_stock import StockCommand
    from ..infrastructure.stock_posting_uow import StockPosting""","""    user: AdminUser = Depends(require_permission("stock_receipt_reverse")),
    service: ReceiptReverse = Depends(receipt_reverse_service),
) -> dict[str, Any]:""")
edit(path,"""        return StockPosting().post(StockCommand(
            operation_id=request.operation_id, command_type="RECEIPT_REVERSE",
            actor=user.username, lines=(), source={"receipt_document_id": document_id},
            metadata={"reason": request.reason},
        ))
    except StockPostingError as exc:""","""        return service.execute(request.operation_id, user.username, document_id, request.reason)
    except ValueError as exc:
        raise HTTPException(422, detail={"code": "COMMAND_INVALID", "message": str(exc)}) from exc
    except StockPostingError as exc:""")
path="api/wms_api_server/app/modules/inventory/public.py"
text=(ROOT/path).read_text(encoding="utf-8")
files[path]=text+"""

from .application.stock_commands import ReceiptReverse
from .api.stock_command_routes import receipt_reverse_service


def build_receipt_reverse_service() -> ReceiptReverse:
    return ReceiptReverse(build_stock_posting_service())


__all__.extend(["receipt_reverse_service", "build_receipt_reverse_service"])
"""
path="api/wms_api_server/app/main.py"
edit(path,"app.dependency_overrides[inventory_receiving.manual_stock_move_service] = inventory_receiving.build_manual_stock_move_service",
 "app.dependency_overrides[inventory_receiving.manual_stock_move_service] = inventory_receiving.build_manual_stock_move_service\napp.dependency_overrides[inventory_receiving.receipt_reverse_service] = inventory_receiving.build_receipt_reverse_service")
path="wiki-raw/wms_admin_ui_reference/receipt-reversal.js"
edit(path,'      const saved = storageKey && localStorage.getItem(storageKey);',
 '      let saved = false;\n      try { saved = Boolean(storageKey && localStorage.getItem(storageKey)); } catch (_) { /* No request starts without durable intent. */ }')
print(json.dumps(files,ensure_ascii=True))
