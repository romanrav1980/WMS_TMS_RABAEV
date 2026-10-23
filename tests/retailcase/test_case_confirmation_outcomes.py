"""CASE confirmation must retain unknown operations and reject actor/content conflicts safely."""
from types import SimpleNamespace
import pytest
from fastapi import HTTPException
from app.modules.inventory import public
from app.modules.inventory.contracts_stock import StockPostingError
from app.services.case_pick_service import CasePickService


@pytest.mark.parametrize('code,oracle,reason,status,confirmed,conflict', [
    ('REQUEST_DEADLINE',None,None,503,False,False),
    ('POSTED_CONNECTION_RESET_FAILED',None,None,503,False,False),
    ('STOCK_RULE_REJECTED',20891,None,503,False,False),
    ('OPERATION_CONTENT_CONFLICT',None,None,409,False,True),
    ('STOCK_RULE_REJECTED',20873,None,409,False,True),
    ('STOCK_RULE_REJECTED',20886,'OPERATION_CONFLICT',409,False,True),
    ('STOCK_RULE_REJECTED',20882,None,403,False,False),
    ('STOCK_RULE_REJECTED',20886,'CASE_PAPER_LINE_CHANGED',409,True,False),
])
def test_confirmation_outcome(monkeypatch,code,oracle,reason,status,confirmed,conflict):
    def post(gateway,task,line,request):
        assert (task,line,request.operation_id)==(1172,1174,'original')
        raise StockPostingError(code,'original',oracle,reason)
    monkeypatch.setattr(public,'post_existing_case_pick',post)
    service=object.__new__(CasePickService);service.gateway=object()
    with pytest.raises(HTTPException) as caught:
        service.confirm_line(1172,1174,SimpleNamespace(operation_id='original'))
    error=caught.value
    assert error.status_code==status
    assert error.detail['operation_id']=='original'
    assert error.detail['outcome_confirmed'] is confirmed
    assert error.detail['operation_id_conflict'] is conflict
