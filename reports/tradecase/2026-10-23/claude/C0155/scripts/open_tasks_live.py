"""C-0155: READ ONLY count of open warehouse tasks per warehouse (to pick a UI warehouse); no writes."""
import sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
with OracleGateway().transaction("C-0155 open tasks READ ONLY") as cur:
    cur.execute("set transaction read only")
    cur.execute("""select nvl(FROM_WARE_ID,TO_WARE_ID) w,count(*) from RRL_WAREHOUSE_TASK where STATUS in('PLANNED','ASSIGNED','IN_PROGRESS')
      group by nvl(FROM_WARE_ID,TO_WARE_ID) order by 2 desc fetch first 8 rows only""")
    print(cur.fetchall())
