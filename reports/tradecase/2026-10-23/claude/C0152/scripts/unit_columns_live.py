"""C-0152: READ ONLY columns of unit/attribute/cell/inventory access objects (no writes)."""
import sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
with OracleGateway().transaction("C-0152 columns READ ONLY") as cur:
    cur.execute("set transaction read only")
    for t in ("RRL_WMS_RECEIPT_UNIT", "RRL_TRADE_STOCK_ATTR", "RRL_REMAINS", "RRL_CELLS", "RRL_PALLETS"):
        cur.execute("select column_name from user_tab_columns where table_name=:t order by column_id", t=t)
        print(t, [r[0] for r in cur.fetchall()])
    cur.execute("select text from user_source where name='RRL_INVENTORY_TASK_ACCESS' and type='PACKAGE' order by line")
    print("".join(r[0] for r in cur.fetchall()))
    cur.execute("select c.WARE_ID,count(*) from RRL_CELLS c where nvl(c.BLOCKED_FOR_REMAINS,0)=1 and c.WARE_ID in(select WARE_ID from RRL_TRADE_SITE) group by c.WARE_ID")
    print("quarantine cells on trade sites", cur.fetchall())
