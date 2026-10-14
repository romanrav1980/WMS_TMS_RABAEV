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
    def __init__(self, saved=None):
        self.saved = saved

    def fetch_all(self, sql, params=None):
        if "RRL_STOCK_RELEASE" in sql:
            return [{"state": "ACTIVE"}]
        return [{"canonical_request": json.dumps(self.saved)}] if self.saved else []


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
    assert subject.post_case_pick(Gateway(saved), 10, 11, request) == {"status": "PICKED"}
    assert seen[0].units == ("original-unit",)


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
