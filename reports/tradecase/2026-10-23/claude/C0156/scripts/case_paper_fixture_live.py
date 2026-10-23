"""C-0156: the /paper answer for real CASE tasks, built READ ONLY from live rows. The line signature is the NOT_APPLIED
RRL_CASE_PICK_PAPER.line_signature executed unchanged as an anonymous block; barcode and device flags are the backend code itself.
Output feeds the UI check as a fixture TRANSPORT (the API on :8088 is not restarted and the package is not applied). Also times each read."""
import json, pathlib, sys, time
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway
from app.transaction_gateway import TransactionGateway
from app.modules.inventory.domain.case_paper import case_line_barcode
from app.modules.inventory.infrastructure.case_paper import POLICY, _device
from app.modules.resources.public import assert_case_task_access
sql = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_case_pick_paper/001_case_pick_paper.sql").read_text(encoding="utf-8")
body = sql[sql.index("create or replace package body"):]
fn = body[body.index(" function line_signature"):body.index(" procedure assert_expected")]
SIGN = "declare\n" + fn + "begin :out := line_signature(:line); end;"
out, timing = {}, {}
with OracleGateway().transaction("C-0156 paper fixture READ ONLY") as cur:
    cur.execute("set transaction read only")
    bound = TransactionGateway(cur)
    for task in (1019, 1020):
        t0 = time.perf_counter(); assert_case_task_access(cur, task, "admin", "case_pick_execute"); timing[f"scope_{task}_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        t0 = time.perf_counter()
        head = bound.fetch_all("select t.CASE_PICK_TASK_ID TASK_ID,t.WARE_ID,w.WAVE_CODE,co.ORDER_NO,c.CUSTOMER_NAME,t.SSCC,t.STATUS,t.ASSIGNED_TO,"
            "t.ASSIGNMENT_VERSION,t.CONTENT_VERSION from RRL_CASE_PICK_TASK t join RRL_PICK_WAVE w on w.PICK_WAVE_ID=t.PICK_WAVE_ID "
            "join RRL_CUSTOMER_ORDER co on co.CUSTOMER_ORDER_ID=t.CUSTOMER_ORDER_ID left join RRL_CUSTOMER c on c.CUSTOMER_ID=t.CUSTOMER_ID "
            "where t.CASE_PICK_TASK_ID=:task", {"task": task})
        lines = bound.fetch_all("select CASE_PICK_LINE_ID LINE_ID,ARTICUL,PRODUCT_NAME,CELL_CODE,PICK_SEQUENCE,"
            "to_char(PLANNED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PLANNED_QTY,"
            "to_char(nvl(PICKED_QTY,0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PICKED_QTY,STATUS,REQUIRED_SCAN_MODE from RRL_CASE_PICK_LINE "
            "where CASE_PICK_TASK_ID=:task order by PICK_SEQUENCE nulls last,CASE_PICK_LINE_ID fetch first 201 rows only", {"task": task})
        timing[f"rows_{task}_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        t0 = time.perf_counter(); policy = {r["articul"]: r for r in bound.fetch_all(POLICY, {"task": task, "line": None})}; timing[f"policy_{task}_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        for item in lines:
            v = cur.var(oracledb.DB_TYPE_VARCHAR); t0 = time.perf_counter(); cur.execute(SIGN, out=v, line=item["line_id"]); item["signature"] = v.getvalue()
            timing[f"signature_{item['line_id']}_ms"] = round((time.perf_counter() - t0) * 1000, 1)
            item["reference"], item["barcode_svg"] = case_line_barcode(task, item["line_id"], item["signature"])
            item["device_required"] = _device(policy[item["articul"]]); item["scale_reading"] = bool(policy[item["articul"]]["weighted_kg"]) and item["device_required"] is None
        out[str(task)] = {"task": head[0], "lines": lines, "prepared_at": "2026-10-23T08:00:00+00:00"}
        print(task, head[0]["status"], [(l["line_id"], l["cell_code"], l["planned_qty"], l["picked_qty"], l["device_required"]) for l in lines])
root = pathlib.Path(__file__).parent.parent
root.joinpath("case-paper-fixture.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
root.joinpath("case-paper-sql-timing.json").write_text(json.dumps(timing, indent=1), encoding="utf-8")
print(timing)
