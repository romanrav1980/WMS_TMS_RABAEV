"""Expose posting outcomes consistently to all existing API command callers."""
from fastapi.responses import JSONResponse
from ..contracts_stock import StockPostingError

UNCERTAIN = {"RESULT_UNCERTAIN", "REQUEST_DEADLINE", "LOCK_RETRY_EXHAUSTED",
    "CONNECTION_UNUSABLE", "STOCK_RELEASE_NOT_ACTIVE", "POSTED_CONNECTION_RESET_FAILED"}
CONFLICT = {"OPERATION_CONTENT_CONFLICT"}


def install_stock_error_handlers(app):
    async def posting_error(_request, error: StockPostingError):
        uncertain = error.code in UNCERTAIN or error.oracle_code in (20891, 20892, 20893)
        conflict = error.code in CONFLICT or error.oracle_code in (20872, 20873)
        status = 503 if uncertain else 403 if error.oracle_code == 20882 else 409
        return JSONResponse(status_code=status, content={"detail": {
            "code": error.code, "operation_id": error.operation_id, "oracle_code": error.oracle_code,
            "outcome_confirmed": not (uncertain or conflict),
            "retry_same_operation_id": uncertain,
            "operation_id_conflict": conflict,
        }})
    app.add_exception_handler(StockPostingError, posting_error)
