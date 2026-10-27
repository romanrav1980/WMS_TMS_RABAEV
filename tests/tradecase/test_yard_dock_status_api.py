from contextlib import contextmanager
import json
from pathlib import Path
import hashlib
import pytest
from pydantic import ValidationError
from fastapi import FastAPI
from app.case_resource_composition import register_case_resource_commands
from fastapi import FastAPI
from app.case_resource_composition import register_case_resource_commands
from app.modules.resources.api.yard_dock_status_routes import _call, command, docks
from app.modules.resources.contracts_yard import YardError
from app.modules.resources.contracts_yard_status import YardDockStatusCommand
from app.modules.resources.infrastructure.yard_dock_status import OracleYardDockStatus

ROOT = Path(__file__).resolve().parents[2]


def test_command_validates_action_reason_and_forbids_extra_fields():
    with pytest.raises(ValidationError):
        YardDockStatusCommand(operation_id="dock-001", action="PAUSE", reason="maintenance")
    with pytest.raises(ValidationError):
        YardDockStatusCommand(operation_id="dock-001", action="BLOCK", reason="  ")
    with pytest.raises(ValidationError):
        YardDockStatusCommand(operation_id="dock-001", action="BLOCK", reason="repairs", blocked=False)


class Var:
    def __init__(self):
        self.value = None

    def setvalue(self, index, value):
        self.value = value

    def getvalue(self):
        return self.value


class Cursor:
    def __init__(self):
        self.request = None
        self.result = Var()
        self.call = None
        self.read_only = False

    def var(self, _kind):
        return Var()

    def execute(self, statement):
        self.read_only = statement == "set transaction read only"

    def callproc(self, name, args):
        self.call = (name, args)
        self.request = json.loads(args[1].getvalue())
        receipt = {"operation_id": self.request["operation_id"], "warehouse_id": args[0],
                   "dock": self.request["dock"], "blocked": self.request["action"] == "BLOCK",
                   "reason": self.request["reason"], "updated_at": "2026-10-27T10:00:00Z"}
        args[3].setvalue(0, json.dumps(receipt))

    def callfunc(self, name, result_type, args):
        self.call = (name, args)
        return '{"warehouse_id":12,"docks":[{"dock":"D1","blocked":true,"ambiguous":false,"reason":"repair"}]}'


class Gateway:
    def __init__(self):
        self.cursor = Cursor()
        self.label = None

    @contextmanager
    def transaction(self, label):
        self.label = label
        yield self.cursor


def test_adapter_sends_one_native_command_and_accepts_its_receipt():
    gateway = Gateway()
    service = OracleYardDockStatus(gateway)
    body = YardDockStatusCommand(operation_id="dock-op-001", action="BLOCK", reason="Broken door")
    result = service.command(12, " d1 ", body, "dispatcher")
    assert gateway.label == "TRADECASE yard dock status command"
    assert gateway.cursor.call[0] == "RRL_YARD_DOCK_STATUS_API.command"
    assert gateway.cursor.request == {"action": "BLOCK", "dock": "d1", "operation_id": "dock-op-001", "reason": "Broken door"}
    assert result["blocked"] is True and result["operation_id"] == "dock-op-001"


def test_dock_list_is_one_read_only_native_snapshot():
    gateway = Gateway()
    result = OracleYardDockStatus(gateway).docks(12, "dispatcher")
    assert gateway.label == "TRADECASE yard dock status READ ONLY"
    assert gateway.cursor.read_only is True
    assert gateway.cursor.call[0] == "RRL_YARD_DOCK_STATUS_API.docks"
    assert result["docks"][0]["reason"] == "repair"


@pytest.mark.parametrize("status,code,confirmed", [
    (403, "YARD_ACCESS_DENIED", False),
    (409, "YARD_OPERATION_CONFLICT", False),
    (409, "YARD_DOCK_AMBIGUOUS", True),
    (503, "YARD_RESULT_UNKNOWN", False),
])
def test_route_preserves_same_operation_for_uncertain_outcome(status, code, confirmed):
    with pytest.raises(Exception) as caught:
        _call(lambda: (_ for _ in ()).throw(YardError(code, status)), "dock-op-001")
    assert caught.value.detail == {"code": code, "operation_id": "dock-op-001",
        "outcome_confirmed": confirmed, "retry_same_operation_id": not confirmed}


def test_route_trims_but_preserves_legacy_dock_spelling():
    class Service:
        def command(self, warehouse, dock, body, actor):
            assert (warehouse, dock, body.action, actor) == (12, "d1", "UNBLOCK", "dispatcher")
            return {"operation_id": body.operation_id, "blocked": False}

    body = YardDockStatusCommand(operation_id="dock-op-002", action="UNBLOCK", reason="Repair complete")
    result = command(body, warehouse=12, dock=" d1 ", user=type("User", (), {"username": "dispatcher"})(), service=Service())
    assert result["blocked"] is False


def test_native_candidate_checks_scope_before_replay_and_locks_exact_dock_row():
    sql = (ROOT / "db/migrations/2026-10-27_yard_dock_status/002_status_api.sql").read_text(encoding="utf-8")
    package_body = sql.index("create or replace package body")
    body = sql[sql.index(" procedure command(", package_body):sql.index(" function docks(", package_body)]
    assert body.index("require(p_actor,'tradecase_yard_operate',p_ware)") < body.index("lock_site(p_ware)") < body.index("RRL_YARD_DOCK_STATUS_EVENT where OPERATION_ID")
    assert "e.ACTOR<>p_actor" in body and "e.REQUEST_HASH<>hash_value" in body
    assert "for update" in body and "where rowid=rid" in body
    assert "YARD_DOCK_AMBIGUOUS" in body and "YARD_DOCK_NOT_FOUND" in body
    assert "YARD_OPERATION_CONFLICT" in body
    assert "upper(trim(d.get_string('dock')))" not in body


def test_native_dock_read_does_not_invent_status_for_duplicate_or_invalid_rows():
    sql = (ROOT / "db/migrations/2026-10-27_yard_dock_status/002_status_api.sql").read_text(encoding="utf-8")
    reader = sql[sql.index(" function docks("):]
    assert "group by DOCK" in reader
    assert "x.DOCK_COUNT>1 then j.put_null('blocked')" in reader
    assert "YARD_DOCK_STATUS_INVALID" in reader and "YARD_DOCK_NAME_REQUIRED" in reader


def test_native_candidate_manifest_hashes_are_current_and_not_applied():
    migration = ROOT / "db/migrations/2026-10-27_yard_dock_status"
    manifest = json.loads((migration / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "NOT_APPLIED"
    assert manifest["migration_id"] == "2026-10-27-yard-dock-status"
    for name, digest in manifest["files_sha256"].items():
        assert hashlib.sha256((migration / name).read_bytes()).hexdigest() == digest
    assert "DOCK_STATUS_HISTORY_PRESENT" in (migration / "rollback.sql").read_text(encoding="utf-8")


def test_application_composes_dock_status_read_and_command_routes():
    app = FastAPI()
    register_case_resource_commands(app)
    routes = {(route.path, tuple(sorted(route.methods or ()))) for route in app.routes if hasattr(route, "methods")}
    assert ("/api/tradecase/warehouses/{warehouse}/yard/docks", ("GET",)) in routes
    assert ("/api/tradecase/warehouses/{warehouse}/yard/docks/{dock}/status", ("POST",)) in routes
