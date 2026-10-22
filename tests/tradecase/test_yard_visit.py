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
    def __init__(self, fail=None):
        self.fail, self.calls = fail, []

    def transaction(self, _name):
        gateway = self

        class Tx:
            def __enter__(self):
                return gateway

            def __exit__(self, *_):
                return False
        return Tx()

    def var(self, _type):
        return SimpleNamespace(value=None, setvalue=lambda _i, v: None, getvalue=lambda: '{"visit_id":1,"replayed":false}')

    def callproc(self, name, args):
        self.calls.append((name, args[0], args[2]))
        if self.fail:
            raise self.fail


def test_adapter_runs_one_native_command_and_maps_an_unknown_outcome():
    gateway = Gateway()
    body = YardTransition(operation_id="op-00001", expected_version=3, action="START")
    assert OracleYardVisits(gateway).transition(7, 1, body, "boss") == {"visit_id": 1, "replayed": False}
    assert gateway.calls == [("RRL_YARD_VISIT_API.command", 7, "boss")]
    with pytest.raises(YardError) as caught:
        OracleYardVisits(Gateway(fail=ora(12170, "ORA-12170: timeout"))).transition(7, 1, body, "boss")
    assert (caught.value.code, caught.value.status) == ("YARD_RESULT_UNKNOWN", 503)


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


VISITS = [dict(visit_id=1, trip_id="T1", vehicle="а123вс", dock="D1", state="WORKING", planned_arrival_at=None,
               arrived_at="2026-10-22T06:00:00Z", docked_at="2026-10-22T06:10:00Z"),
          dict(visit_id=2, trip_id="T2", vehicle="B2", dock=None, state="ARRIVED", planned_arrival_at="2026-10-22T05:00:00Z",
               arrived_at="2026-10-22T06:20:00Z", docked_at=None),
          dict(visit_id=3, trip_id="T3", vehicle=None, dock=None, state="EXPECTED", planned_arrival_at="2026-10-22T09:00:00Z",
               arrived_at=None, docked_at=None),
          dict(visit_id=4, trip_id="T4", vehicle=None, dock=None, state="EXPECTED", planned_arrival_at=None,
               arrived_at=None, docked_at=None)]


def test_visit_holds_dock_from_docking_and_vehicle_from_arrival_with_open_end():
    projection = TimelineProjection(7)
    for row in VISITS:
        projection.yard(row)
    events = {event["event_id"]: event for event in projection.events}
    assert events["YARD_VISIT:1"]["fact_start_at"] == "2026-10-22T06:10:00Z" and events["YARD_VISIT:1"]["fact_finish_status"] == "OPEN"
    assert events["YARD_VISIT:2"]["fact_start_at"] == "2026-10-22T06:20:00Z" and events["YARD_VISIT:2"]["plan_start_at"] is None
    assert events["YARD_VISIT:3"]["time_status"] == "AWARE_PLAN" and events["YARD_VISIT:3"]["fact_start_at"] is None
    assert events["YARD_VISIT:4"]["time_status"] == "TIME_UNRESOLVED"
    assert sorted(projection.bindings) == [("YARD_VISIT:1", "DOCK:7:D1"), ("YARD_VISIT:1", "VEHICLE:А123ВС"),
                                           ("YARD_VISIT:2", "VEHICLE:B2")]


def test_unknown_end_is_occupied_until_now_and_a_second_dock_user_is_a_conflict():
    projection = TimelineProjection(7)
    projection.yard(VISITS[0])
    projection.loading(dict(load_operation_id="L1", tt_id=1, vehicle_number=None, dock="D1", status="LOADED",
                            departure_operation_id=None, loaded_at="2026-10-22T06:30:00Z", departed_at=None))
    projection.add({"event_id": "OTHER", "kind": "TRANSPORT_OPERATION", "fact_start_at": "2026-10-22T07:00:00Z",
                    "fact_finish_at": "2026-10-22T07:30:00Z"}, ["DOCK:7:D1"])
    bindings = [{"event_id": e, "resource_id": r} for e, r in sorted(projection.bindings)]
    found = overlap_candidates(projection.events, bindings, instant("2026-10-22T08:00:00Z"), instant("2026-10-23T00:00:00Z"))
    # The LOAD confirmation is a point and never opens service; the open visit still blocks a later user of the dock.
    assert [c["event_ids"] for c in found] == [["YARD_VISIT:1", "OTHER"]]


class TimelineCur:
    def __init__(self, error=None):
        self.error = error

    def callfunc(self, name, _type, args):
        assert name == "RRL_YARD_VISIT_API.visits" and args == [7, "boss", 1]
        if self.error:
            raise self.error
        return '{"observed_at":"2026-10-22T08:00:00Z","visits":[]}'


def test_timeline_yard_source_is_not_mapped_before_the_migration_and_other_errors_propagate():
    sources = [{"source_id": "yard", "status": "READY"}]
    timeline = ResourceTimeline.__new__(ResourceTimeline)
    start, finish = instant("2026-10-22T00:00:00Z"), instant("2026-10-23T00:00:00Z")
    timeline._read_sources(TimelineCur(), TimelineProjection(7), sources, start, finish, "boss")
    assert sources[0]["status"] == "READY"
    timeline._read_sources(TimelineCur(ora(6550, "ORA-06550: PLS-00201")), TimelineProjection(7), sources, start, finish, "boss")
    assert sources[0]["status"] == "NOT_MAPPED" and sources[0]["observed_at"] is None
    with pytest.raises(oracledb.DatabaseError):
        timeline._read_sources(TimelineCur(ora(20882, "ORA-20882: YARD_ACCESS_DENIED")), TimelineProjection(7),
                               [{"source_id": "yard", "status": "READY"}], start, finish, "boss")


MIGRATION = __import__("pathlib").Path(__file__).resolve().parents[2] / "db/migrations/2026-10-22_yard_visit"


def test_native_command_keeps_json_out_of_sql_checks_owners_before_replay_and_history_append_only():
    import re
    api = (MIGRATION / "002_api.sql").read_text(encoding="utf-8")
    for statement in re.findall(r"(?is)\b(?:select|insert|update|delete)\b[^;]*;", api):
        assert not re.search(r"\.get_(string|number|object|array)\(", statement), statement  # ORA-40573
    command = api[api.rindex("procedure command("):api.rindex("function visits(")]
    assert command.index("require(p_actor,'tradecase_yard_operate'") < command.index("RRL_YARD_VISIT_EVENT where OPERATION_ID")
    assert command.index("require_owners(") < command.index("REQUEST_HASH<>hash_value") < command.index("'replayed',true")
    assert "update RRL_YARD_VISIT_EVENT" not in api and "delete from RRL_YARD_VISIT_EVENT" not in api
    assert "RRL_YARD_VISIT_EVENT_APPEND before update or delete" in (MIGRATION / "001_schema.sql").read_text(encoding="utf-8")
    arrive = api[api.index("action='ARRIVE'"):api.index("v.STATE:='ARRIVED'")]
    assert "YARD_VEHICLE_OCCUPIED" in arrive  # checked before the update, not only by the unique index
