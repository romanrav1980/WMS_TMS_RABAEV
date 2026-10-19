"""One native transaction per site change or document; no stock mutation here."""
from hashlib import sha256
import json
from typing import Any

import oracledb

from ...platform.public import read_oracle_json
from ..contracts_tradecase import TradecaseError, TradeEnvelope, TradeSiteSetting


def canonical(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)


def native_error(exc: oracledb.DatabaseError) -> TradecaseError:
    code = getattr(exc.args[0], "code", 0)
    if code in {20851, 20882}:
        return TradecaseError("TRADECASE_ACCESS_DENIED", 403)
    if code == 1403:
        return TradecaseError("TRADECASE_NOT_FOUND", 404)
    if 20900 <= code <= 20999:
        return TradecaseError(str(exc.args[0]).split("\n", 1)[0].split(":", 1)[-1].strip())
    return TradecaseError("TRADECASE_RESULT_UNKNOWN", 503)


class OracleTradecaseDocuments:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def _command(self, procedure: str, warehouse_id: int, actor: str, value: dict[str, Any]) -> dict[str, Any]:
        assert procedure in {"configure", "receive_document"}
        raw = canonical(value)
        if len(raw.encode()) > 1024 * 1024:
            raise TradecaseError("TRADECASE_MESSAGE_TOO_LARGE", 413)
        try:
            with self.gateway.transaction("TRADECASE " + procedure) as cur:
                request = cur.var(oracledb.DB_TYPE_CLOB)
                request.setvalue(0, raw)
                result = cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_TRADE_DOCUMENT_API." + procedure, [warehouse_id, actor, request, result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            raise native_error(exc) from exc

    def configure(self, warehouse_id: int, body: TradeSiteSetting, actor: str) -> dict[str, Any]:
        value = body.model_dump(mode="json")
        value["payload_hash"] = sha256(canonical(value).encode()).hexdigest()
        return self._command("configure", warehouse_id, actor, value)

    def receive(self, body: TradeEnvelope, actor: str) -> dict[str, Any]:
        value = body.model_dump(mode="json")
        value["payload_hash"] = sha256(canonical(value).encode()).hexdigest()
        business = {key: value[key] for key in ("schema_version", "source_id", "warehouse_id", "document_id", "version", "payload")}
        value["business_hash"] = sha256(canonical(business).encode()).hexdigest()
        return self._command("receive_document", body.warehouse_id, actor, value)

    def _read(self, warehouse_id: int, actor: str, mode: str, kind: str = "", key: str = "", limit: int = 1) -> dict[str, Any]:
        try:
            with self.gateway.transaction("TRADECASE bounded " + mode) as cur:
                result = cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_TRADE_DOCUMENT_API.read_documents", [warehouse_id, actor, mode, kind, key, limit, result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            raise native_error(exc) from exc

    def site(self, warehouse_id: int, actor: str) -> dict[str, Any]:
        return self._read(warehouse_id, actor, "SITE")

    def documents(self, warehouse_id: int, kind: str, after: str, limit: int, actor: str) -> dict[str, Any]:
        return self._read(warehouse_id, actor, "LIST", kind, after, limit)

    def document(self, warehouse_id: int, kind: str, external_id: str, actor: str) -> dict[str, Any]:
        return self._read(warehouse_id, actor, "DETAIL", kind, external_id)
