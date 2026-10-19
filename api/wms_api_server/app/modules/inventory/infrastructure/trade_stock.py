"""Attribute capture preserves the current native unit identity and quantity."""
from hashlib import sha256
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_trade_stock import TradeCellPolicy, TradeOwnerGrant, TradeStockBind, TradeStockError
from ..domain.mark_identity import canonical_mark
from ..domain.pallet_identifiers import normalize_receipt_identifier


class OracleTradeStock:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def _call(self, warehouse_id: int, actor: str, command: str, payload: dict[str, Any]) -> dict[str, Any]:
        raw = json.dumps(dict(payload, command_type=command), sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False)
        value = dict(payload, command_type=command, payload_hash=sha256(raw.encode()).hexdigest())
        try:
            with self.gateway.transaction("TRADECASE stock " + command) as cur:
                hints: list[dict[str, str]] = []
                if command == "BIND":
                    cur.execute("select 1 from RRL_TRADE_STOCK_COMMAND where OPERATION_ID=:id", id=payload["operation_id"])
                    if cur.fetchone() is None:
                        hints = self._codes(cur, warehouse_id, actor, payload["supply_id"])
                request = cur.var(oracledb.DB_TYPE_CLOB)
                request.setvalue(0, json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")))
                codes = cur.var(oracledb.DB_TYPE_CLOB)
                codes.setvalue(0, json.dumps(hints))
                result = cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_TRADE_STOCK_API.execute_command", [warehouse_id, actor, request, codes, result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            number = getattr(exc.args[0], "code", 0)
            status = 403 if number in {20851, 20882} else 404 if number == 1403 else 409 if 20900 <= number <= 20999 else 503
            code = str(exc.args[0]).split("\n", 1)[0].split(":", 1)[-1].strip() if status != 503 else "TRADE_STOCK_RESULT_UNKNOWN"
            raise TradeStockError(code, status) from exc
        except ValueError as exc:
            raise TradeStockError(str(exc), 422) from exc

    def _codes(self, cur: Any, warehouse_id: int, actor: str, supply_id: str) -> list[dict[str, str]]:
        cur.execute("select RRL_ACCESS_API.allowed(:actor,'tradecase_stock_bind','WAREHOUSE',:ware) from dual",
                    actor=actor, ware=str(warehouse_id))
        if cur.fetchone()[0] != 1:
            raise TradeStockError("ACCESS_DENIED", 403)
        cur.execute("""select d.BODY_JSON from RRL_TRADE_DOCUMENT d where d.WARE_ID=:ware
            and d.ENTITY_TYPE='SUPPLY' and d.EXTERNAL_ID=:id and d.STATUS='ACCEPTED'""", ware=warehouse_id, id=supply_id)
        row = cur.fetchone()
        if row is None:
            raise TradeStockError("TRADE_SUPPLY_NOT_FOUND", 404)
        body = read_oracle_json(row[0])
        cur.execute("select nvl(f.GTIN,a.BARCODE_SHT) from RRL_ARTICULS a left join RRL_FINISHED_GOODS_SKU f on f.ARTICUL=a.ACTICUL where a.ACTICUL=:article", article=body["wms_article_id"])
        article = cur.fetchone()
        if article is None:
            raise TradeStockError("TRADE_ARTICLE_MAPPING_REQUIRED")
        gtin = str(article[0]).zfill(14)
        result = [{"system_code": item["system_code"], "code_hash": sha256(canonical_mark(item["system_code"], item["profile_code"], item["code"], gtin)["identity"].encode()).hexdigest()}
                  for item in body["codes"]]
        if len({(item["system_code"], item["code_hash"]) for item in result}) != len(result):
            raise ValueError("DUPLICATE_SUPPLY_CODE")
        return result

    def bind(self, warehouse_id: int, body: TradeStockBind, actor: str) -> dict[str, Any]:
        value = body.model_dump(mode="json")
        try:
            value["scanned_pallet"] = normalize_receipt_identifier(value["scanned_pallet"])
        except ValueError as exc:
            raise TradeStockError(str(exc), 422) from exc
        return self._call(warehouse_id, actor, "BIND", value)

    def cell(self, warehouse_id: int, cell: str, body: TradeCellPolicy, actor: str) -> dict[str, Any]:
        return self._call(warehouse_id, actor, "CELL", dict(body.model_dump(mode="json"), cell=cell))

    def grant(self, warehouse_id: int, body: TradeOwnerGrant, actor: str) -> dict[str, Any]:
        return self._call(warehouse_id, actor, "GRANT", body.model_dump(mode="json"))

    def view(self, warehouse_id: int, after: str, limit: int, actor: str) -> dict[str, Any]:
        return self._call(warehouse_id, actor, "VIEW", {"after": after, "limit": limit})
