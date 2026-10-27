"""C-0172 offline checks: the live real-road route evidence (rests, envelope, windows, approvals) and the route screen fixes."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "runtime/test-evidence/tradecase/2026-10-27/T09/RW27dc7ba57b35.json"
PLAN = ROOT / "admin/wms_admin_frontend/src/features/integrations/tradecase/RoutePlan.tsx"


def evidence():
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_real_road_route_rests_windows_and_approvals():
    r = evidence()
    assert r["status"] == "RUN_COMPLETE_REVIEW" and r["state"]["retired"] and r["state"]["invalid_after_retire"] == 0
    assert r["road_legs"]["unknown_leg_count"] == 0 and len(r["road_legs"]["legs"]) == 4
    assert [x["code"] for x in r["road_totals_segments"]].count("REST") == 2  # 120/15 applied on real legs, out and back
    assert r["road_totals_only"]["issues"] == ["ROUTE_EXCEEDS_PLANNED_RESOURCE_ENVELOPE"]
    assert r["free"]["issues"] == [] and r["reachable"]["issues"] == []
    assert r["missed"]["issues"] == ["DELIVERY_HARD_WINDOW_MISSED"] and r["missed"]["stops"][2]["issues"] == ["DELIVERY_HARD_WINDOW_MISSED"]
    assert r["stale_approval"][0] == 409 and "TT_TIME_SOURCE_CHANGED" in json.dumps(r["stale_approval"])
    assert r["violating_approval"][0] == 409 and "DELIVERY_HARD_WINDOW_MISSED" in json.dumps(r["violating_approval"])
    assert r["reapproved"]["version"] > r["approved"]["version"] and r["time_context_after_change"]["approval_status"] == "SOURCE_CHANGED"


def test_utc_request_only_relabels_local_times():
    raw = evidence()["raw_times"]
    assert [m[0][:19] for m in raw["moscow"]] == [u[0][:19] for u in raw["utc"]]
    assert all(m[0].endswith("+03:00") and u[0].endswith("+00:00") for m, u in zip(raw["moscow"], raw["utc"]))


def test_route_screen_zone_rests_and_shortfall():
    js = PLAN.read_text(encoding="utf-8")
    assert "time_zone=UTC" not in js and 'useState<Zone>("Europe/Moscow")' in js
    assert 'data-help-id="tradecase.route.zone"' in js and 'title="Выбрать часовой пояс показа"' in js
    assert 'x.code === "REST"' in js and "RETURN_HANDOVER" in js and "ROUTE_EXCEEDS_PLANNED_RESOURCE_ENVELOPE:" in js
