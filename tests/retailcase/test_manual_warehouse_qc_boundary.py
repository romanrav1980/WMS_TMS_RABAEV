"""Preserve old wire shape and reject ambiguous manual/electronic weight at HTTP input."""
from types import SimpleNamespace
from pathlib import Path
import sys
import pytest
from pydantic import ValidationError
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "api/wms_api_server"))
from app.modules.inventory.api.outgoing_quality_routes import WeightRequest, weight


BODY = dict(operation_id="MANUAL.QC.TEST", expected_composition_signature="A" * 64,
            quality_kind="WEIGHT", gross_weight="12.5", wood_weight="0")


class Recorder:
    def check(self, identifier, body, actor):
        return dict(identifier=identifier, body=body, actor=actor)


def test_old_request_has_no_new_null_field():
    result = weight(WeightRequest(**BODY), "legacy-place", SimpleNamespace(username="controller"), Recorder())
    assert result["body"] == {**BODY, "note": None}
    assert result["actor"] == "controller"


def test_manual_origin_is_explicit_and_decimal_mass_stays_exact():
    body = {**BODY, "measurement_origin": "MANUAL_CONFIRMED", "gross_weight": "12.500000001"}
    result = weight(WeightRequest(**body), "legacy-place", SimpleNamespace(username="controller"), Recorder())
    assert result["body"] == {**body, "note": None}


@pytest.mark.parametrize("capture_field", ["capture_key", "final_scale_capture"])
def test_manual_and_electronic_source_rejected_before_posting(capture_field):
    with pytest.raises(ValidationError):
        WeightRequest(**BODY, measurement_origin="MANUAL_CONFIRMED", **{capture_field: "B" * 64})


def test_arbitrary_origin_cannot_masquerade_as_manual():
    with pytest.raises(ValidationError):
        WeightRequest(**BODY, measurement_origin="SIMULATED_HARDWARE")
