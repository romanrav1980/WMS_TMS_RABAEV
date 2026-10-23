"""C-0170 LIVE READ ONLY: the current-owner check that already runs before the cached receipt (POSTING_API calls
RRL_CASE_TASK_ACCESS.assert_command at line 78 before the replay lookup and at 263 after the locks; assert_scope calls
RRL_TRADE_CASE_ACCESS.assert_scope first). Called directly for a real trade CASE task with GLOBAL_ADMIN and a non-owner actor."""
import json, pathlib, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway

res = {"probes": []}
with OracleGateway().transaction("C-0170 owner probe READ ONLY") as cur:
    cur.execute("set transaction read only")
    task = 1161  # trade CASE on 220793322 (not CASE1168/1169)
    cur.execute("""select count(*),count(t.CUSTOMER_ORDER_ROW_ID),min(t.SOURCE_OWNER_ID) from RRL_CASE_PICK_LINE l join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=l.PICK_PLAN_LINE_ID
        left join RRL_TRADE_ORDER_LINE t on t.CUSTOMER_ORDER_ROW_ID=pl.CUSTOMER_ORDER_ROW_ID where l.CASE_PICK_TASK_ID=:t""", t=task)
    res["task"] = {"case_task_id": task, "lines_total_tagged_owner": list(cur.fetchone())}
    for actor in ("admin", "STM3"):
        for call, args in (("RRL_TRADE_CASE_ACCESS.assert_scope", [task, actor, 1]),
                           ("RRL_CASE_TASK_ACCESS.assert_scope", [task, actor, "case_pick_short_approve", None])):
            try:
                cur.callproc(call, args); outcome = "ALLOWED"
            except oracledb.DatabaseError as exc:
                outcome = str(exc.args[0]).split("\n")[0]
            res["probes"].append({"actor": actor, "call": call, "outcome": outcome})
    cur.execute("rollback")
pathlib.Path(__file__).resolve().parents[1].joinpath("owner-probe.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps(res, indent=1))
