"""C-0158 offline checks of planned dock intervals: contracts, adapter, routes, timeline projection and the NOT_APPLIED native kit.
Live READ ONLY evidence of the table-independent native parts: reports/tradecase/2026-10-23/claude/C0158/plan-parts-live.json."""
import hashlib
import json
import pathlib
import re
from datetime import datetime, timedelta, timezone
import oracledb
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app.modules.platform.public import get_current_user
from app.modules.resources.api.yard_plan_routes import router
from app.modules.resources.contracts_yard_plan import YardError, YardPlanCancel, YardPlanCreate, YardPlanMove, wire, yard_plan_service
from app.modules.resources.infrastructure.timeline_projection import TimelineProjection
from app.modules.resources.infrastructure.yard_dock_plans import OracleYardDockPlans, error

ROOT = pathlib.Path(__file__).resolve().parents[2]
KIT = ROOT / "db/migrations/2026-10-23_yard_dock_plan"
T0 = datetime(2026, 10, 24, 8, 0, tzinfo=timezone(timedelta(hours=3)))
OP = "yard-plan-0001"


class OraError:
    def __init__(self, code, text=""):
        self.code, self.text = code, text

    def __str__(self):
        return self.text


def ora(code, text=""):
    return oracledb.DatabaseError(OraError(code, text))


def test_contracts_require_aware_ordered_interval_and_exact_fields():
    body = YardPlanCreate(operation_id=OP, visit_id=5, dock="15", planned_from=T0, planned_to=T0 + timedelta(minutes=90))
    assert wire(body, action="PLAN") == {"operation_id": OP, "visit_id": 5, "dock": "15", "planned_from": "2026-10-24T08:00:00+03:00",
                                         "planned_to": "2026-10-24T09:30:00+03:00", "action": "PLAN"}
    YardPlanMove(operation_id=OP, expected_version=2, dock="16", planned_from=T0, planned_to=T0 + timedelta(seconds=1))
    YardPlanCancel(operation_id=OP, expected_version=2, reason="перенос рейса")
    for bad in [dict(planned_to=T0), dict(planned_to=T0 - timedelta(hours=1)), dict(planned_from=T0.replace(tzinfo=None)),
                dict(dock=" "), dict(extra=1), dict(visit_id=0)]:
        with pytest.raises(ValidationError):
            YardPlanCreate(**{**dict(operation_id=OP, visit_id=5, dock="15", planned_from=T0, planned_to=T0 + timedelta(hours=1)), **bad})
    with pytest.raises(ValidationError):
        YardPlanCancel(operation_id=OP, expected_version=1, reason="x")


def test_error_mapping_keeps_unknown_outcomes_retryable():
    assert (error(ora(20911, "ORA-20911: YARD_DOCK_PLAN_CONFLICT")).code, error(ora(20911, "ORA-20911: YARD_DOCK_PLAN_CONFLICT")).status) == ("YARD_DOCK_PLAN_CONFLICT", 409)
    assert error(ora(20882, "ORA-20882: YARD_ACCESS_DENIED")).status == 403
    assert (error(ora(4043)).code, error(ora(4043)).status) == ("YARD_PLAN_NOT_AVAILABLE", 503)
    assert (error(ora(3113)).code, error(ora(3113)).status) == ("YARD_RESULT_UNKNOWN", 503)


class Cursor:
    def __init__(self, receipt=None, fail=None):
        self.receipt, self.fail, self.calls = receipt, fail, []

    def var(self, kind):
        cursor = self

        class Var:
            value = None

            def setvalue(self, _, v):
                self.value = v

            def getvalue(self):
                return json.dumps(cursor.receipt) if self.value is None else self.value
        return Var()

    def callproc(self, name, args):
        self.calls.append((name, args))
        if self.fail:
            raise self.fail

    def callfunc(self, name, kind, args):
        self.calls.append((name, args))
        return json.dumps({"observed_at": "2026-10-24T05:00:00Z", "plans": []})

    def execute(self, sql, *a, **k):
        self.calls.append((sql, None))


class Gateway:
    def __init__(self, cur):
        self.cur = cur

    def transaction(self, name):
        cur = self.cur

        class Ctx:
            def __enter__(self):
                return cur

            def __exit__(self, *a):
                return False
        return Ctx()


def test_adapter_sends_one_canonical_command_and_accepts_only_its_receipt():
    body = YardPlanMove(operation_id=OP, expected_version=1, dock="16", planned_from=T0, planned_to=T0 + timedelta(hours=1))
    cur = Cursor({"operation_id": OP, "plan_id": 7})
    assert OracleYardDockPlans(Gateway(cur)).move(1, 7, body, "op")["plan_id"] == 7
    name, args = cur.calls[0]
    assert name == "RRL_YARD_DOCK_PLAN_API.command" and args[0] == 1 and args[2] == "op"
    sent = json.loads(args[1].value)
    assert sent == {"action": "MOVE", "dock": "16", "expected_version": 1, "operation_id": OP, "plan_id": 7,
                    "planned_from": "2026-10-24T08:00:00+03:00", "planned_to": "2026-10-24T09:00:00+03:00"}
    assert args[1].value == json.dumps(sent, sort_keys=True, separators=(",", ":"))  # same bytes on every retry
    with pytest.raises(YardError) as err:
        OracleYardDockPlans(Gateway(Cursor({"operation_id": "other"}))).move(1, 7, body, "op")
    assert (err.value.code, err.value.status) == ("YARD_RESULT_UNKNOWN", 503)
    with pytest.raises(YardError) as err:
        OracleYardDockPlans(Gateway(Cursor(fail=ora(20911, "ORA-20911: YARD_VEHICLE_PLAN_CONFLICT")))).move(1, 7, body, "op")
    assert err.value.code == "YARD_VEHICLE_PLAN_CONFLICT"


def test_read_is_read_only_and_sends_utc_window():
    cur = Cursor()
    OracleYardDockPlans(Gateway(cur)).plans(1, "op", T0, T0 + timedelta(days=1))
    assert cur.calls[0][0] == "set transaction read only"
    assert cur.calls[1] == ("RRL_YARD_DOCK_PLAN_API.plans", [1, "op", "2026-10-24T05:00:00+00:00", "2026-10-25T05:00:00+00:00"])


def test_routes_map_errors_and_require_timezone():
    class Service:
        def plans(self, ware, actor, start, finish):
            return {"warehouse_id": ware, "actor": actor}

        def plan(self, ware, body, actor):
            raise YardError("YARD_DOCK_PLAN_CONFLICT", 409)

        def cancel(self, ware, plan, body, actor):
            raise YardError("YARD_RESULT_UNKNOWN", 503)
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: type("U", (), {"username": "op"})()
    app.dependency_overrides[yard_plan_service] = Service
    c = TestClient(app)
    base = "/api/tradecase/warehouses/1/yard/dock-plans"
    assert c.get(base, params={"from": "2026-10-24T00:00:00+03:00", "to": "2026-10-25T00:00:00+03:00"}).json() == {"warehouse_id": 1, "actor": "op"}
    assert c.get(base, params={"from": "2026-10-24T00:00:00", "to": "2026-10-25T00:00:00"}).status_code == 422
    r = c.post(base, json={"operation_id": OP, "visit_id": 5, "dock": "15", "planned_from": "2026-10-24T08:00:00+03:00", "planned_to": "2026-10-24T09:00:00+03:00"})
    assert r.status_code == 409 and r.json()["detail"] == {"code": "YARD_DOCK_PLAN_CONFLICT", "operation_id": OP, "outcome_confirmed": True, "retry_same_operation_id": False}
    r = c.post(base + "/7/cancel", json={"operation_id": OP, "expected_version": 1, "reason": "перенос"})
    assert r.status_code == 503 and r.json()["detail"]["retry_same_operation_id"] is True


def test_timeline_plan_is_a_plan_on_the_dock_lane_never_a_fact():
    p = TimelineProjection(9)
    p.yard_plan({"plan_id": 3, "dock": "15", "visit_id": 5, "visit_kind": "OUTBOUND", "trip_id": "T1", "planned_from": "2026-10-24T05:00:00Z", "planned_to": "2026-10-24T06:30:00Z"})
    (e,) = p.events
    assert e["event_id"] == "YARD_DOCK_PLAN:3" and e["kind"] == "YARD_DOCK_PLAN" and e["time_status"] == "AWARE_PLAN"
    assert (e["plan_start_at"], e["plan_finish_at"], e["fact_start_at"], e["fact_finish_at"]) == ("2026-10-24T05:00:00Z", "2026-10-24T06:30:00Z", None, None)
    assert "DOCK:9:15" in p.resources and ("DOCK:9:15", "YARD_DOCK_PLAN:3") in p.bindings or "DOCK:9:15" in p.resources
    source = (ROOT / "api/wms_api_server/app/modules/resources/infrastructure/resource_timeline.py").read_text(encoding="utf-8")
    assert "plan_window(cur, warehouse, actor, start, finish)" in source and source.index("projection.yard(row)") < source.index("projection.yard_plan(row)")


def text(name):
    return (KIT / name).read_text(encoding="utf-8").replace("\r\n", "\n")


def test_native_rules_overlap_locks_replay_and_facts():
    api = text("004_plan_api.sql")
    body = api[api.index("create or replace package body"):]
    assert body.count("p.PLANNED_FROM<p_to and p.PLANNED_TO>p_from") == 2  # half-open [from,to): touching intervals do not conflict
    assert "v.STATE not in('DEPARTED','CANCELLED')" in body and "p.WARE_ID=p_ware and p.DOCK=p_dock" in body and "where v.VEHICLE=p_vehicle and p.STATUS='ACTIVE'" in body
    change = body[body.index("procedure change("):body.index("procedure command(")]
    assert change.index("lock_visit(") < change.index("for update") < change.index("assert_dock(") < change.index("lock_vehicle(") < change.index("assert_free(")
    cmd = body[body.index("procedure command("):body.index("function plans(")]
    assert cmd.index("require(p_actor,'tradecase_yard_operate'") < cmd.index("lock_site(p_ware)") < cmd.index("RRL_YARD_DOCK_PLAN_EVENT where OPERATION_ID")
    replay = cmd[cmd.index("RRL_YARD_DOCK_PLAN_EVENT where OPERATION_ID"):]
    assert replay.index("assert_visit_owners") < replay.index("e.ACTOR<>p_actor or e.REQUEST_HASH<>hash_value")
    assert "if t_from<=now then fail('YARD_PLAN_IN_PAST')" in change and "if v.STATE not in('EXPECTED','ARRIVED')then fail('YARD_PLAN_VISIT_STATE')" in change
    assert not re.search(r"(?i)update\s+RRL_YARD_VISIT\b|insert\s+into\s+RRL_YARD_VISIT\b", body)  # facts are never written by a plan
    plans = body[body.index("function plans("):]
    assert "require(p_actor,'tradecase_view',p_ware)" in plans and "interval '7' day" in plans and plans.index("visit_visible") < plans.index("fetch first 501")
    assert "get_string" not in " ".join(re.findall(r"(?is)\bselect\b.*?;", body))


def test_schema_and_kit():
    schema = text("001_schema.sql")
    assert "RRL_YARD_DOCK_PLAN_VISIT_UK on RRL_YARD_DOCK_PLAN(case when STATUS='ACTIVE'then VISIT_ID end)" in schema
    assert "check(PLANNED_TO>PLANNED_FROM)" in schema and "RRL_YARD_DOCK_PLAN_EVENT_APPEND before update or delete" in schema
    before, after = text("before_visit_body.sql").splitlines(), text("003_visit_body.sql").splitlines()
    assert len(after) == len(before) + 5 and all(x in after for x in before)
    assert len(text("002_visit_spec.sql").splitlines()) == len(text("before_visit_spec.sql").splitlines()) + 2
    assert "DOCK_PLAN_HISTORY_PRESENT" in text("rollback.sql")
    m = json.loads(text("manifest.json"))
    assert m["status"] in {"NOT_APPLIED", "APPLIED"} and m["applied_by_claude"] is False
    for k, v in m["before_sha256"].items():
        assert v in text("000_preflight.sql") and v in text("rollback_verify.sql")
    for v in m["after_sha256"].values():
        assert v in text("verify.sql")
    for name, sha in m["files_sha256"].items():
        assert hashlib.sha256((KIT / name).read_bytes()).hexdigest() == sha, name


@pytest.mark.parametrize("status,code,confirmed", [
    (403, "YARD_ACCESS_DENIED", False), (409, "YARD_OPERATION_CONFLICT", False),
    (409, "YARD_VISIT_NOT_FOUND", False), (409, "YARD_PLAN_NOT_FOUND", False),
    (503, "YARD_RESULT_UNKNOWN", False), (409, "YARD_DOCK_PLAN_CONFLICT", True),
])
def test_plan_refusal_does_not_erase_an_unknown_original_outcome(status, code, confirmed):
    from fastapi import HTTPException
    from app.modules.resources.api.yard_plan_routes import _call
    def refuse():
        raise YardError(code, status)
    with pytest.raises(HTTPException) as result:
        _call(refuse, OP)
    assert result.value.detail == {"code": code, "operation_id": OP,
        "outcome_confirmed": confirmed, "retry_same_operation_id": not confirmed}
