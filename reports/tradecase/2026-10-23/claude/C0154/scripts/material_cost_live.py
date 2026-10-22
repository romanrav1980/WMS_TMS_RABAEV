"""C-0154: READ ONLY cost of the native calls one extra-stop variant makes (RRL_STORE_WINDOW_RULES.material, RRL_TT_ROUTE_SCHEDULE.material,
calculate) on REAL trip sources; projects the evaluation cost for n stops = 1 + (n+1) calculate + 2(n+1) material. No writes."""
import json, sys, time, pathlib, statistics
sys.path.insert(0, "C:/projects/TMS/scripts"); sys.path.insert(0, "C:/projects/TMS/api/wms_api_server")
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import read_oracle_json

out = {"kind": "REAL_TRIP_SOURCES_READ_ONLY_NATIVE_CALL_COST"}
with OracleGateway().transaction("C-0154 material cost READ ONLY") as cur:
    cur.execute("set transaction read only")
    cur.execute("""select p.TRANSTASK_ID,count(distinct p.ADDR) n from RRL_SBORKA_PALLETS p join RRL_TRANSPORT_TASK t on t.ID=p.TRANSTASK_ID
      group by p.TRANSTASK_ID order by n desc fetch first 1 rows only""")
    biggest, biggest_n = cur.fetchone()
    for trip in (33665, 33564, int(biggest)):
        ctx = cur.var(oracledb.DB_TYPE_CLOB); cur.callproc("RRL_TT_TIME_API.context", [trip, "admin", ctx]); src = read_oracle_json(ctx.getvalue())["source"]
        wire = json.dumps(src, ensure_ascii=False); n = len(src["route_material"]["stops"])
        timings = {}
        for name, proc, args in [("window_material", "RRL_STORE_WINDOW_RULES.material", 1), ("route_material", "RRL_TT_ROUTE_SCHEDULE.material", 1), ("calculate", "RRL_TT_ROUTE_SCHEDULE.calculate", 2)]:
            ms = []
            for _ in range(10):
                w = cur.var(oracledb.DB_TYPE_CLOB); w.setvalue(0, wire); r = cur.var(oracledb.DB_TYPE_CLOB)
                t = time.perf_counter(); cur.callproc(proc, [w, r] if args == 1 else [w, "UTC", r]); ms.append((time.perf_counter() - t) * 1000)
            timings[name] = round(statistics.median(ms), 1)
        per_variant = timings["window_material"] + timings["route_material"] + timings["calculate"]
        projected = round(timings["calculate"] + (n + 1) * per_variant, 1)
        out[str(trip)] = {"stops": n, "median_ms": timings, "per_variant_ms": round(per_variant, 1), "calls": {"calculate": n + 2, "material": 2 * (n + 1)}, "projected_evaluate_ms": projected}
        print(trip, out[str(trip)])
    out["largest_trip_by_addresses"] = {"trip": int(biggest), "addresses": int(biggest_n)}
pathlib.Path(__file__).parent.parent.joinpath("material-cost-live.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
