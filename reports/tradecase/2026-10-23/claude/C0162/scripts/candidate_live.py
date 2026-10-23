"""C-0162 READ ONLY evidence: the candidate RRL_STOCK_POOL_CMD.assert_access (with require_edit/require_plan_owners/nonnegative) executed
unchanged as an anonymous block against root's real recorded pool operations (trade plans with 'sources') and the non-trade plan:
  - admin (GLOBAL_ADMIN) → allowed, owners of the recorded classes checked;
  - an active user without any pool right → POOL_ALLOCATION_FORBIDDEN before anything about the stored operation is shown;
  - a new operation id → only the warehouse right (owners are checked by execute for the plan being posted).
No writes: READ ONLY transaction."""
import json, pathlib, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway
K = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_trade_pool_access")
NL = "\n"
body = (K / "002_pool_cmd_body.sql").read_text(encoding="utf-8")
FN = (body[body.index(" function nonnegative("):body.index(" function same_snapshot(")]
      + body[body.index(" procedure require_edit("):body.index(" procedure execute_command(")])
BLOCK = "declare" + NL + FN + "begin assert_access(:req,:actor);end;"
out = {}
with OracleGateway().transaction("C-0162 candidate READ ONLY") as cur:
    cur.execute("set transaction read only")
    cur.execute("select OPERATION_ID,json_value(CANONICAL_REQUEST,'$.source.warehouse'),json_value(CANONICAL_REQUEST,'$.source.article'),"
                "case when dbms_lob.instr(RESOLVED_PLAN_JSON,'\"sources\"')>0 then 1 else 0 end from RRL_STOCK_OPERATION "
                "where COMMAND_TYPE='RESERVATION_ALLOCATE_POOL' order by CREATED_AT desc fetch first 6 rows only")
    ops = cur.fetchall()
    cur.execute("select ID from RUSERS where nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'stock_reservation_edit')=0 and rownum=1")
    nobody = cur.fetchone()[0]
    for op, ware, article, trade in ops:
        for actor in ("admin", nobody):
            req = json.dumps({"operation_id": op, "command_type": "RESERVATION_ALLOCATE_POOL", "source": {"type": "DEMAND_POOL", "warehouse": int(ware), "article": article}})
            try:
                cur.execute(BLOCK, req=req, actor=actor); r = "ALLOWED"
            except oracledb.DatabaseError as e:
                r = str(e.args[0]).split(NL)[0]
            out[f"{op}|{actor}"] = {"trade_plan": bool(trade), "result": r}
            print(op, actor, "trade" if trade else "plain", r)
    ware, article = int(ops[0][1]), ops[0][2]
    for actor in ("admin", nobody):
        req = json.dumps({"operation_id": "C0162.NEW.OPERATION", "command_type": "RESERVATION_ALLOCATE_POOL", "source": {"type": "DEMAND_POOL", "warehouse": ware, "article": article}})
        try:
            cur.execute(BLOCK, req=req, actor=actor); r = "ALLOWED"
        except oracledb.DatabaseError as e:
            r = str(e.args[0]).split(NL)[0]
        out[f"NEW|{actor}"] = {"trade_plan": None, "result": r}; print("new op", actor, r)
pathlib.Path(__file__).parent.parent.joinpath("candidate-live.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
