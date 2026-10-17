"""Identity-only HTTP bridge; native current authority and original actor govern approval."""
import sys
from pathlib import Path
from types import SimpleNamespace
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'api/wms_api_server'))
from app.routers import case_pick
from app.modules.inventory.public import StockPostingError
from app.modules.platform.public import get_current_user


@pytest.fixture
def bridge(monkeypatch):
    calls=[]
    class Service:
        failure=None
        def approve_short(self,short,body):
            calls.append((short,body.model_dump()))
            if self.failure:raise self.failure
            return dict(status='APPROVED')
    service=Service();monkeypatch.setattr(case_pick,'CasePickService',lambda:service)
    app=FastAPI();app.include_router(case_pick.router)
    app.dependency_overrides[get_current_user]=lambda:SimpleNamespace(username='scoped-manager',permissions=set())
    with TestClient(app)as client:yield client,service,calls


def test_role_only_identity_reaches_owner_and_replaces_forged_actor(bridge):
    client,_,calls=bridge
    response=client.post('/api/case-pick/shorts/7/approve',json=dict(operation_id='APPROVE.7',actor='admin'))
    assert response.status_code==200
    assert calls[0][0]==7 and calls[0][1]['actor']=='scoped-manager'


@pytest.mark.parametrize('code,oracle,status,retry',[
    ('STOCK_RULE_REJECTED',20882,403,False),
    ('STOCK_RULE_REJECTED',20851,409,False),
    ('OPERATION_CONTENT_CONFLICT',None,409,False),
    ('RESULT_UNCERTAIN',None,503,True),
])
def test_native_denial_conflict_and_uncertain_result_keep_operation_id(bridge,code,oracle,status,retry):
    client,service,_=bridge
    service.failure=StockPostingError(code,'APPROVE.7',oracle,'native decision')
    response=client.post('/api/case-pick/shorts/7/approve',json=dict(operation_id='APPROVE.7'))
    assert response.status_code==status
    assert response.json()['detail']['operation_id']=='APPROVE.7'
    assert response.json()['detail']['retry_same_operation_id']is retry


def test_nonpositive_short_never_reaches_owner(bridge):
    client,_,calls=bridge
    assert client.post('/api/case-pick/shorts/0/approve',json=dict(operation_id='APPROVE.7')).status_code==422
    assert not calls
