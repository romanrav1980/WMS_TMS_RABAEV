"""C-0190 offline: the mixed-tree runner refuses unsafe starts, journals exact bytes, checks the tree and plans cleanup (no network, no Oracle)."""
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location("c0190_runner", Path(__file__).resolve().parents[2] / "scripts/c0190_mixed_tree_runner.py")
runner = importlib.util.module_from_spec(SPEC)
sys.modules["c0190_runner"] = runner  # dataclasses resolve annotations through the module registry
SPEC.loader.exec_module(runner)

CLEAN = dict(api_ready=True, openapi_paths={runner.MANUAL_ROUTE}, weighted_kg_field=True, tag_rows=0, warehouse=231234567, warehouse_exists=False,
             warehouse_stock_rows=0, warehouse_case_tasks=0, warehouse_waves=0, template_article=True, parent_tare_kg="21.5", manual_net_kg="9.6")


def test_clean_snapshot_may_start():
    assert runner.preflight_findings(CLEAN) == []


@pytest.mark.parametrize("change,code", [
    ({"api_ready": False}, "API_READY_MISSING"),
    ({"openapi_paths": set()}, "MANUAL_NET_ROUTE_MISSING"),
    ({"weighted_kg_field": False}, "MARKING_POLICY_WEIGHTED_KG_MISSING"),
    ({"tag_rows": 1}, "FIXTURE_TAG_COLLISION"),
    ({"warehouse": 210069361}, "PROTECTED_WAREHOUSE"),
    ({"warehouse_exists": True}, "WAREHOUSE_NOT_EMPTY"),
    ({"warehouse_stock_rows": 3}, "WAREHOUSE_NOT_EMPTY"),
    ({"warehouse_case_tasks": 1}, "WAREHOUSE_NOT_EMPTY"),
    ({"warehouse_waves": 1}, "WAREHOUSE_NOT_EMPTY"),
    ({"template_article": False}, "TEMPLATE_ARTICLE_MISSING"),
    ({"parent_tare_kg": None}, "PARENT_TARE_KG_REQUIRED"),
    ({"parent_tare_kg": "0"}, "PARENT_TARE_KG_REQUIRED"),
    ({"manual_net_kg": None}, "MANUAL_NET_KG_REQUIRED"),
    ({"manual_net_kg": "-1"}, "MANUAL_NET_KG_REQUIRED"),
])
def test_unsafe_or_incomplete_start_is_refused_before_any_write(change, code):
    assert code in runner.preflight_findings(CLEAN | change)


def test_manual_net_body_is_the_c0188_contract_only():
    body = runner.manual_net_body("MT.PICK.KG", "9.6", "PK", "CP1")
    assert body == {"operation_id": "MT.PICK.KG", "net_weight_kg": "9.6", "scan_cell": "PK", "scan_container": "CP1", "unit_scans": []}
    assert "fact_qty" not in body and "warehouse_scale_capture" not in body
    for bad in ("0", "abc", "1.0000000001", "-2"):
        with pytest.raises(runner.RunnerStop):
            runner.manual_net_body("op", bad, "PK", "CP1")


def test_ea_and_attach_bodies():
    assert runner.ea_confirm_body("op", "4", "PE", "ART", "CP2") == {"operation_id": "op", "fact_qty": "4", "scan_cell": "PE", "scan_product": "ART", "scan_container": "CP2", "unit_scans": []}
    body = runner.attach_case_body("op", "PAL", 7, 3, 2, "CP2", "BOOK")
    assert body["scan_container"] == "PAL" and body["scan_child"] == "CP2" and body["retained_tare_booking_operation_id"] == "BOOK"
    assert "retained_tare_booking_operation_id" not in runner.attach_case_body("op", "PAL", 7, 3, 2, "CP2", None)


def test_journal_replays_identical_bytes_and_refuses_changed_content():
    j = runner.Journal()
    first = j.record("pick.kg", "POST", "/p", {"b": 1, "a": "x"})
    assert j.record("pick.kg", "POST", "/p", {"a": "x", "b": 1}) == first  # same content, same bytes
    with pytest.raises(runner.RunnerStop, match="STEP_CONTENT_CHANGED"):
        j.record("pick.kg", "POST", "/p", {"a": "y", "b": 1})


def test_unknown_outcome_blocks_every_other_step_until_the_same_step_is_repeated():
    j = runner.Journal()
    j.record("pick.kg", "POST", "/p", {"a": 1})
    with pytest.raises(runner.RunnerStop, match="UNKNOWN_OUTCOME"):
        j.outcome("pick.kg", 503, None)
    with pytest.raises(runner.RunnerStop, match="UNKNOWN_OUTCOME_PENDING:pick.kg"):
        j.record("pick.ea", "POST", "/q", {"b": 2})
    assert j.record("pick.kg", "POST", "/p", {"a": 1})  # the same step may be repeated
    assert j.outcome("pick.kg", 200, {"ok": True}) == {"ok": True} and j.unknown is None
    restored = runner.Journal.from_json(json.loads(json.dumps(j.to_json())))
    assert restored.steps == j.steps and restored.results == j.results and restored.unknown is None


def tree(**changes):
    nodes = [
        {"uid": "MT.PAL", "kind": "CONTAINER", "cell": "X", "version": 3},
        {"uid": "CASE:1", "kind": "CASE", "case_task_id": 1, "sscc": "S1", "cell": "X"},
        {"uid": "CASELOT:A:1", "kind": "STOCK", "case_task_id": 1, "article": "K", "quantity": "9.6"},
        {"uid": "CASE:2", "kind": "CASE", "case_task_id": 2, "sscc": "S2", "cell": "X"},
        {"uid": "CASELOT:B:1", "kind": "STOCK", "case_task_id": 2, "article": "E", "quantity": "4"},
    ]
    return {"nodes": changes.get("nodes", nodes)}


EXPECTED = {"case_tasks": [1, 2], "cell": "X", "quantities": {"K": "9.6", "E": "4"}, "carriers": {1: "S1", 2: "S2"}}


def test_correct_mixed_tree_has_no_findings():
    assert runner.tree_findings(tree(), EXPECTED) == []


@pytest.mark.parametrize("mutate,code", [
    (lambda n: n.append(dict(n[2])), "STOCK_LEAF_COUNTED_TWICE"),
    (lambda n: n[4].update(quantity="5"), "QUANTITY_MISMATCH"),
    (lambda n: n.pop(3), "CASE_CHILDREN_MISMATCH"),
    (lambda n: n[1].update(sscc="OTHER"), "CHILD_SSCC_CHANGED"),
    (lambda n: n[0].update(quantity="1"), "CONTAINER_HOLDS_QUANTITY"),
    (lambda n: n[3].update(cell="Y"), "TREE_CELL_MISMATCH"),
])
def test_tree_defects_are_found(mutate, code):
    nodes = tree()["nodes"]
    mutate(nodes)
    assert code in runner.tree_findings({"nodes": nodes}, EXPECTED)


def test_cleanup_plan_reverses_exactly_what_was_created_in_order():
    state = {"tree_attached": [1, 2], "cases": {"kg": {"task": 1}, "ea": {"task": 2}}, "wave": 9, "tare_bookings": ["B1", "B2"], "lots": {"kg": "L1"}}
    plan = runner.cleanup_plan(state)
    assert plan == ["HU_DETACH_CASE:1", "HU_DETACH_CASE:2", "CASE_CARRIER_RETURN:1", "CASE_CARRIER_RETURN:2", "RESERVATION_RELEASE:wave",
                    "TARE_BOOK_CANCEL:B1", "TARE_BOOK_CANCEL:B2", "TARE_COUNT_ZERO", "WAVE_EXECUTION_FINISH_OR_CANCEL", "INVENTORY_COUNT_ZERO",
                    "ASSERT_WAREHOUSE_ZERO_STOCK_AND_RESERVATION"]
    assert runner.cleanup_plan({}) == ["ASSERT_WAREHOUSE_ZERO_STOCK_AND_RESERVATION"]  # nothing created, nothing reversed


@pytest.fixture
def work():
    """Own temporary folder (independent of the shared pytest tmp_path root)."""
    with tempfile.TemporaryDirectory() as folder:
        yield Path(folder)


class FakeResponse:
    def __init__(self, status, body):
        self.status_code, self._body, self.headers = status, body, {"content-type": "application/json"}

    def json(self):
        return self._body


class FakeHttp:
    def __init__(self, answers):
        self.answers, self.sent = list(answers), []

    def request(self, method, url, content=None, headers=None):
        self.sent.append(content)
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return FakeResponse(*answer)


def live_with(answers, folder):
    live = object.__new__(runner.Live)
    live.api, live.file, live.http = "http://x", folder / "state.json", FakeHttp(answers)
    live.s, live.journal = {"tag": "MT28T", "posts": {}}, runner.Journal()
    return live


def test_lost_response_is_retried_with_identical_bytes_and_returns_the_receipt(work):
    live = live_with([OSError("reset"), (200, {"operation_id": "op"})], work)
    with pytest.raises(runner.RunnerStop, match="UNKNOWN_OUTCOME"):
        live.send("pick.kg", "POST", "/p", {"operation_id": "op", "net_weight_kg": "9.6"})
    assert json.loads((work / "state.json").read_text(encoding="utf-8"))["journal"]["unknown"] == "pick.kg"
    assert live.send("pick.kg", "POST", "/p", {"operation_id": "op", "net_weight_kg": "9.6"}) == {"operation_id": "op"}
    assert live.http.sent[0] == live.http.sent[1]


def test_unexpected_status_stops_and_a_completed_step_is_not_sent_again(work):
    live = live_with([(409, {"detail": {"code": "X"}}), (200, {"ok": 1})], work)
    with pytest.raises(runner.RunnerStop, match="UNEXPECTED_STATUS"):
        live.send("attach.kg", "POST", "/a", {"operation_id": "a"})
    live2 = live_with([(200, {"ok": 1})], work)
    assert live2.send("s", "POST", "/s", {"x": 1}) == {"ok": 1}
    assert live2.send("s", "POST", "/s", {"x": 1}) == {"ok": 1} and len(live2.http.sent) == 1


def test_expected_refusal_is_accepted_for_negative_steps(work):
    live = live_with([(409, {"detail": {"code": "HU_PACK_SAME_LOCATION_REQUIRED"}})], work)
    assert live.send("neg.other_cell", "POST", "/a", {"operation_id": "n"}, expect=(403, 409))["detail"]["code"] == "HU_PACK_SAME_LOCATION_REQUIRED"


def test_plan_mode_needs_no_network_or_oracle(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["runner", "plan"])
    assert runner.main() == 0
    out = json.loads(capsys.readouterr().out)
    assert out["manual_route"] == runner.MANUAL_ROUTE and out["transport"].startswith("TRANSPORT_NOT_WIRED")


def test_live_modes_require_an_explicit_api(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["runner", "run"])
    with pytest.raises(SystemExit):
        runner.main()
