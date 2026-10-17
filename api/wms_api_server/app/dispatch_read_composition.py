"""Transport read failures have a bounded public contract without Oracle diagnostics."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .modules.transport.public import DispatchReadError


def register_dispatch_read_errors(app: FastAPI) -> None:
    async def handle_error(request: Request, error: DispatchReadError) -> JSONResponse:
        return JSONResponse(status_code=error.status, content={"detail": {"code": error.code}})
    app.add_exception_handler(DispatchReadError, handle_error)
