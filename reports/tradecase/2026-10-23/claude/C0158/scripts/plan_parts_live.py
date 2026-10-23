"""C-0158: the parts of NOT_APPLIED RRL_YARD_DOCK_PLAN_API that need no new table, executed unchanged as READ ONLY anonymous blocks:
moment (time parsing), assert_dock (RRL_TT_DOCK of the site), lock_vehicle (dbms_lock, released at rollback). No writes."""
import json, pathlib, sys, time
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway
src = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_yard_dock_plan/004_plan_api.sql").read_text(encoding="utf-8")
body = src[src.index("create or replace package body"):]
def fn(start, end): return body[body.index(start):body.index(end)]
PARTS = fn(" procedure fail(", " procedure require(") + fn(" procedure lock_vehicle(", " procedure assert_free(")
out = {}
def run(cur, name, code):
    t = time.perf_counter()
    try: cur.execute("declare\n" + PARTS + "begin " + code + " end;"); r = "OK"
    except oracledb.DatabaseError as e: r = str(e.args[0]).split("\n")[0]
    out[name] = {"result": r, "ms": round((time.perf_counter() - t) * 1000, 1)}; print(name, out[name])
with OracleGateway().transaction("C-0158 plan parts READ ONLY") as cur:
    cur.execute("set transaction read only")
    cur.execute("select WARE_ID,DOCK from RRL_TT_DOCK where nvl(DOCK_IS_BLOCKED,0)=0 and WARE_ID in(select WARE_ID from RRL_TRADE_SITE) and rownum=1")
    ware, dock = cur.fetchone(); out["site_dock"] = [ware, dock]
    run(cur, "moment_ok", "if moment('2026-10-24T08:00:00+03:00')<>to_timestamp_tz('2026-10-24 05:00:00 +00:00','YYYY-MM-DD HH24:MI:SS TZH:TZM') then raise_application_error(-20999,'TZ'); end if;")
    for bad in ("2026-10-24 08:00", "2026-10-24T08:00:00Z", "2026-13-40T08:00:00+03:00", None):
        run(cur, f"moment_bad:{bad}", f"declare x timestamp with time zone; begin x:=moment({'null' if bad is None else repr(bad)}); end;")
    run(cur, "dock_known", f"assert_dock({ware},'{dock}');")
    run(cur, "dock_other_site", f"assert_dock({ware},'NO-SUCH-DOCK');")
    run(cur, "vehicle_lock", "lock_vehicle('A123BC77'); lock_vehicle('A123BC77'); lock_vehicle(null);")
pathlib.Path(__file__).parent.parent.joinpath("plan-parts-live.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
