from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import get_settings
from ..request_context import RequestContext, reset_request_context, set_request_context, update_request_context
from ..services.api_audit_service import (
    ApiAuditService,
    body_digest,
    decode_limited,
    json_dumps,
    redact_headers,
)


class ApiAuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        settings = get_settings()
        if not settings.audit_enabled:
            return await call_next(request)

        audit = ApiAuditService(settings=settings)
        started = time.perf_counter()
        request_id = str(uuid.uuid4())
        context_token = set_request_context(
            RequestContext(
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                query_string=request.url.query,
                client_ip=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
            )
        )
        request_body_bytes = await request.body()
        request_body, request_truncated = decode_limited(
            request_body_bytes,
            settings.audit_max_body_chars,
        )
        headers = redact_headers(dict(request.headers))
        replay_of = _int_header(request.headers.get("x-wms-replay-of"))
        replay_run_id = request.headers.get("x-wms-replay-run-id")
        replayable = 1 if is_replayable(request) else 0

        local_path = audit.append_local(
            {
                "phase": "STARTED",
                "request_id": request_id,
                "replay_of_call_id": replay_of,
                "replay_run_id": replay_run_id,
                "method": request.method,
                "path": request.url.path,
                "query_string": request.url.query,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "request_headers": headers,
                "request_body": request_body,
                "request_body_sha256": body_digest(request_body_bytes),
                "request_body_truncated": request_truncated,
                "replayable": replayable,
            }
        )

        api_call_id = audit.start_call(
            {
                "request_id": request_id,
                "replay_of_call_id": replay_of,
                "replay_run_id": replay_run_id,
                "method": request.method,
                "path": request.url.path,
                "query_string": request.url.query,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "request_headers_json": json_dumps(headers),
                "request_body": request_body,
                "request_body_sha256": body_digest(request_body_bytes),
                "request_body_truncated": request_truncated,
                "replayable": replayable,
                "local_log_path": local_path,
            }
        )
        update_request_context(api_call_id=api_call_id)

        async def receive() -> dict:
            return {"type": "http.request", "body": request_body_bytes, "more_body": False}

        request._receive = receive  # noqa: SLF001 - FastAPI body replay pattern.

        try:
            response = await call_next(request)
            response_body_bytes = b""
            async for chunk in response.body_iterator:
                response_body_bytes += chunk

            if settings.audit_capture_response_body:
                response_body, response_truncated = decode_limited(
                    response_body_bytes,
                    settings.audit_max_body_chars,
                )
            else:
                response_body, response_truncated = "", 0

            duration_ms = int((time.perf_counter() - started) * 1000)
            finish_entry = {
                "response_status": response.status_code,
                "response_headers_json": json_dumps(dict(response.headers)),
                "response_body": response_body,
                "response_body_truncated": response_truncated,
                "error_text": None,
                "status": "DONE" if response.status_code < 500 else "ERROR",
                "duration_ms": duration_ms,
                "local_log_path": local_path,
            }
            audit.finish_call(api_call_id, finish_entry)
            audit.append_local(
                {
                    "phase": "FINISHED",
                    "api_call_id": api_call_id,
                    "request_id": request_id,
                    **finish_entry,
                }
            )

            response_headers = dict(response.headers)
            if api_call_id is not None:
                response_headers["X-WMS-API-Call-Id"] = str(api_call_id)
            response_headers["X-WMS-Request-Id"] = request_id
            return Response(
                content=response_body_bytes,
                status_code=response.status_code,
                headers=response_headers,
                media_type=response.media_type,
                background=response.background,
            )
        except Exception as exc:
            duration_ms = int((time.perf_counter() - started) * 1000)
            finish_entry = {
                "response_status": 500,
                "response_headers_json": "{}",
                "response_body": "",
                "response_body_truncated": 0,
                "error_text": str(exc),
                "status": "ERROR",
                "duration_ms": duration_ms,
                "local_log_path": local_path,
            }
            audit.finish_call(api_call_id, finish_entry)
            audit.append_local(
                {
                    "phase": "FINISHED",
                    "api_call_id": api_call_id,
                    "request_id": request_id,
                    **finish_entry,
                }
            )
            raise
        finally:
            reset_request_context(context_token)


def is_replayable(request: Request) -> bool:
    path = request.url.path
    if path in {"/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"}:
        return False
    if path.startswith("/api/admin/api-calls") or path.startswith("/api/admin/auth"):
        return False
    return request.method.upper() in {"GET", "POST", "PUT", "PATCH", "DELETE"}


def _int_header(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None
