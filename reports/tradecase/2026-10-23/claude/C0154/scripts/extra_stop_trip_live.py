"""C-0154: evaluate() of RRL_TRADE_EXTRA_STOP_API on REAL trips, READ ONLY anonymous block (package not installed): the PURE section,
distance_km and evaluate are taken unchanged from the migration; only the policy lookup (new table, not installed) is replaced by
"no ban, version 0". Shows what the dispatcher would see on today's data."""
import json, sys, pathlib, time
sys.path.insert(0, "C:/projects/TMS/scripts"); sys.path.insert(0, "C:/projects/TMS/api/wms_api_server")
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway

SQL = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_trade_extra_stop/002_api.sql").read_text(encoding="utf-8")
body = SQL[SQL.rindex("create or replace package body"):]
PURE = body[body.index(" -- PURE BEGIN"):body.index(" -- PURE END")]
helpers = body[body.index(" procedure fail(p_code varchar2)"):body.index(" -- Every warehouse of the trip")]
distance = body[body.index(" -- Road distance of an ordered route"):body.index(" -- Real evaluation: current native time context")]
evaluate = body[body.index(" function evaluate(p_trip number"):body.index(" procedure command(p_request clob")]
typedecl = " type policy_t is record(TRIP_ID number,NEW_STOPS_FORBIDDEN number,VERSION_NO number);\n"  # types precede subprograms
stub = (" function policy(p_trip number)return policy_t is p policy_t;begin p.TRIP_ID:=p_trip;p.NEW_STOPS_FORBIDDEN:=0;p.VERSION_NO:=0;return p;end;\n")
evaluate = evaluate.replace("p RRL_TRADE_ROUTE_STOP_POLICY%rowtype;", "p policy_t;")
BLOCK = "declare\n" + typedecl + PURE + helpers + stub + distance + evaluate + "\nbegin\n :out := evaluate(:trip, 'admin', :req);\nend;"

out = {"kind": "REAL_TRIPS_READ_ONLY_EVALUATE_WITHOUT_POLICY_TABLE"}
with OracleGateway().transaction("C-0154 extra stop real trips READ ONLY") as cur:
    cur.execute("set transaction read only")
    cur.execute("select ADDR from RRL_ADDR where nvl(DELETED3,0)=0 and UNLOAD_NORM_MIN is not null and rownum=1")
    row = cur.fetchone(); extra = row[0] if row else "NO.SUCH.ADDRESS"
    for trip in (33665, 33660, 33564):
        res = cur.var(oracledb.DB_TYPE_CLOB); req = cur.var(oracledb.DB_TYPE_CLOB)
        req.setvalue(0, json.dumps({"address": extra, "zone": "UTC"}))
        t = time.perf_counter()
        try:
            cur.execute(BLOCK, out=res, trip=trip, req=req); r = json.loads(res.getvalue().read())
        except oracledb.DatabaseError as e:
            r = {"error": str(e).split("\n")[0]}
        ms = round((time.perf_counter() - t) * 1000)
        out[str(trip)] = {"ms": ms, "result": r}
        print(trip, ms, "ms", r.get("decision"), r.get("reason"), [i["code"] for i in (r.get("before") or {}).get("issues", [])][:6], r.get("error", ""))
pathlib.Path(__file__).parent.parent.joinpath("extra-stop-trip-live.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
