"""Typed manual transfer command; no caller-supplied SQL or lock plan."""
from typing import Any, Protocol
from ..contracts_stock import StockCommand, StockLine


class StockPostingPort(Protocol):
    def post(self, command: StockCommand) -> dict[str, Any]: ...


class ManualStockMove:
    def __init__(self, posting: StockPostingPort) -> None:
        self.posting = posting

    def execute(self, operation_id: str, actor: str, warehouse_id: int,
                reason: str, lines: tuple[StockLine, ...], *, compatibility: bool = False) -> dict[str, Any]:
        if warehouse_id < 1 or not reason.strip() or len(reason) > 1000:
            raise ValueError("Warehouse and an explicit transfer reason required")
        if any(line.source_cell == line.target_cell for line in lines):
            raise ValueError("Source and target must differ")
        if any(line.reservation_action != "NONE" or line.reservation_id is not None
               or line.target_uid not in (None, line.uid) for line in lines):
            raise ValueError("A dedicated handler is required for reservation or pallet splitting")
        return self.posting.post(StockCommand(
            operation_id=operation_id, command_type="COMPAT_MANUAL_MOVE" if compatibility else "MANUAL_MOVE", actor=actor,
            lines=lines, source={"type": "MANUAL", "warehouse_id": warehouse_id, "reason": reason},
        ))


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
