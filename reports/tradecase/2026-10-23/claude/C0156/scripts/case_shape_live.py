"""C-0156: READ ONLY columns of CASE task/line tables and version-like columns (no writes)."""
import sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
with OracleGateway().transaction("C-0156 CASE shape READ ONLY") as cur:
    cur.execute("set transaction read only")
    for t in ("RRL_CASE_PICK_TASK", "RRL_CASE_PICK_LINE"):
        cur.execute("select column_name from user_tab_columns where table_name=:t order by column_id", t=t)
        print(t, [r[0] for r in cur.fetchall()])
    cur.execute("select STATUS,count(*) from RRL_CASE_PICK_TASK group by STATUS"); print("task statuses", cur.fetchall())
