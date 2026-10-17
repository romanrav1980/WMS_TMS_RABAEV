"""Confirm shares authoritative native preflight and preserves canonical legacy grammar."""
from contextlib import contextmanager
from types import SimpleNamespace
import json
import pytest
import oracledb
from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.wms_api_server.app.modules.inventory.infrastructure.case_confirmation_scope import authorize_existing_case_confirmation
from api.wms_api_server.app.modules.inventory.contracts_case_confirmation import CaseConfirmationAccessError
from api.wms_api_server.app.modules.inventory import public
from api.wms_api_server.app.routers import case_pick
from api.wms_api_server.app.auth import get_current_admin


class Gateway:
    def __init__(self, code=None):
        self.code,self.calls=code,[]
    @contextmanager
    def transaction(self,label):
        yield self
    def execute(self,sql):
        self.calls.append(("sql",sql))
    def callproc(self,name,args):
        self.calls.append((name,args))
        if self.code:raise oracledb.DatabaseError(SimpleNamespace(code=self.code))


def test_preflight_is_readonly_current_native_guard_without_a_second_permission_algorithm():
    gateway=Gateway()
    authorize_existing_case_confirmation(7,8,"authenticated",gateway)
    assert gateway.calls[0]==("sql","set transaction read only")
    assert gateway.calls[1][0]=="RRL_CASE_TASK_ACCESS.assert_command"
    assert json.loads(gateway.calls[1][1][0])=={"command_type":"CASE_PICK_CONFIRM","source":{"case_task_id":7,"case_line_id":8}}
    assert gateway.calls[1][1][1]=="authenticated"


@pytest.mark.parametrize("code,status",[(20882,403),(20886,409),(1403,409),(3113,503)])
def test_native_authorization_and_uncertain_failure_status(code,status):
    with pytest.raises(CaseConfirmationAccessError)as error:
        authorize_existing_case_confirmation(7,8,"authenticated",Gateway(code))
    assert error.value.status==status


def client(monkeypatch,preflight,confirm):
    monkeypatch.setattr(public,"authorize_existing_case_confirmation",preflight,raising=False)
    monkeypatch.setattr(public,"CaseConfirmationAccessError",CaseConfirmationAccessError,raising=False)
    monkeypatch.setattr(case_pick,"CasePickService",lambda:SimpleNamespace(confirm_line=confirm))
    app=FastAPI();app.include_router(case_pick.router)
    app.dependency_overrides[get_current_admin]=lambda:SimpleNamespace(username="native-role-user",permissions=set())
    return TestClient(app)


def test_ordinary_identity_reaches_native_preflight_and_authenticated_actor_wins(monkeypatch):
    calls=[]
    api=client(monkeypatch,lambda task,line,actor:calls.append(("preflight",task,line,actor)),
        lambda task,line,body:calls.append(("post",body.actor,body.operation_id,str(body.fact_qty)))or{"fact_qty":"1"})
    response=api.post("/api/case-pick/tasks/7/lines/8/confirm",json={"operation_id":"original","fact_qty":"1","actor":"browser-admin"})
    assert response.status_code==200,response.text
    assert calls==[("preflight",7,8,"native-role-user"),("post","native-role-user","original","1")]


def test_current_denial_stops_before_stock_service_and_retains_original_identity(monkeypatch):
    def deny(*args):raise CaseConfirmationAccessError("CASE_CURRENT_EXECUTE_REQUIRED","Current scoped execution denied")
    def forbidden(*args):raise AssertionError("Denied preflight must not call writer")
    response=client(monkeypatch,deny,forbidden).post("/api/case-pick/tasks/7/lines/8/confirm",json={"operation_id":"original","fact_qty":"1"})
    assert response.status_code==403
    assert response.json()["detail"]["operation_id"]=="original"and response.json()["detail"]["outcome_confirmed"]is False
