"""C-0177 T10 (BP18 double assignment): competing resource session openings through POST /api/resources/sessions/login on an own
absent warehouse with own shifts, resources, equipment and operators (existing API writers; no stock). The current application
code runs in-process (ASGI TestClient, one client per thread) against real Oracle; 8088 is restarted only by root.
Cases: one operator on two resources at once; two operators on one resource; two operators on one equipment; a reach shift with
capacity 1 and two drivers; the exact same request twice at once and after a lost reply. Then every own session is closed."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
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
from fastapi.testclient import TestClient
from app.main import app
from tools.mcp.tms_mcp_server import oracle_connection

OUT = ROOT / "runtime/test-evidence/tradecase/2026-10-27/C0177"
PASSWORD = re.search(r"PASS=(\S+?)[`,)\s]", (ROOT / "AGENTS.md").read_text(encoding="utf-8"))[1]
TAG = "SC27" + uuid4().hex[:8]
WARE = 240000000 + secrets.randbelow(9000000)
LABEL = sys.argv[1] if len(sys.argv) > 1 else "run"
report = dict(status="FAIL", label=LABEL, mode="ASGI in-process current code + real Oracle", tag=TAG, warehouse=WARE, cases={}, calls=[])
state = dict(created=False, sessions=[], operators=[])


def save():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"session-competition-{LABEL}.json").write_text(json.dumps(dict(report, state=state), indent=1, ensure_ascii=False, default=str), encoding="utf-8")


def post(path, body, client=None):
    start = time.perf_counter()
    r = (client or TestClient(app, raise_server_exceptions=False)).post(path, json=body, auth=("admin", PASSWORD))
    value = r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text[:300]
    report["calls"].append(dict(path=path, status=r.status_code, ms=round((time.perf_counter() - start) * 1000, 1), result=value))
    return r.status_code, value


def ok(path, body, status=200):
    code, value = post(path, body)
    assert code == status, (path, code, value)
    return value


def race(bodies):
    with ThreadPoolExecutor(max_workers=len(bodies)) as pool:
        replies = list(pool.map(lambda b: post("/api/resources/sessions/login", b, TestClient(app, raise_server_exceptions=False)), bodies))
    for code, value in replies:
        if code == 200:
            state["sessions"].append(value["id"])
    return [dict(status=c, result=v) for c, v in replies]


def active(where, **binds):
    with oracle_connection() as c:
        q = c.cursor(); q.execute("select count(*) from RRL_RESOURCE_SESSION s join RRL_RESOURCE r on r.RESOURCE_ID=s.RESOURCE_ID where r.WARE_ID=:w and s.STATUS in('ACTIVE','PAUSED') and " + where, w=WARE, **binds)
        return q.fetchone()[0]


def run():
    with oracle_connection() as c:
        q = c.cursor(); q.execute("select (select count(*) from RRL_WARES where ID=:w)+(select count(*) from RRL_RESOURCE where WARE_ID=:w) from dual", w=WARE)
        assert q.fetchone() == (0,), "fixture must be absent before the first write"
        save()
        q.execute("insert into RRL_WARES(ID,NAME)values(:w,:n)", w=WARE, n="TRADECASE QA sessions " + TAG)
        q.execute("insert into RRL_ACCESS_OBJECT(KIND,OBJECT_ID,TITLE,ACTIVE,VERSION_NO)values('WAREHOUSE',:w,'C-0177 QA',1,1)", w=str(WARE))
        for i in range(1, 4):
            op = f"{TAG}O{i}"
            q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'C-0177 QA operator','TC03QA',:w,0,0)", a=op, p=secrets.token_hex(12), w=WARE)
            state["operators"].append(op)
        c.commit(); state["created"] = True
    save()
    now = datetime.now().astimezone()
    shift = ok("/api/resources/shifts", dict(shift_code=TAG + ".CASE", shift_date=now.date().isoformat(), start_at=(now - timedelta(hours=1)).isoformat(),
                                             finish_at=(now + timedelta(hours=4)).isoformat(), ware_id=WARE, status="OPEN"))["id"]
    equipment = [ok("/api/resources/equipment", dict(equipment_code=f"{TAG}.E{i}", equipment_type="REACHTRUCK", equipment_name="C-0177 QA truck", ware_id=WARE))["id"] for i in (1, 2)]
    resources = [ok("/api/resources", dict(resource_code=f"{TAG}.R{i}", resource_name="C-0177 QA resource", resource_type="REACHTRUCK", resource_class="WAREHOUSE_EQUIPMENT",
                                           equipment_id=equipment[i - 1], ware_id=WARE))["id"] for i in (1, 2)]
    state.update(shift=shift, equipment=equipment, resources=resources); save()
    o1, o2, o3 = state["operators"]
    body = lambda r, op, e=None, s=shift: dict(shift_id=s, resource_id=r, equipment_id=e, operator_user_id=op, terminal_id="QA_NOT_HARDWARE")
    # 1. One operator on two resources at the same moment.
    report["cases"]["operator_twice"] = race([body(resources[0], o1, equipment[0]), body(resources[1], o1, equipment[1])])
    report["cases"]["operator_twice_active"] = active("upper(s.OPERATOR_USER_ID)=upper(:o)", o=o1)
    close_all()
    # 2. Two operators on one resource (and its equipment).
    report["cases"]["resource_twice"] = race([body(resources[0], o1, equipment[0]), body(resources[0], o2, equipment[0])])
    report["cases"]["resource_twice_active"] = active("s.RESOURCE_ID=:r", r=resources[0])
    close_all()
    # 3. Two operators, two resources, one piece of equipment.
    report["cases"]["equipment_twice"] = race([body(resources[0], o1, equipment[0]), body(resources[1], o2, equipment[0])])
    report["cases"]["equipment_twice_active"] = active("s.EQUIPMENT_ID=:e", e=equipment[0])
    close_all()
    # 4. The exact same request twice at once (a repeat after a lost reply sent concurrently), then once more after it.
    same = body(resources[0], o3, equipment[0])
    report["cases"]["same_twice"] = race([same, same])
    report["cases"]["same_again"] = dict(zip(("status", "result"), post("/api/resources/sessions/login", same)))
    if report["cases"]["same_again"]["status"] == 200:
        state["sessions"].append(report["cases"]["same_again"]["result"]["id"])
    report["cases"]["same_active"] = active("upper(s.OPERATOR_USER_ID)=upper(:o)", o=o3)
    close_all()
    # 5. Reach shift with capacity 1: two drivers on two resources at once.
    derived = ok(f"/api/resources/reach-shifts/{shift}", dict(main_drivers=1, duty_drivers=1))  # the existing MAIN/DUTY derivation
    reach = dict(id=next(x["SHIFT_ID"] if "SHIFT_ID" in x else x["shift_id"] for x in derived["shifts"] if (x.get("REACH_SHIFT_ROLE") or x.get("reach_shift_role")) == "MAIN"))
    state["reach_shift"] = reach["id"]; save()
    report["cases"]["reach_capacity"] = race([body(resources[0], o1, equipment[0], reach["id"]), body(resources[1], o2, equipment[1], reach["id"])])
    report["cases"]["reach_capacity_active"] = active("s.SHIFT_ID=:s", s=reach["id"])
    close_all()
    report["status"] = "RUN_COMPLETE"


def close_all():
    for sid in list(state["sessions"]):
        post(f"/api/resources/sessions/{sid}/logout", dict(reason="C-0177 competition case finished"))
        state["sessions"].remove(sid)
    with oracle_connection() as c:  # sessions opened by a request whose reply never reached this script
        q = c.cursor(); q.execute("select s.SESSION_ID from RRL_RESOURCE_SESSION s join RRL_RESOURCE r on r.RESOURCE_ID=s.RESOURCE_ID where r.WARE_ID=:w and s.STATUS in('ACTIVE','PAUSED')", w=WARE)
        stray = [r[0] for r in q.fetchall()]
    for sid in stray:
        post(f"/api/resources/sessions/{sid}/logout", dict(reason="C-0177 competition case finished"))
    report.setdefault("stray_closed", []).extend(stray); save()


def retire():
    close_all()
    with oracle_connection() as c:
        q = c.cursor()
        for op in state["operators"]:
            q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'", a=op)
        q.execute("update RRL_RESOURCE set ACTIVE=0 where WARE_ID=:w", w=WARE)
        q.execute("update RRL_ACCESS_OBJECT set ACTIVE=0 where KIND='WAREHOUSE' and OBJECT_ID=:w", w=str(WARE))
        c.commit()
    state["retired"] = True


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        report["error"] = repr(exc)[:2000]; raise
    finally:
        if state["created"]:
            try:
                retire()
            except Exception as exc:
                state["retire_error"] = repr(exc)[:600]
        save()
        print(json.dumps({k: (v if k != "cases" else {n: ([x["status"] for x in c] if isinstance(c, list) else c) for n, c in v.items()}) for k, v in report.items() if k in ("status", "warehouse", "cases", "error")}, ensure_ascii=False, default=str)[:3000])
