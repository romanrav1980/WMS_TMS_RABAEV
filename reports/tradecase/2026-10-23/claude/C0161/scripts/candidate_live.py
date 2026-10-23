"""C-0161 READ ONLY evidence on the live DB:
1) candidate RRL_TRADE_TOPUP_READ.departed and trip_basis executed unchanged as anonymous blocks on every trade trip with load facts
   (compared with the live trip_basis: the basis must change exactly because load facts/vehicle are now part of it);
2) the Python after-load path (capacity_context) on the same trips must refuse with TOPUP_TRIP_DEPARTED, never compute space.
No writes: the transaction is READ ONLY."""
import json, pathlib, sys, time
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway
from app.modules.integrations.contracts_trade_transport import TradeTransportError
from app.modules.integrations.infrastructure.trade_capacity import capacity_context
K = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_topup_after_load")
NL = "\n"
body = (K / "002_read_body.sql").read_text(encoding="utf-8")
BLOCK = ("declare" + NL + body[body.index(" function sha("):body.index(" function loading_started(")]
         + body[body.index(" function departed("):body.index(" function need_confirmed_boxes(")]
         + "begin :b:=trip_basis(:w,:t);:d:=departed(:w,:t);end;")
out = {}
with OracleGateway().transaction("C-0161 candidate READ ONLY") as cur:
    cur.execute("set transaction read only")
    cur.execute("select distinct l.WARE_ID,l.TRIP_ID from RRL_TRADE_TRIP_LINK l join RRL_TT_HU_LOAD_FACT f on f.TT_ID=l.NATIVE_TASK_ID order by 1,2")
    trips = cur.fetchall()
    for ware, trip in trips:
        row = {}
        b, d = cur.var(oracledb.DB_TYPE_VARCHAR), cur.var(oracledb.DB_TYPE_NUMBER); t = time.perf_counter()
        try:
            cur.execute(BLOCK, b=b, d=d, w=ware, t=trip); row.update(basis=b.getvalue(), departed=int(d.getvalue()), ms=round((time.perf_counter() - t) * 1000, 1))
        except oracledb.DatabaseError as e:
            row["candidate_error"] = str(e.args[0]).split(NL)[0]
        lb = cur.var(oracledb.DB_TYPE_VARCHAR)
        try:
            cur.execute("begin :b:=RRL_TRADE_TOPUP_READ.trip_basis(:w,:t);end;", b=lb, w=ware, t=trip); row["live_basis"] = lb.getvalue()
        except oracledb.DatabaseError as e:
            row["live_basis_error"] = str(e.args[0]).split(NL)[0]
        try:
            capacity_context(cur, ware, trip, "admin"); row["python"] = "COMPUTED"
        except TradeTransportError as e:
            row["python"] = e.code
        out[f"{ware}:{trip}"] = row
        print(ware, trip, {k: row.get(k) for k in ("departed", "python", "candidate_error", "live_basis_error")}, "basis changed:", row.get("basis") != row.get("live_basis"))
pathlib.Path(__file__).parent.parent.joinpath("candidate-live.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
