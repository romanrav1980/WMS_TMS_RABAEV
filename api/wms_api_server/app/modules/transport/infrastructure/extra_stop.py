"""Extra stop adapter: evaluation and decisions are READ ONLY native reads; a decision is one native RRL_TRADE_EXTRA_STOP_API command."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_extra_stop import ExtraStopCommand, ExtraStopError

MISSING = (942, 4043, 6550)  # the extra-stop migration is not applied here


def _error(exc: oracledb.DatabaseError) -> ExtraStopError:
    number = getattr(exc.args[0], "code", 0)
    if number in MISSING:
        return ExtraStopError("EXTRA_STOP_NOT_AVAILABLE", 503)
    if not 20800 <= number <= 20999:
        return ExtraStopError("EXTRA_STOP_RESULT_UNKNOWN", 503)  # outcome unknown: repeat the same operation_id
    code = str(exc.args[0]).split("\n", 1)[0].split(":", 1)[-1].strip()
    return ExtraStopError(code, 403 if number == 20882 else 404 if code.endswith("_NOT_FOUND") else 409)


class OracleExtraStop:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def _read(self, label: str, name: str, args: list[Any]) -> dict[str, Any]:
        try:
            with self.gateway.transaction(label) as cur:
                cur.execute("set transaction read only")
                return read_oracle_json(cur.callfunc(name, oracledb.DB_TYPE_CLOB, args))
        except oracledb.DatabaseError as exc:
            raise _error(exc) from exc

    def evaluate(self, trip: int, address: str, zone: str, actor: str) -> dict[str, Any]:
        request = json.dumps({"address": address, "zone": zone}, ensure_ascii=False)
        return self._read("Extra stop evaluation READ ONLY", "RRL_TRADE_EXTRA_STOP_API.evaluate", [trip, actor, request])

    def decisions(self, trip: int, actor: str) -> dict[str, Any]:
        return self._read("Extra stop decisions READ ONLY", "RRL_TRADE_EXTRA_STOP_API.decisions", [trip, actor])

    def command(self, trip: int, body: ExtraStopCommand, actor: str) -> dict[str, Any]:
        wire = {**body.model_dump(exclude_none=True), "trip_id": trip}
        try:
            with self.gateway.transaction("Extra stop decision") as cur:
                request = cur.var(oracledb.DB_TYPE_CLOB)
                request.setvalue(0, json.dumps(wire, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
                result = cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_TRADE_EXTRA_STOP_API.command", [request, actor, result])
                receipt = read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            raise _error(exc) from exc
        if not isinstance(receipt, dict) or receipt.get("operation_id") != body.operation_id:
            raise ExtraStopError("EXTRA_STOP_RESULT_UNKNOWN", 503)
        return receipt
