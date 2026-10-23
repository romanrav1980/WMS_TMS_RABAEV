"""C-0156: line_signature of the NOT_APPLIED RRL_CASE_PICK_PAPER, executed unchanged as a READ ONLY anonymous block on real CASE lines."""
import json, pathlib, sys, time
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway
sql = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_case_pick_paper/001_case_pick_paper.sql").read_text(encoding="utf-8")
body = sql[sql.index("create or replace package body"):]
fn = body[body.index(" function line_signature"):body.index(" procedure assert_expected")]
BLOCK = "declare\n" + fn + "begin :out := line_signature(:line); end;"
out = {}
with OracleGateway().transaction("C-0156 signature READ ONLY") as cur:
    cur.execute("set transaction read only")
    cur.execute("""select l.CASE_PICK_LINE_ID from RRL_CASE_PICK_LINE l join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID
      where t.STATUS in('NEW','ASSIGNED','IN_PROGRESS') order by l.CASE_PICK_LINE_ID fetch first 3 rows only""")
    lines = [r[0] for r in cur.fetchall()]
    for line in lines:
        sigs = []
        for _ in range(2):
            v = cur.var(oracledb.DB_TYPE_VARCHAR); t = time.perf_counter(); cur.execute(BLOCK, out=v, line=line); sigs.append((v.getvalue(), round((time.perf_counter() - t) * 1000, 1)))
        out[str(line)] = {"signature": sigs[0][0], "stable": sigs[0][0] == sigs[1][0], "ms": [s[1] for s in sigs]}
        print(line, out[str(line)])
pathlib.Path(__file__).parent.parent.joinpath("case-signature-live.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

# Field coverage, READ ONLY: the same function text with one in-memory change after the row reads (nothing is written).
ANCHOR = "  j.put('task'"
CASES = {"picked_qty+1": "l.PICKED_QTY:=nvl(l.PICKED_QTY,0)+1;", "cell": "l.CELL_CODE:=l.CELL_CODE||'X';", "planned_qty+1": "l.PLANNED_QTY:=l.PLANNED_QTY+1;",
         "assigned_to": "t.ASSIGNED_TO:=nvl(t.ASSIGNED_TO,'-')||'X';", "carrier": "t.SSCC:=t.SSCC||'0';", "line_status": "l.STATUS:='PARTIAL_X';",
         "scan_mode": "l.REQUIRED_SCAN_MODE:='X';", "task_status (expected same)": "t.STATUS:='IN_PROGRESS_X';",
         "assignment_version (expected same)": "t.ASSIGNMENT_VERSION:=t.ASSIGNMENT_VERSION+1;", "content_version (expected same)": "t.CONTENT_VERSION:=t.CONTENT_VERSION+1;"}
cover = {}
with OracleGateway().transaction("C-0156 signature coverage READ ONLY") as cur:
    cur.execute("set transaction read only")
    line = lines[0]
    for name, change in CASES.items():
        v = cur.var(oracledb.DB_TYPE_VARCHAR)
        cur.execute("declare\n" + fn.replace(ANCHOR, "  " + change + "\n" + ANCHOR, 1) + "begin :out := line_signature(:line); end;", out=v, line=line)
        cover[name] = v.getvalue() != out[str(line)]["signature"]
        print(name, "changes signature" if cover[name] else "same signature")
pathlib.Path(__file__).parent.parent.joinpath("case-signature-coverage-live.json").write_text(json.dumps({"line": line, "changes": cover}, indent=1), encoding="utf-8")
