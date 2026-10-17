"""Strict identity and terminal receipts; native business/races need separate Oracle proof."""
import hashlib
import json
from contextlib import contextmanager
from types import SimpleNamespace
import pytest
import oracledb
from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.wms_api_server.app.modules.resources.contracts_case_resource import CaseResourceCommand,CaseResourceError,case_resource_service
from api.wms_api_server.app.modules.resources.infrastructure.case_resource_commands import CaseResourceCommands,canonical
from api.wms_api_server.app.modules.resources.api.case_resource_routes import router
from api.wms_api_server.app.modules.platform.public import get_current_user


def body(**changes):
    return CaseResourceCommand(operation_id="durable-resource-id",action="CLAIM",expected_assignment_version=0,resource_session_id=54,reason="Explicit own physical work",**changes)


def ack(request,**changes):
    value=dict(task_id=1136,warehouse_id=13583852,status="ASSIGNED",assignment_version=1,content_version=2,
        assigned_to="current-user",resource_id=58,resource_session_id=54,equipment_id=None,started_at_instant=None,started_shift_time_zone=None,
        operation_id=request.operation_id,action=request.action,actor="current-user",outcome="APPLIED",request_sha256=hashlib.sha256(canonical(request).encode()).hexdigest().upper(),
        outcome_confirmed=True,may_create_corrected_operation=False,error_code=None,changed=True,stock_posted=False)
    return{**value,**changes}


class Variable:
    def __init__(self,value):self.value=value
    def getvalue(self):return self.value


class Gateway:
    def __init__(self,response,error=None):self.response,self.error,self.events,self.calls=response,error,[],[]
    @contextmanager
    def transaction(self,label):
        try:yield self
        except Exception:self.events.append("rollback");raise
        else:self.events.append("commit")
    def execute(self,sql):self.calls.append(("sql",sql))
    def var(self,kind):return Variable(json.dumps(self.response))
    def callproc(self,method,args):
        self.calls.append((method,args[:-1]))
        if self.error:raise oracledb.DatabaseError(SimpleNamespace(code=self.error,message="native refusal"))


@pytest.mark.parametrize("changes",[{"actor":"browser-admin"},{"expected_assignment_version":True},{"resource_session_id":"54"},{"reason":"        "}])
def test_invalid_or_browser_actor_intent_never_reaches_writer(changes):
    request=body().model_dump();request.update(changes)
    with pytest.raises(ValueError):CaseResourceCommand.model_validate(request)


def test_confirmed_rejection_commits_receipt_and_returns_409_with_exact_get_readback():
    request=body();saved=ack(request,outcome="REJECTED",assignment_version=0,error_code="CASE_SHIFT_UNAVAILABLE",changed=False,may_create_corrected_operation=True)
    gateway=Gateway(saved);service=CaseResourceCommands(gateway)
    app=FastAPI();app.include_router(router);app.dependency_overrides[case_resource_service]=lambda:service
    app.dependency_overrides[get_current_user]=lambda:SimpleNamespace(username="current-user",permissions=set())
    client=TestClient(app)
    response=client.post("/api/case-pick/tasks/1136/resource-commands",json=request.model_dump())
    assert response.status_code==409 and response.json()==saved
    assert gateway.events==["commit"],"The definitive ACK must be sent only after native receipt transaction commits"
    reread=client.get("/api/case-pick/resource-commands/durable-resource-id")
    assert reread.status_code==200 and reread.json()==saved
    assert("sql","set transaction read only")in gateway.calls
    assert gateway.calls[0][1][2]=="current-user"


@pytest.mark.parametrize("changes",[{"request_sha256":"0"*64},{"actor":"other"},{"operation_id":"another"},{"stock_posted":True},{"changed":1},
    {"outcome":"REJECTED","error_code":"CASE_SHIFT_UNAVAILABLE","changed":True,"may_create_corrected_operation":True}])
def test_malformed_ack_rolls_back_metadata_instead_of_confirming_or_forking(changes):
    request=body();gateway=Gateway(ack(request,**changes))
    with pytest.raises(CaseResourceError)as error:CaseResourceCommands(gateway).command(1136,request,"current-user")
    assert error.value.code=="CASE_RESOURCE_ACK_INVALID"and error.value.status==503
    assert gateway.events==["rollback"]


@pytest.mark.parametrize("native,status",[(20882,403),(20886,409),(3113,503)])
def test_exception_is_not_a_durable_rejection_and_preserves_original_intent(native,status):
    request=body();service=CaseResourceCommands(Gateway({},error=native))
    app=FastAPI();app.include_router(router);app.dependency_overrides[case_resource_service]=lambda:service
    app.dependency_overrides[get_current_user]=lambda:SimpleNamespace(username="current-user",permissions=set())
    response=TestClient(app).post("/api/case-pick/tasks/1136/resource-commands",json=request.model_dump())
    assert response.status_code==status
    assert response.json()["detail"]["outcome_confirmed"]is False
    assert response.json()["detail"]["operation_id"]==request.operation_id


def test_unicode_canonical_hash_matches_full_normalized_intent_and_sends_authenticated_actor():
    request=CaseResourceCommand(**{**body().model_dump(),"reason":"Explicit choice \u043f\u0440\u0438\u0435\u043c\u043a\u0438"})
    saved=ack(request);gateway=Gateway(saved)
    assert CaseResourceCommands(gateway).command(1136,request,"current-user")==saved
    wire=gateway.calls[0][1][1]
    assert "\\u043f"not in wire and json.loads(wire)["resource_id"]is None
    assert hashlib.sha256(wire.encode("utf-8")).hexdigest().upper()==saved["request_sha256"]
