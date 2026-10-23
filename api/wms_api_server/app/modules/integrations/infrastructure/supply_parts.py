"""SUPPLY parts adapter (C-0163). Parts/END are stored by RRL_TRADE_SUPPLY_PARTS_API in one native transaction each. A complete
transfer is handed to the existing intake as the same canonical SUPPLY under a deterministic event id, then marked delivered in a
separate transaction: a lost response or restart repeats the hand-over with the same event id, which the intake answers idempotently."""
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_supply_parts import (TradeSupplyPart, TradeSupplyPartsEnd, assembled_event_id, canonical, end_wire, part_wire)
from ..contracts_tradecase import TradecaseError, TradeEnvelope
from .tradecase_documents import OracleTradecaseDocuments, native_error


class OracleSupplyParts:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def _call(self, procedure: str, warehouse: int, actor: str, value: dict[str, Any]) -> dict[str, Any]:
        raw = canonical(value)
        if len(raw.encode()) > 1024 * 1024:
            raise TradecaseError("TRADECASE_MESSAGE_TOO_LARGE", 413)
        try:
            with self.gateway.transaction("TRADECASE supply parts " + procedure) as cur:
                request = cur.var(oracledb.DB_TYPE_CLOB)
                request.setvalue(0, raw)
                result = cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_TRADE_SUPPLY_PARTS_API." + procedure, [warehouse, actor, request, result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            raise native_error(exc) from exc

    def _after(self, state: dict[str, Any], actor: str) -> dict[str, Any]:
        if state.get("status") == "COMPLETE":
            return self.deliver(state["warehouse_id"], state["source_id"], state["transfer_id"], actor)
        return state

    def put_part(self, body: TradeSupplyPart, actor: str) -> dict[str, Any]:
        return self._after(self._call("put_part", body.warehouse_id, actor, part_wire(body)), actor)

    def put_end(self, body: TradeSupplyPartsEnd, actor: str) -> dict[str, Any]:
        return self._after(self._call("put_end", body.warehouse_id, actor, end_wire(body)), actor)

    def deliver(self, warehouse: int, source: str, transfer: str, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("TRADECASE supply parts assembled READ") as cur:
                result = cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_TRADE_SUPPLY_PARTS_API.assembled", [warehouse, actor, source, transfer, result])
                packed = read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            raise native_error(exc) from exc
        state = packed["state"]
        if state["status"] != "COMPLETE":
            return state  # already delivered (or rejected): nothing to hand over again
        event = assembled_event_id(source, warehouse, transfer)
        envelope = TradeEnvelope.model_validate({"schema_version": 1, "event_id": event, "source_id": source, "warehouse_id": warehouse,
                                                 "document_id": state["document_id"], "version": state["version"],
                                                 "occurred_at": packed["end_occurred_at"], "payload": {**packed["header"], "codes": packed["codes"]}})
        try:
            receipt, outcome, reason = OracleTradecaseDocuments(self.gateway).receive(envelope, actor), "DELIVERED", None
        except TradecaseError as exc:
            if exc.status != 409:
                raise  # unknown outcome / access: the transfer stays COMPLETE, the same event id is repeated later
            receipt, outcome, reason = {"status": "REJECTED", "code": exc.code}, "DELIVERY_REJECTED", exc.code
        marked = self._call("mark_delivered", warehouse, actor, {"source_id": source, "transfer_id": transfer, "event_id": event,
                                                                  "outcome": outcome, "reason": reason, "result": receipt})
        return {**marked, "delivery": receipt}

    def transfers(self, warehouse: int, limit: int, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("TRADECASE supply transfers READ ONLY") as cur:
                cur.execute("set transaction read only")
                result = cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_TRADE_SUPPLY_PARTS_API.transfers", [warehouse, actor, limit, result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            raise native_error(exc) from exc
