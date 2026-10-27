"""Native, journaled status commands for a warehouse dock."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_yard import YardError
from ..contracts_yard_status import YardDockStatusCommand

MISSING = (942, 4043, 6550)


def _error(exc: oracledb.DatabaseError) -> YardError:
    number = getattr(exc.args[0], "code", 0)
    if number in MISSING:
        return YardError("YARD_DOCK_STATUS_NOT_AVAILABLE", 503)
    if not 20800 <= number <= 20999:
        return YardError("YARD_RESULT_UNKNOWN", 503)
    code = str(exc.args[0]).split("\n", 1)[0].split(":", 1)[-1].strip()
    return YardError(code, 403 if number == 20882 else 409)


class OracleYardDockStatus:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def docks(self, ware: int, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("TRADECASE yard dock status READ ONLY") as cur:
                cur.execute("set transaction read only")
                data = read_oracle_json(cur.callfunc("RRL_YARD_DOCK_STATUS_API.docks", oracledb.DB_TYPE_CLOB, [ware, actor]))
                if not isinstance(data, dict) or data.get("warehouse_id") != ware or not isinstance(data.get("docks"), list):
                    raise YardError("YARD_RESULT_UNKNOWN", 503)
                return data
        except oracledb.DatabaseError as exc:
            raise _error(exc) from exc

    def command(self, ware: int, dock: str, body: YardDockStatusCommand, actor: str) -> dict[str, Any]:
        request_body = body.model_dump(mode="json") | {"dock": dock.strip()}
        try:
            with self.gateway.transaction("TRADECASE yard dock status command") as cur:
                request = cur.var(oracledb.DB_TYPE_CLOB)
                request.setvalue(0, json.dumps(request_body, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
                result = cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_YARD_DOCK_STATUS_API.command", [ware, request, actor, result])
                receipt = read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            raise _error(exc) from exc
        if not isinstance(receipt, dict) or receipt.get("operation_id") != body.operation_id:
            raise YardError("YARD_RESULT_UNKNOWN", 503)
        return receipt
