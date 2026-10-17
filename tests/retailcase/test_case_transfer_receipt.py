"""Only an immutable original event proves a particular handoff."""
from contextlib import contextmanager
import pytest
from api.wms_api_server.app.schemas import CasePickTransferRequest
from api.wms_api_server.app.modules.resources.infrastructure.case_transfer_receipt import transfer_receipt
from api.wms_api_server.app.modules.resources.contracts_case_resource import CaseResourceError


class Gateway:
    def __init__(self, rows):
        self.rows, self.calls = rows, []
    @contextmanager
    def transaction(self, label):
        yield self
    def execute(self, sql, **binds):
        self.calls.append((sql, binds))
    def callproc(self, name, args):
        self.calls.append((name, args))
    def fetchall(self):
        return self.rows


def payload():
    return CasePickTransferRequest(to_resource_id=3, to_resource_session_id=4,
        actor="manager", offline_event_id="HANDOFF:test", expected_content_version=2,
        expected_assigned_to="picker", expected_from_session_id=5, scan_container="INTERNAL:123")


def test_receipt_rechecks_scope_and_reads_original_body_in_one_snapshot():
    request = payload()
    gateway = Gateway([(12, "TRANSFERRED", str(request.model_dump()), "manager")])
    result = transfer_receipt(gateway, 12, "HANDOFF:test", "manager")
    assert result["request"]["expected_assigned_to"] == "picker"
    assert result["outcome_confirmed"] and result["source"] == "IMMUTABLE_TRANSFERRED_EVENT"
    assert gateway.calls[0][0] == "set transaction read only"
    assert gateway.calls[1] == ("RRL_CASE_TRANSFER_SCOPE.assert_manager", [12, "manager"])


def test_absent_receipt_does_not_confirm_cancellation():
    with pytest.raises(CaseResourceError) as error:
        transfer_receipt(Gateway([]), 12, "HANDOFF:absent", "manager")
    assert error.value.status == 404 and error.value.code == "CASE_TRANSFER_RECEIPT_NOT_OBSERVED"


@pytest.mark.parametrize("task,author", [(13, "manager"), (12, "other-manager")])
def test_another_task_or_actor_cannot_supply_the_receipt(task, author):
    with pytest.raises(CaseResourceError) as error:
        transfer_receipt(Gateway([(task, "TRANSFERRED", str(payload().model_dump()), author)]), 12, "HANDOFF:test", "manager")
    assert error.value.status == 403


def test_corrupt_payload_cannot_become_a_success():
    with pytest.raises(CaseResourceError) as error:
        transfer_receipt(Gateway([(12, "TRANSFERRED", "{broken", "manager")]), 12, "HANDOFF:test", "manager")
    assert error.value.status == 503
