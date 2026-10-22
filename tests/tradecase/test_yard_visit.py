"""C-0149 offline checks of yard visits: command contracts, native error mapping, routes and Gantt projection (no Oracle)."""
from types import SimpleNamespace
import oracledb
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app.modules.platform.public import get_current_user
from app.modules.resources.api.yard_routes import router
from app.modules.resources.contracts_yard import YardError, YardExpect, YardTransition, wire, yard_service
from app.modules.resources.domain.timeline_intervals import overlap_candidates, instant
from app.modules.resources.infrastructure.resource_timeline import ResourceTimeline
from app.modules.resources.infrastructure.timeline_projection import TimelineProjection
from app.modules.resources.infrastructure.yard_visits import OracleYardVisits, _error


class OraError:
    def __init__(self, code, text=""):
        self.code, self.text = code, text

    def __str__(self):
        return self.text


def ora(code, text=""):
    return oracledb.DatabaseError(OraError(code, text))


def test_transition_arguments_are_exact():
    YardTransition(operation_id="op-00001", expected_version=1, action="ASSIGN_DOCK", dock="D1")
    YardTransition(operation_id="op-00001", expected_version=2, action="CANCEL", reason="не приехал")
    for bad in [dict(action="ASSIGN_DOCK"), dict(action="ARRIVE", dock="D1"), dict(action="CANCEL"),
                dict(action="START", reason="лишняя"), dict(action="START", expected_version=0),
                dict(action="START", operation_id="bad id"), dict(action="TELEPORT")]:
        with pytest.raises(ValidationError):
            YardTransition(**{"operation_id": "op-00001", "expected_version": 1, **bad})


def test_wire_times_are_second_precision_aware_strings():
    body = YardExpect(operation_id="op-00001", trip_id="T1", planned_arrival_at="2026-10-22T09:30:15.123+03:00")
    assert wire(body, action="EXPECT") == {"operation_id": "op-00001", "trip_id": "T1",
                                           "planned_arrival_at": "2026-10-22T09:30:15+03:00", "action": "EXPECT"}
    with pytest.raises(ValidationError):
        YardExpect(operation_id="op-00001", trip_id="T1", planned_arrival_at="2026-10-22T09:30:00")


@pytest.mark.parametrize("code,text,expected", [
    (20901, "ORA-20901: YARD_DOCK_OR_VEHICLE_OCCUPIED\nORA-06512: at line 1", ("YARD_DOCK_OR_VEHICLE_OCCUPIED", 409)),
    (20882, "ORA-20882: YARD_ACCESS_DENIED", ("YARD_ACCESS_DENIED", 403)),
    (3113, "ORA-03113: end-of-file on communication channel", ("YARD_RESULT_UNKNOWN", 503)),
])
def test_native_errors_are_confirmed_refusals_or_unknown_outcome(code, text, expected):
    error = _error(ora(code, text))
    assert (error.code, error.status) == expected


class Gateway:
    def __init__(self, fail=None, receipt='{"operation_id":"op-00001","visit_id":1,"replayed":false}'):
        self.fail, self.calls, self.receipt = fail, [], receipt

    def transaction(self, _name):
        gateway = self

        class Tx:
            def __enter__(self):
                return gateway

            def __exit__(self, *_):
                return False
        return Tx()

    def var(self, _type):
        return SimpleNamespace(value=None, setvalue=lambda _i, v: None, getvalue=lambda: self.receipt)

    def callproc(self, name, args):
        self.calls.append((name, args[0], args[2]))
        if self.fail:
            raise self.fail


def test_adapter_runs_one_native_command_and_maps_an_unknown_outcome():
    gateway = Gateway()
    body = YardTransition(operation_id="op-00001", expected_version=3, action="START")
    assert OracleYardVisits(gateway).transition(7, 1, body, "boss") == {"operation_id": "op-00001", "visit_id": 1, "replayed": False}
    assert gateway.calls == [("RRL_YARD_VISIT_API.command", 7, "boss")]
    for broken in [Gateway(fail=ora(12170, "ORA-12170: timeout")), Gateway(receipt='{"operation_id":"op-OTHER","visit_id":1}'),
                   Gateway(receipt='{"visit_id":1}')]:
        with pytest.raises(YardError) as caught:  # a foreign or incomplete receipt is never accepted as this operation's outcome
            OracleYardVisits(broken).transition(7, 1, body, "boss")
        assert (caught.value.code, caught.value.status) == ("YARD_RESULT_UNKNOWN", 503)
    with pytest.raises(YardError) as caught:
        OracleYardVisits(Gateway(fail=ora(4043, "ORA-04043: object RRL_YARD_VISIT_API does not exist"))).transition(7, 1, body, "boss")
    assert (caught.value.code, caught.value.status) == ("YARD_NOT_AVAILABLE", 503)


class Service:
    def __init__(self, error=None):
        self.error = error

    def transition(self, ware, visit, body, actor):
        if self.error:
            raise self.error
        return {"visit_id": visit, "warehouse_id": ware, "actor": actor, "action": body.action}


def client(service):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(username="boss")
    app.dependency_overrides[yard_service] = lambda: service
    return TestClient(app)


def test_routes_mark_unknown_outcome_for_retry_with_the_same_operation_id():
    url, body = "/api/tradecase/warehouses/7/yard/visits/5/transitions", {"operation_id": "op-00001", "expected_version": 1, "action": "START"}
    assert client(Service()).post(url, json=body).json() == {"visit_id": 5, "warehouse_id": 7, "actor": "boss", "action": "START"}
    unknown = client(Service(YardError("YARD_RESULT_UNKNOWN", 503))).post(url, json=body)
    assert unknown.status_code == 503 and unknown.json()["detail"] == {
        "code": "YARD_RESULT_UNKNOWN", "outcome_confirmed": False, "retry_same_operation_id": True}
    conflict = client(Service(YardError("YARD_VERSION_CONFLICT", 409))).post(url, json=body)
    assert conflict.status_code == 409 and conflict.json()["detail"]["retry_same_operation_id"] is False
    assert client(Service()).post(url, json={**body, "dock": "D1"}).status_code == 422


def visit(visit_id, state, events, vehicle="А123ВС", planned=None):
    return dict(visit_id=visit_id, trip_id=f"T{visit_id}", vehicle=vehicle, state=state, planned_arrival_at=planned,
                events=[dict(action=a, at=f"2026-10-22T{t}:00Z", dock=d) for a, t, d in events])


def intervals(projection):
    events = {e["event_id"]: e for e in projection.events}
    return {(e, r): (events[e]["fact_start_at"], events[e]["fact_finish_at"]) for e, r in projection.bindings}


def test_reassigned_visit_holds_vehicle_whole_stay_and_each_dock_only_its_part():
    # Synthetic input for the pure projection (not a claim about live Oracle).
    projection = TimelineProjection(7)
    projection.yard(visit(1, "DEPARTED", [("EXPECT", "09:00", None), ("ARRIVE", "10:00", None), ("ASSIGN_DOCK", "10:30", "A"),
                                          ("REASSIGN_DOCK", "11:00", "B"), ("START", "11:10", "B"), ("FINISH", "11:50", "B"),
                                          ("DEPART", "12:00", "B")]))
    assert intervals(projection) == {
        ("YARD_VISIT:1", "VEHICLE:А123ВС"): ("2026-10-22T10:00:00Z", "2026-10-22T12:00:00Z"),
        ("YARD_DOCK:1:1", "DOCK:7:A"): ("2026-10-22T10:30:00Z", "2026-10-22T11:00:00Z"),
        ("YARD_DOCK:1:2", "DOCK:7:B"): ("2026-10-22T11:00:00Z", "2026-10-22T12:00:00Z")}


def test_vehicle_is_held_from_arrival_before_any_dock_and_cancel_releases_both():
    projection = TimelineProjection(7)
    projection.yard(visit(2, "ARRIVED", [("ARRIVE", "10:00", None)], vehicle="B2"))
    projection.yard(visit(3, "CANCELLED", [("ARRIVE", "10:00", None), ("ASSIGN_DOCK", "10:20", "C"), ("CANCEL", "10:40", "C")], vehicle="C3"))
    assert intervals(projection) == {("YARD_VISIT:2", "VEHICLE:B2"): ("2026-10-22T10:00:00Z", None),
                                     ("YARD_VISIT:3", "VEHICLE:C3"): ("2026-10-22T10:00:00Z", "2026-10-22T10:40:00Z"),
                                     ("YARD_DOCK:3:1", "DOCK:7:C"): ("2026-10-22T10:20:00Z", "2026-10-22T10:40:00Z")}


def test_expected_visit_is_a_plan_point_or_unresolved_and_holds_nothing():
    projection = TimelineProjection(7)
    projection.yard(visit(4, "EXPECTED", [("EXPECT", "08:00", None)], planned="2026-10-22T09:00:00Z"))
    projection.yard(visit(5, "EXPECTED", [("EXPECT", "08:00", None)], vehicle=None))
    events = {e["event_id"]: e for e in projection.events}
    assert events["YARD_VISIT:4"]["time_status"] == "AWARE_PLAN" and events["YARD_VISIT:4"]["fact_start_at"] is None
    assert events["YARD_VISIT:5"]["time_status"] == "TIME_UNRESOLVED"
    found = overlap_candidates(projection.events, [{"event_id": e, "resource_id": r} for e, r in projection.bindings],
                               instant("2026-10-22T12:00:00Z"), instant("2026-10-23T00:00:00Z"))
    assert found == []


def test_open_dock_is_occupied_until_now_and_a_second_dock_user_is_a_conflict_but_load_is_a_point():
    projection = TimelineProjection(7)
    projection.yard(visit(1, "WORKING", [("ARRIVE", "06:00", None), ("ASSIGN_DOCK", "06:10", "D1"), ("START", "06:20", "D1")]))
    projection.loading(dict(load_operation_id="L1", tt_id=1, vehicle_number=None, dock="D1", status="LOADED",
                            departure_operation_id=None, loaded_at="2026-10-22T06:30:00Z", departed_at=None))
    projection.add({"event_id": "OTHER", "kind": "TRANSPORT_OPERATION", "fact_start_at": "2026-10-22T07:00:00Z",
                    "fact_finish_at": "2026-10-22T07:30:00Z"}, ["DOCK:7:D1"])
    bindings = [{"event_id": e, "resource_id": r} for e, r in sorted(projection.bindings)]
    found = overlap_candidates(projection.events, bindings, instant("2026-10-22T08:00:00Z"), instant("2026-10-23T00:00:00Z"))
    assert [c["event_ids"] for c in found] == [["YARD_DOCK:1:1", "OTHER"]]


class TimelineCur:
    def __init__(self, error=None):
        self.error = error

    def callfunc(self, name, _type, args):
        assert name == "RRL_YARD_VISIT_API.history" and args == [7, "boss", "2026-10-22T00:00:00+00:00", "2026-10-23T00:00:00+00:00"]
        if self.error:
            raise self.error
        return '{"observed_at":"2026-10-22T08:00:00Z","visits":[]}'


def test_timeline_yard_source_is_not_mapped_before_the_migration_and_other_errors_propagate():
    sources = [{"source_id": "yard", "status": "READY"}]
    timeline = ResourceTimeline.__new__(ResourceTimeline)
    start, finish = instant("2026-10-22T03:00:00+03:00"), instant("2026-10-23T03:00:00+03:00")
    timeline._read_sources(TimelineCur(), TimelineProjection(7), sources, start, finish, "boss")
    assert sources[0]["status"] == "READY"
    for code in (4043, 6550, 942):
        sources = [{"source_id": "yard", "status": "READY"}]
        timeline._read_sources(TimelineCur(ora(code, f"ORA-{code:05d}")), TimelineProjection(7), sources, start, finish, "boss")
        assert sources[0]["status"] == "NOT_MAPPED" and sources[0]["observed_at"] is None
    with pytest.raises(oracledb.DatabaseError):
        timeline._read_sources(TimelineCur(ora(20882, "ORA-20882: YARD_ACCESS_DENIED")), TimelineProjection(7),
                               [{"source_id": "yard", "status": "READY"}], start, finish, "boss")


MIGRATION = __import__("pathlib").Path(__file__).resolve().parents[2] / "db/migrations/2026-10-22_yard_visit"


def body_of(api, name):
    start = api.rindex(name)
    return api[start:api.index("\n end;", start)]


def test_native_command_contract_static():
    import re
    api, schema = ((MIGRATION / f).read_text(encoding="utf-8") for f in ("002_api.sql", "001_schema.sql"))
    for statement in re.findall(r"(?is)\b(?:select|insert|update|delete)\b[^;]*;", api):
        assert not re.search(r"\.get_(string|number|object|array)\(", statement), statement  # ORA-40573
    command = body_of(api, "procedure command(")
    # scope before the site is revealed, again under the locks; owners, actor and body before any cached receipt
    assert command.index("require(p_actor") < command.index("lock_site(") < command.rindex("require(p_actor")
    assert command.index("require_owners(") < command.index("e.ACTOR<>p_actor or e.REQUEST_HASH<>hash_value") < command.index("'replayed',true")
    owners = body_of(api, "procedure require_owners(")
    assert "ORDER_LINK" not in owners and "'$.source_owner_id'" in owners and "ENTITY_TYPE='ORDER'" in owners
    assert "if lines=0 then fail(p_hidden)" in owners and "trim(o.OWNER)is null then fail(p_hidden)" in owners  # fail closed
    assert "bind_vehicle(v)" in body_of(api, "procedure transition(") and "YARD_VEHICLE_REQUIRED" in body_of(api, "procedure bind_vehicle(")
    assert "YARD_INBOUND_UNSUPPORTED" in body_of(api, "procedure expect(")
    assert "j.put('operation_id',p_op)" in body_of(api, "function card(")
    visits = body_of(api, "function visits(")
    assert visits.index("trip_visible(") < visits.index("fetch first 200")  # owner filter before the limit
    history = body_of(api, "function history(")
    assert history.index("trip_visible(") < history.index("fetch first 501") and "EVENT_AT" in history
    assert "RRL_YARD_VISIT_VEHICLE_UK on RRL_YARD_VISIT(case when STATE in('ARRIVED','AT_DOCK','WORKING','WORK_DONE')then VEHICLE end)" in schema
    assert "VEHICLE=upper(trim(VEHICLE))" in schema and "RRL_YARD_VISIT_EVENT_APPEND before update or delete" in schema
    assert "update RRL_YARD_VISIT_EVENT" not in api and "delete from RRL_YARD_VISIT_EVENT" not in api
