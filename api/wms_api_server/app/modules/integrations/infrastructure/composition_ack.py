"""Order composition adapter (C-0164): one native RRL_TRADE_COMPOSITION_API transaction per report / acknowledgment, a read-only list.
A lost response is safe to repeat: the same composition answers the stored snapshot, the same event the stored receipt. No stock write."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_composition_ack import CompositionAck, CompositionReport, ack_wire
from ..contracts_tradecase import TradecaseError
from .tradecase_documents import native_error


class OracleCompositionAck:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def _call(self, procedure: str, warehouse: int, actor: str, value: dict[str, Any]) -> dict[str, Any]:
        raw = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)
        if len(raw.encode()) > 1024 * 1024:
            raise TradecaseError("TRADECASE_MESSAGE_TOO_LARGE", 413)
        try:
            with self.gateway.transaction("TRADECASE order composition " + procedure) as cur:
                cur.execute("set transaction isolation level serializable")
                request = cur.var(oracledb.DB_TYPE_CLOB)
                request.setvalue(0, raw)
                result = cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_TRADE_COMPOSITION_API." + procedure, [warehouse, actor, request, result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            raise native_error(exc) from exc

    def report(self, body: CompositionReport, actor: str) -> dict[str, Any]:
        return self._call("report", body.warehouse_id, actor, body.model_dump(mode="json"))

    def acknowledge(self, body: CompositionAck, actor: str) -> dict[str, Any]:
        return self._call("acknowledge", body.warehouse_id, actor, ack_wire(body))

    def orders(self, warehouse: int, limit: int, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("TRADECASE order compositions READ ONLY") as cur:
                cur.execute("set transaction read only")
                result = cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_TRADE_COMPOSITION_API.orders", [warehouse, actor, limit, result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            raise native_error(exc) from exc
