"""C-0165 READ ONLY: a never-seen SQL text (unique comment) around the same warm PL/SQL call forces a hard parse of the SQL only.
If it stays near the warm time, the cold first call is spent loading PL/SQL units, not parsing or executing the SQL."""
import json, pathlib, sys, time, uuid
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway

res = []
with OracleGateway().transaction("C-0165 hard parse probe READ ONLY") as cur:
    cur.execute("set transaction read only")
    cur.execute("select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where SSCC='099999990000026027'"); task = cur.fetchone()[0]
    cur.execute("select s.PALLET_UID from RRL_CASE_PICK_TASK c join RRL_SBORKA_PALLETS s on s.ID=c.LEGACY_SBORKA_PALLET_ID where c.CASE_PICK_TASK_ID=:t", t=task); uid = cur.fetchone()[0]
    for kind, sql, bind in (("hu", "select dbms_lob.getlength(RRL_STOCK_HU_READ.case_snapshot_json(:x)) /*C0165 {}*/ from dual", task),
                            ("qc", "select dbms_lob.getlength(RRL_STOCK_QC_GATE.status_json(:x)) /*C0165 {}*/ from dual", uid)):
        for attempt in ("same text warm", "new text hard parse", "new text hard parse"):
            text = sql.format("warm" if attempt == "same text warm" else uuid.uuid4().hex)
            t = time.perf_counter(); cur.execute(text, x=bind); cur.fetchall()
            res.append({"call": kind, "attempt": attempt, "ms": round((time.perf_counter() - t) * 1000, 1)})
    cur.execute("rollback")
pathlib.Path(__file__).resolve().parents[1].joinpath("hard-parse.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps(res))
