"""C-0152 offline checks of TRADECASE exceptions: contracts, adapter, routes and native rules (no Oracle)."""
import pathlib
import re
from types import SimpleNamespace
import oracledb
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app.modules.platform.public import get_current_user
from app.modules.inventory.api.quality_case_routes import router
from app.modules.inventory.contracts_quality_case import QualityCaseCommand, QualityCaseError, QuarantineMove, quality_case_service
from app.modules.inventory.contracts_stock import StockPostingError
from app.modules.inventory.infrastructure.quality_cases import OracleQualityCases, _error

MIGRATION = pathlib.Path(__file__).resolve().parents[2] / "db/migrations/2026-10-23_trade_quality_case"


class OraError:
    def __init__(self, code, text=""):
        self.code, self.text = code, text

    def __str__(self):
        return self.text


def ora(code, text=""):
    return oracledb.DatabaseError(OraError(code, text))


def test_case_command_arguments_are_exact():
    QualityCaseCommand(operation_id="op-00001", action="OPEN", pallet_uid="P1", reason="вздутие упаковки")
    QualityCaseCommand(operation_id="op-00001", action="DECIDE", case_id=1, expected_version=1, decision="DEFECT", note="брак подтверждён")
    QualityCaseCommand(operation_id="op-00001", action="APPROVE", case_id=1, expected_version=2, note="акт списания")
    for bad in [dict(action="OPEN", pallet_uid="P1"), dict(action="OPEN", pallet_uid="P1", reason="ok!", case_id=1),
                dict(action="DECIDE", case_id=1, expected_version=1, note="без решения"),
                dict(action="APPROVE", case_id=1, expected_version=1, note="лишнее", decision="DEFECT"),
                dict(action="APPROVE", case_id=1, note="нет версии"), dict(action="DECIDE", case_id=1, expected_version=1, note="x", decision="DEFECT"),
                dict(action="WRITE_OFF", case_id=1, expected_version=1, note="неизвестно")]:
        with pytest.raises(ValidationError):
            QualityCaseCommand(**{"operation_id": "op-00001", **bad})


@pytest.mark.parametrize("code,text,expected", [
    (20911, "ORA-20911: QUALITY_CASE_NOT_FOUND\nORA-06512", ("QUALITY_CASE_NOT_FOUND", 404)),
    (20911, "ORA-20911: QUALITY_COMPOSITION_CHANGED", ("QUALITY_COMPOSITION_CHANGED", 409)),
    (20882, "ORA-20882: QUALITY_ACCESS_DENIED", ("QUALITY_ACCESS_DENIED", 403)),
    (4043, "ORA-04043: object does not exist", ("QUALITY_NOT_AVAILABLE", 503)),
    (3113, "ORA-03113: end-of-file", ("QUALITY_RESULT_UNKNOWN", 503)),
])
def test_native_errors_map_to_refusal_hidden_unavailable_or_unknown(code, text, expected):
    error = _error(ora(code, text))
    assert (error.code, error.status) == expected


class Gateway:
    def __init__(self, fail=None, receipt='{"operation_id":"op-00001","case_id":1,"replayed":false}', release_fail=None):
        self.fail, self.receipt, self.release_fail, self.calls = fail, receipt, release_fail, []

    def transaction(self, _name):
        gateway = self

        class Tx:
            def __enter__(self):
                return gateway

            def __exit__(self, *_):
                return False
        return Tx()

    def execute(self, sql):
        self.calls.append(sql)

    def var(self, _type):
        return SimpleNamespace(setvalue=lambda _i, v: None, getvalue=lambda: self.receipt)

    def callproc(self, name, args):
        self.calls.append((name, args[0], args[2]))
        if name.endswith("assert_release") and self.release_fail:
            raise self.release_fail
        if name.endswith(".command") and self.fail:
            raise self.fail


BODY = QualityCaseCommand(operation_id="op-00001", action="DECIDE", case_id=1, expected_version=1, decision="DEFECT", note="брак")


def test_case_command_is_one_native_call_and_only_its_own_receipt_is_accepted():
    gateway = Gateway()
    assert OracleQualityCases(gateway, None).command(7, BODY, "qc")["case_id"] == 1
    assert ("RRL_TRADE_QUALITY_CASE_API.command", 7, "qc") in gateway.calls
    for broken in [Gateway(receipt='{"operation_id":"op-OTHER","case_id":1}'), Gateway(receipt='{"case_id":1}'),
                   Gateway(fail=ora(12170, "ORA-12170: timeout"))]:
        with pytest.raises(QualityCaseError) as caught:
            OracleQualityCases(broken, None).command(7, BODY, "qc")
        assert (caught.value.code, caught.value.status) == ("QUALITY_RESULT_UNKNOWN", 503)


MOVE = QuarantineMove(operation_id="op-00002", pallet_uid="P1", target_cell="Q-01", reason="подозрение на брак")


def test_quarantine_move_uses_native_access_and_does_not_gate_archived_receipts_on_a_new_case():
    posted = []
    gateway = Gateway()
    result = OracleQualityCases(gateway, lambda c: posted.append(c) or {"operation_id": c.operation_id, "status": "APPLIED"}).quarantine_move(7, MOVE, "keeper")
    assert result["status"] == "APPLIED"
    assert not any("assert_release" in str(call) for call in gateway.calls)
    command = posted[0]
    assert "source_cell" in command.metadata and command.metadata["source_cell"] is None
    assert "unit" in command.metadata and command.metadata["unit"] is None
    assert (command.command_type, command.lines, command.metadata["quantity"], command.metadata["target_cell"]) == ("MOVE_QUARANTINE", (), "0", "Q-01")
    assert command.source == {"type": "QUALITY", "warehouse_id": 7, "uid": "P1"}


def test_native_hold_and_posting_errors_keep_their_meaning():
    for error, status in [(StockPostingError("RESULT_UNCERTAIN", "op-00002"), 503), (StockPostingError("QUARANTINE_MOVE_FORBIDDEN", "op-00002", 20882), 403),
                          (StockPostingError("QUARANTINE_CELL_REQUIRED", "op-00002", 20879), 409),
                          (StockPostingError("STOCK_RULE_REJECTED", "op-00002", 20911, "QUALITY_HOLD_ACTIVE"), 409)]:
        def post(_c, error=error):
            raise error
        with pytest.raises(QualityCaseError) as caught:
            OracleQualityCases(Gateway(), post).quarantine_move(7, MOVE, "keeper")
        assert caught.value.status == status


class Service:
    def __init__(self, error=None):
        self.error = error

    def command(self, ware, body, actor):
        if self.error:
            raise self.error
        return {"operation_id": body.operation_id, "warehouse_id": ware, "actor": actor}


def client(service):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(username="qc")
    app.dependency_overrides[quality_case_service] = lambda: service
    return TestClient(app)


def test_routes_mark_unknown_outcome_for_retry_with_the_same_operation_id():
    url = "/api/tradecase/warehouses/7/exceptions/cases"
    body = {"operation_id": "op-00001", "action": "APPROVE", "case_id": 1, "expected_version": 2, "note": "акт"}
    assert client(Service()).post(url, json=body).json() == {"operation_id": "op-00001", "warehouse_id": 7, "actor": "qc"}
    unknown = client(Service(QualityCaseError("QUALITY_RESULT_UNKNOWN", 503))).post(url, json=body)
    assert unknown.status_code == 503 and unknown.json()["detail"]["retry_same_operation_id"] is True
    hidden = client(Service(QualityCaseError("QUALITY_CASE_NOT_FOUND", 404))).post(url, json=body)
    assert hidden.status_code == 404 and hidden.json()["detail"]["outcome_confirmed"] is True
    assert client(Service()).post(url, json={**body, "decision": "DEFECT"}).status_code == 422


def body_of(api, name):
    start = api.rindex(name)
    return api[start:api.index("\n end;", start)]


def test_native_rules_static():
    api, schema = ((MIGRATION / f).read_text(encoding="utf-8") for f in ("002_api.sql", "001_schema.sql"))
    for statement in re.findall(r"(?is)\b(?:select|insert|update|delete)\b[^;]*;", api):
        assert not re.search(r"\.get_(string|number|object|array)\(", statement), statement  # ORA-40573
    command = body_of(api, "procedure command(")
    assert "'OPEN'then 'tradecase_quality_control'" in command and "'APPROVE'then 'tradecase_quality_approve'" in command
    assert command.index("require(p_actor,permission") < command.index("lock_site(") < command.rindex("require(p_actor,permission")
    assert command.index("require_case_owners(") < command.index("e.ACTOR<>p_actor or e.REQUEST_HASH<>hash_value") < command.index("'replayed',true")
    opening = body_of(api, "procedure open_case(")
    assert opening.index("pallet_visible(") < opening.index("QUALITY_QUARANTINE_REQUIRED") < opening.index("QUALITY_CODE_COMPOSITION_REQUIRED")
    change = body_of(api, "procedure change_case(")
    assert change.count("assert_unchanged(v)") == 2 and "action='APPROVE'and v.STATE='DEFECT'" in change and "v.STATE:='WAITING_POSTING'" in change
    assert "release_quality_hold(v.QUALITY_HOLD_ID" in change and "POSTED" not in api  # approved is not posted: no stock write-off here
    assert "create_quality_hold('PALLET',uid_value" in opening  # the existing quality entity carries the hold
    assert "BASE_QTY" not in schema and "OWNER_ID" not in schema  # codes only, no second quantity ledger
    overview = body_of(api, "function overview(")
    assert overview.index("case_visible(") < overview.index("fetch first 100") and "put_null('discrepancies')" in overview
    assert body_of(api, "function quarantine(").index("pallet_visible(") < body_of(api, "function quarantine(").index("fetch first 200")
    # no stock effect: the package never writes stock rows
    assert not re.search(r"(?i)(insert into|update|delete from)\s+RRL_(REMAINS|WMS_RECEIPT_UNIT|PALLETS|TRADE_STOCK_ATTR)\b", api)
    assert "RRL_TRADE_QUALITY_CASE_EVENT_APPEND before update or delete" in schema and "RRL_TRADE_QUALITY_CASE_UNIT_FROZEN before update or delete" in schema
    assert "case when STATE<>'RELEASED'then PALLET_UID end" in schema
