"""Late intents cannot overwrite a newer assignment, including empty and ABA handoffs."""
import pytest
from fastapi import HTTPException
from api.wms_api_server.app.schemas import CasePickTransferRequest
from api.wms_api_server.app.modules.resources.infrastructure.case_handoff import validate, replay


class Gateway:
    def __init__(self, rows):
        self.rows = rows
    def fetch_all(self, *args):
        return self.rows


def test_legacy_event_body_stays_byte_compatible_for_exact_replay():
    body = dict(to_resource_id=3, to_resource_session_id=4, to_equipment_id=None, reason="TEST",
        actor="manager", offline_event_id="HANDOFF:test", scan_container="INTERNAL:1",
        expected_content_version=2, expected_assigned_to="picker", expected_from_session_id=5)
    request = CasePickTransferRequest(**body)
    assert str(request.model_dump()) == str(body)
    rows = [dict(case_pick_task_id=12, event_type="TRANSFERRED", payload_json=str(body), created_by="manager")]
    assert replay(Gateway(rows), 12, request)


@pytest.mark.parametrize("quantity", [0, 1])
def test_assignment_aba_conflict_even_when_owner_and_content_match(quantity):
    task = dict(picked_qty=quantity, sscc="INTERNAL:1", content_version=2,
                assigned_to="picker", resource_session_id=5, assignment_version=9)
    request = CasePickTransferRequest(to_resource_id=3, expected_assignment_version=7,
        expected_content_version=2, expected_assigned_to="picker", expected_from_session_id=5)
    with pytest.raises(HTTPException) as error:
        validate(Gateway([task]), 12, request)
    assert error.value.status_code == 409
    assert error.value.detail["code"] == "CASE_HANDOFF_STALE_ASSIGNMENT_VERSION"


def test_empty_carrier_still_checks_the_expected_owner():
    task = dict(picked_qty=0, sscc="INTERNAL:1", content_version=2,
                assigned_to="new-owner", resource_session_id=6, assignment_version=9)
    with pytest.raises(HTTPException) as error:
        validate(Gateway([task]), 12, CasePickTransferRequest(to_resource_id=3,
            expected_content_version=2, expected_assigned_to="old-owner", expected_from_session_id=5))
    assert error.value.detail["code"] == "CASE_HANDOFF_STALE_OWNER_OR_CONTENT"
