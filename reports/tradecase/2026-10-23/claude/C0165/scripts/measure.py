"""C-0165 READ ONLY measurement: the same Python callers as the two GET routes, every cursor execute/callproc timed separately.
Probe 1 runs on a brand-new connection, then warm repeats. Usage: measure.py <label> [repeats]. Nothing is written."""
import json, pathlib, statistics, sys, time
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.bulk_loading_read import bulk_loading_preview
from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality

SSCC, ACTOR = "099999990000026027", "admin"
label, repeats = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 5
trace = []
orig_exec, orig_proc = oracledb.Cursor.execute, oracledb.Cursor.callproc


def timed_exec(self, statement, *a, **k):
    t = time.perf_counter()
    try:
        return orig_exec(self, statement, *a, **k)
    finally:
        trace.append(("SQL", " ".join(str(statement).split())[:110], round((time.perf_counter() - t) * 1000, 1)))


def timed_proc(self, name, *a, **k):
    t = time.perf_counter()
    try:
        return orig_proc(self, name, *a, **k)
    finally:
        trace.append(("CALL", name, round((time.perf_counter() - t) * 1000, 1)))


oracledb.Cursor.execute, oracledb.Cursor.callproc = timed_exec, timed_proc
out = {"label": label, "identifier": SSCC, "actor": ACTOR, "probes": {}}
for name, run in (("bulk-box-preview", lambda g: bulk_loading_preview(g, SSCC, ACTOR)), ("outgoing-quality", lambda g: OutgoingQuality(g).status(SSCC, ACTOR))):
    probes = []
    for i in range(repeats):
        g = OracleGateway()  # probe 0: new gateway; the gateway pools connections, so later probes are warm
        trace.clear(); t = time.perf_counter()
        try:
            result, error = run(g), None
        except Exception as exc:  # the exact refusal is part of the evidence
            result, error = None, f"{type(exc).__name__}: {getattr(exc, 'detail', exc)}"
        total = round((time.perf_counter() - t) * 1000, 1)
        probes.append({"probe": i, "total_ms": total, "error": error, "steps": list(trace),
                       "result_sha": None if result is None else __import__("hashlib").sha256(json.dumps(result, sort_keys=True, default=str).encode()).hexdigest()})
        if i == 0:
            out.setdefault("results", {})[name] = result
    warm = [p["total_ms"] for p in probes[1:]]
    out["probes"][name] = {"first_ms": probes[0]["total_ms"], "warm_min": min(warm), "warm_median": statistics.median(warm), "warm_max": max(warm),
                           "n_warm": len(warm), "results_identical": len({p["result_sha"] for p in probes}) == 1, "probes": probes}
OUT = pathlib.Path(__file__).resolve().parents[1]
(OUT / f"measure-{label}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
for name, p in out["probes"].items():
    print(name, "first", p["first_ms"], "warm min/med/max", p["warm_min"], p["warm_median"], p["warm_max"], "identical", p["results_identical"], "error", p["probes"][0]["error"])
    agg = {}
    for probe in p["probes"][1:]:
        for kind, s, ms in probe["steps"]:
            agg.setdefault(s, []).append(ms)
    for s, v in sorted(agg.items(), key=lambda x: -statistics.median(x[1]))[:8]:
        print("   ", statistics.median(v), "ms x", len(v) // p["n_warm"], s)
