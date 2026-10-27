"""C-0185 T10 driver: owned temporary inbound visit on 220793322 -> BLOCK B22D1161 (dock-status API) -> real UI plan attempt at
1440/390 (c0185_ui.cjs) -> finally UNBLOCK (separate operation) and CANCEL only the owned visit -> readback. API 8093, identity admin.
The only non-API write is one tagged SUPPLY metadata document (no ERP receipt). Unknown outcomes are retried with the same body only."""
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import base64, json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[6]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection

OUT = Path(__file__).resolve().parents[1]
STATE = OUT / "c0185-state.json"
API, W, DOCK, OTHER = "http://127.0.0.1:8093", 220793322, "B22D1161", "N22DA1168"
PASSWORD = re.search(r"PASS=(\S+?)[`,)\s]", (ROOT / "AGENTS.md").read_text(encoding="utf-8"))[1]
AUTH = {"Authorization": "Basic " + base64.b64encode(f"admin:{PASSWORD}".encode()).decode(), "Content-Type": "application/json"}
s = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else dict(tag="C0185." + uuid4().hex[:10], calls=[], results={})
TAG = s["tag"]


def save():
    STATE.write_text(json.dumps(s, indent=1, ensure_ascii=False, default=str), encoding="utf-8")


def http(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(3):  # an unknown outcome is repeated with exactly the same bytes, never a different command
        start = time.perf_counter()
        try:
            r = urllib.request.urlopen(urllib.request.Request(API + path, data=data, headers=AUTH, method=method), timeout=90)
            code, raw = r.status, r.read()
        except urllib.error.HTTPError as e:
            code, raw = e.code, e.read()
        except OSError as e:
            code, raw = 0, str(e).encode()
        value = json.loads(raw) if raw[:1] in (b"{", b"[") else raw.decode("utf-8", "replace")[:300]
        s["calls"].append(dict(method=method, path=path, body=body, status=code, ms=round((time.perf_counter() - start) * 1000, 1), attempt=attempt))
        save()
        if code not in (0, 502, 503, 504):
            return code, value
    return code, value


def step(key, method, path, body, ok=(200,)):
    if key not in s["results"]:
        code, value = http(method, path, body)
        assert code in ok, (key, code, value)
        s["results"][key] = value
        save()
    return s["results"][key]


def query(sql, **binds):
    with oracle_connection() as c:
        q = c.cursor()
        q.execute("set transaction read only")
        q.execute(sql, binds)
        return [list(r) for r in q.fetchall()]


def snapshot():
    now = datetime.now(timezone.utc)
    win = urllib.parse.urlencode({"from": (now - timedelta(days=1)).isoformat(), "to": (now + timedelta(days=6)).isoformat()})
    docks = http("GET", f"/api/tradecase/warehouses/{W}/yard/docks")[1]["docks"]
    visits = http("GET", f"/api/tradecase/warehouses/{W}/yard/visits?active=true")[1]["visits"]
    plans = http("GET", f"/api/tradecase/warehouses/{W}/yard/dock-plans?{win}")[1]["plans"]
    stock = query("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE),count(*) from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w", w=W)
    return dict(docks={d["dock"]: dict(blocked=d["blocked"], ambiguous=d.get("ambiguous")) for d in docks},
                visits=sorted([v["visit_id"], v["state"]] for v in visits), plans=sorted([p["plan_id"], p["visit_id"], p["dock"]] for p in plans), stock=stock)


def preflight():
    if "before" in s:
        return
    snap = snapshot()
    assert snap["docks"].get(DOCK) == dict(blocked=False, ambiguous=False), ("dock not open/unambiguous", snap["docks"])
    assert snap["docks"].get(OTHER) == dict(blocked=False, ambiguous=False), snap["docks"]
    assert not snap["visits"], ("active visits present; abort without writing", snap["visits"])
    s.update(before=snap, slow_marker=query("select nvl(max(LOG_ID),0) from RRL_SQL_SLOW_LOG")[0][0], started=datetime.now(timezone.utc).isoformat())
    save()


def fixture():
    if s.get("supply_created"):
        return
    with oracle_connection() as c:
        q = c.cursor()
        q.execute("select NAME from RRL_WARES where ID=:w", w=W)
        assert q.fetchone()[0].startswith("TRADECASE QA ")
        q.execute("select count(*) from RRL_TRADE_DOCUMENT where WARE_ID=:w and EXTERNAL_ID=:id", w=W, id=TAG)
        assert q.fetchone()[0] == 0
        q.execute("select SOURCE_ID from RRL_TRADE_SITE where WARE_ID=:w and ENABLED=1", w=W)
        source = q.fetchone()[0]
        body = json.dumps(dict(entity_type="SUPPLY", owner_id="SNS", pallet_identifier=TAG, fixture="C-0185 controlled metadata; no ERP receipt proof"))
        q.execute("insert into RRL_TRADE_DOCUMENT(WARE_ID,ENTITY_TYPE,EXTERNAL_ID,SOURCE_ID,VERSION_NO,CONTENT_HASH,BODY_JSON,STATUS,CHANGED_BY)"
                  "values(:w,'SUPPLY',:id,:src,1,:h,:b,'ACCEPTED','admin')", w=W, id=TAG, src=source, h=sha256(body.encode()).hexdigest(), b=body)
        c.commit()
    s["supply_created"] = True
    save()


def status(key, action, reason):
    r = step(key, "POST", f"/api/tradecase/warehouses/{W}/yard/docks/{DOCK}/status", dict(operation_id=f"{TAG}.{key}", action=action, reason=reason))
    assert r["blocked"] is (action == "BLOCK") and r["dock"] == DOCK, r


def cleanup():
    s["cleanup"] = "started"
    save()
    if "block" in s["results"]:
        status("unblock", "UNBLOCK", "C-0185 QA: blocked-plan check finished, dock reopened")
    vid = s["results"].get("visit", {}).get("visit_id")
    if vid:
        current = [v for v in http("GET", f"/api/tradecase/warehouses/{W}/yard/visits?active=true")[1]["visits"] if v["visit_id"] == vid]
        if current:
            step("cancel_visit", "POST", f"/api/tradecase/warehouses/{W}/yard/visits/{vid}/transitions",
                 dict(operation_id=f"{TAG}.cancel", action="CANCEL", expected_version=current[0]["version"], reason="C-0185 QA visit no longer needed"))
    after = snapshot()
    s["after"] = after
    s["visit_final"] = query("select STATE from RRL_YARD_VISIT where VISIT_ID=:v", v=vid) if vid else None
    s["plans_for_visit"] = query("select count(*) from RRL_YARD_DOCK_PLAN where VISIT_ID=:v", v=vid) if vid else None
    s["slow_sql"] = query("select LOG_ID,ELAPSED_MS,API_PATH,substr(SQL_TEXT,1,160) from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 10 rows only", m=s["slow_marker"])
    s["checks"] = dict(dock_open=after["docks"].get(DOCK) == dict(blocked=False, ambiguous=False), visits_unchanged=after["visits"] == s["before"]["visits"],
                       plans_unchanged=after["plans"] == s["before"]["plans"], stock_equal=after["stock"] == s["before"]["stock"],
                       visit_cancelled=(s["visit_final"] == [["CANCELLED"]]) if vid else None, no_plan_for_visit=(s["plans_for_visit"] == [[0]]) if vid else None)
    s["cleanup"] = "done"
    save()


def main():
    preflight()
    fixture()
    try:
        v = step("visit", "POST", f"/api/tradecase/warehouses/{W}/yard/visits",
                 dict(operation_id=f"{TAG}.visit", supply_ids=[TAG], vehicle=TAG,
                      planned_arrival_at=(datetime.now(timezone.utc) + timedelta(hours=3)).replace(microsecond=0).isoformat()))
        status("block", "BLOCK", "C-0185 QA: damaged door, blocked-plan check")
        ui = subprocess.run(["node", str(OUT / "scripts" / "c0185_ui.cjs")], env={**os.environ, "VISIT": str(v["visit_id"])}, capture_output=True, text=True, timeout=400)
        s["ui"] = dict(code=ui.returncode, out=ui.stdout[-400:], err=ui.stderr[-800:])
        save()
    finally:
        cleanup()
    print(json.dumps(dict(tag=TAG, ui=s.get("ui", {}).get("code"), checks=s["checks"], slow=s["slow_sql"][:3]), ensure_ascii=False, default=str))


main()
