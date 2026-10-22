"""C-0143 offline checks of the top-up decision boundary (no Oracle): contracts, wire format, terms, outcome mapping."""
import json
import pytest
from pydantic import ValidationError
from app.modules.integrations.contracts_trade_topup import TopupDecision, TopupSapReply, TopupSave
from app.modules.integrations.contracts_trade_transport import TradeTransportError
from app.modules.integrations.infrastructure import trade_topup, trade_topup_proposals as proposals
from app.modules.inventory.contracts_stock import StockCommand, StockPostingError


def test_decision_contract_requires_boxes_only_for_adjust():
    TopupDecision(operation_id="op1", expected_version=1, action="ADJUST", boxes=20)
    TopupDecision(operation_id="op1", expected_version=1, action="REJECT")
    for bad in (dict(action="ADJUST"), dict(action="REJECT", boxes=5), dict(action="ADJUST", boxes=0)):
        with pytest.raises(ValidationError):
            TopupDecision(operation_id="op1", expected_version=1, **bad)


def test_sap_reply_requires_order_or_reason():
    TopupSapReply(operation_id="o", source_id="SAP", event_id="e1", expected_version=2, outcome="ACCEPTED", sap_order_id="104")
    TopupSapReply(operation_id="o", source_id="SAP", event_id="e1", expected_version=2, outcome="REJECTED", reason="no stock")
    with pytest.raises(ValidationError):
        TopupSapReply(operation_id="o", source_id="SAP", event_id="e1", expected_version=2, outcome="ACCEPTED")
    with pytest.raises(ValidationError):
        TopupSapReply(operation_id="o", source_id="SAP", event_id="e1", expected_version=2, outcome="REJECTED", sap_order_id="104")


def test_save_keeps_preview_rules():
    with pytest.raises(ValidationError):
        TopupSave(operation_id="o", need_ids=["N1", "N1"], max_age_minutes=60)
    with pytest.raises(ValidationError):
        TopupSave(operation_id="o", need_ids=["N1"], max_age_minutes=0)


def test_topup_commands_are_lineless_stock_commands_only():
    wire = json.loads(StockCommand(operation_id="TC.TOPUP:1", command_type="TRADE_TOPUP_CONFIRM", actor="u", lines=(),
                                   source={"proposal_id": 7, "warehouse": 1, "trip_id": "R1"}, metadata={"expected_version": 2}).canonical_json())
    assert wire["lines"] == [] and wire["source"]["proposal_id"] == 7
    with pytest.raises(ValueError):
        StockCommand(operation_id="x", command_type="MANUAL_MOVE", actor="u", lines=(), source={}).canonical_json()


def _calculation(snapshot_at: str, mrc: str = "200.00", boxes: str = "40") -> dict:
    need = dict(document_id="N1", document_version=3, calculation_signature="s" * 64, snapshot_at=snapshot_at, recipient_id="R", sku_id="A",
                units_per_box=10, additional_boxes=boxes, forecast_quantity="1", target_quantity="1", available_quantity="0",
                in_transit_quantity="0", current_trip_quantity="600")
    return dict(items=[dict(need=need, priority=1, article="ART", source_owner_id="SNS", target_owner_id="BLC", mrc=mrc, min_expiry_date="2026-11-01",
                            proposed_boxes=40, capacity={"fitting_boxes": 60}, uncovered_boxes="0", limited_by=None, sender_stock_boxes=350,
                            already_confirmed_boxes="0")])


@pytest.mark.parametrize("snapshot", ["2026-10-22T10:00:00+00:00", "2026-10-22T13:00:00.123456+03:00", "2026-10-22T10:00:00Z"])
def test_items_wire_is_oracle_parsable(snapshot):
    item = proposals._items(_calculation(snapshot))[0]
    assert item["need_snapshot_at"].startswith("2026-10-22T10:00:00.") and item["need_snapshot_at"].endswith("+00:00")
    assert item["mrc"] == 200 and isinstance(item["need_boxes"], int)
    assert proposals._items(_calculation(snapshot, mrc="199.99", boxes="40.5"))[0]["mrc"] == 199.99


class _Docs:
    """Cursor stub for _document(): returns ORDER bodies by id."""
    def __init__(self, orders: dict[str, dict]):
        self.orders, self.row = orders, None

    def execute(self, sql: str, **kw):
        body = self.orders.get(kw.get("id"))
        self.row = None if body is None else (json.dumps(body), 1)

    def fetchone(self):
        return self.row


def _order(recipient: str, line: dict) -> dict:
    return dict(recipient_id=recipient, lines=[{**dict(line_id="L1", sku_id="A", source_owner_id="SNS", target_owner_id="BLC", mrc=200, min_osg_days=5), **line}])


def test_terms_come_from_main_order_of_same_recipient_and_goods(monkeypatch):
    monkeypatch.setattr(trade_topup, "_document", lambda cur, ware, kind, key: (cur.orders[key], 1))
    trip = dict(planned_departure_at="2026-10-22T08:00:00Z", orders=[dict(order_id="O1", line_id="L1"), dict(order_id="O2", line_id="L1")])
    cur = _Docs({"O1": _order("R", {}), "O2": _order("OTHER", {"mrc": 999})})
    assert trade_topup._terms(cur, 1, trip, "R", "A") == dict(source_owner_id="SNS", target_owner_id="BLC", mrc="200", min_expiry_date="2026-10-27")
    with pytest.raises(TradeTransportError) as missing:
        trade_topup._terms(cur, 1, trip, "NOBODY", "A")
    assert missing.value.code == "TOPUP_STOCK_TERMS_REQUIRED"
    cur.orders["O2"] = _order("R", {"mrc": 250})
    with pytest.raises(TradeTransportError) as ambiguous:
        trade_topup._terms(cur, 1, trip, "R", "A")
    assert ambiguous.value.code == "TOPUP_STOCK_TERMS_AMBIGUOUS"


class _Posting:
    def __init__(self, error: StockPostingError | None):
        self.error, self.commands = error, []

    def post(self, command):
        self.commands.append(command)
        if self.error:
            raise self.error
        return {"proposal_id": command.source["proposal_id"], "status": "CONFIRMED"}


@pytest.mark.parametrize("error,status,code", [
    (None, None, None),
    (StockPostingError("STOCK_RULE_REJECTED", "op", 20911, "TRADE_TOPUP_CAPACITY_BASIS_CHANGED"), 409, "TRADE_TOPUP_CAPACITY_BASIS_CHANGED"),
    (StockPostingError("STOCK_RULE_REJECTED", "op", 20882, "TRADE_TOPUP_ACCESS_DENIED"), 403, "TRADE_TOPUP_ACCESS_DENIED"),
    (StockPostingError("RESULT_UNCERTAIN", "op"), 503, "TRADE_TOPUP_RESULT_UNKNOWN"),
    (StockPostingError("LOCK_RETRY_EXHAUSTED", "op", 54), 503, "TRADE_TOPUP_RESULT_UNKNOWN"),
])
def test_confirm_outcome_never_turns_unknown_into_refusal(monkeypatch, error, status, code):
    posting = _Posting(error)
    monkeypatch.setattr(proposals, "build_stock_posting_service", lambda: posting)
    from app.modules.integrations.contracts_trade_topup import TopupConfirm
    service = proposals.OracleTopupProposals(gateway=None)
    if error is None:
        assert service.confirm(5, "R1", 7, TopupConfirm(operation_id="op", expected_version=2), "u")["status"] == "CONFIRMED"
    else:
        with pytest.raises(TradeTransportError) as raised:
            service.confirm(5, "R1", 7, TopupConfirm(operation_id="op", expected_version=2), "u")
        assert (raised.value.status, raised.value.code) == (status, code)
    sent = posting.commands[0]
    assert sent.command_type == "TRADE_TOPUP_CONFIRM" and sent.source == {"type": "TRADE_TOPUP", "proposal_id": 7, "warehouse": 5, "trip_id": "R1"}
    assert sent.metadata == {"expected_version": 2}


def test_sap_rejection_releases_through_stock_posting_with_reason(monkeypatch):
    posting = _Posting(None)
    monkeypatch.setattr(proposals, "build_stock_posting_service", lambda: posting)
    proposals.OracleTopupProposals(None).sap_reply(5, "R1", 7, TopupSapReply(operation_id="op", source_id="SAP", event_id="e9", expected_version=3,
                                                                             outcome="REJECTED", reason="Customer blocked"), "sap")
    sent = posting.commands[0]
    assert sent.command_type == "TRADE_TOPUP_RELEASE"
    assert sent.metadata == {"expected_version": 3, "reason": "SAP_REJECTED", "sap": {"source_id": "SAP", "event_id": "e9", "reason": "Customer blocked"}}


@pytest.mark.parametrize("status,code", [(403,"TRADE_TOPUP_ACCESS_DENIED"),(404,"TRADE_TOPUP_PROPOSAL_NOT_FOUND"),(409,"TRADE_TOPUP_OPERATION_CONFLICT"),(503,"TRADE_TOPUP_RESULT_UNKNOWN")])
def test_early_failure_does_not_claim_original_operation_outcome(status,code):
    from fastapi import HTTPException
    from app.modules.integrations.api.trade_transport_routes import _topup
    def failed():
        raise TradeTransportError(code,status)
    with pytest.raises(HTTPException) as caught:
        _topup(failed)
    assert caught.value.detail["outcome_confirmed"] is False
    assert caught.value.detail["retry_same_operation_id"] is True
