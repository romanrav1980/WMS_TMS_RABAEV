"""C-0150: READ ONLY RUSERS column names and RRL_ACCESS_API.alive/is_admin source (no values, no writes)."""
import sys, re
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
with OracleGateway().transaction("C-0150 RUSERS shape READ ONLY") as cur:
    cur.execute("set transaction read only")
    cur.execute("select column_name from user_tab_columns where table_name='RUSERS' order by column_id")
    print("RUSERS", [c[0] for c in cur.fetchall() if not re.search("PASS|PWD|HASH|SALT", c[0])])
    cur.execute("select text from user_source where name='RRL_ACCESS_API' and type='PACKAGE BODY' and line between 3 and 6 order by line")
    print("".join(r[0] for r in cur.fetchall()))
    cur.execute("select line,text from user_source where name='RRL_HAS_WRIGHT' order by line")
    print("".join(r[1] for r in cur.fetchall())[:900])
