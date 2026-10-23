"""C-0156 SQL cost of the paper reader on the CASE tasks with the most lines (READ ONLY). The package is NOT_APPLIED, so the per-line
signature runs as the unchanged function in an anonymous block (one round trip per line here; installed, it is one SQL for all lines)."""
import json, pathlib, sys, time
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway
from app.transaction_gateway import TransactionGateway
from app.modules.inventory.infrastructure.case_paper import POLICY
sql = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_case_pick_paper/001_case_pick_paper.sql").read_text(encoding="utf-8")
body = sql[sql.index("create or replace package body"):]
fn = body[body.index(" function line_signature"):body.index(" procedure assert_expected")]
LOOP = "declare\n" + fn + "begin for r in(select CASE_PICK_LINE_ID id from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:task)loop :n:=line_signature(r.id);end loop;end;"
ms = lambda t: round((time.perf_counter() - t) * 1000, 1)
out = []
with OracleGateway().transaction("C-0156 scale READ ONLY") as cur:
    cur.execute("set transaction read only"); g = TransactionGateway(cur)
    big = g.fetch_all("select CASE_PICK_TASK_ID TASK,count(*) N,count(distinct ARTICUL) A from RRL_CASE_PICK_LINE group by CASE_PICK_TASK_ID order by 2 desc fetch first 3 rows only")
    for row in big:
        task = row["task"]; r = {"task": task, "lines": row["n"], "articles": row["a"]}
        for run in ("cold", "warm"):
            t = time.perf_counter(); g.fetch_all("select CASE_PICK_LINE_ID,ARTICUL,CELL_CODE,PLANNED_QTY,PICKED_QTY,STATUS,REQUIRED_SCAN_MODE from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:task fetch first 201 rows only", {"task": task}); r[f"lines_{run}_ms"] = ms(t)
            t = time.perf_counter(); g.fetch_all(POLICY, {"task": task, "line": None}); r[f"policy_{run}_ms"] = ms(t)
            v = cur.var(oracledb.DB_TYPE_VARCHAR); t = time.perf_counter(); cur.execute(LOOP, task=task, n=v); r[f"signatures_{run}_ms"] = ms(t)
        out.append(r); print(r)
pathlib.Path(__file__).parent.parent.joinpath("case-paper-scale-live.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
