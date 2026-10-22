"""Durable top-up proposals: save/decide in one Oracle transaction; confirm/release through StockPosting only."""
from datetime import datetime, timezone
from hashlib import sha256
from decimal import Decimal
import json
from typing import Any
import oracledb
from ...inventory.public import StockCommand, StockPostingError, build_stock_posting_service
from ...platform.public import read_oracle_json
from ..contracts_trade_topup import TopupConfirm, TopupDecision, TopupRelease, TopupSapReply, TopupSave
from ..contracts_trade_transport import TradeTransportError
from ..contracts_tradecase import TradecaseError
from .trade_topup import allocate

UNCERTAIN = {"RESULT_UNCERTAIN", "REQUEST_DEADLINE", "CONNECTION_UNUSABLE", "LOCK_RETRY_EXHAUSTED", "STOCK_RELEASE_NOT_ACTIVE"}


def _encode(value: Any) -> str:
    return json.dumps(value, default=str, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def _oracle_error(exc: oracledb.DatabaseError) -> TradeTransportError:
    number = getattr(exc.args[0], "code", 0)
    if not 20800 <= number <= 20999:
        return TradeTransportError("TRADE_TOPUP_RESULT_UNKNOWN", 503)
    code = str(exc.args[0]).split("\n", 1)[0].split(":", 1)[-1].strip()
    return TradeTransportError(code, 403 if number in {20851, 20882} else 409)


def _call(cur: Any, procedure: str, body: dict[str, Any], actor: str) -> dict[str, Any]:
    wire = cur.var(oracledb.DB_TYPE_CLOB);wire.setvalue(0, _encode(body))
    result = cur.var(oracledb.DB_TYPE_CLOB)
    cur.callproc(procedure, [wire, actor, result])
    return read_oracle_json(result.getvalue())


def _number(value: Any) -> int | float:
    """Oracle JSON reads numbers, not numeric strings; amounts here are whole boxes and 2-decimal prices."""
    exact = Decimal(str(value))
    return int(exact) if exact == exact.to_integral_value() else float(exact)


def _items(calculation: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for x in calculation["items"]:
        need = x["need"]
        snapshot = datetime.fromisoformat(need["snapshot_at"].replace("Z", "+00:00")).astimezone(timezone.utc)
        out.append(dict(need_id=need["document_id"], need_version=need["document_version"], need_signature=need["calculation_signature"],
                        need_snapshot_at=snapshot.strftime("%Y-%m-%dT%H:%M:%S.%f+00:00"), priority=x["priority"], recipient_id=need["recipient_id"],
                        sku_id=need["sku_id"], article=x["article"], units_per_box=need["units_per_box"], source_owner_id=x["source_owner_id"],
                        target_owner_id=x["target_owner_id"], mrc=_number(x["mrc"]), min_expiry_date=x["min_expiry_date"],
                        need_boxes=_number(need["additional_boxes"]), proposed_boxes=x["proposed_boxes"],
                        calculation=dict(capacity=x["capacity"], uncovered_boxes=x["uncovered_boxes"], limited_by=x["limited_by"],
                                         sender_stock_boxes=x["sender_stock_boxes"], already_confirmed_boxes=x["already_confirmed_boxes"],
                                         need=dict(forecast_quantity=need["forecast_quantity"], target_quantity=need["target_quantity"],
                                                   available_quantity=need["available_quantity"], in_transit_quantity=need["in_transit_quantity"],
                                                   current_trip_quantity=need["current_trip_quantity"], additional_boxes=need["additional_boxes"]))))
    return out


class OracleTopupProposals:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def save(self, ware: int, trip: str, body: TopupSave, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("TRADECASE topup proposal save") as cur:
                # Match the access-revision/site lock order of native document intake.
                cur.execute("lock table RRL_ACCESS_REV in share mode wait 5")
                cur.callproc("RRL_ACCESS_API.assert_allowed", [actor, "tradecase_topup_approve", "WAREHOUSE", str(ware)])
                cur.execute("select ENABLED from RRL_TRADE_SITE where WARE_ID=:w for update", w=ware)
                identity = dict(body.model_dump(mode="json"), warehouse_id=ware, trip_id=trip)
                client_hash = sha256(json.dumps(identity, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()
                saved = cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_TRADE_TOPUP_API.load_saved", [ware, trip, body.operation_id, client_hash, actor, saved])
                if saved.getvalue() is not None:
                    return read_oracle_json(saved.getvalue())
                basis = cur.callfunc("RRL_TRADE_TOPUP_READ.trip_basis", oracledb.DB_TYPE_VARCHAR, [ware, trip, None])
                calculation = allocate(cur, ware, trip, body, actor)
                request = dict(operation_id=body.operation_id, client_request_hash=client_hash, warehouse_id=ware, trip_id=trip, trip_version=calculation["trip_version"],
                               max_age_minutes=body.max_age_minutes, capacity_basis=basis,
                               calculation_signature=calculation["calculation_signature"], items=_items(calculation))
                result = _call(cur, "RRL_TRADE_TOPUP_API.save", request, actor)
                return result
        except TradecaseError as exc:
            raise TradeTransportError(exc.code, exc.status) from exc
        except oracledb.DatabaseError as exc:
            raise _oracle_error(exc) from exc

    def _api(self, procedure: str, body: dict[str, Any], actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("TRADECASE topup " + procedure) as cur:
                return _call(cur, procedure, body, actor)
        except oracledb.DatabaseError as exc:
            raise _oracle_error(exc) from exc

    def decide(self, ware: int, trip: str, proposal: int, body: TopupDecision, actor: str) -> dict[str, Any]:
        return self._api("RRL_TRADE_TOPUP_API.decide", dict(body.model_dump(), proposal_id=proposal, warehouse_id=ware, trip_id=trip), actor)

    def list(self, ware: int, trip: str, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("TRADECASE topup proposals READ ONLY") as cur:
                cur.execute("set transaction read only")
                items = read_oracle_json(cur.callfunc("RRL_TRADE_TOPUP_API.list_trip", oracledb.DB_TYPE_CLOB, [ware, trip, actor]))
                return dict(warehouse_id=ware, trip_id=trip, items=items, approval_available=False)
        except oracledb.DatabaseError as exc:
            raise _oracle_error(exc) from exc

    def _post(self, ware: int, trip: str, proposal: int, kind: str, operation: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]:
        command = StockCommand(operation_id=operation, command_type=kind, actor=actor, lines=(),
                               source={"type": "TRADE_TOPUP", "proposal_id": proposal, "warehouse": ware, "trip_id": trip}, metadata=metadata)
        try:
            return build_stock_posting_service().post(command)
        except oracledb.DatabaseError as exc:
            raise _oracle_error(exc) from exc
        except StockPostingError as exc:
            uncertain = exc.code in UNCERTAIN
            # An unknown outcome is never reported as a refusal: the same operation must be repeated.
            raise TradeTransportError((exc.rule_reason or exc.code) if not uncertain else "TRADE_TOPUP_RESULT_UNKNOWN",
                                      503 if uncertain else 403 if exc.oracle_code == 20882 else 409) from exc

    def confirm(self, ware: int, trip: str, proposal: int, body: TopupConfirm, actor: str) -> dict[str, Any]:
        return self._post(ware, trip, proposal, "TRADE_TOPUP_CONFIRM", body.operation_id, {"expected_version": body.expected_version}, actor)

    def release(self, ware: int, trip: str, proposal: int, body: TopupRelease, actor: str) -> dict[str, Any]:
        return self._post(ware, trip, proposal, "TRADE_TOPUP_RELEASE", body.operation_id,
                          {"expected_version": body.expected_version, "reason": "CANCELLED"}, actor)

    def sap_reply(self, ware: int, trip: str, proposal: int, body: TopupSapReply, actor: str) -> dict[str, Any]:
        if body.outcome == "ACCEPTED":
            return self._api("RRL_TRADE_TOPUP_API.sap_accept", dict(operation_id=body.operation_id, expected_version=body.expected_version, proposal_id=proposal, warehouse_id=ware, trip_id=trip, source_id=body.source_id,
                                                                    event_id=body.event_id, sap_order_id=body.sap_order_id), actor)
        # Rejection frees this proposal's own holds in the same transaction that records the SAP reason.
        sap = dict(source_id=body.source_id, event_id=body.event_id, reason=body.reason)
        return self._post(ware, trip, proposal, "TRADE_TOPUP_RELEASE", body.operation_id,
                          {"expected_version": body.expected_version, "reason": "SAP_REJECTED", "sap": sap}, actor)
