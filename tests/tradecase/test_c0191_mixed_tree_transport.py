"""C-0191 offline: transport/store adapter input contract, request bodies, single-recipient receipt and fail-closed stops (no network, no Oracle)."""
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("c0191_transport", ROOT / "scripts/c0191_mixed_tree_transport.py")
adapter = importlib.util.module_from_spec(SPEC)
sys.modules["c0191_transport"] = adapter
SPEC.loader.exec_module(adapter)  # import performs no live work

INPUTS = {"store_address": "QA STORE 1", "vehicle_number": "MT28V1", "dock": "MT28D1", "driver_name": "C0191 QA driver", "paper_reference": "PAPER-1",
          "pallet_type_id": 1, "shipment_date": "2026-11-01", "store_policy_expected_version": 0,
          "root_measurements": {"origin": "SYNTHETIC_FIXTURE", "gross_weight_kg": "30.2", "width_m": "1.2", "depth_m": "0.8", "height_m": "1.1"},
          "qc": {"mode": "SCAN"},
          "vehicle_geometry": {"cargo_length_mm": 3000, "cargo_width_mm": 2400, "cargo_height_mm": 2400, "outer_height_mm": 3000, "outer_length_mm": 6000, "max_places": 2}}


def test_complete_inputs_pass():
    assert adapter.validate_inputs(INPUTS) == []


@pytest.mark.parametrize("path,value,code", [
    (("store_address",), "", "INPUT_REQUIRED:store_address"),
    (("pallet_type_id",), 0, "INPUT_REQUIRED:pallet_type_id"),
    (("shipment_date",), "01.11.2026", "INPUT_REQUIRED:shipment_date"),
    (("store_policy_expected_version",), -1, "INPUT_REQUIRED:store_policy_expected_version"),
    (("root_measurements", "origin"), "GUESSED", "INPUT_REQUIRED:root_measurements.origin"),
    (("root_measurements", "gross_weight_kg"), "0", "INPUT_REQUIRED:root_measurements.gross_weight_kg"),
    (("qc", "mode"), "NONE", "INPUT_REQUIRED:qc.mode"),
    (("vehicle_geometry", "max_places"), 0, "INPUT_REQUIRED:vehicle_geometry.max_places"),
])
def test_missing_fixture_inputs_are_named(path, value, code):
    import copy
    data = copy.deepcopy(INPUTS)
    target = data
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    assert code in adapter.validate_inputs(data)


def test_weight_qc_requires_its_values_and_origin():
    data = dict(INPUTS, qc={"mode": "WEIGHT"})
    found = adapter.validate_inputs(data)
    assert {"INPUT_REQUIRED:qc.origin", "INPUT_REQUIRED:qc.gross_weight", "INPUT_REQUIRED:qc.wood_weight"} <= set(found)


def test_synthetic_values_are_never_labelled_as_physical():
    assert adapter.evidence("SYNTHETIC_FIXTURE", "MT28X", "FLOOR").startswith("SYNTHETIC_FIXTURE_NOT_PHYSICAL:")
    assert adapter.evidence("OPERATOR_MEASURED", "MT28X", "FLOOR").startswith("OPERATOR_MEASURED:")
    assert len(adapter.evidence("SYNTHETIC_FIXTURE", "T" * 200, "X")) <= 100


COMPOSITION = {"nodes": [{"uid": "MT28X.PAL", "kind": "CONTAINER", "version": 7, "cell": "MT28XPK"},
                         {"uid": "CASE:1", "kind": "CASE", "case_task_id": 1, "sscc": "S1"},
                         {"uid": "CASELOT:K:1", "kind": "STOCK", "article": "K", "quantity": "9.6"},
                         {"uid": "CASE:2", "kind": "CASE", "case_task_id": 2, "sscc": "S2"},
                         {"uid": "CASELOT:E:1", "kind": "STOCK", "article": "E", "quantity": "4"}]}


def test_loading_body_is_one_nested_root_load_with_declared_measurements():
    body = adapter.loading_body("MT28X", "MT28X.PAL", COMPOSITION, 55, INPUTS)
    assert body["identifier"] == body["scan_container"] == "MT28X.PAL" and body["expected_version"] == 7 and body["scan_cell"] == "MT28XPK"
    assert body["transport_task_id"] == 55 and body["scan_vehicle"] == "MT28V1" and body["scan_dock"] == "MT28D1" and body["physical_boxes"] == []
    assert body["measurements"] == {"origin": "MANUAL_CONFIRMED", "content_version": 7, "gross_weight_kg": "30.2", "width_m": "1.2", "depth_m": "0.8", "height_m": "1.1"}


def test_receipt_counts_each_loaded_stock_leaf_once():
    assert adapter.receipt_observations(COMPOSITION) == [{"lot_uid": "CASELOT:K:1", "accepted": "9.6"}, {"lot_uid": "CASELOT:E:1", "accepted": "4"}]
    with pytest.raises(adapter.RunnerStop):
        adapter.receipt_observations({"nodes": COMPOSITION["nodes"] + [dict(COMPOSITION["nodes"][2])]})
    with pytest.raises(adapter.RunnerStop):
        adapter.receipt_observations({"nodes": COMPOSITION["nodes"][:2]})


PREVIEW = {"already_received": False, "requires_marked_recipient_flow": False, "mode": "PAPER_COUNT", "root_scan_identifier": "MT28X.PAL",
           "store_address": "QA STORE 1", "composition_signature": "A" * 64}


def test_store_receipt_is_the_single_root_pallet_for_the_single_recipient():
    body = adapter.store_receipt_body("MT28X", "MT28X.LOAD", PREVIEW, INPUTS, adapter.receipt_observations(COMPOSITION), "MT28X.PAL")
    assert body["scan_place"] == "MT28X.PAL" and body["store_address"] == "QA STORE 1" and body["load_operation_id"] == "MT28X.LOAD"
    assert body["expected_composition_signature"] == "A" * 64 and len(body["observations"]) == 2
    assert body["paper_reference"].startswith("SYNTHETIC_FIXTURE_NOT_PHYSICAL:")


@pytest.mark.parametrize("change,code", [
    ({"already_received": True}, "STORE_PLACE_ALREADY_RECEIVED"),
    ({"requires_marked_recipient_flow": True}, "STORE_MARKED_RECIPIENT_FLOW_REQUIRED"),
    ({"mode": "WEIGHT_PHOTO"}, "STORE_POLICY_NOT_PAPER_COUNT"),
    ({"root_scan_identifier": "CASE-SSCC-1"}, "STORE_ROOT_OR_RECIPIENT_MISMATCH"),
    ({"store_address": "OTHER STORE"}, "STORE_ROOT_OR_RECIPIENT_MISMATCH"),
])
def test_store_receipt_stops_instead_of_splitting_or_inventing(change, code):
    with pytest.raises(adapter.RunnerStop, match=code):
        adapter.store_receipt_body("MT28X", "MT28X.LOAD", PREVIEW | change, INPUTS, [], "MT28X.PAL")


class FakeLive:
    def __init__(self, stages=("FIXTURE", "WAVE", "PICK_KG_MANUAL_NET", "PICK_EA", "TREE"), answers=None):
        self.s = {"tag": "MT28X", "warehouse": 231000001, "stages_done": list(stages), "measurements": {"manual_net_kg": "9.6", "parent_tare_kg": "21"}}
        self.sent, self.saves, self.answers = [], 0, dict(answers or {})

    def save(self):
        self.saves += 1

    def send(self, key, method, path, body, expect=(200,)):
        self.sent.append((key, method, path, body))
        return self.answers.get(key, {})


def test_adapter_refuses_incomplete_inputs_and_an_unverified_tree():
    with pytest.raises(adapter.RunnerStop, match="TRANSPORT_INPUTS_INCOMPLETE"):
        adapter.MixedTreeTransport(FakeLive(), dict(INPUTS, dock=""))
    with pytest.raises(adapter.RunnerStop, match="C0190_TREE_NOT_VERIFIED"):
        adapter.MixedTreeTransport(FakeLive(stages=("FIXTURE",)), INPUTS)


def test_resumed_run_must_keep_the_original_inputs():
    live = FakeLive()
    adapter.MixedTreeTransport(live, INPUTS)
    with pytest.raises(adapter.RunnerStop, match="TRANSPORT_INPUTS_CHANGED_AFTER_START"):
        adapter.MixedTreeTransport(live, dict(INPUTS, vehicle_number="OTHER"))


def test_missing_real_transport_document_is_an_explicit_stop_not_a_synthetic_ack():
    live = FakeLive(answers={"t.depart": {"detail": {"message": "DOCUMENT_NOT_READY: transport document missing"}}})
    flow = adapter.MixedTreeTransport(live, INPUTS)
    flow.t["transport_task_id"] = 55
    with pytest.raises(adapter.RunnerStop, match="EXTERNAL_TRANSPORT_DOCUMENT_REQUIRED"):
        flow.depart()
    assert [k for k, *_ in live.sent] == ["t.depart"]  # nothing else (no document, no acknowledgement) was sent


def test_completed_stages_are_not_repeated_on_resume():
    live = FakeLive()
    flow = adapter.MixedTreeTransport(live, INPUTS)
    calls = []
    flow.stage("SHIPMENT", lambda: calls.append(1))
    flow.stage("SHIPMENT", lambda: calls.append(2))
    assert calls == [1] and flow.t["last_verified_stage"] == "SHIPMENT"


def test_run_reports_the_last_verified_stage_on_a_stop():
    live = FakeLive()
    flow_cls = adapter.MixedTreeTransport
    original = flow_cls.shipment
    flow_cls.shipment = lambda self: (_ for _ in ()).throw(adapter.RunnerStop("ST_CREATE_FAILED"))
    try:
        result = adapter.run(live, INPUTS)
    finally:
        flow_cls.shipment = original
    assert result == {"stopped": "ST_CREATE_FAILED", "last_verified_stage": None} and live.s["transport"]["stopped"] == "ST_CREATE_FAILED"


def test_stage_order_covers_control_load_departure_and_receipt():
    assert adapter.STAGES == ("SHIPMENT", "TRANSPORT_TASK", "FLOOR_QC_TARE", "LOAD", "TARE_HANDOVER", "DEPART", "STORE_RECEIPT")


# ---------------- K-0224 rework: DOCID <= 15 and reconciled SHIPMENT metadata ----------------

def test_st_number_fits_docid_and_is_stable_per_run():
    st = adapter.st_number_for("MT28ABCDEF123")
    assert len(st) <= adapter.DOCID_MAX == 15 and st.startswith("ST") and st.isalnum() and st == st.upper()
    assert adapter.st_number_for("MT28ABCDEF123") == st  # resume gets the same number
    assert adapter.st_number_for("MT28ABCDEF124") != st and len(adapter.st_number_for("ANY.OTHER.TAG.FORMAT.LONGER")) == 15
    with pytest.raises(adapter.RunnerStop):
        adapter.st_number_for("")


class MetaLive:
    """In-memory legacy shipment tables; metadata writes can commit and then raise (post-commit failure)."""
    def __init__(self):
        self.s = {"tag": "MT28X", "warehouse": 231000001, "stages_done": ["TREE"], "articles": {"kg": "MT28XK", "ea": "MT28XE"},
                  "measurements": {"manual_net_kg": "9.6"}}
        self.pallets, self.rows, self.fulfillments, self.saves = [], [], [], 0

    def save(self):
        self.saves += 1

    def read(self, sql, **b):
        if "from RRL_SBORKA_PALLETS where PALLET_UID" in sql:
            return [(p["id"], p["st"], p["ware"]) for p in self.pallets if p["uid"] == b["u"]]
        if "from RRL_SBORKA_PALLET_ROWS where PALLET_UID" in sql:
            return [(r["id"], r["qty"], r["docid"]) for r in self.rows if r["uid"] == b["u"] and r["article"] == b["a"]]
        if "from RRL_CUSTOMER_ORDER_FULFILLMENT" in sql:
            return [(f["id"], f["uid"], f["address"], f.get("status", "PLANNED"), f.get("qty", 0), f.get("weight", 0), f.get("source", "QA_C0191_ONLY"))
                    for f in self.fulfillments if f["order"] == b["o"] and f["pallet"] == b["s"]]
        raise AssertionError(sql)

    def one(self, sql, **b):
        if "trunc(sysdate)" in sql:
            return "2026-10-29"
        if "ST_NUMBER=:st" in sql:
            return sum(1 for p in self.pallets if p["st"] == b["st"] and p["uid"] != b["u"]) + sum(1 for r in self.rows if r["docid"] == b["st"] and r["uid"] != b["u"])
        if "CONDITION=0" in sql:
            return sum(1 for p in self.pallets if p["id"] == b["s"] and p.get("condition") == 0)
        if "RRL_CUSTOMER_ORDER where ORDER_NO" in sql:
            return {"MT28X.ORD.kg": 501, "MT28X.ORD.ea": 502}[b["n"]]
        raise AssertionError(sql)


def flow_with(live, fail_after_commit=()):
    flow = object.__new__(adapter.MixedTreeTransport)
    flow.live, flow.inputs, flow.tag, flow.ware = live, INPUTS, "MT28X", 231000001
    flow.t = live.s.setdefault("transport", {"inputs": INPUTS, "stages_done": []})
    flow.writes, flow.intent_seen = [], []
    failing = set(fail_after_commit)

    def call(function, args):
        flow.writes.append(function)
        flow.intent_seen.append(any(v.get("state") == "SENT" and v.get("intent", {}).get("target") == function for v in flow.t.get("shipment_writes", {}).values()))
        if function == "RRL_SBORKA_PALLETS_ADD2":
            live.pallets.append({"id": 900 + len(live.pallets), "st": args[0], "uid": args[3], "ware": args[8]}); result = live.pallets[-1]["id"]
        else:
            live.rows.append({"id": 700 + len(live.rows), "uid": args[0], "article": args[1], "qty": args[9], "docid": args[12]}); result = live.rows[-1]["id"]
            assert len(args[12]) <= 15  # the DOCID constraint that failed live (ORA-12899)
        if function in failing:
            failing.discard(function); raise RuntimeError("post-commit failure")
        return result

    def execute(sql, **b):
        flow.writes.append(sql.split()[0])
        if sql.startswith("update"):
            next(p for p in live.pallets if p["id"] == b["s"])["condition"] = 0
        else:
            live.fulfillments.append({"id": 300 + len(live.fulfillments), "order": b["o"], "pallet": b["s"], "uid": b["u"], "address": b["a"]})
    flow.metadata_call, flow.metadata_exec = call, execute
    return flow


def test_shipment_metadata_is_written_once_with_a_bounded_docid():
    live = MetaLive()
    flow = flow_with(live)
    st = adapter.st_number_for("MT28X")
    flow.ensure_shipment_metadata(st, "MT28X.ST.PAL")
    assert len(live.pallets) == 1 and len(live.rows) == 2 and len(live.fulfillments) == 2
    assert all(r["docid"] == st and len(st) <= 15 for r in live.rows)
    assert all(v["state"] == "DONE" for v in flow.t["shipment_writes"].values())


@pytest.mark.parametrize("failing", ["RRL_SBORKA_PALLETS_ADD2", "RRL_SBORKA_PALLET_ROWS_ADD4"])
def test_post_commit_failure_then_resume_creates_no_duplicate(failing):
    live = MetaLive()
    st = adapter.st_number_for("MT28X")
    flow = flow_with(live, fail_after_commit={failing})
    with pytest.raises(RuntimeError, match="post-commit"):
        flow.ensure_shipment_metadata(st, "MT28X.ST.PAL")
    assert any(v["state"] == "SENT" for v in flow.t["shipment_writes"].values())  # the unknown write is visible in the state
    flow2 = flow_with(live)
    flow2.t = flow.t
    flow2.ensure_shipment_metadata(st, "MT28X.ST.PAL")
    assert len(live.pallets) == 1 and len(live.rows) == 2 and len(live.fulfillments) == 2  # reconciled, nothing duplicated


def test_resume_after_completion_writes_nothing():
    live = MetaLive()
    st = adapter.st_number_for("MT28X")
    flow_with(live).ensure_shipment_metadata(st, "MT28X.ST.PAL")
    again = flow_with(live)
    again.ensure_shipment_metadata(st, "MT28X.ST.PAL")
    assert again.writes == []


def test_failed_pre_rework_st_with_a_long_number_stops_for_root_repair():
    live = MetaLive()
    live.pallets.append({"id": 1, "st": "MT28X00000001.ST", "uid": "MT28X.ST.PAL", "ware": 231000001})
    with pytest.raises(adapter.RunnerStop, match="EXISTING_ST_NUMBER_EXCEEDS_DOCID_15"):
        flow_with(live).ensure_shipment_metadata(adapter.st_number_for("MT28X"), "MT28X.ST.PAL")


def test_foreign_use_of_the_st_number_is_a_collision_stop():
    live = MetaLive()
    st = adapter.st_number_for("MT28X")
    live.rows.append({"id": 5, "uid": "OTHER.PAL", "article": "Z", "qty": 1, "docid": st})
    with pytest.raises(adapter.RunnerStop, match="ST_NUMBER_COLLISION"):
        flow_with(live).ensure_shipment_metadata(st, "MT28X.ST.PAL")


def test_mismatching_existing_row_is_not_reused():
    live = MetaLive()
    st = adapter.st_number_for("MT28X")
    live.pallets.append({"id": 9, "st": st, "uid": "MT28X.ST.PAL", "ware": 231000001, "condition": 0})
    live.rows.append({"id": 7, "uid": "MT28X.ST.PAL", "article": "MT28XK", "qty": "1", "docid": st})
    with pytest.raises(adapter.RunnerStop, match="ST_ROW_MISMATCH"):
        flow_with(live).ensure_shipment_metadata(st, "MT28X.ST.PAL")


# ---------------- K-0231 rework 2: exact persisted intent and full fulfillment reconciliation ----------------

def test_exact_intent_is_persisted_before_every_metadata_write():
    live = MetaLive()
    flow = flow_with(live)
    flow.ensure_shipment_metadata(adapter.st_number_for("MT28X"), "MT28X.ST.PAL")
    assert flow.intent_seen and all(flow.intent_seen)  # each CALL found its SENT intent already in the state
    writes = flow.t["shipment_writes"]
    assert set(writes) == {"st.pallet", "st.condition", "st.row.kg", "st.row.ea", "st.fulfillment.kg", "st.fulfillment.ea"}
    pallet = writes["st.pallet"]["intent"]
    assert pallet["kind"] == "CALL" and pallet["target"] == "RRL_SBORKA_PALLETS_ADD2" and pallet["args"][0] == adapter.st_number_for("MT28X")
    assert pallet["args"][5] == flow.t["st_day"]  # the date is fixed once in the state, so the intent is stable on resume
    assert writes["st.fulfillment.kg"]["intent"]["args"] == {"a": "QA STORE 1", "o": 501, "s": pallet and writes["st.pallet"]["result"], "u": "MT28X.ST.PAL"}


def test_changed_intent_on_resume_stops_before_reconciling_or_writing():
    live = MetaLive()
    st = adapter.st_number_for("MT28X")
    flow = flow_with(live, fail_after_commit={"RRL_SBORKA_PALLET_ROWS_ADD4"})
    with pytest.raises(RuntimeError):
        flow.ensure_shipment_metadata(st, "MT28X.ST.PAL")
    live.s["measurements"]["manual_net_kg"] = "9.7"  # regenerated row intent differs from the stored one
    again = flow_with(live)
    again.t = flow.t
    with pytest.raises(adapter.RunnerStop, match="SHIPMENT_INTENT_CHANGED:st.row.kg"):
        again.ensure_shipment_metadata(st, "MT28X.ST.PAL")
    assert again.writes == []


def test_shipment_intent_is_json_safe_and_deterministic():
    from decimal import Decimal
    from datetime import date
    one = adapter.shipment_intent("k", "CALL", "F", [Decimal("9.60"), date(2026, 10, 29), None])
    assert one == adapter.shipment_intent("k", "CALL", "F", [Decimal("9.60"), date(2026, 10, 29), None]) and one["args"] == ["9.60", "2026-10-29", None]
    assert adapter.shipment_intent("k", "EXEC", "SQL", {"b": 1, "a": 2}) == adapter.shipment_intent("k", "EXEC", "SQL", {"a": 2, "b": 1})
    with pytest.raises(adapter.RunnerStop):
        adapter.shipment_intent("k", "DROP", "X", [])


@pytest.mark.parametrize("field,value", [("uid", "OTHER.PAL"), ("address", "OTHER STORE"), ("status", "SHIPPED"), ("qty", 1), ("weight", "0.5"), ("source", "SAP")])
def test_mismatching_fulfillment_under_the_same_order_and_st_stops_before_an_insert(field, value):
    live = MetaLive()
    st = adapter.st_number_for("MT28X")
    live.pallets.append({"id": 9, "st": st, "uid": "MT28X.ST.PAL", "ware": 231000001, "condition": 0})
    for article, qty in (("MT28XK", "9.6"), ("MT28XE", "4")):
        live.rows.append({"id": len(live.rows) + 1, "uid": "MT28X.ST.PAL", "article": article, "qty": qty, "docid": st})
    row = {"id": 31, "order": 501, "pallet": 9, "uid": "MT28X.ST.PAL", "address": "QA STORE 1"}
    row[field] = value
    live.fulfillments.append(row)
    flow = flow_with(live)
    with pytest.raises(adapter.RunnerStop, match="FULFILLMENT_MISMATCH"):
        flow.ensure_shipment_metadata(st, "MT28X.ST.PAL")
    assert "insert" not in flow.writes and len(live.fulfillments) == 1


def test_fully_matching_fulfillment_is_reused_and_duplicates_stop():
    assert adapter.fulfillment_match([(5, "U", "A", "PLANNED", 0, 0, "QA_C0191_ONLY")], "U", "A") == 5
    assert adapter.fulfillment_match([], "U", "A") is None
    with pytest.raises(adapter.RunnerStop, match="FULFILLMENT_DUPLICATE"):
        adapter.fulfillment_match([(5, "U", "A", "PLANNED", 0, 0, "QA_C0191_ONLY")] * 2, "U", "A")


def test_shipment_binds_the_intact_root_once_without_detaching_children(monkeypatch):
    live = FakeLive()
    live.s.update({"articles": {"kg": "K", "ea": "E"}, "cases": {"kg": {"task": 1, "carrier": "S1"}, "ea": {"task": 2, "carrier": "S2"}}})
    flow = adapter.MixedTreeTransport(live, INPUTS)
    flow.ensure_shipment_metadata = lambda st, uid: None
    snapshot = {**COMPOSITION, "nodes": [dict(node, cell="MT28XPK") for node in COMPOSITION["nodes"]], "quantities": [{"article": "K", "base_uom": "KG", "quantity": "9.6"}, {"article": "E", "base_uom": "EA", "quantity": "4"}], "findings": []}
    live.composition = lambda identifier: snapshot
    flow.shipment()
    assert [(key, path) for key, _, path, _ in live.sent] == [("t.bind.root", "/api/warehouse-hus/bind-shipment")]
    body = live.sent[0][3]
    assert body["scanned_root"] == "MT28X.PAL" and body["expected_root_version"] == 7

class FloorTareLive(FakeLive):
    def __init__(self):
        super().__init__()
        self.s["transport"] = {"st_pallet": "MT28X.ST.PAL"}; self.s["root_tare_booking"] = "MT28X.ROOT.TARE.BOOK"

    def composition(self, root):
        return COMPOSITION

    def get(self, path):
        if path == "/api/outgoing-quality/MT28X.ST.PAL":
            return {"composition_signature": "sig"}
        if path.endswith("/availability"):
            return [{"pallet_type_id": 1, "available_quantity": "0", "balance_version": 3}]
        raise AssertionError(path)


def test_root_tare_uses_existing_command_with_root_scans_not_floor_endpoint():
    live = FloorTareLive()
    flow = object.__new__(adapter.MixedTreeTransport)
    flow.live, flow.inputs, flow.tag, flow.ware = live, INPUTS, "MT28X", 231000001
    flow.t = live.s["transport"]
    flow.root = "MT28X.PAL"
    flow.floor_qc_tare()
    calls = {key: (path, body) for key, _, path, body in live.sent}
    assert "t.floor" not in calls
    assert "t.tare.book" not in calls
    assert live.s["root_tare_booking"] == "MT28X.ROOT.TARE.BOOK"


def test_weight_qc_declares_manual_origin_instead_of_only_a_note():
    data = dict(INPUTS, qc={"mode": "WEIGHT", "origin": "OPERATOR_MEASURED", "gross_weight": "14.0", "wood_weight": "2.0"})
    live = FloorTareLive()
    flow = object.__new__(adapter.MixedTreeTransport)
    flow.live, flow.inputs, flow.tag, flow.ware = live, data, "MT28X", 231000001
    flow.t = live.s["transport"]
    flow.root = "MT28X.PAL"
    flow.floor_qc_tare()
    body = next(body for key, _, _, body in live.sent if key == "t.qc")
    assert body["measurement_origin"] == "MANUAL_CONFIRMED"
    assert "OPERATOR_MEASURED:QC_WEIGHT:MT28X" in body["note"]
