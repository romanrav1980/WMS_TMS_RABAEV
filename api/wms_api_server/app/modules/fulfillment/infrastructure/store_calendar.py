"""Existing source-book configuration and date exceptions, native current warehouse authority."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json


def call_calendar(gateway: Any, procedure: str, arguments: list[Any], read_only: bool = False) -> dict[str, Any]:
    try:
        with gateway.transaction("Store delivery calendar native command" if not read_only else "Store calendar READ ONLY") as cur:
            if read_only:
                cur.execute("set transaction read only")
            result = cur.var(oracledb.DB_TYPE_CLOB)
            bound = []
            for value in arguments:
                if isinstance(value, dict):
                    payload = cur.var(oracledb.DB_TYPE_CLOB)
                    payload.setvalue(0, json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
                    bound.append(payload)
                else:
                    bound.append(value)
            cur.callproc(procedure, [*bound, result])
            return read_oracle_json(result.getvalue())
    except oracledb.DatabaseError as exc:
        code = getattr(exc.args[0], "code", 0)
        if code == 20882:
            raise PermissionError("STORE_CAL_CURRENT_WARE_ACTOR_REQUIRED") from exc
        if code in {20886, 1841, 1843, 1858, 1861, 6502, 12899}:
            raise ValueError(str(exc.args[0]).split("\n", 1)[0]) from exc
        raise


def configure_calendar(gateway: Any, warehouse: int, store: str, body: dict[str, Any], actor: str) -> dict[str, Any]:
    return call_calendar(gateway, "RRL_STORE_CALENDAR_API.configure", [warehouse, store, body, actor])


def calendar_context(gateway: Any, warehouse: int, store: str, day: str, actor: str) -> dict[str, Any]:
    return call_calendar(gateway, "RRL_STORE_CALENDAR_API.context", [warehouse, store, day, actor], True)


def set_exception(gateway: Any, operation: str, body: dict[str, Any], actor: str) -> dict[str, Any]:
    return call_calendar(gateway, "RRL_STORE_CALENDAR_API.set_exception", [operation, actor, body])
