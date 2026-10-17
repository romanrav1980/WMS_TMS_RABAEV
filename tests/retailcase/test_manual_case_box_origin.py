"""Frozen loading origin must agree with the source CASE QC, including manual mode."""
from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "api/wms_api_server"))
from app.modules.finance.domain.physical_boxes import physical_box_count


def evidence(origin):
    electronic = origin == "WAREHOUSE_SCALE_QC"
    qc = dict(origin=origin, capture_key="C" * 64 if electronic else None, qc_operation_id="QC.ONE",
              signature_version=4, measured_content_version=2, gross_weight_kg="12.5", tare_weight_kg="0.5", net_weight_kg="12")
    node = dict(uid="CASE:5", case_task_id=5, kind="CASE", version=3, scale_qc=qc)
    proof = dict(box_uid=node["uid"], box_content_version=3, case_box_task_id=5, measurement_origin=origin,
                 coverage_complete=1, final_scale_capture=qc["capture_key"], warehouse_qc_operation="QC.ONE",
                 signature_version=4, measured_content_version=2, gross_weight_kg="12.5", tare_weight_kg="0.5",
                 net_weight_kg="12", device_mode="TEST" if electronic else None)
    return dict(nodes=[node]), proof


@pytest.mark.parametrize("origin", ["MANUAL_CONFIRMED", "WAREHOUSE_SCALE_QC"])
def test_frozen_original_origin_accepted(origin):
    tree, proof = evidence(origin)
    assert physical_box_count(tree, [proof]) == 1


def test_manual_cannot_be_relabeled_as_device_measurement():
    tree, proof = evidence("MANUAL_CONFIRMED")
    proof["measurement_origin"] = "WAREHOUSE_SCALE_QC"
    with pytest.raises(ValueError):
        physical_box_count(tree, [proof])


def test_manual_cannot_carry_fictitious_device_mode():
    tree, proof = evidence("MANUAL_CONFIRMED")
    proof["device_mode"] = "HARDWARE"
    with pytest.raises(ValueError):
        physical_box_count(tree, [proof])
