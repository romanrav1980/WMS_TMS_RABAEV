import sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select CASE_PICK_TASK_ID,CASE_PICK_LINE_ID from RRL_CASE_PICK_LINE where ARTICUL='QW1916CB9F1A864'");task,line=q.fetchone()
 try:
  q.execute("set transaction read only");r=q.callfunc("RRL_ORDER_WEIGHT_READ.snapshot_json",oracledb.DB_TYPE_CLOB,[task,line,"admin"]);print(r.read()if hasattr(r,"read")else r)
 except oracledb.DatabaseError as e:print(e)
