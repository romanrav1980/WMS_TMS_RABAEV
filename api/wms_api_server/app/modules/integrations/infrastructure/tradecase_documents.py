"""One native transaction per site change or document; no stock mutation here."""
from hashlib import sha256
from decimal import Decimal
import json
from typing import Any

import oracledb

from ...platform.public import read_oracle_json
from ..contracts_tradecase import TradecaseError, TradeEnvelope, TradeSiteSetting
from ..domain.order_units import REGISTRY_UNIT, normalize_line
from .order_unit_registry import article_conversions


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

    def _command(self, procedure: str, warehouse_id: int, actor: str, value: dict[str, Any], prepare: Any = None) -> dict[str, Any]:
        assert procedure in {"configure", "receive_document"}
        try:
            with self.gateway.transaction("TRADECASE " + procedure) as cur:
                if prepare is not None:
                    value = prepare(cur, value)  # same transaction as the native command
                raw = canonical(value)
                if len(raw.encode()) > 1024 * 1024:
                    raise TradecaseError("TRADECASE_MESSAGE_TOO_LARGE", 413)
                request = cur.var(oracledb.DB_TYPE_CLOB)
                request.setvalue(0, raw)
                result = cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_TRADE_DOCUMENT_API." + procedure, [warehouse_id, actor, request, result])
                response = read_oracle_json(result.getvalue())
                if value.get("payload", {}).get("entity_type") == "ORDER" and response.get("status") != "REJECTED":
                    # A competing identical delivery may have won with an earlier SKU snapshot.
                    # Return its persisted normalization, never this attempt's discarded calculation.
                    cur.execute("select REQUEST_JSON from RRL_TRADE_MESSAGE where WARE_ID=:w and SOURCE_ID=:s and EVENT_ID=:e",
                                w=warehouse_id, s=value["source_id"], e=value["event_id"])
                    persisted = cur.fetchone()
                    if persisted is None:
                        raise TradecaseError("TRADECASE_RESULT_UNKNOWN", 503)
                    value = read_oracle_json(persisted[0])
            if response.get("status") == "REJECTED":
                raise TradecaseError(response["code"], 409)
            lines = [x.get("normalization") for x in value.get("payload", {}).get("lines", []) if isinstance(x, dict)]
            if any(lines):  # derived from the stored body, so an exact replay returns the same line outcome
                response["line_results"] = []
                for line in value["payload"]["lines"]:
                    outcome = line.get("normalization") or dict(status="UNCHANGED", error_code=None, integration_error=False,
                                                                executable=Decimal(line["quantity"]) > 0)
                    response["line_results"].append(dict(line_id=line["line_id"], quantity=line["quantity"], uom=line["uom"],
                        **{key: outcome[key] for key in ("status", "error_code", "integration_error", "executable")}))
                response["loaded_with_integration_error"] = response.get("status") == "ACCEPTED" and any(line["integration_error"] for line in response["line_results"])
            return response
        except oracledb.DatabaseError as exc:
            raise native_error(exc) from exc

    def _normalize_order(self, cur: Any, value: dict[str, Any]) -> dict[str, Any]:
        """C-0175: an exact replay goes to the native command with its stored request (never renormalized); a new ORDER gets each line
        normalized once from the current SKU setting and the article's published coefficients."""
        cur.execute("select PAYLOAD_HASH,REQUEST_JSON from RRL_TRADE_MESSAGE where WARE_ID=:w and SOURCE_ID=:s and EVENT_ID=:e",
                    w=value["warehouse_id"], s=value["source_id"], e=value["event_id"])
        stored = cur.fetchone()
        if stored is not None:
            return read_oracle_json(stored[1]) if stored[0] == value["payload_hash"] else value
        if value["payload"].get("order_kind") == "BUYOUT":
            return value  # a buyout basis stays in base pieces; it is not a shipment line
        requested_units: dict[str, set[str]] = {}
        for line in value["payload"]["lines"]:
            if line["uom"] in REGISTRY_UNIT:
                requested_units.setdefault(line["sku_id"], set()).add(REGISTRY_UNIT[line["uom"]])
        sku_rows, registries = {}, {}
        for line in value["payload"]["lines"]:
            sku_id = line["sku_id"]
            if sku_id not in sku_rows:
                cur.execute("select BODY_JSON,VERSION_NO from RRL_TRADE_DOCUMENT where WARE_ID=:w and ENTITY_TYPE='SKU' and EXTERNAL_ID=:k and STATUS='ACCEPTED'",
                            w=value["warehouse_id"], k=sku_id)
                sku_rows[sku_id] = cur.fetchone()
            row = sku_rows[sku_id]
            sku = read_oracle_json(row[0]) if row else {}
            if row is None and line["uom"] in ("EA", "BOX"):
                continue  # the current EA/BOX contract; the native document intake waits for the SKU as before
            setting = sku.get("processing_uom")
            if setting is None and line["uom"] in ("EA", "BOX"):
                continue  # no single processing unit configured: unchanged
            units = requested_units.get(sku_id, set()) | ({REGISTRY_UNIT[setting]} if setting in REGISTRY_UNIT else set())
            if sku_id not in registries:
                registries[sku_id] = article_conversions(cur, sku["wms_article_id"], units) if sku.get("wms_article_id") else {}
            conversions = registries[sku_id]
            result = normalize_line(Decimal(line["quantity"]), line["uom"], setting,
                                    Decimal(str(sku["processing_step"])) if sku.get("processing_step") is not None else None,
                                    sku.get("round_to_processing_unit") is not False, conversions)
            if row is None:
                result.update(status="SKU_SETTINGS_MISSING", error_code="ORDER_UNIT_SKU_SETTINGS_MISSING", quantity=None, uom=None, executable=False, integration_error=True)
            result.update(sku_version=int(row[1]) if row else None, processing_step=sku.get("processing_step"), round_to_processing_unit=sku.get("round_to_processing_unit"))
            line["normalization"] = result
            line["quantity"] = result["quantity"] if result["executable"] else "0"
            line["uom"] = result["uom"] or line["uom"]
        return value

    def configure(self, warehouse_id: int, body: TradeSiteSetting, actor: str) -> dict[str, Any]:
        value = body.model_dump(mode="json")
        value["payload_hash"] = sha256(canonical(value).encode()).hexdigest()
        return self._command("configure", warehouse_id, actor, value)

    def receive(self, body: TradeEnvelope, actor: str) -> dict[str, Any]:
        value = body.model_dump(mode="json")
        # Additive optional mappings must not change the hash of an older unchanged message.
        for key in ("wms_article_id", "wms_customer_id", "buyout_mode", "processing_uom", "processing_step", "round_to_processing_unit"):
            if value["payload"].get(key) is None:
                value["payload"].pop(key, None)
        value["payload_hash"] = sha256(canonical(value).encode()).hexdigest()
        business = {key: value[key] for key in ("schema_version", "source_id", "warehouse_id", "document_id", "version", "payload")}
        value["business_hash"] = sha256(canonical(business).encode()).hexdigest()
        if value["payload"].get("entity_type") == "ORDER":
            return self._command("receive_document", body.warehouse_id, actor, value, prepare=self._normalize_order)
        return self._command("receive_document", body.warehouse_id, actor, value)

    def retry(self, warehouse_id: int, event_id: str, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("TRADECASE retry deferred document") as cur:
                result = cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_TRADE_DOCUMENT_API.retry_document", [warehouse_id, actor, event_id, result])
                response = read_oracle_json(result.getvalue())
            # A business rejection is committed with its journal/outbox before returning HTTP 409.
            if response.get("status") == "REJECTED":
                raise TradecaseError(response["code"], 409)
            return response
        except oracledb.DatabaseError as exc:
            raise native_error(exc) from exc

    def _read(self, warehouse_id: int, actor: str, mode: str, kind: str = "", key: str = "", limit: int = 1) -> dict[str, Any]:
        try:
            with self.gateway.transaction("TRADECASE bounded " + mode) as cur:
                if mode == "DETAIL" and kind == "ORDER":
                    cur.execute("set transaction read only")
                result = cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_TRADE_DOCUMENT_API.read_documents", [warehouse_id, actor, mode, kind, key, limit, result])
                card = read_oracle_json(result.getvalue())
                if mode == "DETAIL" and kind == "ORDER" and card["payload"].get("order_kind") != "BUYOUT":
                    card["execution"] = order_execution(cur, warehouse_id, card)
                return card
        except oracledb.DatabaseError as exc:
            raise native_error(exc) from exc

    def site(self, warehouse_id: int, actor: str) -> dict[str, Any]:
        return self._read(warehouse_id, actor, "SITE")

    def documents(self, warehouse_id: int, kind: str, after: str, limit: int, actor: str) -> dict[str, Any]:
        return self._read(warehouse_id, actor, "LIST", kind, after, limit)

    def document(self, warehouse_id: int, kind: str, external_id: str, actor: str) -> dict[str, Any]:
        return self._read(warehouse_id, actor, "DETAIL", kind, external_id)

    def messages(self, warehouse_id: int, after: str, limit: int, actor: str) -> dict[str, Any]:
        return self._read(warehouse_id, actor, "MESSAGES", key=after, limit=limit)

    def message(self, warehouse_id: int, event_id: str, actor: str) -> dict[str, Any]:
        return self._read(warehouse_id, actor, "MESSAGE", key=event_id)

    def need(self,warehouse_id:int,key:str,max_age:int,actor:str)->dict[str,Any]:
        from .trade_need import need_preview
        return need_preview(self.gateway,warehouse_id,key,max_age,actor)


def order_execution(cursor: Any, warehouse: int, card: dict[str, Any]) -> dict[str, Any]:
    """Document read projection; called only after native warehouse/document authorization, in the same RO snapshot.

    Fulfillment compositions remain the quantity authority. Active load links classify each fulfillment once,
    including nested loads; old unloaded facts never increase the current loaded quantity.
    """
    cursor.execute("""select /* TRADE_ORDER_EXECUTION_LINES */ ol.SKU_ID,cr.ARTICUL,
        json_value(sd.BODY_JSON,'$.title'),json_value(sd.BODY_JSON,'$.units_per_box' returning number),
        tl.DOCUMENT_VERSION,ol.EXTERNAL_LINE_ID
        from RRL_TRADE_ORDER_LINK tl
        join RRL_TRADE_ORDER_LINE ol on ol.CUSTOMER_ORDER_ID=tl.CUSTOMER_ORDER_ID
        join RRL_CUSTOMER_ORDER_ROW cr on cr.CUSTOMER_ORDER_ROW_ID=ol.CUSTOMER_ORDER_ROW_ID
        left join RRL_TRADE_DOCUMENT sd on sd.WARE_ID=tl.WARE_ID and sd.ENTITY_TYPE='SKU'
            and sd.EXTERNAL_ID=ol.SKU_ID and sd.VERSION_NO=ol.SKU_VERSION
        where tl.WARE_ID=:warehouse and tl.EXTERNAL_ID=:order_id
        order by ol.EXTERNAL_LINE_ID fetch first 201 rows only""",
        warehouse=warehouse, order_id=card["document_id"])
    rows = cursor.fetchall()
    if not rows:
        return {"available": False, "reason": "UNBOUND"}
    if len(rows) > 200:
        return {"available": False, "reason": "LINE_BOUND"}
    if any(row[4] != card["document_version"] for row in rows):
        return {"available": False, "reason": "STALE_BINDING"}
    source_lines = {line["line_id"]: line for line in card["payload"]["lines"]}
    by_article: dict[str, dict[str, Any]] = {}
    for sku, article, title, box, _, line_id in rows:
        if line_id not in source_lines:
            return {"available": False, "reason": "STALE_BINDING"}
        source = source_lines[line_id]
        unit, quantity = source["uom"], source["quantity"]
        if not box or unit not in {"EA", "BOX"}:
            return {"available": False, "reason": "PACKAGING"}
        item = by_article.setdefault(article, dict(sku_id=sku, title=title, units_per_box=box, ordered=0, picked=0, loaded=0, shipped=0))
        if item["sku_id"] != sku or item["units_per_box"] != box:
            return {"available": False, "reason": "PACKAGING"}
        item["ordered"] += Decimal(str(quantity)) * (Decimal(str(box)) if unit == "BOX" else 1)
    cursor.execute("""select /* TRADE_ORDER_EXECUTION_FACTS */ j.ARTICLE,j.BASE_UOM,sum(j.QUANTITY),
        sum(case when exists(select 1 from RRL_TT_HU_LOAD_ST ls join RRL_TT_HU_LOAD_FACT lf
            on lf.LOAD_OPERATION_ID=ls.LOAD_OPERATION_ID where ls.SBORKA_PALLET_ID=f.LEGACY_SBORKA_PALLET_ID
            and ls.ACTIVE_FLAG=1 and lf.STATUS in('LOADED','DEPARTED'))then j.QUANTITY else 0 end),
        sum(case when exists(select 1 from RRL_TT_HU_LOAD_ST ls join RRL_TT_HU_LOAD_FACT lf
            on lf.LOAD_OPERATION_ID=ls.LOAD_OPERATION_ID where ls.SBORKA_PALLET_ID=f.LEGACY_SBORKA_PALLET_ID
            and ls.ACTIVE_FLAG=1 and lf.STATUS='DEPARTED')then j.QUANTITY else 0 end)
        from RRL_TRADE_ORDER_LINK tl join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.CUSTOMER_ORDER_ID=tl.CUSTOMER_ORDER_ID
        outer apply json_table(f.FACT_COMPOSITION_JSON,'$[*]'columns(ARTICLE varchar2(160)path'$.article',
            BASE_UOM varchar2(20)path'$.base_uom',QUANTITY number path'$.quantity'))j
        where tl.WARE_ID=:warehouse and tl.EXTERNAL_ID=:order_id and tl.DOCUMENT_VERSION=:version
        and f.STATUS in('PICKED','SHIPPED') group by j.ARTICLE,j.BASE_UOM""",
        warehouse=warehouse, order_id=card["document_id"], version=card["document_version"])
    for article, unit, picked, loaded, shipped in cursor:
        if article not in by_article or unit != "EA" or not 0 <= shipped <= loaded <= picked:
            return {"available": False, "reason": "COMPOSITION"}
        by_article[article].update(picked=picked, loaded=loaded, shipped=shipped)
    items = []
    for item in by_article.values():
        item["retained"] = item["picked"] - item["loaded"]
        box = item["units_per_box"]
        item["boxes"] = {key: format((Decimal(str(item[key])) / Decimal(str(box))).normalize(), "f") for key in ("ordered", "picked", "loaded", "shipped", "retained")}
        items.append({key: format(Decimal(str(value)).normalize(), "f") if key in {"units_per_box", "ordered", "picked", "loaded", "shipped", "retained"} else value for key, value in item.items()})
    return {"available": True, "items": items}
