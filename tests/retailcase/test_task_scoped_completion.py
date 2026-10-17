"""Scoped native writes retain explicit correlation, revision and canonical recovery."""
from contextlib import contextmanager
from types import SimpleNamespace
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from api.wms_api_server.app.auth import AdminUser, get_current_admin
from api.wms_api_server.app.schemas import WarehouseTaskStatusRequest
from api.wms_api_server.app.routers import warehouse_tasks
from api.wms_api_server.app.modules.inventory.contracts_task_completion import TaskCompletionAccessError
from api.wms_api_server.app.modules.inventory.infrastructure.task_completion_scope import authorize_task_completion
from api.wms_api_server.app.modules.inventory.infrastructure import task_completion
from api.wms_api_server.app.modules.inventory.contracts_stock import StockPostingError


class Gateway:
    def __init__(self, current=(0, 1), committed=0):
        self.current, self.committed, self.statements = current, committed, []
    @contextmanager
    def transaction(self, label):
        yield self
    def execute(self, statement, **binds):
        self.statements.append(statement)
    def fetchone(self):
        return (self.committed,) if len(self.statements) == 3 else self.current
    def fetch_all(self, statement, binds=None):
        return [{"state": "ACTIVE"}] if "RRL_STOCK_RELEASE" in statement else []


def test_planned_hu_preflight_delegates_to_native_authority_without_changing_wire():
    import json
    class HuGateway(Gateway):
        def callproc(self, procedure, args):
            self.native_call=(procedure,args)
    gateway=HuGateway(current=(0,0,3))
    authorize_task_completion(gateway,17,"operator","original",None)
    procedure,args=gateway.native_call
    assert procedure=="RRL_WAREHOUSE_TASK_ACCESS.assert_completion"
    assert args[1]=="operator"
    assert json.loads(args[0])=={"command_type":"HU_TASK_COMPLETE","source":{"task_id":17},"metadata":{}}
    with pytest.raises(TaskCompletionAccessError,match="TASK_OPERATION_ID_REQUIRED"):
        authorize_task_completion(gateway,17,"operator",None,None)


@pytest.mark.parametrize("current,operation,signature,committed,error", [
    ((0, 1), None, "A" * 64, 0, "TASK_OPERATION_ID_REQUIRED"),
    ((0, 1), "original", None, 0, "TASK_EXPECTED_SIGNATURE_REQUIRED"),
    ((0, 0), "original", "A" * 64, 0, "TASK_CURRENT_SCOPED_EXECUTE_REQUIRED"),
    (None, "original", "A" * 64, 0, "TASK_CURRENT_ACTIVE_ACTOR_REQUIRED"),
    ((0, 1), "original", None, 1, None),
    ((0, 1), "original", "A" * 64, 0, None),
    ((1, 0), None, None, 0, None),
])
def test_preflight_requires_correlation_and_version_except_bound_committed_replay(current, operation, signature, committed, error):
    gateway = Gateway(current, committed)
    if error:
        with pytest.raises(TaskCompletionAccessError, match=error):
            authorize_task_completion(gateway, 1, "operator", operation, signature)
    else:
        authorize_task_completion(gateway, 1, "operator", operation, signature)
    assert gateway.statements[0] == "set transaction read only"
    assert all("for update" not in sql.lower() for sql in gateway.statements)


def test_optional_signature_never_changes_an_old_canonical_request_body(monkeypatch):
    commands = []
    monkeypatch.setattr(task_completion, "_post_completion", lambda command: commands.append(command) or {})
    task_completion.complete_existing_task(Gateway(), 1, WarehouseTaskStatusRequest(operation_id="original"), "operator")
    assert "expected_task_signature" not in commands[0].metadata
    task_completion.complete_existing_task(Gateway(), 1,
        WarehouseTaskStatusRequest(operation_id="new", expected_task_signature="A" * 64), "operator")
    assert commands[1].metadata["expected_task_signature"] == "A" * 64


@pytest.mark.parametrize("error,confirmed,status", [
    (StockPostingError("RESULT_UNCERTAIN", "original"), False, 503),
    (StockPostingError("STOCK_RULE_REJECTED", "original", 20872, "OPERATION_CONFLICT"), False, 409),
    (StockPostingError("STOCK_RULE_REJECTED", "original", 20886, "TASK_SCAN_CONFLICT"), True, 409),
    (StockPostingError("STOCK_RULE_REJECTED", "original", 20882, "TASK_COMPLETE_FORBIDDEN"), False, 403),
])
def test_error_envelope_never_erases_uncertain_or_conflicting_original_command(monkeypatch, error, confirmed, status):
    class Posting:
        def post(self, command):
            raise error
    monkeypatch.setattr(task_completion, "StockPosting", Posting)
    with pytest.raises(HTTPException) as caught:
        task_completion._post_completion(SimpleNamespace())
    assert caught.value.status_code == status
    assert caught.value.detail["operation_id"] == "original"
    assert caught.value.detail["outcome_confirmed"] is confirmed


def test_http_native_only_identity_can_complete_but_cannot_assign(monkeypatch):
    calls = []
    class Service:
        gateway = Gateway()
        def complete_task(self, task, request, actor):
            calls.append((task, request.updated_by, request.operation_id, actor))
            return {"status": "DONE"}
    monkeypatch.setattr(warehouse_tasks, "WarehouseTaskService", Service)
    app = FastAPI()
    app.include_router(warehouse_tasks.router)
    app.dependency_overrides[get_current_admin] = lambda: AdminUser("operator", "Operator", "NONE", set())
    with TestClient(app) as client:
        body = dict(operation_id="original", expected_task_signature="A" * 64, updated_by="spoof")
        assert client.post("/api/warehouse-tasks/1/complete", json=body).status_code == 200
        assert calls == [(1, "operator", "original", "operator")]
        assert client.post("/api/warehouse-tasks/1/assign", json={}).status_code == 403
        assert client.post("/api/warehouse-tasks/1/complete", json={**body, "expected_task_signature": "bad"}).status_code == 422
