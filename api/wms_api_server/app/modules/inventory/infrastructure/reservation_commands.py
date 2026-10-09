"""Explicit reservation commands; a single database-wide switch selects the cutover."""
from decimal import Decimal
from fastapi import HTTPException
from ..contracts_stock import StockCommand, StockPostingError
from .stock_posting_uow import StockPosting


def post_reservation(gateway, action: str, request, actor: str | None, reservation_id: int | None = None):
    rows = gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
    if rows and rows[0]["state"] == "PREPARED":
        return None
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
        code = 503 if exc.code in {"STOCK_RELEASE_NOT_ACTIVE", "REQUEST_DEADLINE",
                                  "CONNECTION_UNUSABLE", "LOCK_RETRY_EXHAUSTED"} else 409
        raise HTTPException(code, detail={"code": exc.code, "operation_id": exc.operation_id,
                                         "oracle_code": exc.oracle_code}) from exc
