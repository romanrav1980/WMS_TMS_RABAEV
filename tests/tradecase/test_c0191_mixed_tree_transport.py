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
