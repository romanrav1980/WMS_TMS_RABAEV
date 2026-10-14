from __future__ import annotations
from ....oracle_gateway import OracleGateway
from ....transaction_gateway import TransactionGateway
from typing import Any
from ..contracts_case_short import CasePickShortDecisionRequest
"""Existing shortage approval enters the same atomic posting transaction."""
from ..contracts_stock import StockCommand
from .stock_posting_uow import StockPosting
from .release_boundary import require_active_release


def post_short_approval(gateway: OracleGateway | TransactionGateway, short_id: int, request: CasePickShortDecisionRequest) -> dict[str, Any]:
    require_active_release(gateway,request.operation_id)
    if short_id < 1 or not request.actor:
        raise ValueError("Shortage ID and authenticated actor required")
    return StockPosting().post(StockCommand(
        operation_id=request.operation_id or "CASE.SHORT.APPROVE:" + str(short_id),
        command_type="CASE_SHORT_APPROVE", actor=request.actor, lines=(),
        source={"short_id": short_id}, metadata={"reason": request.reason_text, **({"decision": "RESTORE"} if request.decision == "RESTORE" else
            {"decision": "WEIGHT_TOLERANCE", "expected_weight_policy_version": request.expected_weight_policy_version,
             "expected_content_version": request.expected_content_version, "expected_order_weight_signature": request.expected_order_weight_signature}
            if request.decision == "WEIGHT_TOLERANCE" else {})}))
