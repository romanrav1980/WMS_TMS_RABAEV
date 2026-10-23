"""C-0156 offline checks of the CASE pick paper sheet: CPICK barcode, READ ONLY snapshot, route, confirm metadata and the native candidate.
Live evidence of the signature on real lines: reports/tradecase/2026-10-23/claude/C0156/case-signature-*.json."""
import hashlib
import json
import pathlib
import re
import oracledb
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.schemas import CasePickLineConfirmRequest
from app.modules.platform.public import get_current_user
from app.modules.resources.public import CaseReadError
from app.case_paper_composition import case_scope
from app.modules.inventory.contracts_case_paper import CasePaperError, case_paper_service
from app.modules.inventory.domain.case_paper import REFERENCE, case_line_barcode
from app.modules.inventory.infrastructure import case_paper as subject
from app.modules.inventory.infrastructure import case_pick_commands
from app.modules.inventory.api.case_paper_routes import router

ROOT = pathlib.Path(__file__).resolve().parents[2]
MIG = ROOT / "db/migrations/2026-10-23_case_pick_paper"
SIG = "A1" * 32


class OraError:
    def __init__(self, code):
        self.code = code


class Cursor:
    def __init__(self, head, lines, fail=None):
        self.head, self.lines, self.fail, self.sql, self.rows = head, lines, fail, [], []
        self.description = None

    def execute(self, sql, params=None):
        self.sql.append(sql)
        if "RRL_CASE_PICK_PAPER.line_signature" in sql:
            if self.fail:
                raise oracledb.DatabaseError(OraError(self.fail))
            rows = [r for r in self.lines if params["line"] is None or r["LINE_ID"] == params["line"]][:params["limit"]]
        elif "from RRL_CASE_PICK_TASK t" in sql:
            rows = self.head
        elif "MARKING_REQUIRED" in sql:
            rows = [{"ARTICUL": a, "WEIGHTED_KG": int(a == "KG"), "SERIALIZED_WEIGHT_BOXES": int(a == "BOX"), "MARKING_REQUIRED": int(a == "M")}
                    for a in dict.fromkeys(r["ARTICUL"] for r in self.lines if params["line"] is None or r["LINE_ID"] == params["line"])]
        else:
            rows = []
        names = list(rows[0]) if rows else ["X"]
        self.description = [(n,) for n in names]
        self.rows = [tuple(r[n] for n in names) for r in rows]

    def fetchall(self):
        return self.rows


class Gateway:
    def __init__(self, cursor):
        self.cursor = cursor

    def transaction(self, name):
        cursor = self.cursor

        class Ctx:
            def __enter__(self):
                return cursor

            def __exit__(self, *a):
                return False
        return Ctx()


def line(i, **kw):
    return {"LINE_ID": i, "ARTICUL": "A", "PRODUCT_NAME": "P", "CELL_CODE": "C1", "PICK_SEQUENCE": i, "PLANNED_QTY": "2",
            "PICKED_QTY": "0", "STATUS": "NEW", "REQUIRED_SCAN_MODE": None, "SIGNATURE": SIG, **kw}


HEAD = [{"TASK_ID": 7, "WARE_ID": 9104, "WAVE_CODE": "W", "ORDER_NO": "O", "CUSTOMER_NAME": "C", "SSCC": "1" * 18, "STATUS": "ASSIGNED",
         "ASSIGNED_TO": "op", "ASSIGNMENT_VERSION": 3, "CONTENT_VERSION": 2}]


@pytest.fixture
def scopes():
    return []


def run(cursor, scopes, **kw):
    return subject.OracleCasePaper(Gateway(cursor), lambda cur, t, a, p: scopes.append((t, a, p))).snapshot(7, "op", **kw)


def test_barcode_is_code128_of_the_existing_identity():
    reference, svg = case_line_barcode(7, 11, SIG)
    assert reference == f"CPICK:7:11:{SIG}" and REFERENCE.fullmatch(reference)
    assert svg.startswith("<svg") and "7 / 11" in svg and svg.count("<rect") == 3 * (len(reference) + 3) + 1  # start, data, check, stop(4 bars)
    for bad in [(0, 1, SIG), (1, 0, SIG), (1, 1, SIG.lower()), (1, 1, "A" * 63)]:
        with pytest.raises(ValueError):
            case_line_barcode(*bad)


def test_snapshot_is_read_only_scoped_and_flags_device_lines(scopes):
    cur = Cursor(HEAD, [line(1), line(2, ARTICUL="M"), line(3, ARTICUL="BOX"), line(4, ARTICUL="KG"), line(5, ARTICUL="M")])
    out = run(cur, scopes)
    assert len(cur.sql) == 4  # read only, head, lines (with native signature), one policy projection for all distinct articles
    assert cur.sql[0] == "set transaction read only" and scopes == [(7, "op", "case_pick_execute")]
    assert not any(re.search(r"\b(insert|update|delete|merge)\b", s, re.I) for s in cur.sql)
    assert [x["reference"] for x in out["lines"]][:2] == [f"CPICK:7:1:{SIG}", f"CPICK:7:2:{SIG}"]
    assert [x["device_required"] for x in out["lines"]] == [None, "MARKING_SCAN_REQUIRED", "WEIGHT_LABEL_SCAN_REQUIRED", None, "MARKING_SCAN_REQUIRED"]
    assert [x["scale_reading"] for x in out["lines"]] == [False, False, False, True, False] and out["task"]["sscc"] == "1" * 18


def test_policy_projection_matches_the_marking_policy_endpoint():
    norm = lambda s: re.sub(r"\s+", "", s)
    source = (ROOT / "api/wms_api_server/app/modules/inventory/infrastructure/case_pick_policy.py").read_text(encoding="utf-8")
    original = source[source.index("select l.ARTICUL,"):source.index("from RRL_CASE_PICK_LINE l where")]
    assert norm(original) in norm(subject.POLICY)


def test_expected_signature_is_checked_for_one_line(scopes):
    assert run(Cursor(HEAD, [line(1)]), scopes, line=1, expected_signature=SIG)["lines"][0]["line_id"] == 1
    for kw, code in [(dict(line=1, expected_signature="B" * 64), "CASE_PAPER_LINE_CHANGED"), (dict(expected_signature=SIG), "CASE_PAPER_LINE_CHANGED"),
                     (dict(line=5), "CASE_LINE_NOT_FOUND")]:
        with pytest.raises(CasePaperError) as err:
            run(Cursor(HEAD, [line(1)]), scopes, **kw)
        assert err.value.code == code


def test_missing_package_bound_and_missing_task(scopes):
    for code in (904, 6550, 4067):
        with pytest.raises(CasePaperError) as err:
            run(Cursor(HEAD, [line(1)], fail=code), scopes)
        assert (err.value.code, err.value.status) == ("CASE_PAPER_NOT_AVAILABLE", 503)
    with pytest.raises(oracledb.DatabaseError):
        run(Cursor(HEAD, [line(1)], fail=1), scopes)
    with pytest.raises(CasePaperError) as err:
        run(Cursor(HEAD, [line(i) for i in range(1, subject.LINE_LIMIT + 2)]), scopes)
    assert err.value.code == "CASE_PAPER_LINE_BOUND"
    with pytest.raises(CasePaperError) as err:
        run(Cursor([], []), scopes)
    assert err.value.status == 404


def test_route_maps_errors_and_validates_signature():
    class Service:
        def snapshot(self, task, actor, line, expected):
            if task == 1:
                raise CasePaperError("CASE_CURRENT_WARE_VIEWER_REQUIRED", 403)
            if task == 2:
                raise CasePaperError("CASE_PAPER_NOT_AVAILABLE", 503)
            return {"task": task, "actor": actor, "line": line, "expected": expected}
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: type("U", (), {"username": "op"})()
    app.dependency_overrides[case_paper_service] = Service
    client = TestClient(app)
    assert client.get(f"/api/case-pick/tasks/3/paper?line=4&expected_signature={SIG}").json() == {"task": 3, "actor": "op", "line": 4, "expected": SIG}
    assert client.get("/api/case-pick/tasks/1/paper").status_code == 403
    assert client.get("/api/case-pick/tasks/2/paper").json() == {"detail": {"code": "CASE_PAPER_NOT_AVAILABLE"}}
    assert client.get("/api/case-pick/tasks/3/paper?expected_signature=abc").status_code == 422


class PostGateway:
    def __init__(self, saved=None):
        self.saved = saved

    def fetch_all(self, sql, params=None):
        if "RRL_STOCK_RELEASE" in sql:
            return [{"state": "ACTIVE"}]
        return [{"canonical_request": json.dumps(self.saved)}] if self.saved else []


def posted(monkeypatch, request, saved=None):
    seen = []
    monkeypatch.setattr(case_pick_commands, "resolve_case_codes", lambda *a: ())
    monkeypatch.setattr(case_pick_commands, "StockPosting", lambda: type("P", (), {"post": lambda self, c: seen.append(c) or {"status": "PICKED"}})())
    case_pick_commands.post_case_pick(PostGateway(saved), 7, 11, request)
    return seen[0]


def test_confirm_carries_the_sheet_version_only_when_given(monkeypatch):
    with_paper = posted(monkeypatch, CasePickLineConfirmRequest(operation_id="op-1", actor="op", fact_qty="1", expected_case_signature=SIG))
    assert with_paper.metadata["expected_case_signature"] == SIG and with_paper.metadata["requested_confirmation"]["expected_case_signature"] == SIG
    plain = posted(monkeypatch, CasePickLineConfirmRequest(operation_id="op-2", actor="op", fact_qty="1"))
    assert "expected_case_signature" not in plain.metadata and "expected_case_signature" not in plain.metadata["requested_confirmation"]
    with pytest.raises(ValueError):
        CasePickLineConfirmRequest(operation_id="op-3", actor="op", fact_qty="1", expected_case_signature="abc")


def test_exact_replay_needs_no_current_sheet_and_changed_bytes_conflict(monkeypatch):
    request = CasePickLineConfirmRequest(operation_id="op-1", actor="op", fact_qty="1", expected_case_signature=SIG)
    first = posted(monkeypatch, request)
    saved = {"actor": "op", "command_type": "CASE_PICK_CONFIRM", "source": first.source, "metadata": first.metadata, "units": []}
    assert posted(monkeypatch, request, saved).metadata == first.metadata  # replays the stored command; no signature read here
    other = CasePickLineConfirmRequest(operation_id="op-1", actor="op", fact_qty="1", expected_case_signature="B" * 64)
    with pytest.raises(case_pick_commands.StockPostingError):
        posted(monkeypatch, other, saved)
    legacy = {**saved, "metadata": {**first.metadata, "requested_confirmation": {k: v for k, v in first.metadata["requested_confirmation"].items() if k != "expected_case_signature"}}}
    plain = CasePickLineConfirmRequest(operation_id="op-1", actor="op", fact_qty="1")
    assert posted(monkeypatch, plain, legacy).source == first.source  # stored before the field existed


def text(name):
    return (MIG / name).read_text(encoding="utf-8").replace("\r\n", "\n")


def test_native_candidate_adds_one_locked_hook_and_signs_only_the_line():
    before, after = text("before_rrl_stock_case_pick_cmd.sql").splitlines(), text("002_case_pick_cmd.sql").splitlines()
    added = [x for x in after if x not in before]
    assert len(after) == len(before) + 3 and all(x in after for x in before) and len([x for x in added if not x.strip().startswith("--")]) == 1
    i = next(n for n, x in enumerate(after) if "RRL_CASE_PICK_PAPER.assert_expected" in x)
    assert "CASE_TASK_ACTOR_CONFLICT" in after[i - 3] and "CASE_CELL_CARRIER_SCAN_REQUIRED" in after[i + 2]
    assert "for update" in "\n".join(after[:i]).split("procedure execute")[-1].lower() or "lock" in "\n".join(after[:i]).lower()
    body = text("001_case_pick_paper.sql").split("package body")[1]
    assert "ASSIGNMENT_VERSION" not in body and "CONTENT_VERSION" not in body and "t.STATUS" not in body
    assert all(f in body for f in ("ASSIGNED_TO", "SSCC", "CELL_CODE", "PLANNED_QTY", "PICKED_QTY", "REQUIRED_SCAN_MODE", "POLICY_VERSION"))
    assert "-20886" in body and "insert" not in body.lower() and "update" not in body.lower()
    manifest = json.loads(text("manifest.json"))
    assert manifest["applied_by_claude"] is False and manifest["status"] == "NOT_APPLIED"
    assert all(h in text("verify.sql") for h in manifest["after_sha256"].values())
    assert manifest["before_sha256"]["RRL_STOCK_CASE_PICK_CMD:PACKAGE BODY"] in text("000_preflight.sql") and manifest["before_sha256"]["RRL_STOCK_CASE_PICK_CMD:PACKAGE BODY"] in text("rollback_verify.sql")
    for name, sha in manifest["files_sha256"].items():
        assert hashlib.sha256((MIG / name).read_bytes()).hexdigest() == sha, name


def test_composition_maps_the_existing_case_scope(monkeypatch):
    import app.case_paper_composition as composition
    def deny(cur, task, actor, permission):
        assert permission == "case_pick_execute"
        raise CaseReadError("CASE_TASK_NOT_FOUND", "x", 404)
    monkeypatch.setattr(composition, "assert_case_task_access", deny)
    with pytest.raises(CasePaperError) as err:
        case_scope(None, 7, "op", "case_pick_execute")
    assert (err.value.code, err.value.status) == ("CASE_TASK_NOT_FOUND", 404)
