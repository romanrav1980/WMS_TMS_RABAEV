"""C-0165 READ ONLY: first native call in a brand-new session (separate process); argument = call order, e.g. hu,hu,qc."""
import sys,time
sys.path.insert(0,'C:/projects/TMS/scripts'); sys.path.insert(0,'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
order=sys.argv[1].split(",")
g=OracleGateway()
with g.transaction("C-0165 fresh session READ ONLY") as cur:
    cur.execute("set transaction read only")
    t=time.perf_counter(); cur.execute("select 1 from dual"); cur.fetchall(); print("dual",round((time.perf_counter()-t)*1000,1))
    cur.execute("select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where SSCC='099999990000026027'"); task=cur.fetchone()[0]
    cur.execute("select PALLET_UID from RRL_SBORKA_PALLETS s join RRL_CASE_PICK_TASK c on s.ID=c.LEGACY_SBORKA_PALLET_ID where c.CASE_PICK_TASK_ID=:t",t=task); uid=cur.fetchone()[0]
    for step in order:
        t=time.perf_counter()
        if step=="hu": cur.execute("select dbms_lob.getlength(RRL_STOCK_HU_READ.case_snapshot_json(:t)) from dual",t=task)
        elif step=="qc": cur.execute("select dbms_lob.getlength(RRL_STOCK_QC_GATE.status_json(:p)) from dual",p=uid)
        cur.fetchall(); print(step,round((time.perf_counter()-t)*1000,1))
