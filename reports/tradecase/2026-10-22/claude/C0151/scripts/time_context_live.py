"""C-0151: READ ONLY native time context + schedule for TRADECASE trips: which route inputs are missing (no writes)."""
import json, sys, time
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import read_oracle_json
def shape(v, d=0):
    if isinstance(v, dict): return {k: shape(x, d + 1) for k, x in v.items()} if d < 4 else "{..}"
    if isinstance(v, list): return [shape(v[0], d + 1), f"len={len(v)}"] if v else []
    return v if isinstance(v, (bool, int, float)) or v is None else type(v).__name__
for trip in [int(a) for a in sys.argv[1:]] or [33665]:
    with OracleGateway().transaction("C-0151 time context READ ONLY") as cur:
        cur.execute("set transaction read only")
        out = cur.var(oracledb.DB_TYPE_CLOB); t = time.perf_counter()
        cur.callproc("RRL_TT_TIME_API.context", [trip, "admin", out]); ctx = read_oracle_json(out.getvalue()); t1 = time.perf_counter()
        wire = cur.var(oracledb.DB_TYPE_CLOB); wire.setvalue(0, json.dumps(ctx["source"], ensure_ascii=False))
        cur.callproc("RRL_TT_ROUTE_SCHEDULE.calculate", [wire, "UTC", out]); res = read_oracle_json(out.getvalue()); t2 = time.perf_counter()
        print("TRIP", trip, "context_ms", round((t1 - t) * 1000), "calc_ms", round((t2 - t1) * 1000))
        print(" source keys", json.dumps(shape(ctx["source"]), ensure_ascii=False)[:2500])
        print(" result", json.dumps({k: res[k] for k in res if k not in ("stops",)}, ensure_ascii=False, default=str)[:900])
        print(" stop0", json.dumps(res.get("stops", [{}])[:1], ensure_ascii=False, default=str)[:700])
