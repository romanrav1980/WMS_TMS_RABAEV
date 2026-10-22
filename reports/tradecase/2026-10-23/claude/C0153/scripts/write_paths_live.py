"""C-0153: READ ONLY: stock-table triggers that confine writes to the posting context (coverage of the hold guard)."""
import sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
with OracleGateway().transaction("C-0153 write paths READ ONLY") as cur:
    cur.execute("set transaction read only")
    for t in ("RRL_STOCK_REMAINS_GUARD", "RRL_STOCK_UNIT_GUARD", "RRL_PHYSICAL_VERSION_GUARD"):
        cur.execute("select status,triggering_event,trigger_body from user_triggers where trigger_name=:t", t=t)
        r = cur.fetchone(); print(t, r[0], r[1], " ".join(str(r[2]).split())[:500])
    cur.execute("select text from user_source where name='RRL_STOCK_WRITE_GUARD' and type='PACKAGE BODY' order by line")
    print("WRITE_GUARD", " ".join("".join(x[0] for x in cur.fetchall()).split())[:1200])
