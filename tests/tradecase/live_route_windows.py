"""C-0172 T09: the full program route depot -> hub -> branch -> store -> depot on REAL road legs of the running OSRM, through the
existing commands only: road refresh, route input from the road totals, native window/rest calculation, time approval, a changed
store window and the dispatcher's decision. Own absent warehouse, addresses, trip and planning rows (the same fixture pattern as
live_extra_stop.py); no goods, reservations or financial rows. Coordinates are real towns of the Sverdlovsk region, not SNS/BLC stores."""
from datetime import datetime, timedelta
import json
from pathlib import Path
import re
import os
import secrets
import sys
import time
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "api/wms_api_server"), str(ROOT), str(Path(__file__).parent)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
import oracledb
from tools.mcp.tms_mcp_server import oracle_connection
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.warehouse_depot import WarehouseDepot
os.environ.setdefault("TRADECASE_ADMIN_USER", "admin")
os.environ.setdefault("TRADECASE_ADMIN_PASSWORD", re.search(r"PASS=(\S+?)[`,)\s]", (ROOT / "AGENTS.md").read_text(encoding="utf-8"))[1])
from live_document_acceptance import http, expect, CALLS

OUT = ROOT / "runtime/test-evidence/tradecase/2026-10-27/T09"
TAG = "RW27" + uuid4().hex[:10]
WARE = 240000000 + secrets.randbelow(9000000)
POINTS = [("DEPOT", 56.8389, 60.5975), ("HUB", 56.4149, 61.9189), ("BRANCH", 56.7760, 62.0460), ("STORE", 56.9070, 62.0340)]
ADDR = {name: TAG + "." + name for name, _, _ in POINTS}
DAY = (datetime.now() + timedelta(days=2)).date()
PRE = "/api/transport/preflight"
report = dict(status="FAIL", tag=TAG, warehouse=WARE, day=DAY.isoformat(), road="LIVE OSRM (running tms2-osrm)", checks=[], timings=[])
state = dict(created=False, depot_version=0, trip=None, pallets=[])


def save():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / (TAG + ".json")).write_text(json.dumps(dict(report, state=state, http=CALLS), indent=1, ensure_ascii=False, default=str), encoding="utf-8")


def fenced(fn, *args):
    """The shared policy fence can be held by another session (LOCK_TIMEOUT, nothing applied): repeat the same command later."""
    for attempt in range(20):
        try:
            return fn(*args)
        except Exception as exc:
            if "LOCK_TIMEOUT" not in str(exc) or attempt == 19: raise
            report.setdefault("fence_waits", []).append(str(exc)[:160]); time.sleep(30)


def call(method, path, body=None, status=200):
    def once():
        answer = http(method, path, body)
        if "LOCK_TIMEOUT" in json.dumps(answer[1]):
            raise RuntimeError("LOCK_TIMEOUT " + json.dumps(answer[1])[:120])
        return answer
    start = time.perf_counter(); result = expect(status, fenced(once))
    report["timings"].append(dict(method=method, path=path.split("?")[0], status=status, ms=round((time.perf_counter() - start) * 1000, 1))); return result


def config(sql_list):
    fenced(_config, sql_list)


def _config(sql_list):
    with oracle_connection() as c:
        q = c.cursor(); q.callproc("RRL_STOCK_CONFIG_API.begin_change", ["admin", "warehouse_settings_edit"])
        try:
            for sql, binds in sql_list:
                q.execute(sql, binds)
            c.commit()
        finally:
            q.callproc("RRL_STOCK_CONFIG_API.end_change")


def windows(pairs):
    """Own ST delivery windows (local Moscow time), the same planning columns live_extra_stop.py sets."""
    config([("update RRL_SBORKA_PALLETS set ZONE_TIME_PLAN_IN=to_date(:a,'YYYY-MM-DD HH24:MI'),ZONE_TIME_PLAN_OUT=to_date(:b,'YYYY-MM-DD HH24:MI') where ID=:p",
             dict(a=f"{DAY} {a}", b=f"{DAY} {b}", p=pid)) for (pid, _), (a, b) in zip(state["pallets"], pairs)])


def calc(zone="Europe/Moscow"):
    return call("GET", f"{PRE}/trips/{state['trip']}/delivery-windows?time_zone={zone}&depot_address=&max_age_hours=24")


def hhmm(iso):
    return iso[11:16] if iso else None


def summary(w):
    return dict(status=w["status"], departure=hhmm(w.get("departure_at")), return_at=hhmm(w.get("return_at")),
                stops=[dict(address=s["address"].split(".")[-1], arrival=hhmm(s.get("arrival_at")), start=hhmm(s.get("service_start_at")),
                            finish=hhmm(s.get("service_finish_at")), wait=s.get("wait_min"), late=s.get("late_min"), issues=s.get("issues")) for s in w.get("stops", [])],
                issues=[i["code"] for i in w.get("issues", [])], breaks=w.get("driver_breaks_included"), rests=w.get("rests") or w.get("breaks"))


def run():
    with oracle_connection() as c:
        q = c.cursor(); q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual"); assert q.fetchone() == ("RABAEV", "orcl")
        q.execute("""select (select count(*) from RRL_WARES where ID=:w)+(select count(*) from RRL_ACCESS_OBJECT where KIND='WAREHOUSE' and OBJECT_ID=to_char(:w))
            +(select count(*) from RRL_ADDR where ADDR like :t) from dual""", w=WARE, t=TAG + ".%")
        assert q.fetchone() == (0,), "fixture must be absent before the first write"
        q.execute("select nvl(max(LOG_ID),0) from RRL_SQL_SLOW_LOG"); report["slow_marker"] = q.fetchone()[0]
        save()  # state before the first write
        q.execute("insert into RRL_WARES(ID,NAME)values(:w,:n)", w=WARE, n="TRADECASE QA route windows " + TAG)
        q.execute("insert into RRL_ACCESS_OBJECT(KIND,OBJECT_ID,TITLE,ACTIVE,VERSION_NO)values('WAREHOUSE',:w,'Route windows QA',1,1)", w=str(WARE))
        for name, lat, lon in POINTS:  # program: unloading 15 minutes, strict windows
            q.execute("insert into RRL_ADDR(ADDR,SHIROTA,DOLGOTA,DELETED3,UNLOAD_NORM_MIN,TW_STRICT,TRANSPORT_TYPE,STOL)values(:a,:lat,:lon,0,15,1,'0',0)", a=ADDR[name], lat=lat, lon=lon)
        c.commit(); state["created"] = True; save()
    for attempt in range(10):  # the shared policy fence may be held by another session's configuration change; the same operation is repeated
        try:
            state["depot_version"] = WarehouseDepot(OracleGateway()).apply(TAG + ".depot", dict(warehouse_id=WARE, expected_version=0, depot_address=ADDR["DEPOT"],
                reason="Owned route windows acceptance"), "admin")["version"]; break
        except Exception as exc:
            if "LOCK_TIMEOUT" not in str(exc) or attempt == 9: raise
            report.setdefault("fence_waits", []).append(str(exc)[:120]); time.sleep(30)
    save()
    with oracle_connection() as c:
        q = c.cursor(); q.callproc("RRL_STOCK_CONFIG_API.begin_change", ["admin", "warehouse_settings_edit"])
        try:
            out = q.var(oracledb.DB_TYPE_NUMBER); q.callproc("RRL_TRANSPORT_EDIT_API.create_trip", ["1", datetime.combine(DAY, datetime.min.time()), "admin", out])
            state["trip"] = int(out.getvalue())
            for i, name in enumerate(("HUB", "BRANCH", "STORE"), 1):
                uid = TAG + ".PALLET." + str(i)
                pid = int(q.callfunc("RRL_SBORKA_PALLETS_ADD2", oracledb.DB_TYPE_NUMBER, [TAG + ".ST." + str(i), ADDR[name], 1, uid, "1", datetime.combine(DAY, datetime.min.time()), "", "admin", WARE]))
                q.execute("update RRL_SBORKA_PALLETS set TRANSTASK_ID=:t,ORD=:o where ID=:p", t=state["trip"], o=i, p=pid)
                state["pallets"].append((pid, uid))
            for name in ("HUB", "BRANCH", "STORE"):
                q.execute("insert into RRL_STORE_PROFILE(STORE_ADDR,PROFILE_VERSION,RECEIVING_WINDOW_MODE,TIMEZONE_REGION,UPDATED_BY,UPDATED_AT)values(:a,1,'WEEKLY','Europe/Moscow','admin',systimestamp)", a=ADDR[name])
                for d in range(1, 8):
                    q.execute("insert into RRL_STORE_RECEIVING_WINDOW(STORE_ADDR,WEEKDAY,FROM_MINUTE,TO_MINUTE)values(:a,:d,0,1439)", a=ADDR[name], d=d)
            c.commit()
        finally:
            q.callproc("RRL_STOCK_CONFIG_API.end_change")
    save()
    trip = state["trip"]
    plate = "RW27V" + str(WARE)  # own vehicle and driver on the trip: the route input requires them (TT_ROUTE_VEHICLE_REQUIRED)
    state["vehicle"] = call("POST", "/api/admin/transport/vehicles", dict(num_plat=plate, transtype_id="10", max_weight_kg=8000, max_pallets=33, sobstvennyy=True), 201)["id"]
    state["driver"] = call("POST", "/api/admin/transport/drivers", dict(name="Route windows QA " + TAG, license_number="TEST_NOT_ROAD_" + TAG), 201)["id"]; save()
    call("PATCH", f"/api/admin/transport/tasks/{trip}", dict(transport=plate, voditel_id=state["driver"], shipment_time="08:00", primechanie="C-0172 isolated QA, no real dispatch"))
    windows([("00:00", "23:59")] * 3)  # first: no window limits, to read the real road timetable
    # 1. Real road legs through the served API, exact replay and stale basis.
    legs = call("GET", f"{PRE}/trips/{trip}/road-legs")
    body = dict(operation_id=TAG + ".road", trip_id=trip, expected_version=legs["route_input_version"], source_hash=legs["source_hash"])
    receipt = call("POST", PRE + "/road-refreshes", body)
    assert receipt["provider"] in ("osrm", "valhalla") and receipt["updated_legs"] == 4, receipt
    assert call("POST", PRE + "/road-refreshes", body) == receipt
    legs = call("GET", f"{PRE}/trips/{trip}/road-legs"); report["road_legs"] = legs
    assert legs["unknown_leg_count"] == 0 and [x["from_address"].split(".")[-1] for x in legs["legs"]] == ["DEPOT", "HUB", "BRANCH", "STORE"], legs
    report["checks"].append("Four real directed road legs depot-hub-branch-store-depot from the running provider; exact replay returns the same receipt")
    # 2. Dispatcher route input from the road totals (existing command) creates the planned operations.
    context = call("GET", f"{PRE}/trips/{trip}/route-context")
    route_input = dict(operation_id=TAG + ".input", trip_id=trip, expected_version=context["version"], source_hash=context["source_hash"],
                       drive_min=int(round(legs["drive_min"])), drive_back_min=int(round(legs["drive_back_min"])), source_reference="Road legs " + receipt["provider"] + " " + TAG,
                       reason="Route input from real road legs")
    report["route_input"] = call("POST", PRE + "/route-inputs", route_input)
    assert call("POST", PRE + "/route-inputs", route_input) == report["route_input"]
    raw = calc(); report["road_totals_only"] = summary(raw); report["road_totals_segments"] = raw["segments"]
    # Finding: pure road totals leave out unloading and the 120/15 rests, so the planned vehicle time ends before the real return.
    assert raw["driver_breaks_included"] and [x["code"] for x in raw["issues"]] == ["ROUTE_EXCEEDS_PLANNED_RESOURCE_ENVELOPE"], report["road_totals_only"]
    assert [x["code"] for x in raw["segments"]].count("REST") >= 1
    report["checks"].append("Real legs: native inserts REST after 120 min driving; road totals alone as route input exceed the planned vehicle time")
    def minutes(a, b):
        return int(-(-(datetime.fromisoformat(b) - datetime.fromisoformat(a)).total_seconds() // 60))
    last = raw["stops"][-1]
    leave = max(x["finish_at"] for x in raw["segments"] if x.get("address") == last["address"] and x["code"] != "DRIVE")
    context = call("GET", f"{PRE}/trips/{trip}/route-context")
    from_calc = dict(route_input, operation_id=TAG + ".input.calc", expected_version=context["version"], source_hash=context["source_hash"],
                     drive_min=minutes(raw["departure_at"], last["arrival_at"]), drive_back_min=minutes(leave, raw["return_at"]),
                     source_reference="Native route calculation on road legs incl. unloading and rests " + TAG, reason="Route input from the full route calculation")
    report["route_inputs_calc"] = []
    for _ in range(3):  # the dispatcher adds exactly the shown shortfall of the planned vehicle time to the return estimate
        report["route_inputs_calc"].append(call("POST", PRE + "/route-inputs", from_calc))
        free = calc(); report["free"] = summary(free); report["free_segments"] = free["segments"]
        if not free.get("issues"):
            break
        handover = next(x["start_at"] for x in free["segments"] if x["code"] == "RETURN_HANDOVER")
        context = call("GET", f"{PRE}/trips/{trip}/route-context")
        from_calc = dict(from_calc, operation_id=TAG + ".input.calc." + str(len(report["route_inputs_calc"])), expected_version=context["version"], source_hash=context["source_hash"],
                         drive_back_min=from_calc["drive_back_min"] + minutes(handover, free["return_at"]))
    assert free["status"] == "NO_EARLIEST_WINDOW_VIOLATION" and not free.get("issues"), report["free"]
    report["checks"].append(f"Route input from the full calculation ({from_calc['drive_min']}/{from_calc['drive_back_min']} min): timetable on real legs without violations")
    save()
    # 3. Reachable windows around the computed arrivals; then the store window ends before the real arrival.
    arrivals = [s["arrival_at"] for s in free["stops"]]
    def shift(iso, minutes):
        return (datetime.fromisoformat(iso[:16]) + timedelta(minutes=minutes)).strftime("%H:%M")
    reachable = [(shift(a, -30), shift(a, 45)) for a in arrivals]
    windows(reachable); ok = calc(); report["reachable"] = summary(ok)
    assert ok["status"] == "NO_EARLIEST_WINDOW_VIOLATION" and not ok.get("issues"), report["reachable"]
    report["checks"].append("Reachable windows " + str(reachable) + ": no violation")
    timing = call("GET", f"{PRE}/trips/{trip}/time-context"); report["time_context_before"] = {k: timing.get(k) for k in ("version", "source_hash", "approval_status")}
    approval = dict(operation_id=TAG + ".approve", trip_id=trip, expected_version=timing["version"], source_hash=timing["source_hash"],
                    time_zone="Europe/Moscow", reason="Dispatcher approves real-road timetable")
    report["approval_body"] = approval
    report["approved"] = call("POST", PRE + "/time-approvals", approval)
    assert call("POST", PRE + "/time-approvals", approval) == report["approved"]
    report["checks"].append("Time approval and exact replay")
    save()
    late = list(reachable); late[2] = (shift(arrivals[2], -60), shift(arrivals[2], -10))
    windows(late); missed = calc(); report["missed"] = summary(missed)
    assert any("DELIVERY_HARD_WINDOW_MISSED" in (s.get("issues") or []) for s in missed["stops"]) or "DELIVERY_HARD_WINDOW_MISSED" in report["missed"]["issues"], report["missed"]
    report["checks"].append("Store window ending before the real arrival: DELIVERY_HARD_WINDOW_MISSED shown")
    utc = calc("UTC"); report["utc_view"] = summary(utc)  # the zone the tradecase route screen currently requests
    report["raw_times"] = dict(moscow=[(x["arrival_at"], x["window_from"], x["window_to"]) for x in missed["stops"]], utc=[(x["arrival_at"], x["window_from"], x["window_to"]) for x in utc["stops"]])
    after = call("GET", f"{PRE}/trips/{trip}/time-context"); report["time_context_after_change"] = {k: after.get(k) for k in ("version", "source_hash", "approval_status")}
    report["stale_approval"] = http("POST", PRE + "/time-approvals", dict(approval, operation_id=TAG + ".approve.stale"))
    assert report["stale_approval"][0] == 409, report["stale_approval"]
    report["checks"].append("Changed store window: old approval basis refused (" + json.dumps(report["stale_approval"][1], ensure_ascii=False)[:120] + "); approval status " + str(after.get("approval_status")))
    # Dispatcher decision on the hard violation: approving the violating timetable on the current basis.
    report["violating_approval"] = http("POST", PRE + "/time-approvals", dict(approval, operation_id=TAG + ".approve.violation", expected_version=after["version"], source_hash=after["source_hash"],
                                        reason="Attempt to approve a timetable that misses the store window"))
    assert report["violating_approval"][0] == 409 and "DELIVERY_HARD_WINDOW_MISSED" in json.dumps(report["violating_approval"][1]), report["violating_approval"]
    report["checks"].append("Approval of the timetable that misses the strict store window is refused (TT_TIME_ROUTE_SCHEDULE_REJECTED)")
    # Decision by the original process: the store window is restored (agreed with the store) and the timetable is approved again.
    windows(reachable); again = calc(); report["restored"] = summary(again); assert not again.get("issues"), report["restored"]
    current = call("GET", f"{PRE}/trips/{trip}/time-context")
    report["reapproved"] = call("POST", PRE + "/time-approvals", dict(approval, operation_id=TAG + ".approve.again", expected_version=current["version"], source_hash=current["source_hash"],
                                                                     reason="Store window agreed again; approve the real-road timetable"))
    report["checks"].append("Window agreed again: timetable without violations approved on the new basis")
    save()


def retire(st, ware, tag):
    """Only own planning metadata (live_extra_stop.py pattern); approval/refresh receipts stay as immutable history."""
    addresses = [tag + "." + name for name, _, _ in POINTS]
    if st.get("depot_version"):
        st["depot_version"] = fenced(WarehouseDepot(OracleGateway()).apply, tag + ".depot.retire", dict(warehouse_id=ware, expected_version=st["depot_version"], depot_address=None,
            reason="Retire owned route windows fixture"), "admin")["version"]; st["depot_retired"] = True
    with oracle_connection() as c:
        q = c.cursor()
        for pid, uid in st.get("pallets", []):
            q.execute("delete from RRL_SBORKA_PALLETS where ID=:p and PALLET_UID=:u", p=pid, u=uid)
        if st.get("trip"):
            q.execute("delete from RRL_TT_OPERATIONS where TT_ID=:t and FACT_START is null and FACT_END is null", t=st["trip"])
            q.execute("update RRL_TRANSPORT_TASK set DELETED=1 where ID=:t and USER_ID='admin'", t=st["trip"])
        if st.get("vehicle"):
            q.execute("update RRL_TR_VEHICLE set DELETED=1 where ID=:v and NUM like 'RW27V%'", v=st["vehicle"])
        for a in addresses:
            q.execute("delete from RRL_ADDR_DISTANCE_MATRIX where FROM_ADDR=:a or TO_ADDR=:a", a=a)
            q.execute("update RRL_ADDR set DELETED3=1 where ADDR=:a", a=a)
        q.execute("update RRL_ACCESS_OBJECT set ACTIVE=0 where KIND='WAREHOUSE' and OBJECT_ID=:w", w=str(ware))
        c.commit()
        q.execute("select count(*) from USER_OBJECTS where STATUS='INVALID'"); st["invalid_after_retire"] = q.fetchone()[0]
    st["retired"] = True


if __name__ == "__main__":
    if sys.argv[1:2] == ["--retire"]:  # retire an earlier own run from its evidence file
        path = Path(sys.argv[2]); old = json.loads(path.read_text(encoding="utf-8")); assert old["tag"].startswith("RW27") and not old["state"].get("retired")
        retire(old["state"], old["warehouse"], old["tag"]); path.write_text(json.dumps(old, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
        print(json.dumps(old["state"])); sys.exit(0)
    try:
        run(); report["status"] = "RUN_COMPLETE_REVIEW"
    except Exception as exc:
        report["error"] = repr(exc)[:3000]; raise
    finally:
        if state["created"] and "--keep" not in sys.argv:
            retire(state, WARE, TAG)
        save()
        print(json.dumps(dict(status=report["status"], tag=TAG, trip=state["trip"], checks=report["checks"], error=report.get("error")), ensure_ascii=False)[:3000])
