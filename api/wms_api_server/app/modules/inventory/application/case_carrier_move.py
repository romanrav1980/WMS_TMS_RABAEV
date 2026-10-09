"""One explicit command for moving every lot of a CASE carrier."""
from .stock_commands import StockPostingPort
from ..contracts_stock import StockCommand


class CaseCarrierMove:
    def __init__(self, posting: StockPostingPort) -> None:
        self.posting = posting

    def execute(self, operation_id: str, actor: str, task_id: int, carrier: str,
                target_cell: str, expected_version: int) -> dict:
        if task_id < 1 or not carrier or not target_cell or expected_version < 0:
            raise ValueError("Carrier, destination and observed content version required")
        return self.posting.post(StockCommand(operation_id=operation_id, command_type="CASE_CARRIER_MOVE",
            actor=actor, lines=(), source={"case_task_id": task_id},
            metadata={"scan_container": carrier, "target_cell": target_cell,
                "scanned_to_cell": target_cell, "expected_content_version": expected_version}))
