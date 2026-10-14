"""Trip-specific estimated route durations, atomically passed to original ARM generator."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from .trip_edit import trip_error


def route_context(gateway: Any, trip: int, actor: str) -> dict[str, Any]:
    try:
        with gateway.transaction("Current route input READ ONLY") as cur:
            cur.execute("set transaction read only")
            result = cur.var(oracledb.DB_TYPE_CLOB)
            cur.callproc("RRL_TT_ROUTE_API.context", [trip, actor, result])
            return read_oracle_json(result.getvalue())
    except oracledb.DatabaseError as exc:
        raise trip_error(exc) from exc


def apply_route_input(gateway: Any, operation: str, body: dict[str, Any], actor: str) -> dict[str, Any]:
    request = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    try:
        with gateway.transaction("Route estimate and original ARM regeneration") as cur:
            result = cur.var(oracledb.DB_TYPE_CLOB)
            payload = cur.var(oracledb.DB_TYPE_CLOB)
            payload.setvalue(0, request)
            cur.callproc("RRL_TT_ROUTE_API.apply_input", [operation, actor, payload, result])
            return read_oracle_json(result.getvalue())
    except oracledb.DatabaseError as exc:
        raise trip_error(exc) from exc
