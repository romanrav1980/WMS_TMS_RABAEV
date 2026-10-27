"""C-0187 T06: weighed-line and weighted-box CASE write paths (offline; fake Oracle cursor and a recording StockPosting port).
A mocked capture/scan here is a contract test, not hardware or live weight evidence."""
import json
from types import SimpleNamespace

import oracledb
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from api.wms_api_server.app.auth import AdminUser, get_current_admin
from api.wms_api_server.app.modules.inventory.api.error_handlers import install_stock_error_handlers
from api.wms_api_server.app.modules.inventory.api.weighted_case_routes import router
from api.wms_api_server.app.modules.inventory.contracts_stock import StockPostingError
from api.wms_api_server.app.modules.inventory.contracts_weighted_case import WeighedLineRequest, WeightedCaseRequest, weighted_case_service
from api.wms_api_server.app.modules.inventory.infrastructure import weighted_case_pick as module

CAPTURE = "A" * 64
OTHER_CAPTURE = "B" * 64


def ora(code):
    return oracledb.DatabaseError(SimpleNamespace(code=code))


class Cursor:
    """Answers only the reads the weighted CASE paths make; anything else fails the test."""
    def __init__(self, capture=None, box=None, rows=None, profiles=(), scope_error=None, sku_error=None, decode_error=None):
        self.capture, self.box, self.rows, self.profiles = capture, box, rows or [], set(profiles)
        self.scope_error, self.sku_error, self.decode_error, self.calls = scope_error, sku_error, decode_error, []

    def execute(self, sql, *args, **binds):
        self.calls.append(("execute", sql.split()[0] if sql.strip() else sql, binds)); self.last = sql

    def fetchone(self):
        assert "RRL_WH_SCALE_CAPTURE" in self.last
        return self.capture

    def fetchall(self):
        if "RRL_SKU_RECEIPT_PROFILE" in self.last:
            return list(self.profiles)
        assert "RRL_WMS_RECEIPT_UNIT" in self.last
        return self.rows

    def callproc(self, name, args):
        self.calls.append(("callproc", name, list(args)))
        if name == "RRL_CASE_TASK_ACCESS.assert_scope" and self.scope_error:
            raise ora(self.scope_error)
        if name == "RRL_WEIGHT_BOX_READ.assert_sku" and self.sku_error:
            raise ora(self.sku_error)

    def callfunc(self, name, kind, args):
        assert name == "RRL_WEIGHT_BOX_READ.decode_json"
        if self.decode_error:
            raise ora(self.decode_error)
        return json.dumps(self.box)


class Gateway:
    def __init__(self, cursor, saved=None):
        self.cursor, self.saved = cursor, saved

    def fetch_all(self, sql, params):
        assert "RRL_STOCK_OPERATION" in sql
        return [{"canonical_request": json.dumps(self.saved)}] if self.saved else []

    def transaction(self, name):
        cursor = self.cursor

        class Scope:
            def __enter__(self): return cursor
            def __exit__(self, *exc): return False
        return Scope()


@pytest.fixture
def posted(monkeypatch):
    commands = []

    class Posting:
        def post(self, command):
            commands.append(command)
            return {"operation_id": command.operation_id, "status": "APPLIED"}
    monkeypatch.setattr(module, "StockPosting", Posting)
    return commands


def line_request(**changes):
    return WeighedLineRequest(**({"operation_id": "op-line", "warehouse_scale_capture": CAPTURE, "scan_cell": "C-01", "scan_container": "SSCC1"} | changes))


def box_request(**changes):
    return WeightedCaseRequest(**({"operation_id": "op-box", "weighted_box_barcode": "BOX-1", "scan_cell": "C-01", "scan_container": "SSCC1"} | changes))


BOX = {"identity": 501, "gtin": "04600000000017", "net_weight_kg": "2.345"}
ROW = ("ART-7", "1.5", 3, 0, "UNIT-501", "2.345", "KG")


# 1. Weighed line: the accepted NET capture of exactly this task/line in the actor's scope.

def test_net_capture_of_this_line_posts_cumulative_quantity_once(posted):
    cur = Cursor(capture=("2.5", "ART-7", "1.25"))
    result = module.WeightedCasePick(Gateway(cur)).weigh_line(11, 22, line_request(), "picker")
    assert result["status"] == "APPLIED" and len(posted) == 1
    command = posted[0]
    assert command.command_type == "CASE_PICK_CONFIRM" and command.source == {"case_task_id": 11, "case_line_id": 22}
    assert command.metadata["fact_qty"] == "3.75" and command.metadata["warehouse_scale_capture"] == CAPTURE
    assert ("callproc", "RRL_CASE_TASK_ACCESS.assert_scope", [11, "picker", "case_pick_execute"]) in cur.calls
    binds = next(c[2] for c in cur.calls if c[0] == "execute" and c[2].get("p_key"))
    assert binds == {"p_key": CAPTURE, "p_task": 11, "p_line": 22}  # the read is bound to this line and NET basis in SQL


def test_capture_of_another_line_missing_or_not_net_does_not_post(posted):
    with pytest.raises(ValueError):
        module.WeightedCasePick(Gateway(Cursor(capture=None))).weigh_line(11, 22, line_request(), "picker")
    assert posted == []


def test_capture_query_requires_net_basis():
    import inspect
    assert "c.MEASUREMENT_BASIS='NET'" in inspect.getsource(module.WeightedCasePick.weigh_line)


@pytest.mark.parametrize("code", [20882, 20886])
def test_scope_denial_is_a_refusal_without_posting(posted, code):
    with pytest.raises(StockPostingError) as refused:
        module.WeightedCasePick(Gateway(Cursor(capture=("1", "A", "0"), scope_error=code))).weigh_line(11, 22, line_request(), "picker")
    assert refused.value.code == "WEIGHED_CASE_SOURCE_REJECTED" and refused.value.oracle_code == code and posted == []


def test_malformed_capture_key_is_rejected_by_the_contract():
    with pytest.raises(ValidationError):
        line_request(warehouse_scale_capture="not-a-key")


# 2. Exact replay returns the stored result once; any change conflicts and cannot post again.

def saved_line(**changes):
    request = line_request().model_dump(mode="json")
    return {"actor": "picker", "command_type": "CASE_PICK_CONFIRM", "source": {"case_task_id": 11, "case_line_id": 22},
            "metadata": {"fact_qty": "3.75", "weighed_confirmation": request}, "units": []} | changes


def test_exact_replay_reuses_stored_metadata_without_reading_the_source(posted):
    cur = Cursor()
    module.WeightedCasePick(Gateway(cur, saved=saved_line())).weigh_line(11, 22, line_request(), "picker")
    assert cur.calls == [] and len(posted) == 1 and posted[0].metadata["fact_qty"] == "3.75"


@pytest.mark.parametrize("task,line,actor,body", [
    (11, 22, "picker", line_request(warehouse_scale_capture=OTHER_CAPTURE)),
    (11, 22, "other", line_request()),
    (12, 22, "picker", line_request()),
    (11, 23, "picker", line_request()),
    (11, 22, "picker", line_request(scan_container="SSCC2")),
])
def test_changed_capture_actor_task_line_or_body_conflicts(posted, task, line, actor, body):
    with pytest.raises(StockPostingError) as refused:
        module.WeightedCasePick(Gateway(Cursor(), saved=saved_line())).weigh_line(task, line, body, actor)
    assert refused.value.code == "OPERATION_CONTENT_CONFLICT" and posted == []


def test_replay_of_a_weighted_box_operation_under_the_line_route_conflicts(posted):
    other = saved_line(metadata={"weighted_confirmation": box_request().model_dump(mode="json", exclude_none=True)})
    with pytest.raises(StockPostingError):
        module.WeightedCasePick(Gateway(Cursor(), saved=other)).weigh_line(11, 22, line_request(), "picker")
    assert posted == []


# 3. Weighted box: the physical box reserved to this line, exact KG, every marking profile, then exactly one posting.

def test_valid_reserved_box_reaches_the_posting_port_exactly_once(posted, monkeypatch):
    monkeypatch.setattr(module, "resolve_case_codes", lambda *a: ("UNIT-501",))
    cur = Cursor(box=BOX, rows=[ROW])
    module.WeightedCasePick(Gateway(cur)).confirm(11, 22, box_request(), "picker")
    assert len(posted) == 1
    command = posted[0]
    assert command.units == ("UNIT-501",) and command.metadata["fact_qty"] == "3.845" and command.metadata["weighted_policy_version"] == 3
    assert ("callproc", "RRL_WEIGHT_BOX_READ.assert_sku", ["ART-7", BOX["gtin"]]) in cur.calls


@pytest.mark.parametrize("rows", [[], [ROW, ROW]])
def test_box_not_reserved_to_this_line_or_ambiguous_is_rejected(posted, rows):
    with pytest.raises(ValueError, match="not reserved"):
        module.WeightedCasePick(Gateway(Cursor(box=BOX, rows=rows))).confirm(11, 22, box_request(), "picker")
    assert posted == []


def test_box_of_another_sku_is_rejected_by_the_native_gtin_check(posted):
    with pytest.raises(StockPostingError) as refused:
        module.WeightedCasePick(Gateway(Cursor(box=BOX, rows=[ROW], sku_error=20886))).confirm(11, 22, box_request(), "picker")
    assert refused.value.code == "WEIGHTED_BOX_SCAN_REJECTED" and posted == []


@pytest.mark.parametrize("row", [ROW[:5] + ("2.346", "KG"), ROW[:6] + ("EA",)])
def test_wrong_kg_or_non_kg_unit_is_rejected(posted, row):
    with pytest.raises(ValueError, match="net KG differ"):
        module.WeightedCasePick(Gateway(Cursor(box=BOX, rows=[row]))).confirm(11, 22, box_request(), "picker")
    assert posted == []


SCAN = {"system_code": "CHZ", "profile_code": "BOX", "code": "010460000000001721ABC"}


@pytest.mark.parametrize("marked,profiles,scans", [
    (1, {("CHZ", "BOX")}, []),                     # required marking not scanned
    (1, {("CHZ", "BOX")}, [SCAN, SCAN]),           # duplicate marking scan
    (0, set(), [SCAN]),                            # marking scanned for an unmarked SKU
    (1, set(), []),                                # policy says marked but no current profile: stale policy/profile
])
def test_missing_duplicate_or_stale_marking_is_rejected(posted, marked, profiles, scans):
    row = ROW[:3] + (marked,) + ROW[4:]
    with pytest.raises(ValueError, match="government unit profile"):
        module.WeightedCasePick(Gateway(Cursor(box=BOX, rows=[row], profiles=profiles))).confirm(11, 22, box_request(unit_scans=scans), "picker")
    assert posted == []


def test_marking_of_another_physical_unit_is_rejected(posted, monkeypatch):
    monkeypatch.setattr(module, "resolve_case_codes", lambda *a: ("UNIT-999",))
    row = ROW[:3] + (1,) + ROW[4:]
    with pytest.raises(ValueError, match="another physical unit"):
        module.WeightedCasePick(Gateway(Cursor(box=BOX, rows=[row], profiles={("CHZ", "BOX")}))).confirm(11, 22, box_request(unit_scans=[SCAN]), "picker")
    assert posted == []


def test_already_issued_box_is_not_found_again():
    import inspect
    assert "u.STOCK_STATUS!='ISSUED'" in inspect.getsource(module.prepare_weighted_case)  # a duplicate barcode after posting finds no reserved box


@pytest.mark.parametrize("code", [20886, 1403])
def test_malformed_box_label_is_a_confirmed_refusal(posted, code):
    with pytest.raises(StockPostingError) as refused:
        module.WeightedCasePick(Gateway(Cursor(decode_error=code))).confirm(11, 22, box_request(), "picker")
    assert refused.value.code == "WEIGHTED_BOX_SCAN_REJECTED" and posted == []


def test_weighted_box_replay_and_conflict(posted):
    request = box_request()
    saved = {"actor": "picker", "command_type": "CASE_PICK_CONFIRM", "source": {"case_task_id": 11, "case_line_id": 22},
             "metadata": {"weighted_confirmation": request.model_dump(mode="json", exclude_none=True)}, "units": ["UNIT-501"]}
    module.WeightedCasePick(Gateway(Cursor(), saved=saved)).confirm(11, 22, request, "picker")
    assert len(posted) == 1 and posted[0].units == ("UNIT-501",)
    with pytest.raises(StockPostingError) as refused:
        module.WeightedCasePick(Gateway(Cursor(), saved=saved)).confirm(11, 22, box_request(weighted_box_barcode="BOX-2"), "picker")
    assert refused.value.code == "OPERATION_CONTENT_CONFLICT" and len(posted) == 1


# 4. Routes: case_pick_execute and actionable confirmed refusals.

class Service:
    def __init__(self, error=None):
        self.error, self.calls = error, []

    def weigh_line(self, task, line, request, actor):
        self.calls.append(("line", task, line, actor))
        if self.error: raise self.error
        return {"status": "APPLIED"}

    def confirm(self, task, line, request, actor):
        self.calls.append(("box", task, line, actor))
        if self.error: raise self.error
        return {"status": "APPLIED"}


def client(service, permissions):
    app = FastAPI(); app.include_router(router); install_stock_error_handlers(app)
    app.dependency_overrides[get_current_admin] = lambda: AdminUser("picker", "Picker", "QA", set(permissions))
    app.dependency_overrides[weighted_case_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


LINE_BODY = {"operation_id": "op-line", "warehouse_scale_capture": CAPTURE, "scan_cell": "C-01", "scan_container": "SSCC1"}
BOX_BODY = {"operation_id": "op-box", "weighted_box_barcode": "BOX-1", "scan_cell": "C-01", "scan_container": "SSCC1"}


@pytest.mark.parametrize("path,body", [("weigh-line", LINE_BODY), ("weighted-box", BOX_BODY)])
def test_routes_require_case_pick_execute(path, body):
    service = Service()
    denied = client(service, {"case_pick_view"}).post(f"/api/case-pick/tasks/11/lines/22/{path}", json=body)
    assert denied.status_code == 403 and "case_pick_execute" in denied.json()["detail"] and service.calls == []
    ok = client(service, {"case_pick_execute"}).post(f"/api/case-pick/tasks/11/lines/22/{path}", json=body)
    assert ok.status_code == 200 and ok.json() == {"case_pick_task_id": 11, "case_pick_line_id": 22, "status": "APPLIED"}


@pytest.mark.parametrize("path,body,code", [("weigh-line", LINE_BODY, "WEIGHED_CASE_SOURCE_REJECTED"), ("weighted-box", BOX_BODY, "WEIGHTED_BOX_SCAN_REJECTED")])
def test_value_errors_are_confirmed_409_refusals(path, body, code):
    response = client(Service(ValueError("The NET capture belongs to another CASE line or is missing")), {"case_pick_execute"}).post(
        f"/api/case-pick/tasks/11/lines/22/{path}", json=body)
    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == code and detail["outcome_confirmed"] is True and detail["retry_same_operation_id"] is False and detail["message"]


@pytest.mark.parametrize("error,status,confirmed,retry", [
    (StockPostingError("WEIGHED_CASE_SOURCE_REJECTED", "op-line", 20882), 403, True, False),
    (StockPostingError("OPERATION_CONTENT_CONFLICT", "op-line"), 409, False, False),
    (StockPostingError("RESULT_UNCERTAIN", "op-line"), 503, False, True),
])
def test_posting_errors_keep_their_outcome_semantics(error, status, confirmed, retry):
    response = client(Service(error), {"case_pick_execute"}).post("/api/case-pick/tasks/11/lines/22/weigh-line", json=LINE_BODY)
    detail = response.json()["detail"]
    assert response.status_code == status and detail["outcome_confirmed"] is confirmed and detail["retry_same_operation_id"] is retry


def test_unknown_fields_are_rejected_before_any_service_call():
    service = Service()
    response = client(service, {"case_pick_execute"}).post("/api/case-pick/tasks/11/lines/22/weigh-line", json=LINE_BODY | {"weight_kg": "9"})
    assert response.status_code == 422 and service.calls == []
