"""C-0152: READ ONLY: which native objects read RRL_QUALITY_HOLD / quarantine cells (no writes)."""
import sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
with OracleGateway().transaction("C-0152 hold readers READ ONLY") as cur:
    cur.execute("set transaction read only")
    for pat in ("RRL_QUALITY_HOLD", "QUARANTI"):
        cur.execute("select name,type,count(*) from user_source where upper(text) like :p group by name,type order by 1", p=f"%{pat}%")
        print(pat, cur.fetchall())
    cur.execute("select line,text from user_source where name='RRL_STOCK_INTERNAL_CMD' and type='PACKAGE BODY' and line between 86 and 96 order by line")
    print("".join(r[1] for r in cur.fetchall()))
