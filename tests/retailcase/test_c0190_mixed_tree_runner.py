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


def test_read_only_preflight_does_not_require_operator_measurements():
    snapshot = CLEAN | {"parent_tare_kg": None, "manual_net_kg": None, "require_measurements": False}
    assert runner.preflight_findings(snapshot) == []


def test_live_preflight_blocks_until_fixture_configuration_recovery_is_proven():
    assert "FIXTURE_CONFIG_RECOVERY_UNVERIFIED" in runner.preflight_findings(CLEAN)
    assert runner.preflight_findings(CLEAN | {"fixture_config_recovery_verified": True}) == []


def test_clean_snapshot_may_start():
    assert runner.preflight_findings(CLEAN | {"fixture_config_recovery_verified": True}) == []


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
    state = {"tree_attached": [1, 2], "cases": {"kg": {"task": 1}, "ea": {"task": 2}}, "wave": 9, "tare_bookings": ["B1", "B2"], "root_tare_booking": "ROOT", "lots": {"kg": "L1"}}
    plan = runner.cleanup_plan(state)
    assert plan == ["HU_DETACH_CASE:1", "HU_DETACH_CASE:2", "CASE_CARRIER_RETURN:1", "CASE_CARRIER_RETURN:2", "RESERVATION_RELEASE:wave",
                    "TARE_BOOK_CANCEL:B1", "TARE_BOOK_CANCEL:B2", "TARE_BOOK_CANCEL:ROOT", "TARE_COUNT_ZERO", "WAVE_EXECUTION_FINISH_OR_CANCEL", "INVENTORY_COUNT_ZERO",
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
    assert out["manual_route"] == runner.MANUAL_ROUTE and out["transport"] == "C0191 requires --transport-inputs after TREE"


def test_live_modes_require_an_explicit_api(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["runner", "run"])
    with pytest.raises(SystemExit):
        runner.main()


# ---------------- K-0217 rework: cleanup scope, native journal, exact refusals ----------------

OWN = {"MT.LOT.K", "MT.LOT.E", "CASELOT:K:1", "CASELOT:E:1"}
EXPECTED_LEFT = {"MTK": "19.2", "MTE": "8"}
ROWS = [("MT.LOT.K", "PK", "MTK", "KG", 3, "9.6"), ("CASELOT:K:1", "PK", "MTK", "KG", 1, "9.6"),
        ("MT.LOT.E", "PE", "MTE", "EA", 3, "4"), ("CASELOT:E:1", "PE", "MTE", "EA", 1, "4")]


def test_cleanup_scope_accepts_only_this_runs_lots_with_the_exact_remainder():
    assert runner.cleanup_scope_findings(ROWS, 0, 0, OWN, EXPECTED_LEFT) == []


@pytest.mark.parametrize("rows,reservations,tasks,code", [
    (ROWS + [("OTHER.LOT", "PK", "MTK", "KG", 1, "0")], 0, 0, "FOREIGN_UID:OTHER.LOT"),
    (ROWS + [("MT.LOT.K", "PK", "SHARED", "EA", 1, "0")], 0, 0, "FOREIGN_ARTICLE:SHARED"),
    (ROWS[:-1], 0, 0, "REMAINDER_MISMATCH:MTE"),
    (ROWS, 1, 0, "ACTIVE_RESERVATIONS:1"),
    (ROWS, 0, 2, "FOREIGN_OPEN_TASKS:2"),
])
def test_cleanup_refuses_anything_that_is_not_this_runs_exact_state(rows, reservations, tasks, code):
    findings = runner.cleanup_scope_findings(rows, reservations, tasks, OWN, EXPECTED_LEFT)
    assert any(f.startswith(code) for f in findings), findings


class PostingError(Exception):
    def __init__(self, code, oracle_code=None, rule_reason=None):
        super().__init__(code); self.code, self.oracle_code, self.rule_reason = code, oracle_code, rule_reason


@pytest.mark.parametrize("error,status", [(None, 200), (PostingError("STOCK_RULE_REJECTED", 20886, "X"), 409), (PostingError("RESULT_UNCERTAIN"), 0),
                                          (PostingError("CASE", 20891), 0), (PostingError("RESOURCE_NOT_FOUND", 1403), 0),
                                          (PostingError("STOCK_RULE_REJECTED", 20891), 0), (PostingError("REQUEST_DEADLINE", 20886), 0),
                                          (OSError("reset"), 0)])
def test_native_outcome_classification(error, status):
    assert runner.native_status(error) == status


def native_live(folder, answers):
    live = live_with([], folder)
    calls = []

    def stock_post(command):
        stored = json.loads((folder / "state.json").read_text(encoding="utf-8"))["journal"]["steps"]
        calls.append((command, any(k.startswith("native.") for k in stored)))  # the command was journaled before posting
        answer = answers.pop(0)
        if isinstance(answer, BaseException):
            raise answer
        return answer
    live.stock_post = stock_post
    return live, calls


def test_native_command_is_journaled_before_posting_and_retried_with_identical_content(work):
    live, calls = native_live(work, [PostingError("RESULT_UNCERTAIN"), {"operation_id": "MT28T.return.kg"}])
    with pytest.raises(runner.RunnerStop, match="UNKNOWN_OUTCOME:native.return.kg"):
        live.post("return.kg", "CASE_CARRIER_RETURN", {"destinations": {"L": "PK"}}, {"case_task_id": 1})
    assert live.journal.unknown == "native.return.kg" and calls[0][1] is True
    with pytest.raises(runner.RunnerStop, match="UNKNOWN_OUTCOME_PENDING:native.return.kg"):
        live.post("count.zero", "INVENTORY_COUNT", {"counts": []}, {"revision_id": 1})  # later stages are blocked
    assert live.post("return.kg", "CASE_CARRIER_RETURN", {"destinations": {"L": "PK"}}, {"case_task_id": 1}) == {"operation_id": "MT28T.return.kg"}
    assert calls[0][0] == calls[1][0] and calls[0][0]["operation_id"] == "MT28T.return.kg"
    assert live.post("return.kg", "CASE_CARRIER_RETURN", {"destinations": {"L": "PK"}}, {"case_task_id": 1}) == {"operation_id": "MT28T.return.kg"} and len(calls) == 2


def test_changed_native_content_under_the_same_operation_is_refused_before_posting(work):
    live, calls = native_live(work, [PostingError("RESULT_UNCERTAIN")])
    with pytest.raises(runner.RunnerStop):
        live.post("count.zero", "INVENTORY_COUNT", {"counts": [{"uid": "L", "quantity": "0", "expected_stock_version": 3}]}, {"revision_id": 1})
    with pytest.raises(runner.RunnerStop, match="STEP_CONTENT_CHANGED:native.count.zero"):
        live.post("count.zero", "INVENTORY_COUNT", {"counts": [{"uid": "L", "quantity": "0", "expected_stock_version": 4}]}, {"revision_id": 1})
    assert len(calls) == 1  # re-read quantities never reuse the operation id with other content


def test_confirmed_native_refusal_is_final_not_unknown(work):
    live, calls = native_live(work, [PostingError("STOCK_RULE_REJECTED", 20886, "CASE_RETURN_DESTINATION_REQUIRED")])
    with pytest.raises(runner.RunnerStop, match="NATIVE_REFUSED"):
        live.post("return.ea", "CASE_CARRIER_RETURN", {}, {"case_task_id": 2})
    assert live.journal.unknown is None and live.journal.results["native.return.ea"]["status"] == 409


BEFORE = {"nodes": [{"uid": "MT.PAL", "version": 3}]}


@pytest.mark.parametrize("name,detail", [
    ("stale_parent_version", {"code": "STOCK_RULE_REJECTED", "reason": "HU_CONTENT_VERSION_CONFLICT"}),
    ("foreign_carrier_scan", {"code": "HU_CASE_CARRIER_SCAN_REQUIRED"}),
    ("other_cell", {"code": "STOCK_RULE_REJECTED", "reason": "HU_PACK_SAME_LOCATION_REQUIRED: cell"}),
    ("changed_body_same_operation", {"code": "STOCK_RULE_REJECTED", "reason": "OPERATION_CONFLICT"}),
])
def test_each_refusal_must_be_its_expected_rule_with_the_parent_unchanged(name, detail):
    runner.check_refusal(name, {"detail": detail}, BEFORE, BEFORE)
    with pytest.raises(runner.RunnerStop, match="REFUSAL_CHANGED_PARENT_COMPOSITION"):
        runner.check_refusal(name, {"detail": detail}, BEFORE, {"nodes": [{"uid": "MT.PAL", "version": 4}]})


@pytest.mark.parametrize("name", list(runner.EXPECTED_REFUSALS))
def test_an_unrelated_denial_does_not_pass_as_the_expected_refusal(name):
    for wrong in ({"detail": {"code": "ACCESS_DENIED"}}, {"detail": "Permission required"}, {"detail": {"code": "HU_CHILD_ALREADY_HAS_PARENT"}}):
        with pytest.raises(runner.RunnerStop, match="UNEXPECTED_REFUSAL"):
            runner.check_refusal(name, wrong, BEFORE, BEFORE)


def test_tree_stage_checks_every_negative_by_name():
    import inspect
    source = inspect.getsource(runner.Live.tree)
    assert all(f'"{name}"' in source for name in runner.EXPECTED_REFUSALS) and "check_refusal(name" in source and "expect=(409,)" in source

class _MetaCursor:
    def __init__(self, store):
        self.store = store

    def callproc(self, *_args):
        return None

    def execute(self, *_args):
        self.store["calls"] += 1
        if self.store.get("commit_then_drop"):
            self.store["count"] = 1
            self.store["commit_then_drop"] = False
            raise OSError("connection dropped after commit")
        if self.store.get("drop_before_commit"):
            self.store["drop_before_commit"] = False
            raise OSError("connection dropped before commit")
        self.store["count"] = 1


class _MetaConnection:
    def __init__(self, store):
        self.store = store

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def cursor(self):
        return _MetaCursor(self.store)

    def commit(self):
        return None

    def rollback(self):
        return None


def _meta_live(store):
    live = object.__new__(runner.Live)
    live.s, live.journal = {}, runner.Journal()
    live.save = lambda: None
    live.connect = lambda: _MetaConnection(store)
    live.one = lambda _sql, **_binds: store["count"]
    return live


def test_fixture_metadata_is_reconciled_before_repeat_and_never_posted_twice():
    store = {"count": 0, "calls": 0}
    live = _meta_live(store)
    live.meta("insert fixture", "select count(*) from fixture")
    assert store == {"count": 1, "calls": 1}
    live.meta("insert fixture", "select count(*) from fixture")
    assert store == {"count": 1, "calls": 1}


def test_fixture_metadata_accepts_a_commit_that_lost_its_response():
    store = {"count": 0, "calls": 0, "commit_then_drop": True}
    live = _meta_live(store)
    live.meta("insert fixture", "select count(*) from fixture")
    assert store["calls"] == 1 and live.journal.unknown is None
    assert next(iter(live.journal.results.values()))["value"]["reconciled_after_error"] is True


def test_fixture_metadata_blocks_later_steps_until_the_same_intent_reconciles():
    store = {"count": 0, "calls": 0, "drop_before_commit": True}
    live = _meta_live(store)
    with pytest.raises(runner.RunnerStop, match="UNKNOWN_OUTCOME"):
        live.meta("insert fixture", "select count(*) from fixture")
    assert live.journal.unknown and store["count"] == 0
    with pytest.raises(runner.RunnerStop, match="UNKNOWN_OUTCOME_PENDING"):
        live.journal.record("fixture.other", "ORACLE_CONFIG", "reconcile", {})
    live.meta("insert fixture", "select count(*) from fixture")
    assert store["count"] == 1 and live.journal.unknown is None

def test_fixture_verification_passes_only_parameters_used_in_select():
    store = {"count": 0, "calls": 0}
    live = _meta_live(store)
    def verify(sql, **binds):
        assert binds == {"a": "TEST"}
        return store["count"]
    live.one = verify
    live.meta("insert fixture(:a,:b)", "select count(*) from fixture where id=:a", a="TEST", b="unused")
    assert store["calls"] == 1


def test_saved_http_refusal_still_stops_on_resume(work):
    live = live_with([(409, {"detail": {"code": "DENIED"}})], work)
    for _ in range(2):
        with pytest.raises(runner.RunnerStop, match="UNEXPECTED_STATUS"):
            live.send("attach", "POST", "/a", {"operation_id": "same"})
    assert len(live.http.sent) == 1

def test_saved_native_refusal_still_stops_on_resume(work):
    live, calls = native_live(work, [PostingError("STOCK_RULE_REJECTED", 20886, "DENIED")])
    for _ in range(2):
        with pytest.raises(runner.RunnerStop, match="NATIVE_REFUSED"):
            live.post("return.kg", "CASE_CARRIER_RETURN", {}, {"case_task_id": 1})
    assert len(calls) == 1

def test_failed_state_replace_preserves_previous_durable_journal(work, monkeypatch):
    live = live_with([], work)
    live.save()
    original = live.file.read_bytes()
    live.journal.record("pick", "POST", "/p", {"operation_id": "same"})
    def refuse_replace(*args):
        raise PermissionError("file locked")
    monkeypatch.setattr(runner.os, "replace", refuse_replace)
    with pytest.raises(PermissionError):
        live.save()
    assert live.file.read_bytes() == original
    pending = live.file.with_name(live.file.name + ".pending")
    assert "pick" in json.loads(pending.read_text(encoding="utf-8"))["journal"]["steps"]
    assert live.http.sent == []

def test_resume_can_traverse_completed_steps_to_reach_unknown_step():
    j = runner.Journal()
    j.record("first", "POST", "/first", {"x": 1})
    j.outcome("first", 200, {"ok": True})
    j.record("second", "POST", "/second", {"x": 2})
    with pytest.raises(runner.RunnerStop, match="UNKNOWN_OUTCOME"):
        j.outcome("second", 0, None)
    assert j.record("first", "POST", "/first", {"x": 1})
    assert j.unknown == "second"
    with pytest.raises(runner.RunnerStop, match="STEP_CONTENT_CHANGED"):
        j.record("first", "POST", "/first", {"x": 3})
    with pytest.raises(runner.RunnerStop, match="UNKNOWN_OUTCOME_PENDING"):
        j.record("third", "POST", "/third", {})
    j.record("second", "POST", "/second", {"x": 2})
    j.outcome("second", 200, {"ok": True})
    assert j.unknown is None

def test_fixture_changed_statement_cannot_reuse_same_identity():
    live = _meta_live({"count": 0, "calls": 0})
    live.meta("insert original", "select count(*) from fixture where id=:a", a="OWN")
    with pytest.raises(runner.RunnerStop, match="STEP_CONTENT_CHANGED"):
        live.meta("insert changed", "select count(*) from fixture where id=:a", a="OWN")


def test_unjournaled_existing_fixture_is_refused_on_every_attempt():
    store = {"count": 1, "calls": 0}
    live = _meta_live(store)
    with pytest.raises(runner.RunnerStop, match="FIXTURE_ALREADY_EXISTS"):
        live.meta("insert fixture", "select count(*) from fixture")
    with pytest.raises(runner.RunnerStop, match="FIXTURE_REFUSED"):
        live.meta("insert fixture", "select count(*) from fixture")
    assert store["calls"] == 0


def test_fixture_unknown_boundary_is_durable_before_execute():
    store = {"count": 0, "calls": 0}
    live = _meta_live(store)
    original_connect = live.connect
    def connect():
        assert live.journal.unknown.startswith("fixture.")
        return original_connect()
    live.connect = connect
    live.meta("insert fixture", "select count(*) from fixture")
    assert live.journal.unknown is None

def test_fixture_identifier_survives_restart_without_allocating_another(work):
    live = live_with([], work)
    calls = []
    def allocate():
        calls.append(1)
        return 42
    assert live.fixture_value("order.kg", allocate) == 42
    restored = live_with([], work)
    restored.s = json.loads(live.file.read_text(encoding="utf-8"))
    assert restored.fixture_value("order.kg", allocate) == 42
    assert len(calls) == 1

def test_document_lost_reply_recovers_created_id_without_second_create(work):
    live = live_with([], work)
    rows, calls = [], []
    def create():
        calls.append(1)
        rows.append((51,))
        raise OSError("reply lost")
    with pytest.raises(OSError):
        live.create_fixture_document("wave", {"warehouse": 1}, lambda: rows, create)
    assert live.journal.unknown == "document.wave"
    assert live.create_fixture_document("wave", {"warehouse": 1}, lambda: rows, create) == 51
    assert len(calls) == 1 and live.journal.unknown is None


def test_document_unknown_without_visible_result_never_repeats_create(work):
    live = live_with([], work)
    calls = []
    def create():
        calls.append(1)
        raise OSError("connection lost")
    with pytest.raises(OSError):
        live.create_fixture_document("plan", {"order": 2}, lambda: [], create)
    with pytest.raises(runner.RunnerStop, match="DOCUMENT_OUTCOME_UNRESOLVED"):
        live.create_fixture_document("plan", {"order": 2}, lambda: [], create)
    assert len(calls) == 1
@pytest.mark.parametrize("lost_at", ["attach.kg", "attach.ea", "after_tree"])
def test_tree_resume_reuses_original_versions_and_preserves_both_children(work, monkeypatch, lost_at):
    live = live_with([], work)
    live.s.update(warehouse=1, cells={"src": "SRC"}, articles={"kg": "K", "ea": "E"},
                  measurements={"parent_tare_kg": "20", "manual_net_kg": "9.6"},
                  cases={"kg": {"task": 11, "carrier": "CP11", "pallet_type": 1}, "ea": {"task": 12, "carrier": "CP12", "pallet_type": 1}})
    attached, seen, failures = [], {}, []
    live.one = lambda sql, **kwargs: 2 if "CONTENT_VERSION" in sql else "PICK"
    live.get = lambda path: [{"pallet_type_id": 1, "physical_quantity": "0", "balance_version": 0}] if "/availability" in path else []
    live.composition = lambda uid: {"nodes": [{"version": len(attached) + 1, "cell": "PICK"}], "children": list(attached)}
    live.replay_equal = lambda key: None
    monkeypatch.setattr(runner, "tree_findings", lambda *args: [])
    def send(key, method, path, body, expect=(200,)):
        wire = live.journal.record(key, method, path, body)
        if key in seen:
            assert seen[key] == wire
        seen[key] = wire
        if key in live.journal.results:
            return live.journal.results[key]["value"]
        if key.startswith("attach."):
            task = body["child_case_task_id"]
            if task not in attached:
                attached.append(task)
            if key == lost_at and not failures:
                failures.append(key)
                live.journal.unknown = key
                live.save()
                raise OSError("reply lost after commit")
        value = {"detail": {"code": runner.EXPECTED_REFUSALS[key[4:]]}} if key.startswith("neg.") else {"ok": True}
        live.journal.outcome(key, 409 if key.startswith("neg.") else 200, value)
        live.save()
        return value
    live.send = send
    if lost_at != "after_tree":
        with pytest.raises(OSError):
            live.tree()
    else:
        live.tree()
    live.s = json.loads(live.file.read_text(encoding="utf-8"))
    live.tree()
    assert attached == [11, 12]
    assert live.s["tree_attached"] == [11, 12]
    assert len(live.s["refusals"]) == 4


def test_transport_inputs_are_explicit_json_and_never_inferred(tmp_path):
    inputs = tmp_path / "transport.json"
    inputs.write_text(json.dumps({"store_address": "QA"}), encoding="utf-8")
    assert runner.load_transport_inputs(str(inputs)) == {"store_address": "QA"}
    with pytest.raises(runner.RunnerStop, match="TRANSPORT_INPUTS_FILE_REQUIRED"):
        runner.load_transport_inputs(None)
    with pytest.raises(runner.RunnerStop, match="TRANSPORT_INPUTS_FILE_MISSING"):
        runner.load_transport_inputs(str(tmp_path / "missing.json"))
    (tmp_path / "invalid.json").write_text("[", encoding="utf-8")
    with pytest.raises(runner.RunnerStop, match="TRANSPORT_INPUTS_FILE_INVALID"):
        runner.load_transport_inputs(str(tmp_path / "invalid.json"))
    (tmp_path / "list.json").write_text("[]", encoding="utf-8")
    with pytest.raises(runner.RunnerStop, match="TRANSPORT_INPUTS_OBJECT_REQUIRED"):
        runner.load_transport_inputs(str(tmp_path / "list.json"))

def test_cleanup_expected_remainder_uses_persisted_post_load_values_only():
    state = {"articles": {"kg": "MTK", "ea": "MTE"}, "measurements": {"manual_net_kg": "9.6"}}
    assert runner.cleanup_expected_remainder(state) == {"MTK": "19.2", "MTE": "8"}
    state["transport"] = {"expected_remainder_after_load": {"MTK": "9.6", "MTE": "4"}}
    assert runner.cleanup_expected_remainder(state) == {"MTK": "9.6", "MTE": "4"}
    state["transport"]["expected_remainder_after_load"] = {"MTK": "20", "MTE": "4"}
    with pytest.raises(runner.RunnerStop, match="TRANSPORT_REMAINDER_INVALID"):
        runner.cleanup_expected_remainder(state)

def test_finalizer_sql_persists_command_and_reconciles_a_post_commit_error(work):
    live = live_with([], work)
    state, calls = {"retired": 0}, []

    def one(sql, **binds):
        return state["retired"]

    class Connection:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def cursor(self):
            return self
        def execute(self, sql, binds):
            calls.append((sql, binds))
            state["retired"] = 1
            raise OSError("post-commit disconnect")
        def commit(self):
            pass

    live.one = one
    live.connect = lambda: Connection()
    live.finalizer_sql(
        "retire.driver",
        "update RUSERS set DELETED=1 where ID=:id",
        {"id": "MT28D0123456ab"},
        "select count(*) from RUSERS where ID=:id and DELETED=1",
        {"id": "MT28D0123456ab"},
        1,
    )
    assert len(calls) == 1
    saved = live.journal.results["finalizer.retire.driver"]
    assert saved["status"] == 200 and saved["value"]["reconciled_after_error"] is True
    live.finalizer_sql(
        "retire.driver",
        "update RUSERS set DELETED=1 where ID=:id",
        {"id": "MT28D0123456ab"},
        "select count(*) from RUSERS where ID=:id and DELETED=1",
        {"id": "MT28D0123456ab"},
        1,
    )
    assert len(calls) == 1

def test_finalizer_sql_marks_unknown_when_initial_read_only_reconciliation_fails(work):
    live = live_with([], work)
    def failing_one(sql, **binds):
        raise RuntimeError("invalid bind name")
    live.one = failing_one

    with pytest.raises(RuntimeError, match="invalid bind name"):
        live.finalizer_sql(
            "repair.bad_read",
            "update RRL_SBORKA_PALLETS set DOCID=:p_new where ID=:p_id",
            {"p_new": "SAFE", "p_id": 1},
            "select count(*) from RRL_SBORKA_PALLETS where ID=:p_id and DOCID=:p_new",
            {"p_new": "SAFE", "p_id": 1},
            1,
        )

    assert live.journal.unknown == "finalizer.repair.bad_read"
    assert "finalizer.repair.bad_read" not in live.journal.results