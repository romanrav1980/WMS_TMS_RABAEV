"""Quality exception adapter: reads are one READ ONLY snapshot; each case command is one native RRL_TRADE_QUALITY_CASE_API call;
the quarantine move is the existing MOVE_QUARANTINE posting command (same runner, journal and unknown-outcome rules)."""
import json
from typing import Any, Callable
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_quality_case import QualityCaseCommand, QualityCaseError, QuarantineMove
from ..contracts_stock import StockCommand, StockPostingError

MISSING = (942, 4043, 6550)  # the quality case migration is not applied here
TRANSIENT = {"STOCK_RELEASE_NOT_ACTIVE", "REQUEST_DEADLINE", "LOCK_RETRY_EXHAUSTED", "CONNECTION_UNUSABLE", "RESULT_UNCERTAIN"}


def _error(exc: oracledb.DatabaseError) -> QualityCaseError:
    number = getattr(exc.args[0], "code", 0)
    if number in MISSING:
        return QualityCaseError("QUALITY_NOT_AVAILABLE", 503)
    if not 20800 <= number <= 20999:
        return QualityCaseError("QUALITY_RESULT_UNKNOWN", 503)  # outcome unknown: repeat the same operation_id
    code = str(exc.args[0]).split("\n", 1)[0].split(":", 1)[-1].strip()
    return QualityCaseError(code, 403 if number == 20882 else 404 if code.endswith("_NOT_FOUND") else 409)


class OracleQualityCases:
    def __init__(self, gateway: Any, post: Callable[[StockCommand], dict[str, Any]]) -> None:
        self.gateway, self.post = gateway, post

    def _read(self, label: str, name: str, args: list[Any]) -> dict[str, Any]:
        try:
            with self.gateway.transaction(label) as cur:
                cur.execute("set transaction read only")
                return read_oracle_json(cur.callfunc(name, oracledb.DB_TYPE_CLOB, args))
        except oracledb.DatabaseError as exc:
            raise _error(exc) from exc

    def overview(self, ware: int, actor: str) -> dict[str, Any]:
        return dict(warehouse_id=ware, **self._read("TRADECASE quality exceptions READ ONLY", "RRL_TRADE_QUALITY_CASE_API.overview", [ware, actor]))

    def detail(self, ware: int, case: int, actor: str) -> dict[str, Any]:
        return self._read("TRADECASE quality case READ ONLY", "RRL_TRADE_QUALITY_CASE_API.case_detail", [ware, actor, case])

    def command(self, ware: int, body: QualityCaseCommand, actor: str) -> dict[str, Any]:
        wire = body.model_dump(exclude_none=True)
        try:
            with self.gateway.transaction("TRADECASE quality case command") as cur:
                request = cur.var(oracledb.DB_TYPE_CLOB)
                request.setvalue(0, json.dumps(wire, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
                result = cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_TRADE_QUALITY_CASE_API.command", [ware, request, actor, result])
                receipt = read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            raise _error(exc) from exc
        # A receipt is accepted only for this very operation; anything else is an unknown outcome.
        if not isinstance(receipt, dict) or receipt.get("operation_id") != body.operation_id:
            raise QualityCaseError("QUALITY_RESULT_UNKNOWN", 503)
        return receipt

    def quarantine_move(self, ware: int, body: QuarantineMove, actor: str) -> dict[str, Any]:
        # An open, defect or posted case keeps the pallet in quarantine. This read precedes the posting transaction, so a case
        # opened in between is not seen: the native guard belongs to RRL_TRADE_STOCK_GUARD (root boundary, see RESULT_C0152).
        try:
            with self.gateway.transaction("TRADECASE quality release check READ ONLY") as cur:
                cur.execute("set transaction read only")
                cur.callproc("RRL_TRADE_QUALITY_CASE_API.assert_release", [ware, actor, body.pallet_uid])
        except oracledb.DatabaseError as exc:
            raise _error(exc) from exc
        command = StockCommand(operation_id=body.operation_id, command_type="MOVE_QUARANTINE", actor=actor, lines=(),
                               source={"type": "QUALITY", "warehouse_id": ware, "uid": body.pallet_uid},
                               metadata={"uid": body.pallet_uid, "target_cell": body.target_cell, "quantity": "0", "reason": body.reason})
        try:
            return self.post(command)
        except StockPostingError as exc:
            raise QualityCaseError(exc.code, 503 if exc.code in TRANSIENT else 403 if exc.oracle_code == 20882 else 409) from exc
