import pytest
from fastapi import HTTPException
from app.routers.case_pick import move_case_carrier, return_case_carrier
from app.modules.inventory.contracts_case_return import CaseCarrierReturnRequest
from app.modules.inventory.contracts_stock import StockPostingError
from app.modules.inventory import public


@pytest.mark.parametrize("code,oracle,status,confirmed", [
    ("RULE_REJECTED", 20882, 403, True),
    ("RULE_REJECTED", 20886, 409, True),
    ("RESULT_UNCERTAIN", None, 503, False),
])
def test_return_uses_native_scope_and_preserves_uncertain_retry(monkeypatch, code, oracle, status, confirmed):
    def fail(task, request, actor):
        assert (task, actor) == (1149, "current-user")
        raise StockPostingError(code, request.operation_id, oracle, "NATIVE_RULE")
    monkeypatch.setattr(public, "return_existing_case_carrier", fail)
    request = CaseCarrierReturnRequest(operation_id="RETURN.ONE", scan_container="INTERNAL.PALLET",
        expected_content_version=1, destinations={"LOT.ONE": "CELL.ONE"})
    user = type("User", (), {"username": "current-user"})()
    with pytest.raises(HTTPException) as error:
        return_case_carrier(1149, request, user)
    assert error.value.status_code == status
    assert error.value.detail["operation_id"] == "RETURN.ONE"
    assert error.value.detail["outcome_confirmed"] is confirmed
    assert error.value.detail["retry_same_operation_id"] is (not confirmed)


@pytest.mark.parametrize("error,oracle,status,confirmed,retry", [
    ("RULE_REJECTED", 20882, 403, True, False),
    ("RESULT_UNCERTAIN", None, 503, False, True),
])
def test_move_carrier_does_not_mark_access_denial_as_unknown(monkeypatch, error, oracle, status, confirmed, retry):
    class Service:
        def execute(self, operation, actor, task, scan, cell, version):
            assert (operation, actor, task, scan, cell, version) == (
                "MOVE.ONE", "current-user", 1149, "INTERNAL.PALLET", "CELL.2", 1)
            raise StockPostingError(error, operation, oracle, "NATIVE_RULE")

    monkeypatch.setattr(public, "build_case_carrier_move_service", lambda: Service())
    request = type("Request", (), {"operation_id": "MOVE.ONE", "scan_container": "INTERNAL.PALLET",
        "scanned_to_cell": "CELL.2", "expected_content_version": 1})()
    user = type("User", (), {"username": "current-user"})()

    with pytest.raises(HTTPException) as failure:
        move_case_carrier(1149, request, user)

    assert failure.value.status_code == status
    assert failure.value.detail["outcome_confirmed"] is confirmed
    assert failure.value.detail["retry_same_operation_id"] is retry
