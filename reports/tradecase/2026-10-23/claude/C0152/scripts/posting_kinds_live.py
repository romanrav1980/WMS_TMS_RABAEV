"""C-0152: READ ONLY list of native posting command kinds and quality/inventory objects (no writes)."""
import re, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
with OracleGateway().transaction("C-0152 posting kinds READ ONLY") as cur:
    cur.execute("set transaction read only")
    cur.execute("select text from user_source where name='RRL_STOCK_POSTING_API' and type='PACKAGE BODY' order by line")
    body = "".join(r[0] for r in cur.fetchall())
    print("kinds", sorted(set(re.findall(r"'([A-Z][A-Z_]{4,})'", " ".join(re.findall(r"g_kind\s*(?:=|in)\s*\(?[^)]*\)?", body))))))
    cur.execute("""select object_name,object_type from user_objects where object_type in('TABLE','PACKAGE') and regexp_like(object_name,
      'QUAL|QUARANT|DEFECT|WRITE|INVENT|COUNT|DISCREP|SHORT|DAMAGE|LOSS') order by 2,1""")
    for n, t in cur.fetchall(): print(t, n)
    cur.execute("select STOCK_STATUS,count(*) from RRL_WMS_RECEIPT_UNIT group by STOCK_STATUS order by 2 desc")
    print("unit statuses", cur.fetchall())
