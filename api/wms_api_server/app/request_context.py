from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class RequestContext:
    request_id: str | None = None
    api_call_id: int | None = None
    method: str | None = None
    path: str | None = None
    query_string: str | None = None
    client_ip: str | None = None
    user_agent: str | None = None


_request_context: ContextVar[RequestContext | None] = ContextVar("wms_request_context", default=None)


def set_request_context(context: RequestContext) -> Token[RequestContext | None]:
    return _request_context.set(context)


def update_request_context(**changes) -> None:
    current = _request_context.get()
    if current is None:
        return
    _request_context.set(replace(current, **changes))


def reset_request_context(token: Token[RequestContext | None]) -> None:
    _request_context.reset(token)


def get_request_context() -> RequestContext | None:
    return _request_context.get()
