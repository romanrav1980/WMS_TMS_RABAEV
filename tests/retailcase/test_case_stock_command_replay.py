import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "api/wms_api_server"))
import json
from decimal import Decimal
import pytest
from app.schemas import CasePickLineConfirmRequest
from app.modules.inventory.infrastructure import case_pick_commands as subject
from app.modules.inventory.contracts_stock import StockPostingError


class Gateway:
    def __init__(self, saved=None, weighted_kg=False):
        self.saved, self.weighted_kg, self.calls = saved, weighted_kg, []

    def fetch_all(self, sql, params=None):
        self.calls.append(sql)
        if "RRL_STOCK_RELEASE" in sql:
            return [{"state": "ACTIVE"}]
        if "CANONICAL_REQUEST" in sql:
            return [{"canonical_request": json.dumps(self.saved)}] if self.saved else []
        if "WEIGHTED_KG" in sql:
            return [{"weighted_kg": int(self.weighted_kg)}]
        raise AssertionError(f"Unexpected query: {sql}")


def test_replay_uses_original_units_even_after_they_moved(monkeypatch):
    request = CasePickLineConfirmRequest(operation_id="case-1", actor="operator",
        fact_qty="1", unit_scans=[{"system_code": "CRPT", "profile_code": "TOBACCO", "code": "old-code"}])
    submitted = request.model_dump(mode="json")
    submitted["fact_qty"] = "1"
    metadata = {"fact_qty": "1", "requested_confirmation": submitted}
    saved = {"actor": "operator", "command_type": "CASE_PICK_CONFIRM",
        "source": {"case_task_id": 10, "case_line_id": 11}, "metadata": metadata, "units": ["original-unit"]}
    monkeypatch.setattr(subject, "resolve_case_codes", lambda *args: pytest.fail("Must not resolve moved codes during replay"))
    seen = []
    class Posting:
        def post(self, command):
            seen.append(command)
            return {"status": "PICKED"}
    monkeypatch.setattr(subject, "StockPosting", Posting)
    gateway = Gateway(saved, weighted_kg=True)
    assert subject.post_case_pick(gateway, 10, 11, request) == {"status": "PICKED"}
    assert seen[0].units == ("original-unit",)
    assert not any("WEIGHTED_KG" in sql for sql in gateway.calls)


def test_changed_actor_cannot_reuse_saved_operation(monkeypatch):
    request = CasePickLineConfirmRequest(operation_id="case-1", actor="other", fact_qty="1")
    saved = {"actor": "operator", "command_type": "CASE_PICK_CONFIRM", "source": {}, "metadata": {}, "units": []}
    with pytest.raises(StockPostingError, match="OPERATION_CONTENT_CONFLICT"):
        subject.post_case_pick(Gateway(saved), 10, 11, request)


def test_quantity_survives_above_binary_float_integer_precision(monkeypatch):
    quantity = "9007199254740993.000000001"
    request = CasePickLineConfirmRequest(operation_id="case-2", actor="operator", fact_qty=quantity)
    seen = []
    class Posting:
        def post(self, command):
            seen.append(command)
            return {}
    monkeypatch.setattr(subject, "StockPosting", Posting)
    subject.post_case_pick(Gateway(), 10, 11, request)
    assert request.fact_qty == Decimal(quantity)
    assert seen[0].metadata["fact_qty"] == quantity


def test_new_weighted_kg_command_requires_a_weight_source(monkeypatch):
    request = CasePickLineConfirmRequest(operation_id="case-weighted", actor="operator", fact_qty="1.25")
    monkeypatch.setattr(subject, "StockPosting", lambda: pytest.fail("must not post a source-less KG fact"))
    with pytest.raises(StockPostingError, match="CASE_WEIGHT_SOURCE_REQUIRED"):
        subject.post_case_pick(Gateway(weighted_kg=True), 10, 11, request)


def test_non_weighted_command_keeps_the_existing_confirm_path(monkeypatch):
    request = CasePickLineConfirmRequest(operation_id="case-each", actor="operator", fact_qty="1")
    seen = []
    class Posting:
        def post(self, command):
            seen.append(command)
            return {"status": "PICKED"}
    monkeypatch.setattr(subject, "StockPosting", Posting)
    assert subject.post_case_pick(Gateway(weighted_kg=False), 10, 11, request) == {"status": "PICKED"}
    assert seen[0].metadata["fact_qty"] == "1"
