"""Use the existing return transaction; native guards preserve completed history."""
from typing import Any
from ..contracts_case_empty import CaseEmptyInput
from ..contracts_stock import StockCommand
from .stock_posting_uow import StockPosting


class CaseEmpty:
    def dispose(self, task: int, body: CaseEmptyInput, actor: str) -> dict[str, Any]:
        return StockPosting().post(StockCommand(
            operation_id=body.operation_id, command_type="CASE_CARRIER_RETURN", actor=actor,
            lines=(), source={"case_task_id": task}, metadata={
                "expected_content_version": body.expected_content_version,
                "scan_container": body.scan_container, "reason": body.reason,
                "allow_empty": True, "empty_disposition": "ACCEPTED_SHORT", "destinations": {},
            }))
