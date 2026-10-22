"""C-0153 offline checks: native write-off posting kind, native quality hold, migration integrity, adapter and route (no Oracle)."""
import hashlib
import json
import pathlib
import re
from types import SimpleNamespace
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app.modules.platform.public import get_current_user
from app.modules.inventory.api.quality_case_routes import router
from app.modules.inventory.contracts_quality_case import QualityCaseError, QualityWriteOff, quality_case_service
from app.modules.inventory.contracts_stock import StockPostingError
from app.modules.inventory.infrastructure.quality_cases import OracleQualityCases

M = pathlib.Path(__file__).resolve().parents[2] / "db/migrations/2026-10-23_trade_quality_posting"
read = lambda name: (M / name).read_text(encoding="utf-8")
BODY = QualityWriteOff(operation_id="op-00009", case_id=4, expected_version=3)


def body_of(sql, name):
    start = sql.rindex(name)
    return sql[start:sql.index("\n end;", start)]


def test_write_off_is_one_native_posting_command_and_only_its_receipt_counts():
    posted = []
    service = OracleQualityCases(None, lambda c: posted.append(c) or {"operation_id": c.operation_id, "status": "POSTED"})
    assert service.write_off(7, BODY, "boss")["status"] == "POSTED"
    command = posted[0]
    assert (command.command_type, command.lines, command.source, command.metadata) == (
        "TRADE_QUALITY_WRITE_OFF", (), {"case_id": 4, "warehouse_id": 7}, {"expected_case_version": 3})
    assert json.loads(command.canonical_json())["command_type"] == "TRADE_QUALITY_WRITE_OFF"  # registered as a no-lines command
    with pytest.raises(QualityCaseError) as caught:
        OracleQualityCases(None, lambda c: {"operation_id": "op-OTHER"}).write_off(7, BODY, "boss")
    assert (caught.value.code, caught.value.status) == ("QUALITY_RESULT_UNKNOWN", 503)


@pytest.mark.parametrize("error,expected", [
    (StockPostingError("RULE_REJECTED", "op-00009", 20886, "QUALITY_HOLD_ACTIVE"), ("QUALITY_HOLD_ACTIVE", 409)),
    (StockPostingError("RULE_REJECTED", "op-00009", 20886, "QUALITY_COMPOSITION_CHANGED"), ("QUALITY_COMPOSITION_CHANGED", 409)),
    (StockPostingError("SCOPE", "op-00009", 20882), ("SCOPE", 403)),
    (StockPostingError("RESULT_UNCERTAIN", "op-00009"), ("RESULT_UNCERTAIN", 503)),
])
def test_runner_refusals_keep_their_native_reason(error, expected):
    def post(_command):
        raise error
    with pytest.raises(QualityCaseError) as caught:
        OracleQualityCases(None, post).write_off(7, BODY, "boss")
    assert (caught.value.code, caught.value.status) == expected


def test_route_marks_unknown_outcome_for_retry():
    class Service:
        def __init__(self, error=None):
            self.error = error

        def write_off(self, ware, body, actor):
            if self.error:
                raise self.error
            return {"operation_id": body.operation_id, "warehouse_id": ware, "actor": actor}

    def client(service):
        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(username="boss")
        app.dependency_overrides[quality_case_service] = lambda: service
        return TestClient(app)
    url, body = "/api/tradecase/warehouses/7/exceptions/write-offs", {"operation_id": "op-00009", "case_id": 4, "expected_version": 3}
    assert client(Service()).post(url, json=body).json()["warehouse_id"] == 7
    unknown = client(Service(QualityCaseError("RESULT_UNCERTAIN", 503))).post(url, json=body)
    assert unknown.status_code == 503 and unknown.json()["detail"]["retry_same_operation_id"] is True
    assert client(Service()).post(url, json={**body, "quantity": "1"}).status_code == 422
    with pytest.raises(ValidationError):
        QualityWriteOff(operation_id="op-00009", case_id=4, expected_version=0)


def test_write_off_owner_checks_everything_and_writes_everything_in_one_transaction():
    sql = read("004_quality_writeoff.sql")
    describe = body_of(sql, "procedure describe(")
    for rule in ["q.STATE<>'WAITING_POSTING'", "q.VERSION_NO<>v_expected", "assert_scope(v_case,p_actor)", "v_h<>0",
                 "BLOCKED_FOR_REMAINS,0)=1", "RRL_WMS_HU_LINK", "composition_hash(q.PALLET_UID)<>q.COMPOSITION_HASH",
                 "u.UNIT_VERSION=cu.UNIT_VERSION", "u.HARD_RESERVATION_ID is null", "actual<>n or total<>n", "total<>v_qty"]:
        assert rule in describe, rule
    scope = body_of(sql, "procedure assert_scope(")
    assert "'tradecase_quality_post'" in scope and "assert_owner(p_actor,v_ware,o.OWNER_ID,1)" in scope
    compile_ = body_of(sql, "procedure compile_command(")
    assert "row_key(r,'RRL_TRADE_QUALITY_CASE'" in compile_ and "stock_closure(" in compile_ and "anchor(r,60,'UNIT'" in compile_
    assert "SAP.OUTBOX:QUALITY_WRITE_OFF:" in compile_ and "declare_stock_events" in compile_
    execute = body_of(sql, "procedure execute_command(")
    order = ["CLOSURE_CHANGED: quality write-off", "RRL_STOCK_EFFECT_CORE.consume(", "p_quality_case=>v_case", "set STATE='POSTED'",
             "sql%rowcount<>1", "release_quality_hold(", "enqueue_stock_events(", "insert into RRL_SAP_RECEIPT_OUTBOX"]
    positions = [execute.index(x) for x in order]
    assert positions == sorted(positions) and "'external_sap_ack',false" in execute
    assert "kind_name<>'TRADE_QUALITY_WRITE_OFF'" in body_of(sql, "procedure validate_consume(")
    assert "accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_EFFECT_CORE)" in sql


def test_shared_owners_change_only_by_the_registration():
    effect, effect_spec = read("002_effect_core.sql"), read("002_effect_core_spec.sql")
    assert "package RRL_STOCK_QUALITY_WRITEOFF)" in effect_spec and "p_quality_case number default null" in effect_spec
    assert ">1 then raise_application_error(-20886,'CONSUMPTION_ONE_EXPLICIT_EXCEPTION_REQUIRED')" in effect
    quality = effect[effect.index("if p_quality_case is not null"):effect.index("elsif p_disposal_receipt")]
    assert "validate_consume(p_quality_case" in quality and "assert_quarantine(" in quality
    posting = read("007_stock_posting_api.sql")
    assert posting.count("RRL_STOCK_QUALITY_WRITEOFF.") == 4 and "'TRADE_QUALITY_WRITE_OFF')then lock table RRL_ACCESS_REV in share mode" in posting
    before = read("before_rrl_stock_posting_api.sql").replace("\r", "")
    added = [l for l in posting.split("\n") if l.rstrip() not in {b.rstrip() for b in before.split("\n")}]
    assert len(added) == 5 and all("TRADE_QUALITY_WRITE_OFF" in l for l in added)  # nothing else changed
    assert "kind_text='TRADE_QUALITY_WRITE_OFF'" in read("006_regulatory_stock_outbox.sql")


def test_native_quality_hold_runs_after_locks_for_every_stock_command():
    guard = read("005_trade_stock_guard.sql")
    command = body_of(guard, "procedure assert_command_stock(")
    hold, loop = command.index("from RRL_QUALITY_HOLD where ENTITY_TYPE='PALLET'"), command.index("for w in(select distinct c.WARE_ID")
    assert hold < loop  # before the trade-site loop: applies to every pallet the runner locked
    block = command[hold:loop]
    assert "not in('INVENTORY_COUNT','INVENTORY_REGISTER_LOT')" in block and "fail('QUALITY_HOLD_ACTIVE')" in block
    assert "q.CASE_ID=hold_case and q.PALLET_UID=p_uid and q.STATE='WAITING_POSTING'" in block  # the authorized write-off only
    assert "hold_case:=src.get_number('case_id')" in block  # JSON value read in PL/SQL, not inside SQL
    assert re.search(r"command_kind not in\('SAP_RECEIPT'[^)]*'TRADE_QUALITY_WRITE_OFF'\)then", guard)


def test_case_commands_take_the_stock_lock_and_fail_closed():
    api = read("003_quality_case_api.sql")
    assert "resource_lock_id(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid))" in body_of(api, "procedure lock_stock(")
    opening = body_of(api, "procedure open_case(")
    assert opening.index("lock_stock(uid_value)") < opening.index("from RRL_REMAINS")
    change = body_of(api, "procedure change_case(")
    assert change.index("lock_stock(v.PALLET_UID)") < change.index("assert_unchanged(v)")
    assert "left join RRL_TRADE_STOCK_ATTR" in body_of(api, "function cell_visible(") and "a.OWNER_ID is null" in body_of(api, "function cell_visible(")
    card = body_of(api, "function card(")
    assert "'external_status'" in card and "RRL_SAP_RECEIPT_OUTBOX" in card and "ACKNOWLEDGED_AT" in card


def test_migration_before_versions_match_hashes_and_rollback_is_guarded():
    hashes = json.loads(read("before_hashes.json"))
    files = {"RRL_STOCK_EFFECT_CORE:PACKAGE": "before_rrl_stock_effect_core_spec.sql", "RRL_STOCK_EFFECT_CORE:PACKAGE BODY": "before_rrl_stock_effect_core.sql",
             "RRL_STOCK_POSTING_API:PACKAGE BODY": "before_rrl_stock_posting_api.sql", "RRL_TRADE_STOCK_GUARD:PACKAGE BODY": "before_rrl_trade_stock_guard.sql",
             "RRL_REGULATORY_STOCK_OUTBOX:PACKAGE BODY": "before_rrl_regulatory_stock_outbox.sql"}
    for key, name in files.items():
        text = re.sub(r"^create or replace ", "", read(name).replace("\r", "")).rstrip("\n").removesuffix("\n/").rstrip("\n")
        assert hashlib.sha256(text.encode()).hexdigest().upper() == hashes[key], key
    case_parts = [x.strip("\n") for x in read("before_rrl_trade_quality_case_api.sql").replace("\r", "").split("\n/\n") if x.strip()]
    for part, kind in zip(case_parts, ("PACKAGE", "PACKAGE BODY")):  # the installed C-0152 version (read live after root's apply)
        text = re.sub(r"^create or replace ", "", part)
        assert hashlib.sha256(text.encode()).hexdigest().upper() == hashes["RRL_TRADE_QUALITY_CASE_API:" + kind]
    preflight = read("000_preflight.sql")
    assert all(f"same('{k.split(':')[0]}','{k.split(':')[1]}','{v}')" in preflight for k, v in hashes.items())
    apply = read("apply.sql").split("\n")
    pos = {name: apply.index("@@" + name) for name in ("003_quality_case_api.sql", "002_effect_core_spec.sql", "004_quality_writeoff.sql", "002_effect_core.sql", "007_stock_posting_api.sql")}
    assert pos["003_quality_case_api.sql"] < pos["004_quality_writeoff.sql"] and pos["002_effect_core_spec.sql"] < pos["004_quality_writeoff.sql"] < pos["002_effect_core.sql"] < pos["007_stock_posting_api.sql"]
    rollback = read("rollback.sql")
    assert "STATE='POSTED'" in rollback and "COMMAND_TYPE='TRADE_QUALITY_WRITE_OFF'" in rollback
    assert rollback.index("@@before_rrl_stock_posting_api.sql") < rollback.index("drop package RRL_STOCK_QUALITY_WRITEOFF")
    for name in ("000_preflight.sql", "001_schema.sql", "002_effect_core.sql", "003_quality_case_api.sql", "004_quality_writeoff.sql",
                 "005_trade_stock_guard.sql", "006_regulatory_stock_outbox.sql", "007_stock_posting_api.sql"):
        for statement in re.findall(r"(?is)\b(?:select|insert|update|delete)\b[^;]*;", read(name)):
            assert not re.search(r"\.get_(string|number|object|array)\(", statement), (name, statement[:80])  # ORA-40573
