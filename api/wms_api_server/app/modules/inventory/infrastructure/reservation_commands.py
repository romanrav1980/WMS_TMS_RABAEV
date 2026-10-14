from __future__ import annotations
from ....oracle_gateway import OracleGateway
from ....transaction_gateway import TransactionGateway
from typing import Any
from ....schemas import StockReservationCreateRequest, StockReservationPromoteRequest, StockReservationStatusRequest
"""Explicit reservation commands; a single database-wide switch selects the cutover."""
from decimal import Decimal
from fastapi import HTTPException
from ..contracts_stock import StockCommand, StockPostingError
from .stock_posting_uow import StockPosting
from .release_boundary import require_active_release


def post_reservation(gateway: OracleGateway | TransactionGateway, action: str, request: StockReservationCreateRequest | StockReservationPromoteRequest | StockReservationStatusRequest, actor: str | None, reservation_id: int | None = None) -> dict[str, Any]:
    require_active_release(gateway,request.operation_id)
    if not actor:
        raise ValueError("Authenticated reservation actor required")
    metadata = request.model_dump(mode="json", exclude={"created_by", "updated_by", "operation_id", "unit_keys"})
    if getattr(request, "qty", None) is not None:
        metadata["qty"] = format(Decimal(str(request.qty)), "f")
    operation = request.operation_id
    if not operation:
        if action in {"RELEASE", "CANCEL", "CONSUME"}:
            operation = f"RESERVATION.{action}:{reservation_id}"
        else:
            raise ValueError("operation_id required for reservation creation/promotion")
    try:
        return StockPosting().post(StockCommand(
            operation_id=operation, command_type="RESERVATION_" + action, actor=actor, lines=(),
            source={"type": "STOCK_RESERVATION", "reservation_id": reservation_id},
            units=tuple(request.unit_keys), metadata=metadata,
        ))
    except StockPostingError as exc:
        uncertain = exc.code in {"RESULT_UNCERTAIN","STOCK_RELEASE_NOT_ACTIVE", "REQUEST_DEADLINE",
                                  "CONNECTION_UNUSABLE", "LOCK_RETRY_EXHAUSTED"}
        raise HTTPException(503 if uncertain else 409,
            detail={"code": exc.code, "operation_id": exc.operation_id,"oracle_code": exc.oracle_code,
                    "outcome_confirmed":not uncertain,"retry_same_operation_id":uncertain}) from exc
