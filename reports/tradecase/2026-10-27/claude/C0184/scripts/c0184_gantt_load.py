"""C-0184 T10: bounded read-only load profile of GET /api/resources/timeline on the running API 8093.
Two QA warehouses, one 6 h window, per warehouse 3 serial GETs then 1 round of 4 concurrent GETs (14 total, cap 30).
A 403 stops that warehouse. Oracle is read only (set transaction read only) for RRL_SQL_SLOW_LOG. Credentials stay in memory."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import base64, hashlib, json, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection

OUT = Path(__file__).resolve().parents[1]
API, WAREHOUSES, WINDOW, CAP = "http://127.0.0.1:8093", [220793322, 226192056], ("2026-10-27T12:00:00+00:00", "2026-10-27T18:00:00+00:00"), 30
PASSWORD = re.search(r"PASS=(\S+?)[`,)\s]", (ROOT / "AGENTS.md").read_text(encoding="utf-8"))[1]
AUTH = {"Authorization": "Basic " + base64.b64encode(f"admin:{PASSWORD}".encode()).decode()}
sent = 0
REPEAT = "repeat" in sys.argv  # second pass: one more concurrent round per warehouse only, to see whether the concurrent latency reproduces


def processes():
    ps = "Get-NetTCPConnection -State Listen -LocalPort 8088,8093 | ForEach-Object { $p = Get-CimInstance Win32_Process -Filter \"ProcessId=$($_.OwningProcess)\"; \"$($_.LocalPort)|$($p.ProcessId)|$($p.CreationDate)\" }"
    return sorted(set(subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True).stdout.split()))


def get(ware):
    global sent
    sent += 1; assert sent <= CAP, "request cap"
    q = urllib.parse.urlencode(dict(warehouse_id=ware, start_at=WINDOW[0], finish_at=WINDOW[1]))
    start = time.perf_counter()
    try:
        r = urllib.request.urlopen(urllib.request.Request(f"{API}/api/resources/timeline?{q}", headers=AUTH), timeout=120); raw = r.read(); status = r.status
    except urllib.error.HTTPError as e:
        raw, status = e.read(), e.code
    ms = round((time.perf_counter() - start) * 1000, 1)
    row = dict(status=status, ms=ms, bytes=len(raw))
    if status == 200:
        d = json.loads(raw); events = sorted(e["event_id"] for e in d["events"] + d["unscheduled"]); pairs = sorted(f'{a["event_id"]}>{a["resource_id"]}' for a in d["assignments"])
        row.update(resources=len(d["resources"]), events=len(events), assignments=len(pairs),
                   resource_kinds=sorted({x["kind"] for x in d["resources"]}), sources={s["source_id"]: s["status"] for s in d["sources"]},
                   ids_hash=hashlib.sha256(json.dumps([events, pairs]).encode()).hexdigest()[:16])
    else:
        row["body"] = raw[:300].decode("utf-8", "replace")
    return row


def main():
    report = dict(api=API, window=WINDOW, started=datetime.now(timezone.utc).isoformat(), processes_before=processes(), warehouses={})
    for ware in WAREHOUSES:
        w = report["warehouses"][str(ware)] = dict(serial=[], concurrent=[])
        for _ in range(0 if REPEAT else 3):
            row = get(ware); w["serial"].append(row)
            if row["status"] == 403: w["stopped"] = "403"; break
        if "stopped" in w: continue
        with ThreadPoolExecutor(max_workers=4) as pool:
            w["concurrent"] = list(pool.map(lambda _: get(ware), range(4)))
        rows = w["serial"] + w["concurrent"]
        if REPEAT: w["serial_ms"] = None
        w["same_ids"] = len({r.get("ids_hash") for r in rows}) == 1
        for k, part in (("serial", w["serial"]), ("concurrent", w["concurrent"])) if not REPEAT else (("concurrent", w["concurrent"]),):
            ms = sorted(r["ms"] for r in part); w[k + "_ms"] = dict(min=ms[0], median=ms[len(ms) // 2], max=ms[-1])
    report["requests"] = sent
    time.sleep(2)
    with oracle_connection() as c:
        q = c.cursor(); q.execute("set transaction read only")
        q.execute("""select to_char(CREATED_AT,'HH24:MI:SS.FF3'),ELAPSED_MS,API_METHOD,API_PATH,OPERATION_KIND,substr(SQL_TEXT,1,200),ROW_COUNT
            from RRL_SQL_SLOW_LOG where CREATED_AT>=cast(to_timestamp_tz(:t,'YYYY-MM-DD"T"HH24:MI:SS.FF TZH:TZM') as timestamp) order by ELAPSED_MS desc fetch first 20 rows only""",
                  t=report["started"].replace("+00:00", " +00:00"))
        report["slow_log_since_start"] = [list(r) for r in q.fetchall()]
        q.execute("select systimestamp, sessiontimezone from dual"); report["db_clock"] = [str(x) for x in q.fetchone()]
    report["processes_after"] = processes()
    report["finished"] = datetime.now(timezone.utc).isoformat()
    (OUT / ("c0184-gantt-load-repeat.json" if REPEAT else "c0184-gantt-load.json")).write_text(json.dumps(report, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("requests", "processes_before", "processes_after")}, default=str))
    for ware, w in report["warehouses"].items():
        print(ware, w.get("stopped"), w.get("same_ids"), w.get("serial_ms"), w.get("concurrent_ms"),
              [(r["status"], r.get("resources"), r.get("events"), r.get("assignments"), r["bytes"]) for r in w["serial"][:1]])
    print("slow", report["slow_log_since_start"][:5])


main()
