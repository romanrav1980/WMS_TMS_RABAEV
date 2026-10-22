"""C-0154 offline checks of the extra-stop decision: contracts, adapter, routes and native rules (no Oracle).
Live evidence of the pure part on the real calculator: reports/tradecase/2026-10-23/claude/C0154/extra-stop-pure-live.json."""
import json
import pathlib
import re
from types import SimpleNamespace
import oracledb
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app.modules.platform.public import get_current_user
from app.modules.transport.api.extra_stop_routes import router
from app.modules.transport.contracts_extra_stop import ExtraStopCommand, ExtraStopError, extra_stop_service
from app.modules.transport.infrastructure.extra_stop import OracleExtraStop, _error

ROOT = pathlib.Path(__file__).resolve().parents[2]
API = (ROOT / "db/migrations/2026-10-23_trade_extra_stop/002_api.sql").read_text(encoding="utf-8")
SCHEMA = (ROOT / "db/migrations/2026-10-23_trade_extra_stop/001_schema.sql").read_text(encoding="utf-8")
H = "a" * 64


class OraError:
    def __init__(self, code, text=""):
        self.code, self.text = code, text

    def __str__(self):
        return self.text


def ora(code, text=""):
    return oracledb.DatabaseError(OraError(code, text))


def test_command_arguments_are_exact():
    ExtraStopCommand(operation_id="TC.STOP.UI:abcd1234", action="APPROVE", reason="клиент просит", address="A", expected_version=2, source_hash=H, position=1, proposal_fingerprint=H)
    ExtraStopCommand(operation_id="TC.STOP.UI:abcd1234", action="DECLINE", reason="не нужно", address="A", expected_version=2, source_hash=H)
    ExtraStopCommand(operation_id="TC.STOP.UI:abcd1234", action="SET_POLICY", reason="запрет", new_stops_forbidden=True, expected_policy_version=0)
    for bad in [dict(action="APPROVE", address="A", expected_version=2, source_hash=H, position=1), dict(action="DECLINE", address="A", expected_version=2, source_hash=H, proposal_fingerprint=H),
                dict(action="APPROVE", address="A", expected_version=2, source_hash=H), dict(action="DECLINE", address="A", expected_version=2, source_hash=H, position=0),
                dict(action="SET_POLICY", new_stops_forbidden=True), dict(action="SET_POLICY", new_stops_forbidden=True, expected_policy_version=0, address="A"),
                dict(action="APPROVE", address="A", expected_version=2, source_hash="x", position=0, proposal_fingerprint=H), dict(action="APPROVE", address="A", expected_version=2, source_hash=H, position=0, proposal_fingerprint=H, reason="x")]:
        with pytest.raises(ValidationError):
            ExtraStopCommand(**{"operation_id": "TC.STOP.UI:abcd1234", "reason": "основание", **bad})


@pytest.mark.parametrize("code,text,expected", [
    (20911, "ORA-20911: EXTRA_STOP_SOURCE_CHANGED", ("EXTRA_STOP_SOURCE_CHANGED", 409)),
    (20911, "ORA-20911: EXTRA_STOP_TRIP_NOT_FOUND", ("EXTRA_STOP_TRIP_NOT_FOUND", 404)),
    (20882, "ORA-20882: EXTRA_STOP_ACCESS_DENIED", ("EXTRA_STOP_ACCESS_DENIED", 403)),
    (4043, "ORA-04043: object does not exist", ("EXTRA_STOP_NOT_AVAILABLE", 503)),
    (3113, "ORA-03113", ("EXTRA_STOP_RESULT_UNKNOWN", 503)),
])
def test_native_errors(code, text, expected):
    e = _error(ora(code, text))
    assert (e.code, e.status) == expected


class Gateway:
    def __init__(self, receipt):
        self.receipt, self.calls = receipt, []

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
        holder = SimpleNamespace(value=None)
        holder.setvalue = lambda _i, v: setattr(holder, "value", v)
        holder.getvalue = lambda: self.receipt
        return holder

    def callproc(self, name, args):
        self.calls.append((name, json.loads(args[0].value), args[1]))


def test_decision_is_one_native_command_with_the_trip_and_only_its_receipt_counts():
    body = ExtraStopCommand(operation_id="TC.STOP.UI:abcd1234", action="DECLINE", reason="не нужно", address="A", expected_version=2, source_hash=H)
    g = Gateway('{"operation_id":"TC.STOP.UI:abcd1234","action":"DECLINE"}')
    assert OracleExtraStop(g).command(77, body, "disp")["action"] == "DECLINE"
    name, wire, actor = g.calls[-1]
    assert name == "RRL_TRADE_EXTRA_STOP_API.command" and wire["trip_id"] == 77 and wire["source_hash"] == H and actor == "disp"
    with pytest.raises(ExtraStopError) as caught:
        OracleExtraStop(Gateway('{"operation_id":"other"}')).command(77, body, "disp")
    assert (caught.value.code, caught.value.status) == ("EXTRA_STOP_RESULT_UNKNOWN", 503)


def test_routes():
    class Service:
        def evaluate(self, trip, address, zone, actor, position=None):
            return {"trip": trip, "address": address, "zone": zone, "actor": actor}

        def decisions(self, trip, actor):
            raise ExtraStopError("EXTRA_STOP_NOT_AVAILABLE", 503)

        def command(self, trip, body, actor):
            return {"operation_id": body.operation_id, "trip": trip}
    app = FastAPI()
    app.include_router(router)
    from app.modules.platform.public import require_permission  # the dependency factory returns a fresh callable; override by route
    for route in app.routes:
        for dep in getattr(route, "dependant", SimpleNamespace(dependencies=[])).dependencies:
            if dep.call is not extra_stop_service:
                app.dependency_overrides[dep.call] = lambda: SimpleNamespace(username="disp")
    app.dependency_overrides[extra_stop_service] = lambda: Service()
    c = TestClient(app)
    assert c.get("/api/transport/preflight/trips/77/extra-stops", params={"address": " A ", "zone": "UTC"}).json() == {"trip": 77, "address": "A", "zone": "UTC", "actor": "disp"}
    r = c.get("/api/transport/preflight/trips/77/extra-stops/decisions")
    assert r.status_code == 503 and r.json()["detail"]["retry_same_operation_id"] is True
    assert c.get("/api/transport/preflight/trips/77/extra-stops", params={"address": "A", "zone": "Mars/Base"}).status_code == 422


def body_of(name):
    start = API.rindex(name)
    return API[start:API.index("\n end;", start)]


def test_native_rules_static():
    pure = API[API.index(" -- PURE BEGIN"):API.index(" -- PURE END")]
    assert "RRL_TRADE_" not in pure and "RRL_ACCESS_API" not in pure  # the pure part only uses the existing calculator and material owners
    verdict = body_of("function verdict(")
    assert "'DELIVERY_HARD_WINDOW_MISSED','ROUTE_EXCEEDS_PLANNED_RESOURCE_ENVELOPE','DRIVER_TRIP_DRIVE_LIMIT'" in verdict and "return 'UNKNOWN'" in verdict
    evaluate = body_of("function assess(")
    order = ["new_stops_forbidden", "BASE_ROUTE_NOT_CONFIRMED", "ALREADY_ON_ROUTE", "EXTRA_ADDRESS_NOT_UNIQUE", "variant(src,stops,pos", "'PROPOSE'", "EXTRA_STOP_INPUTS_MISSING", "EXTRA_STOP_BREAKS_DEADLINE"]
    positions = [evaluate.index(x) for x in order]
    assert positions == sorted(positions)
    variant = body_of("function variant(")
    assert "RRL_STORE_WINDOW_RULES.material(" in variant and "RRL_TT_ROUTE_SCHEDULE.material(" in variant  # native owners rebuild the route
    command = body_of("procedure command(")
    assert command.index("require_edit(v_trip") < command.index("for update wait 5") < command.rindex("require_edit(v_trip")
    assert command.index("e.ACTOR<>p_actor or e.REQUEST_HASH<>hash_value") < command.index("'replayed',true")
    assert "ev:=json_object_t.parse(evaluate_internal(v_trip,p_actor,p_request,after_src))" in command and "EXTRA_STOP_SOURCE_CHANGED" in command
    assert "ev.get_string('decision')<>'PROPOSE'or ev.get_number('position')<>v_position" in command and "'WAITING_SAP_ORDER'" in command
    assert "'transport_dispatch_edit'" in body_of("procedure require_edit(")
    assert "STALE_ROUTE_CHANGED" in body_of("function decisions(")
    assert "RRL_TRADE_EXTRA_STOP_EVENT_APPEND before update or delete" in SCHEMA
    for statement in re.findall(r"(?is)\b(?:insert|update|delete)\b[^;]*;", API):
        assert not re.search(r"\w\.(get_\w+|to_clob)\b", statement), statement[:100]  # JSON methods never inside SQL DML


def test_live_evidence_matches_the_program_example():
    data = json.loads((ROOT / "reports/tradecase/2026-10-23/claude/C0154/extra-stop-pure-live.json").read_text(encoding="utf-8"))
    assert data["extra_15_slack_30"]["decision"] == "PROPOSE" and data["extra_15_slack_30"]["before_slack_min"] == 30
    assert data["extra_15_slack_30"]["added_min"] == 15 and data["extra_15_slack_30"]["after_slack_min"] == 15
    assert data["extra_45_slack_30"]["decision"] == "REJECT"
    assert data["new_stops_forbidden"]["decision"] == "FORBIDDEN"
    assert data["extra_legs_unknown"]["decision"] == "UNKNOWN" and data["extra_rule_missing"]["decision"] == "UNKNOWN"
    assert data["extra_15_position_2"]["decision"] == "PROPOSE" and data["extra_15_position_2"]["position"] == 2
    assert [v["position"] for v in data["extra_15_position_2"]["variants"]] == [2]  # a chosen position evaluates exactly one variant


def test_evaluation_is_bounded_and_caller_cannot_supply_route_data():
    spec = API[:API.index("create or replace package body")]
    assert "evaluate_source" not in spec  # the pure part with controlled legs is private
    evaluate = body_of("function evaluate_internal(")
    assert "q.remove('extra_rule');q.remove('new_stops_forbidden')" in evaluate and "assess(c.get_object('source').to_clob,q.to_clob,null,p_after)" in evaluate
    source = body_of("function assess(")
    assert "stops.get_size>20 then" in source and "EXTRA_STOP_POSITION_REQUIRED" in source and "for pos in nvl(pick,0)..nvl(pick,stops.get_size)loop" in source


def test_review_rules_access_fence_proposal_lock_and_single_approval():
    command = body_of("procedure command(")
    fence, first, row, second = (command.index(x) for x in ("lock table RRL_ACCESS_REV in share mode", "require_edit(v_trip", "for update wait 5", "for update wait 5"))
    assert fence < first < row < command.rindex("require_edit(v_trip")  # current access fence before the trip row, rights before and under
    assert "if act='APPROVE'and(v_position is null or given_print is null)then fail('EXTRA_STOP_REQUEST_INVALID')" in command
    lock, final = command.index("RRL_TT_ROUTE_SCHEDULE.lock_material(after_src)"), command.rindex("evaluate_internal(v_trip,p_actor,p_request,after_src)")
    assert lock < final  # inputs of the proposal are locked, then evaluated once more inside the same transaction
    assert command.index("fingerprint<>given_print") < command.index("EXTRA_STOP_ALREADY_APPROVED") < command.index("insert into RRL_TRADE_EXTRA_STOP_EVENT")
    assert "e.DECISION='APPROVED'and e.SOURCE_HASH=given_hash and e.PROPOSAL_FINGERPRINT=fingerprint" in command
    internal = body_of("function evaluate_internal(")
    assert "sha(base_hash||chr(10)||p_after)" in internal  # fingerprint of the whole AFTER source plus the base route
    decisions = body_of("function decisions(")
    assert "STALE_INPUTS_CHANGED" in decisions and "checked<5" in decisions and "x.NEWEST=1" in decisions
    assert "PROPOSAL_FINGERPRINT is not null" in SCHEMA


def test_live_fingerprint_is_stable_and_follows_inputs():
    data = json.loads((ROOT / "reports/tradecase/2026-10-23/claude/C0154/extra-stop-pure-live.json").read_text(encoding="utf-8"))
    assert data["fingerprint"]["stable"] is True and data["fingerprint"]["changes_with_extra_norm"] is True
