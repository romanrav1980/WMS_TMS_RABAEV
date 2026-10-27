"""C-0172: depersonalized extract of the live real-road route run (the run itself is opt-in: tests/tradecase/live_route_windows.py).
Checks the timetable rules on the recorded native segments: 15 min rest after each 120 min of driving, the planned vehicle time
against the real return, the strict store window and the approval refusals."""
import json
import pathlib
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUN = json.loads((ROOT / "tests/fixtures/tradecase_route_windows_20261027.json").read_text(encoding="utf-8"))


def minutes(segment):
    return (datetime.fromisoformat(segment["finish_at"]) - datetime.fromisoformat(segment["start_at"])).total_seconds() / 60


def test_rest_after_each_120_minutes_of_driving():
    driven, rests = 0.0, 0
    for segment in RUN["full_input"]["segments"]:
        if segment["code"] == "DRIVE":
            driven += minutes(segment)
            assert driven <= 120.5, "driving continued past 120 minutes without rest"
        elif segment["code"] == "REST":
            assert 119 <= driven <= 120.5 and 14.9 <= minutes(segment) <= 15.1
            driven, rests = 0.0, rests + 1
    assert rests == 2


def test_planned_vehicle_time_covers_the_real_return():
    def handover_and_return(segments):
        handover = next(s["start_at"] for s in segments if s["code"] == "RETURN_HANDOVER")
        back = max(s["finish_at"] for s in segments if s["code"] == "DRIVE")
        return datetime.fromisoformat(handover), datetime.fromisoformat(back)
    planned, real = handover_and_return(RUN["road_totals_only"]["segments"])
    assert planned < real and RUN["road_totals_only"]["issues"] == ["ROUTE_EXCEEDS_PLANNED_RESOURCE_ENVELOPE"]
    planned, real = handover_and_return(RUN["full_input"]["segments"])
    assert planned >= real and RUN["full_input"]["issues"] == []


def test_strict_window_and_approvals():
    store = RUN["missed"]["stops"][-1]
    assert store["issues"] == ["DELIVERY_HARD_WINDOW_MISSED"] and float(store["late"]) > 0
    assert RUN["stale_approval"][0] == 409 and "TT_TIME_SOURCE_CHANGED" in json.dumps(RUN["stale_approval"])
    assert RUN["violating_approval"][0] == 409 and "DELIVERY_HARD_WINDOW_MISSED" in json.dumps(RUN["violating_approval"])
    assert RUN["approvals"] == {"first_version": 1, "second_version": 2, "after_change": "SOURCE_CHANGED"}
