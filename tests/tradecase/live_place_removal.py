"""C-0176 live check: remove selected places of one assembly from a trip. The current application code runs in-process (ASGI) against
real Oracle (8088 is restarted only by root). Own absent warehouse, own planning rows (the assembly/trip fixture pattern of
live_road_refresh.py / live_extra_stop.py): one ST with 4 places assigned to own trip through the existing ST command; no goods.
Without arguments: the places read only (the removal command needs db/migrations/2026-10-27_tt_selected_places).
--after-kit (required for the places read too: the membership version is native): remove 2 of 4, exact replay, changed payload, competing command, stale snapshot, rights; then cleanup."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
from pathlib import Path
import re
import secrets
import sys
import time
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
import oracledb
from fastapi.testclient import TestClient
from app.main import app
from tools.mcp.tms_mcp_server import oracle_connection

OUT = ROOT / "runtime/test-evidence/tradecase/2026-10-27/C0176"
AFTER_KIT = "--after-kit" in sys.argv
PASSWORD = re.search(r"PASS=(\S+?)[`,)\s]", (ROOT / "AGENTS.md").read_text(encoding="utf-8"))[1]
TAG = "PR27" + uuid4().hex[:10]
WARE = 240000000 + secrets.randbelow(9000000)
ST = TAG + ".ST"
client = TestClient(app)
report = dict(status="FAIL", mode="ASGI in-process current code + real Oracle (not served 8088)", after_kit=AFTER_KIT, tag=TAG, warehouse=WARE, checks=[], calls=[])
state = dict(created=False, trip=None, members=[])


def save():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / (TAG + ".json")).write_text(json.dumps(dict(report, state=state), indent=1, ensure_ascii=False, default=str), encoding="utf-8")


def call(method, path, body=None, status=200, auth=None):
    start = time.perf_counter()
    r = client.request(method, path, json=body, auth=auth or ("admin", PASSWORD))
    value = r.json() if r.content else None
    report["calls"].append(dict(method=method, path=path, status=r.status_code, ms=round((time.perf_counter() - start) * 1000, 1), result=value))
    assert r.status_code == status, (r.status_code, value)
    return value


def run():
    with oracle_connection() as c:
        q = c.cursor()
        q.execute("select (select count(*) from RRL_WARES where ID=:w)+(select count(*) from RRL_SBORKA_PALLETS where ST_NUMBER=:s) from dual", w=WARE, s=ST)
        assert q.fetchone() == (0,), "fixture must be absent before the first write"
        save()
        q.execute("insert into RRL_WARES(ID,NAME)values(:w,:n)", w=WARE, n="TRADECASE QA place removal " + TAG)
        q.execute("insert into RRL_ACCESS_OBJECT(KIND,OBJECT_ID,TITLE,ACTIVE,VERSION_NO)values('WAREHOUSE',:w,'C-0176 QA',1,1)", w=str(WARE))
        c.commit(); state["created"] = True
    with oracle_connection() as c:
        q = c.cursor(); q.callproc("RRL_STOCK_CONFIG_API.begin_change", ["admin", "warehouse_settings_edit"])
        try:
            out = q.var(oracledb.DB_TYPE_NUMBER); q.callproc("RRL_TRANSPORT_EDIT_API.create_trip", ["1", datetime(2026, 10, 29), "admin", out]); state["trip"] = int(out.getvalue())
            for i in range(1, 5):
                uid = TAG + ".PLACE." + str(i)
                pid = int(q.callfunc("RRL_SBORKA_PALLETS_ADD2", oracledb.DB_TYPE_NUMBER, [ST, TAG + ".ADDR", i, uid, "1", datetime(2026, 10, 29), "", "admin", WARE]))
                state["members"].append([pid, uid])
            c.commit()
        finally:
            q.callproc("RRL_STOCK_CONFIG_API.end_change")
    save()
    trip = state["trip"]
    call("POST", f"/api/admin/transport/tasks/{trip}/sts", dict(st_numbers=[ST]))  # the whole assembly through the existing command
    if not AFTER_KIT:  # the places read needs the kit's membership version function
        report["places_before_kit"] = call("GET", f"/api/transport/trips/{trip}/sts/{ST}/places", status=503)
        report["status"] = "KIT_PENDING"; return
    places = call("GET", f"/api/transport/trips/{trip}/sts/{ST}/places")
    report["places_before"] = places
    assert places["on_trip"] == 4 and [p["member_id"] for p in places["places"]] == [m[0] for m in state["members"]]
    report["checks"].append("Places of the assembly read with membership, load and shipment flags and the membership version; all 4 on the trip")
    ids = [m[0] for m in state["members"]]
    body = dict(operation_id=TAG + ".remove", st_number=ST, member_ids=ids[2:], expected_source_hash=places["source_hash"], reason="Reduced trip keeps 2 places")
    first = call("POST", f"/api/transport/trips/{trip}/place-removals", body)
    assert first["removed"] == ids[2:] and first["on_trip_after"] == 2, first
    assert call("POST", f"/api/transport/trips/{trip}/place-removals", body) == first  # the exact stored reply
    report["conflict"] = call("POST", f"/api/transport/trips/{trip}/place-removals", dict(body, reason="Changed payload"), status=409)
    report["stale"] = call("POST", f"/api/transport/trips/{trip}/place-removals", dict(body, operation_id=TAG + ".stale", member_ids=[ids[0]]), status=409)
    after = call("GET", f"/api/transport/trips/{trip}/sts/{ST}/places")
    assert [p["on_trip"] for p in after["places"]] == [True, True, False, False] and after["on_trip"] == 2
    report["checks"].append("2 of 4 removed in one command; exact replay returns the same receipt; changed payload and stale snapshot refused")
    # Two competing commands on the same snapshot: one removes, the other sees the changed snapshot.
    bodies = [dict(operation_id=TAG + ".race." + n, st_number=ST, member_ids=[ids[0]], expected_source_hash=after["source_hash"], reason="Competing removal " + n) for n in "AB"]
    with ThreadPoolExecutor(max_workers=2) as pool:
        replies = list(pool.map(lambda b: client.post(f"/api/transport/trips/{trip}/place-removals", json=b, auth=("admin", PASSWORD)), bodies))
    report["race"] = [dict(status=r.status_code, result=r.json()) for r in replies]
    assert sorted(r.status_code for r in replies) == [200, 409], report["race"]
    report["checks"].append("Two competing removals of the same place: exactly one applied, the other refused")
    # The same operation sent twice at once (a lost reply repeated): both get the stored receipt; one journal row.
    current = call("GET", f"/api/transport/trips/{trip}/sts/{ST}/places")
    remaining = [p["member_id"] for p in current["places"] if p["on_trip"]]
    twin = dict(operation_id=TAG + ".twin", st_number=ST, member_ids=remaining[-1:], expected_source_hash=current["source_hash"], reason="Repeated after a lost reply")
    with ThreadPoolExecutor(max_workers=2) as pool:
        replies = list(pool.map(lambda _: client.post(f"/api/transport/trips/{trip}/place-removals", json=twin, auth=("admin", PASSWORD)), range(2)))
    report["twin"] = [dict(status=r.status_code, result=r.json()) for r in replies]
    with oracle_connection() as c:
        q = c.cursor(); q.execute("select count(*) from RRL_TT_PLACE_REMOVAL_CMD where OPERATION_ID=:o", o=twin["operation_id"]); journal = q.fetchone()[0]
    assert [r.status_code for r in replies] == [200, 200] and replies[0].json() == replies[1].json() and journal == 1, (report["twin"], journal)
    report["checks"].append("The same operation twice at once: 2 x 200 with the identical receipt and one journal row")
    # Rights: an own actor without the dispatcher right is refused before any stored reply.
    actor, secret = "PR27" + uuid4().hex[:9], secrets.token_hex(16)
    with oracle_connection() as c:
        q = c.cursor(); q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'C-0176 QA','TC03QA',:w,0,1)", a=actor, p=secret, w=WARE); c.commit()
    report["denied"] = call("POST", f"/api/transport/trips/{trip}/place-removals", body, status=403, auth=(actor, secret))
    with oracle_connection() as c:
        q = c.cursor(); q.execute("update RUSERS set DELETED=1 where ID=:a", a=actor); c.commit()
    report["checks"].append("Actor without the dispatcher right: 403 even for the stored operation")
    report["status"] = "PASS"


def retire():
    """Own planning rows only; the removal journal stays as history."""
    with oracle_connection() as c:
        q = c.cursor()
        for pid, uid in state["members"]:
            q.execute("delete from RRL_SBORKA_PALLETS where ID=:p and PALLET_UID=:u and TRANSTASK_ID is null", p=pid, u=uid)
        c.commit()
    if state["trip"] and db_on_trip():  # the rest of the assembly leaves the trip through the existing whole-ST removal
        call("DELETE", f"/api/admin/transport/tasks/{state['trip']}/sts/{ST}")
    with oracle_connection() as c:
        q = c.cursor()
        for pid, uid in state["members"]:
            q.execute("delete from RRL_SBORKA_PALLETS where ID=:p and PALLET_UID=:u and TRANSTASK_ID is null", p=pid, u=uid)
        if state["trip"]:
            q.execute("update RRL_TRANSPORT_TASK set DELETED=1 where ID=:t and USER_ID='admin'", t=state["trip"])
        q.execute("update RRL_ACCESS_OBJECT set ACTIVE=0 where KIND='WAREHOUSE' and OBJECT_ID=:w", w=str(WARE))
        c.commit()
        q.execute("select count(*) from RRL_SBORKA_PALLETS where ST_NUMBER=:s", s=ST); state["left_rows"] = q.fetchone()[0]
    state["retired"] = True


def db_on_trip():
    with oracle_connection() as c:
        q = c.cursor(); q.execute("select count(*) from RRL_SBORKA_PALLETS where ST_NUMBER=:s and TRANSTASK_ID=:t", s=ST, t=state["trip"])
        return q.fetchone()[0] > 0


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        report["error"] = repr(exc)[:3000]; raise
    finally:
        if state["created"]:
            try:
                retire()
            except Exception as exc:
                state["retire_error"] = repr(exc)[:800]
        save(); print(json.dumps({k: report.get(k) for k in ("status", "warehouse", "checks", "error")}, ensure_ascii=False)[:2500])
