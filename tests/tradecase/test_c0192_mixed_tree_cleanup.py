"""C-0192 offline: cleanup only after complete delivery, only this run's objects, journaled exact commands (no network, no Oracle)."""
import copy
import importlib.util
import sys
import types
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location("c0192_cleanup", Path(__file__).resolve().parents[2] / "scripts/c0192_mixed_tree_cleanup.py")
cleanup = importlib.util.module_from_spec(SPEC)
sys.modules["c0192_cleanup"] = cleanup
SPEC.loader.exec_module(cleanup)  # import performs no live work

DRIVER, RECEIVER = "MT28D0123456ab", "MT28R0123456cd"  # the C0191 pattern: prefix + 9 hex
ALL = ["SHIPMENT", "TRANSPORT_TASK", "FLOOR_QC_TARE", "LOAD", "TARE_HANDOVER", "DEPART", "STORE_RECEIPT"]


def state(stages=ALL, **change):
    s = {"tag": "MT28X", "warehouse": 234459647, "wave": 644, "revision": 77, "lots": {"kg": "MT28X.LOT.K", "ea": "MT28X.LOT.E"},
         "carrier_lots": {"kg": ["CASELOT:K:1"], "ea": ["CASELOT:E:1"]},
         "cases": {"kg": {"task": 1182, "pallet_type": 1}, "ea": {"task": 1183, "pallet_type": 1}},
         "journal": {"results": {"t.vehicle": {"status": 201, "value": {"id": 9}}, "t.driver": {"status": 201, "value": {"id": 4}},
                                 "t.task": {"status": 200, "value": {"task_id": 55}}, "t.driver.binding": {"status": 200, "value": {"version": 1}}}},
         "transport": {"stages_done": list(stages), "last_verified_stage": stages[-1] if stages else None, "inputs": {"pallet_type_id": 7, "vehicle_number": "MT28V1"},
                       "transport_task_id": 55, "vehicle_id": 9, "driver_id": 4, "driver_user": DRIVER, "receiver_user": RECEIVER,
                       "expected_remainder_after_load": {"MT28XK": "9.6", "MT28XE": "4"}}}
    for path, value in change.items():
        target = s
        keys = path.split("__")
        for k in keys[:-1]:
            target = target[k]
        target[keys[-1]] = value
    return s


def test_complete_delivery_of_this_fixture_may_be_cleaned():
    assert cleanup.delivery_findings(state()) == []


@pytest.mark.parametrize("change,code", [
    ({"transport__stages_done": ALL[:6]}, "DELIVERY_INCOMPLETE"),
    ({"transport__stopped": "EXTERNAL_TRANSPORT_DOCUMENT_REQUIRED"}, "DELIVERY_STOPPED"),
    ({"tag": "TC03X"}, "FIXTURE_IDENTITY_INCOMPLETE"),
    ({"wave": None}, "FIXTURE_IDENTITY_INCOMPLETE"),
    ({"transport__driver_user": "admin"}, "FOREIGN_OR_MISSING_USER:driver_user"),
    ({"transport__receiver_user": "TC03QA1"}, "FOREIGN_OR_MISSING_USER:receiver_user"),
    ({"transport__vehicle_id": 10}, "TRANSPORT_ID_NOT_FROM_THIS_RUN:vehicle_id"),
    ({"transport__transport_task_id": 99}, "TRANSPORT_ID_NOT_FROM_THIS_RUN:transport_task_id"),
    ({"transport__expected_remainder_after_load": {}}, "EXPECTED_REMAINDER_AFTER_LOAD_MISSING"),
])
def test_incomplete_delivery_or_foreign_identifiers_stop_before_cleanup(change, code):
    assert any(f.startswith(code) for f in cleanup.delivery_findings(state(**change)))
    assert cleanup.cleanup_plan(state(**change))[0].startswith("STOP:")


def test_plan_returns_tare_between_two_actors_finishes_the_wave_and_retires_only_run_users():
    assert cleanup.cleanup_plan(state()) == ["TARE_RETURN_OFFER:driver", "TARE_RETURN_ACCEPT:warehouse", "TARE_COUNT_ZERO:root", "DRIVER_BINDING_OFF",
                                             "WAVE_FINISH_EXECUTION", "VERIFY_OWN_STOCK_SCOPE", "INVENTORY_COUNT_OWN_LOTS_ZERO", "VERIFY_WAREHOUSE_EMPTY",
                                             "STOP:RETIRE_REQUIRES_DURABLE_OWNER_FINALIZER"]
    assert not any("DETACH" in step or "RETURN:" in step.replace("TARE_RETURN", "") for step in cleanup.cleanup_plan(state()))  # departed tree untouched


def test_root_tare_is_not_closed_twice_when_c0190_closes_the_same_pallet_type():
    s = state(transport__inputs={"pallet_type_id": 1, "vehicle_number": "MT28V1"})
    assert cleanup.zero_root_tare_here(s["transport"], s["cases"]) is False and "TARE_COUNT_ZERO:by_C0190_cleanup" in cleanup.cleanup_plan(s)


OWN = {"MT28X.LOT.K", "MT28X.LOT.E", "CASELOT:K:1", "CASELOT:E:1"}
ROWS = [("MT28X.LOT.K", "PK", "MT28XK", "KG", 3, "9.6"), ("MT28X.LOT.E", "PE", "MT28XE", "EA", 3, "4")]
EXPECTED = {"MT28XK": "9.6", "MT28XE": "4"}


def test_own_remainder_passes_the_stock_scope():
    assert cleanup.stock_findings(ROWS, 0, OWN, EXPECTED) == []


@pytest.mark.parametrize("rows,reservations,code", [
    (ROWS + [("SHARED.LOT", "PK", "MT28XK", "KG", 1, "0")], 0, "FOREIGN_UID:SHARED.LOT"),
    (ROWS + [("MT28X.LOT.K", "PK", "OTHER", "EA", 1, "0")], 0, "FOREIGN_ARTICLE:OTHER"),
    (ROWS[:1], 0, "REMAINDER_MISMATCH:MT28XE"),
    (ROWS, 2, "ACTIVE_RESERVATIONS:2"),
])
def test_foreign_rows_or_unexpected_quantities_stop_the_count(rows, reservations, code):
    assert any(f.startswith(code) for f in cleanup.stock_findings(rows, reservations, OWN, EXPECTED))


class FakeJournal:
    def __init__(self, results):
        self.results = results


class FakeLive:
    def __init__(self, s, rows=ROWS, reservations=0, left=(0, 0), wave=None, balances=None):
        self.s, self.journal, self.http = s, FakeJournal(s["journal"]["results"]), "admin-client"
        self.sent, self.posts, self.sql, self.replays = [], [], [], []
        self.rows, self.reservations, self.left = rows, reservations, left
        self.wave = wave if wave is not None else {"ready": True, "completed": False}
        self.balances = balances if balances is not None else [{"custodian_kind": "WAREHOUSE", "custodian_id": "234459647", "pallet_type_id": 7,
                                                                 "condition_code": "GOOD", "quantity": "1", "balance_version": 5}]

    def save(self):
        pass

    def send(self, key, method, path, body, expect=(200,)):
        self.sent.append((key, method, path, body, self.http)); return {}

    def post(self, key, kind, metadata, source):
        self.posts.append((key, kind, metadata, source)); return {}

    def replay_equal(self, key):
        self.replays.append(key)

    def get(self, path):
        return self.wave if path.endswith("/execution") else self.balances

    def read(self, sql, **binds):
        return self.rows if "RRL_REMAINS" in sql else []

    def one(self, sql, **binds):
        if "PASS" in sql:
            return "secret"
        if "RESERVATION" in sql:
            return self.reservations
        return self.left

    def connect(self):
        live = self

        class Conn:
            def __enter__(self): return self
            def __exit__(self, *e): return False
            def cursor(self):
                class Q:
                    def execute(self, sql, **b): live.sql.append((sql.split()[0], b))
                return Q()
            def commit(self): live.sql.append(("commit", {}))
        return Conn()


@pytest.fixture
def no_network(monkeypatch):
    monkeypatch.setitem(sys.modules, "httpx", types.SimpleNamespace(Client=lambda auth, timeout: f"client:{auth[0]}"))


SAFE = ["tare_return", "tare_zero", "binding_off", "wave_finish", "own_stock_zero"]


def test_safe_stages_complete_then_cleanup_stops_before_any_user_or_right_mutation(no_network):
    live = FakeLive(state())
    result = cleanup.run(live)
    assert result["stopped"].startswith("RETIRE_REQUIRES_DURABLE_OWNER_FINALIZER") and result["steps"] == SAFE
    assert "retire" not in live.s["c0192"]["steps_done"] and live.s["c0192"]["retire_pending"]["users"] == [DRIVER, RECEIVER]
    assert live.sql == []  # no RUSERS/RIGHTS DML (and no connect at all)
    assert [k for k, *_ in live.sent] == ["c.tare.return.offer", "c.tare.return.accept", "c.tare.zero", "c.driver.binding.off", "c.wave.finish"]  # no rights API either
    assert live.sent[0][4] == f"client:{DRIVER}" and live.sent[1][4] == "admin-client"  # two distinct actors
    assert live.sent[0][3]["from_kind"] == "VEHICLE" and live.sent[0][3]["to_kind"] == "WAREHOUSE"
    assert live.sent[2][3]["expected_version"] == 5 and live.sent[3][3] == {"user_id": DRIVER, "active": False, "expected_version": 1}
    assert live.sent[4][3] == {"operation_id": "MT28X.C.WAVE.FINISH"} and live.replays == ["c.wave.finish"]
    assert live.posts[0][1] == "INVENTORY_COUNT" and [c["uid"] for c in live.posts[0][2]["counts"]] == ["MT28X.LOT.K", "MT28X.LOT.E"]


def test_resume_after_the_retire_stop_repeats_no_completed_command_and_stops_again(no_network):
    live = FakeLive(state())
    cleanup.run(live)
    sent, posts, replays = list(live.sent), list(live.posts), list(live.replays)
    result = cleanup.run(live)
    assert result["stopped"].startswith("RETIRE_REQUIRES_DURABLE_OWNER_FINALIZER")
    assert live.sent == sent and live.posts == posts and live.replays == replays and live.sql == []


def test_foreign_stock_stops_before_any_count_and_before_users_are_retired(no_network):
    live = FakeLive(state(), rows=ROWS + [("SHARED.LOT", "PK", "MT28XK", "KG", 1, "1")])
    result = cleanup.run(live)
    assert result["stopped"].startswith("STOCK_SCOPE_REFUSED") and live.posts == [] and live.sql == []


def test_wave_not_ready_stops(no_network):
    live = FakeLive(state(), wave={"ready": False, "completed": False})
    assert cleanup.run(live)["stopped"].startswith("WAVE_NOT_READY_TO_FINISH") and live.posts == []


def test_incomplete_delivery_sends_nothing(no_network):
    live = FakeLive(state(stages=ALL[:6]))
    result = cleanup.run(live)
    assert result["stopped"].startswith("CLEANUP_REFUSED:DELIVERY_INCOMPLETE") and live.sent == [] and live.posts == []


def test_warehouse_left_with_stock_after_the_count_is_a_stop(no_network):
    live = FakeLive(state(), left=(1, 0))
    assert cleanup.run(live)["stopped"].startswith("WAREHOUSE_NOT_EMPTY_AFTER_CLEANUP")


def test_resumed_cleanup_does_not_repeat_completed_steps(no_network):
    s = state()
    live = FakeLive(s, wave={"ready": False, "completed": False})
    cleanup.run(live)  # stops at the wave after tare/binding
    sent_before = [k for k, *_ in live.sent]
    live.wave = {"ready": True, "completed": False}
    cleanup.run(live)
    keys = [k for k, *_ in live.sent]
    assert keys[:len(sent_before)] == sent_before and keys.count("c.tare.return.offer") == 1 and "c.wave.finish" in keys
