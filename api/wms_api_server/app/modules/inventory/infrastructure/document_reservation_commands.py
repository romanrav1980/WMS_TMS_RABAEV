from __future__ import annotations
from ....oracle_gateway import OracleGateway
from ....transaction_gateway import TransactionGateway
"""Document reservation release uses one Oracle transaction for the complete selected scope."""
from uuid import uuid4
from fastapi import HTTPException
from ..contracts_stock import StockCommand, StockPostingError
from .stock_posting_uow import StockPosting
from .release_boundary import require_active_release


def release_document_reservations(gateway: OracleGateway | TransactionGateway, document_type: str, document_id: int, actor: str,
                                  reason: str, *, only_cancelled: bool = False,
                                  reservation_kind: str | None = None) -> bool:
    require_active_release(gateway,None)
    if document_type not in {"PICK_WAVE", "PICK_PLAN", "PRODUCTION_ORDER"}:
        raise ValueError("Unsupported reservation document")
    operation = "DOC.RELEASE:" + uuid4().hex
    try:
        StockPosting().post(StockCommand(operation_id=operation,
            command_type="DOCUMENT_RELEASE_RESERVATIONS", actor=actor, lines=(),
            source={"document_type": document_type, "document_id": document_id},
            metadata={"reason": reason, "only_cancelled_replenishment": int(only_cancelled),
                      "reservation_kind": reservation_kind}))
    except StockPostingError as exc:
        raise HTTPException(409, detail={"code": exc.code, "operation_id": exc.operation_id,
                                        "oracle_code": exc.oracle_code}) from exc
    return True
