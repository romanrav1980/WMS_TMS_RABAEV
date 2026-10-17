"""Resource intent wire/ACK/error contracts; mocked Oracle boundary, no DB writes."""
import json
from contextlib import contextmanager
from copy import deepcopy
from types import SimpleNamespace
import oracledb
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.wms_api_server.app.modules.resources.contracts_case_resource import CaseResourceCommand
from api.wms_api_server.app.modules.resources.contracts_task_resource import TaskResourceCommand
from api.wms_api_server.app.modules.resources.contracts_resource_intents import (
    ResourceIntentAbandon, ResourceIntentError, ResourceIntentQuery, resource_intent_service)
from api.wms_api_server.app.modules.resources.infrastructure.case_resource_commands import canonical as case_canonical
from api.wms_api_server.app.modules.resources.infrastructure.task_resource_commands import canonical as task_canonical
from api.wms_api_server.app.modules.resources.infrastructure.resource_intent_commands import (
    ResourceIntentCommands, control_wire, digest, original)
from api.wms_api_server.app.modules.resources.api.resource_intent_routes import router
from api.wms_api_server.app.modules.platform.public import get_current_user


def body(domain="CASE", **changes):
    if domain == "CASE":
        old = CaseResourceCommand(operation_id="original-intent", action="CLAIM", expected_assignment_version=9,
            resource_session_id=55, reason="Explicit Unicode reason for recovery")
        wire = case_canonical(old)
    else:
        old = TaskResourceCommand(operation_id="original-intent", action="ASSIGN", target="picker",
            expected_assignment_version=9, expected_task_signature="A" * 64, resource_session_id=55)
        wire = task_canonical(old)
    return ResourceIntentAbandon(operation_id="control-intent", domain=domain, task_id=1138,
        reason="Never received original command outcome", original_wire=wire, **changes)


def abandoned(request, **changes):
    command = original(request)
    return dict(operation_id=request.operation_id, status="ABANDONED", domain=request.domain,
        task_id=request.task_id, actor="operator", action=command.action,
        target="operator" if request.domain == "CASE" else command.target,
        original_operation_id=command.operation_id, original_wire=request.original_wire,
        original_request_sha256=digest(request.original_wire), control_request_sha256=digest(control_wire(request)),
        original_expected_assignment_version=9, assignment_version_at_abandon=12,
        outcome_confirmed=True, stock_posted=False, **changes)


class Variable:
    def __init__(self, response): self.response = response
    def getvalue(self): return self.response


class Gateway:
    def __init__(self, response=None, error=None):
        self.response, self.error, self.events, self.calls = response, error, [], []
    @contextmanager
    def transaction(self, label):
        self.events.append("begin")
        try:
            yield self
        except Exception:
            self.events.append("rollback")
            raise
        else:
            self.events.append("commit")
    def var(self, kind): return Variable(self.response)
    def execute(self, sql): self.events.append(sql)
    def callproc(self, name, args):
        self.calls.append((name, args[:-1]))
        if self.error: raise self.error


@pytest.mark.parametrize("domain", ["CASE", "TASK"])
def test_existing_canonical_builder_and_stale_original_version_preserved(domain):
    request = body(domain)
    gateway = Gateway(abandoned(request))
    ack = ResourceIntentCommands(gateway).abandon(request, "operator")
    assert ack["original_expected_assignment_version"] == 9 and ack["assignment_version_at_abandon"] == 12
    assert gateway.calls[0][1] == [control_wire(request), "operator"]
    assert gateway.events == ["begin", "commit"]
    assert json.loads(gateway.calls[0][1][0])["original_wire"] == request.original_wire


def test_noncanonical_original_refused_before_gateway_call():
    request = body().model_copy(update={"original_wire": json.dumps(json.loads(body().original_wire), indent=2)})
    gateway = Gateway()
    with pytest.raises(ResourceIntentError) as caught:
        ResourceIntentCommands(gateway).abandon(request, "operator")
    assert caught.value.status == 422 and gateway.events == []


@pytest.mark.parametrize("change", [
    {"operation_id": "wrong-control"}, {"actor": "foreign"}, {"domain": "TASK"},
    {"task_id": 999}, {"action": "START"}, {"target": "foreign"},
    {"original_operation_id": "other"}, {"original_request_sha256": "B" * 64},
    {"control_request_sha256": "B" * 64}, {"original_expected_assignment_version": 10},
    {"outcome_confirmed": False}, {"stock_posted": True}, {"status": "RECORDED"},
])
def test_wrong_native_ack_does_not_commit_control(change):
    request = body()
    response = abandoned(request)
    response.update(change)
    gateway = Gateway(response)
    with pytest.raises(ResourceIntentError) as caught:
        ResourceIntentCommands(gateway).abandon(request, "operator")
    assert caught.value.status == 503 and gateway.events[-1] == "rollback"


@pytest.mark.parametrize("domain", ["CASE", "TASK"])
def test_resolution_and_receipt_are_read_only_and_exact_identity(domain):
    request = body(domain)
    proof = abandoned(request)
    command = original(request)
    query = ResourceIntentQuery(domain=domain, task_id=1138, original_operation_id=command.operation_id,
        action=command.action, target=proof["target"], original_request_sha256=digest(request.original_wire))
    response = dict(status="ABANDONED", domain=domain, task_id=1138, actor="operator",
        original_operation_id=command.operation_id, original_request_sha256=query.original_request_sha256,
        original_receipt=None, abandonment=proof)
    gateway = Gateway(response)
    assert ResourceIntentCommands(gateway).resolution(query, "operator") == response
    assert gateway.events[1] == "set transaction read only"
    gateway = Gateway(proof)
    assert ResourceIntentCommands(gateway).receipt("control-intent", "operator") == proof
    assert gateway.events[1] == "set transaction read only"


@pytest.mark.parametrize("code,status", [(1403,404), (20882,403), (20886,409), (3113,503)])
def test_native_unknown_forbidden_conflict_outcomes_never_invent_abandonment(code,status):
    gateway = Gateway(error=oracledb.DatabaseError(SimpleNamespace(code=code)))
    with pytest.raises(ResourceIntentError) as caught:
        ResourceIntentCommands(gateway).receipt("control-intent", "operator")
    assert caught.value.status == status and gateway.events[-1] == "rollback"


def client(service):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(username="server-actor")
    app.dependency_overrides[resource_intent_service] = lambda: service
    return TestClient(app)


class Service:
    def __init__(self): self.calls = []
    def abandon(self, body, actor):
        self.calls.append((body, actor))
        raise ResourceIntentError("RESOURCE_INTENT_RECORDED_READ_REQUIRED", 409, body.operation_id)
    def resolution(self, query, actor):
        self.calls.append((query, actor))
        raise ResourceIntentError("UNKNOWN", 404, query.original_operation_id)
    def receipt(self, operation, actor):
        raise ResourceIntentError("FORBIDDEN", 403, operation)


def test_api_uses_only_server_actor_and_preserves_original_recorded_conflict():
    service = Service()
    response = client(service).post("/api/resources/metadata-intents/abandonments", json=body().model_dump())
    assert response.status_code == 409 and response.json()["detail"]["outcome_confirmed"] is False
    assert service.calls[0][1] == "server-actor"
    changed = body().model_dump(); changed["actor"] = "forged"
    assert client(service).post("/api/resources/metadata-intents/abandonments", json=changed).status_code == 422


def test_resolution_unknown_remains_404_and_invalid_domain_action_is_422():
    service = Service()
    params = dict(domain="CASE",task_id=1138,original_operation_id="old",action="CLAIM",target="server-actor",original_request_sha256="A"*64)
    response = client(service).get("/api/resources/metadata-intents/resolution",params=params)
    assert response.status_code == 404 and response.json()["detail"]["read_before_retry"] is True
    params["action"] = "ASSIGN"
    assert client(service).get("/api/resources/metadata-intents/resolution",params=params).status_code == 422


def test_control_cannot_reuse_original_operation_and_original_model_remains_strict():
    request = body().model_dump(); request["operation_id"] = "original-intent"
    with pytest.raises(ValueError): ResourceIntentAbandon.model_validate(request)
    request = body().model_dump(); value = json.loads(request["original_wire"]); value["actor"] = "forged"; request["original_wire"] = json.dumps(value)
    with pytest.raises(ValueError): ResourceIntentAbandon.model_validate(request)

@pytest.mark.parametrize("domain", ["CASE", "TASK"])
@pytest.mark.parametrize("outcome", ["APPLIED", "REJECTED"])
def test_recorded_resolution_preserves_old_receipt_and_never_abandons(domain,outcome):
    request=body(domain);command=original(request)
    ack=dict(task_id=1138,status="ASSIGNED",assignment_version=10,assigned_to="operator",
        resource_id=59,resource_session_id=55,equipment_id=None,started_at_instant=None,started_shift_time_zone=None,
        operation_id=command.operation_id,action=command.action,actor="operator",outcome=outcome,
        request_sha256=digest(request.original_wire),outcome_confirmed=True,stock_posted=False,
        changed=outcome=="APPLIED",may_create_corrected_operation=outcome=="REJECTED",
        error_code=None if outcome=="APPLIED"else"STATE_CHANGED")
    if domain=="CASE":ack.update(warehouse_id=13583852,content_version=3)
    else:ack.update(target="picker",task_signature="A"*64)
    query=ResourceIntentQuery(domain=domain,task_id=1138,original_operation_id=command.operation_id,
        action=command.action,target="operator"if domain=="CASE"else"picker",original_request_sha256=digest(request.original_wire))
    response=dict(status="RECORDED",domain=domain,task_id=1138,actor="operator",
        original_operation_id=command.operation_id,original_request_sha256=query.original_request_sha256,
        original_receipt=ack,abandonment=None)
    gateway=Gateway(deepcopy(response))
    assert ResourceIntentCommands(gateway).resolution(query,"operator")==response
    assert gateway.calls[0][0].endswith('.resolve') and gateway.events[1]=="set transaction read only"
