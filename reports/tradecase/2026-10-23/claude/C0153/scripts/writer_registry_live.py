"""C-0153: READ ONLY: writer registry shape and how disposal/write paths are registered (no writes)."""
import sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
with OracleGateway().transaction("C-0153 writer registry READ ONLY") as cur:
    cur.execute("set transaction read only")
    cur.execute("select column_name from user_tab_columns where table_name='RRL_STOCK_WRITER_REGISTRY' order by column_id"); print([r[0] for r in cur.fetchall()])
    cur.execute("select * from RRL_STOCK_WRITER_REGISTRY where rownum<=200")
    rows = cur.fetchall(); print(len(rows)); [print(r) for r in rows if any('DISPOS' in str(x) or 'RETURN' in str(x) or 'TARE_RESOLVE' in str(x) for x in r)]
    cur.execute("select name,type,line,substr(text,1,160) from user_source where upper(text) like '%RRL_STOCK_WRITER_REGISTRY%' and name<>'X' order by 1,3")
    for r in cur.fetchall()[:12]: print(r)
    cur.execute("select trigger_name,table_name from user_triggers where table_name in('RRL_REMAINS','RRL_WMS_RECEIPT_UNIT','RRL_STOCK_LEG','RRL_SAP_RECEIPT_OUTBOX')"); print(cur.fetchall())
