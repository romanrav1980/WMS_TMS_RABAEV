import pytest
from fastapi import HTTPException
from app.routers.case_pick import return_case_carrier
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
