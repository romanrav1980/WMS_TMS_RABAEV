"""Enter the stock coordinator before reading mutable MES document state."""
from fastapi import HTTPException
from ..contracts_stock import StockCommand, StockPostingError
from .stock_posting_uow import StockPosting


def release_supply(gateway, order_id: int, request):
    rows = gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
    if rows and rows[0]["state"] == "PREPARED":
        return None
    if not request.operation_id:
        raise HTTPException(422, detail={"code": "OPERATION_ID_REQUIRED"})
    try:
        result = StockPosting().post(StockCommand(
            operation_id=request.operation_id, command_type="MES_RELEASE_TO_PRODUCTION",
            actor=request.created_by, lines=(), source={"production_order_id": order_id},
            metadata={"to_cell": request.to_cell, "to_ware_id": request.to_ware_id,
                      "allow_partial": int(request.allow_partial or 0)},
        ))
    except StockPostingError as exc:
        uncertain = exc.code in {"RESULT_UNCERTAIN", "STOCK_RELEASE_NOT_ACTIVE", "REQUEST_DEADLINE",
                                 "CONNECTION_UNUSABLE", "LOCK_RETRY_EXHAUSTED"}
        raise HTTPException(503 if uncertain else 409, detail={
            "code": exc.code, "operation_id": exc.operation_id,
            "oracle_code": exc.oracle_code, "outcome_confirmed": not uncertain,
        }) from exc
    return {"status": "ok", "production_order_id": order_id,
            "created_task_count": result["task_count"], **result}
