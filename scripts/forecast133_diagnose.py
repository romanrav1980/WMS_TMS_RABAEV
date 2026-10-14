import sys
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'api/wms_api_server'))
import oracledb
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 cur=c.cursor();result=cur.var(oracledb.DB_TYPE_CLOB)
 try:
  cur.callproc('RRL_FORECAST_PROJECTOR.project_load',['CASE.SINGLE.LOAD:a6bcf2cbe3:1029','admin',result]);print(result.getvalue().read());c.rollback()
 except Exception as exc: print(str(exc))
