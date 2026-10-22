"""Yard visit adapter: every write is one native RRL_YARD_VISIT_API command; reads are one READ ONLY snapshot."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_yard import YardError, YardExpect, YardTransition, wire


def _error(exc: oracledb.DatabaseError) -> YardError:
    number = getattr(exc.args[0], "code", 0)
    if not 20800 <= number <= 20999:
        return YardError("YARD_RESULT_UNKNOWN", 503)  # outcome unknown: repeat the same operation_id
    code = str(exc.args[0]).split("\n", 1)[0].split(":", 1)[-1].strip()
    return YardError(code, 403 if number == 20882 else 409)


class OracleYardVisits:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def visits(self, ware: int, actor: str, active: bool) -> dict[str, Any]:
        try:
            with self.gateway.transaction("TRADECASE yard visits READ ONLY") as cur:
                cur.execute("set transaction read only")
                result = read_oracle_json(cur.callfunc("RRL_YARD_VISIT_API.visits", oracledb.DB_TYPE_CLOB, [ware, actor, 1 if active else 0]))
                return dict(warehouse_id=ware, **result)
        except oracledb.DatabaseError as exc:
            raise _error(exc) from exc

    def _command(self, ware: int, body: dict[str, Any], actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("TRADECASE yard visit command") as cur:
                request = cur.var(oracledb.DB_TYPE_CLOB)
                request.setvalue(0, json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
                result = cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_YARD_VISIT_API.command", [ware, request, actor, result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            raise _error(exc) from exc

    def expect(self, ware: int, body: YardExpect, actor: str) -> dict[str, Any]:
        return self._command(ware, wire(body, action="EXPECT", visit_kind="OUTBOUND"), actor)

    def transition(self, ware: int, visit: int, body: YardTransition, actor: str) -> dict[str, Any]:
        return self._command(ware, wire(body, visit_id=visit), actor)
