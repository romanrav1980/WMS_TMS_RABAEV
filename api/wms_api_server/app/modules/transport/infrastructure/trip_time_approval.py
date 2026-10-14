"""Immutable approval of explicit region for the existing planned ARM dates."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from .trip_edit import trip_error

def read_time_context(cur: Any, trip: int, actor: str) -> dict[str, Any]:
    result = cur.var(oracledb.DB_TYPE_CLOB)
    cur.callproc("RRL_TT_TIME_API.context", [trip, actor, result])
    return read_oracle_json(result.getvalue())

def time_context(gateway: Any, trip: int, actor: str) -> dict[str, Any]:
    try:
        with gateway.transaction("Original ARM approval context READ ONLY") as cur:
            cur.execute("set transaction read only")
            return read_time_context(cur, trip, actor)
    except oracledb.DatabaseError as exc:
        raise trip_error(exc) from exc

def approve_time(gateway: Any, operation: str, body: dict[str, Any], actor: str) -> dict[str, Any]:
    request = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    if len(request) > 2000:
        from ..contracts_plan import TransportPlanError
        raise TransportPlanError("TT_TIME_REQUEST_BOUND", "Сократите основание", 422)
    try:
        with gateway.transaction("Approve original ARM region atomically") as cur:
            result = cur.var(oracledb.DB_TYPE_CLOB)
            request_bind = cur.var(oracledb.DB_TYPE_CLOB)
            request_bind.setvalue(0, request)
            cur.callproc("RRL_TT_TIME_API.approve", [operation, actor, request_bind, result])
            return read_oracle_json(result.getvalue())
    except oracledb.DatabaseError as exc:
        raise trip_error(exc) from exc
