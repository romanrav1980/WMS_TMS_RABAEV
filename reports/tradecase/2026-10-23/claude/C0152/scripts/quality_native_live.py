"""C-0152: READ ONLY shape of native quality/quarantine objects (columns, counts, source excerpts; no writes)."""
import re, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
with OracleGateway().transaction("C-0152 quality native READ ONLY") as cur:
    cur.execute("set transaction read only")
    for t in ("RRL_QUALITY_HOLD", "RRL_INVENTORY_TASK", "RRL_STORE_DISCREPANCY_CASE", "RRL_STORE_LOSS_RECOGNITION"):
        cur.execute("select column_name||':'||data_type from user_tab_columns where table_name=:t order by column_id", t=t)
        cols = [r[0] for r in cur.fetchall()]
        cur.execute(f"select count(*) from {t}"); print(t, cur.fetchone()[0], cols)
    cur.execute("select STATUS,count(*) from RRL_QUALITY_HOLD group by STATUS") if False else None
    for name, pat in [("RRL_STOCK_INTERNAL_CMD", r"QUARANT|quarant"), ("RRL_STOCK_QUALITY_ENTRY", r"procedure|function|QUALITY_HOLD|raise_application_error")]:
        cur.execute("select line,text from user_source where name=:n and type='PACKAGE BODY' order by line", n=name)
        rows = cur.fetchall(); hits = [l for l, t in rows if re.search(pat, t)]
        print("==", name, len(rows), "lines")
        for l, t in rows:
            if l in hits: print(" ", l, t.rstrip()[:220])
