from datetime import datetime
import pytest
from api.wms_api_server.app.modules.resources.infrastructure.timeline_projection import TimelineProjection
from api.wms_api_server.app.modules.resources.domain.timeline_intervals import instant, overlaps, overlap_candidates


def test_offsets_and_midnight_are_instants_not_calendar_dates():
    assert instant("2026-10-15T00:30:00+03:00") == instant("2026-10-14T21:30:00+00:00")
    assert overlaps("2026-10-14T23:50:00+03:00", "2026-10-15T00:40:00+03:00",
                    instant("2026-10-15T00:00:00+03:00"), instant("2026-10-15T01:00:00+03:00"))


def test_local_clock_is_not_silently_assumed_utc():
    with pytest.raises(ValueError, match="Aware"):
        instant("2026-10-15T00:30:00")


def test_confirmed_moment_is_in_half_open_window_but_has_no_occupancy():
    start=instant("2026-10-15T00:00:00Z");finish=instant("2026-10-16T00:00:00Z")
    assert overlaps(start.isoformat(),start.isoformat(),start,finish)
    assert not overlaps(finish.isoformat(),finish.isoformat(),start,finish)
    events=[dict(event_id=k,kind='LOAD_CONFIRMATION',fact_start_at=start.isoformat(),fact_finish_at=start.isoformat())for k in ['A','B']]
    assert overlap_candidates(events,[dict(event_id=k,resource_id='DOCK:1:A')for k in ['A','B']],finish,finish)==[]


def test_loading_confirmations_bind_frozen_vehicle_and_dock_and_departure_once():
    projection=TimelineProjection(1)
    row=dict(load_operation_id='LOAD.A',tt_id=4,vehicle_number='TEST',dock='A',status='DEPARTED',
             departure_operation_id='DEPART.4',loaded_at='2026-10-15T01:00:00+00:00',departed_at='2026-10-15T02:00:00+00:00')
    projection.loading(row);projection.loading(dict(row,load_operation_id='LOAD.B'))
    assert len(projection.events)==3
    assert ('LOAD_CONFIRMATION:LOAD.A','DOCK:1:A')in projection.bindings
    assert ('LOAD_CONFIRMATION:LOAD.A','VEHICLE:TEST')in projection.bindings
    assert ('TRIP_DEPARTURE:DEPART.4','DOCK:1:A')not in projection.bindings
    assert all(e['fact_start_at']==e['fact_finish_at']for e in projection.events)


def test_half_open_boundary_is_not_a_conflict():
    assert not overlaps("2026-10-15T01:00:00+00:00", "2026-10-15T02:00:00+00:00",
                        instant("2026-10-15T02:00:00+00:00"), instant("2026-10-15T03:00:00+00:00"))


def test_multiresource_work_does_not_conflict_with_itself_or_its_fact():
    events = [{"event_id": "A", "kind": "TASK", "plan_start_at": "2026-10-15T01:00:00Z",
               "plan_finish_at": "2026-10-15T02:00:00Z", "fact_start_at": "2026-10-15T01:05:00Z",
               "fact_finish_at": "2026-10-15T01:55:00Z"}]
    bindings = [{"event_id": "A", "resource_id": value} for value in ("PERSON:1", "REACH:1", "PERSON:1")]
    assert overlap_candidates(events, bindings, instant("2026-10-15T02:00:00Z"), instant("2026-10-15T03:00:00Z")) == []


def test_attendance_is_not_a_second_task_and_conflicts_stay_per_resource():
    events = [{"event_id": key, "kind": kind, "plan_start_at": "2026-10-15T01:00:00Z",
               "plan_finish_at": "2026-10-15T02:00:00Z"} for key, kind in (("A", "TASK"), ("B", "TASK"), ("S", "ATTENDANCE"))]
    bindings = [{"event_id": key, "resource_id": resource} for key, resource in
                (("A", "PERSON:1"), ("A", "REACH:1"), ("B", "PERSON:1"), ("S", "PERSON:1"))]
    result = overlap_candidates(events, bindings, instant("2026-10-15T02:00:00Z"), instant("2026-10-15T03:00:00Z"))
    assert result == [{"resource_id": "PERSON:1", "phase": "plan", "event_ids": ["A", "B"], "status": "OVERLAP_REVIEW"}]


def test_open_fact_does_not_project_occupancy_into_the_future():
    events = [{"event_id": "A", "kind": "TASK", "fact_start_at": "2026-10-15T01:00:00Z"},
              {"event_id": "B", "kind": "TASK", "fact_start_at": "2026-10-15T03:00:00Z", "fact_finish_at": "2026-10-15T04:00:00Z"}]
    bindings = [{"event_id": key, "resource_id": "PERSON:1"} for key in ("A", "B")]
    assert overlap_candidates(events, bindings, instant("2026-10-15T02:00:00Z"), instant("2026-10-15T05:00:00Z")) == []


def test_finished_task_without_resolved_end_is_not_claimed_to_still_be_running():
    events = [{"event_id": "A", "kind": "TASK", "status": "DONE", "fact_start_at": "2026-10-15T01:00:00Z"},
              {"event_id": "B", "kind": "TASK", "fact_start_at": "2026-10-15T02:00:00Z", "fact_finish_at": "2026-10-15T03:00:00Z"}]
    bindings = [{"event_id": key, "resource_id": "PERSON:1"} for key in ("A", "B")]
    assert overlap_candidates(events, bindings, instant("2026-10-15T04:00:00Z"), instant("2026-10-15T05:00:00Z")) == []




@pytest.mark.parametrize("status", ["IN_PROGRESS", "PARTIAL", "WAIT_REPLENISHMENT"])
def test_active_case_projection_has_open_fact_and_matches_overlap_occupancy(status):
    projection = TimelineProjection(13583852)
    projection.original[59] = projection.lane("RESOURCE:59", "CASE_PICKER", "Picker")
    projection.case_task({"case_pick_task_id": 1138, "pick_wave_id": 569, "status": status,
        "total_lines": 1, "picked_lines": 0, "fact_start_at": "2026-10-15T13:31:00+00:00",
        "fact_local_finish": None, "resource_id": 59, "equipment_id": None, "assigned_to": "picker"})
    event = projection.events[0]
    assert event["fact_finish_status"] == "OPEN"
    assert event["fact_finish_at"] is None
    assert event["time_status"] == "AWARE_FACT"
    other = {"event_id": "OTHER", "kind": "TASK", "fact_start_at": "2026-10-15T13:40:00Z",
             "fact_finish_at": "2026-10-15T13:45:00Z"}
    bindings = [{"event_id": key, "resource_id": "RESOURCE:59"} for key in (event["event_id"], "OTHER")]
    overlaps_now = overlap_candidates([event, other], bindings, instant("2026-10-15T13:50:00Z"), instant("2026-10-15T14:00:00Z"))
    assert overlaps_now == [{"resource_id": "RESOURCE:59", "phase": "fact",
        "event_ids": [event["event_id"], "OTHER"], "status": "OVERLAP_REVIEW"}]


@pytest.mark.parametrize("status", ["DONE", "CANCELLED", "SHIPPED", "WAIT_CONTROL", "CONTROL_IN_PROGRESS", "CONTROLLED", "READY_TO_SHIP"])
def test_post_pick_case_projection_keeps_finish_unknown_without_claiming_running(status):
    projection = TimelineProjection(13583852)
    projection.case_task({"case_pick_task_id": 1136, "pick_wave_id": 567, "status": status,
        "total_lines": 1, "picked_lines": 1, "fact_start_at": "2026-10-15T13:31:00+00:00",
        "fact_local_finish": "2026-10-15T09:40:00", "resource_id": None, "equipment_id": None, "assigned_to": None})
    event = projection.events[0]
    assert event["fact_finish_status"] == "UNRESOLVED" and event["fact_finish_at"] is None
    assert event["legacy_time"]["fact_finish"] == "2026-10-15T09:40:00"
    other = {"event_id": "OTHER", "kind": "TASK", "fact_start_at": "2026-10-15T13:40:00Z",
             "fact_finish_at": "2026-10-15T13:45:00Z"}
    bindings = [{"event_id": key, "resource_id": "RESOURCE:59"} for key in (event["event_id"], "OTHER")]
    assert overlap_candidates([event, other], bindings, instant("2026-10-15T13:50:00Z"), instant("2026-10-15T14:00:00Z")) == []


@pytest.mark.parametrize("status", ["IN_PROGRESS", "PARTIAL", "WAIT_REPLENISHMENT", "DONE"])
def test_legacy_case_without_aware_start_stays_unresolved_and_occupancy_unknown(status):
    projection = TimelineProjection(13583852)
    projection.case_task({"case_pick_task_id": 1138, "pick_wave_id": 569, "status": status,
        "total_lines": 1, "picked_lines": 0, "fact_start_at": None,
        "fact_local_finish": "2026-10-15T09:40:00", "resource_id": None, "equipment_id": None, "assigned_to": None})
    event = projection.events[0]
    assert event["fact_finish_status"] == "UNRESOLVED"
    assert event["time_status"] == "TIME_UNRESOLVED"
    assert event["fact_start_at"] is None and event["fact_finish_at"] is None
    assert overlap_candidates([event], [{"event_id": event["event_id"], "resource_id": "RESOURCE:59"}],
        instant("2026-10-15T13:50:00Z"), instant("2026-10-15T14:00:00Z")) == []
