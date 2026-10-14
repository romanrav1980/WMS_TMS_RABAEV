import sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=5000;q=c.cursor()
 q.execute("select NAME,LINE,POSITION,TEXT from USER_ERRORS where NAME in('RRL_STOCK_TARE_POLICY','RRL_STOCK_TARE_CMD','RRL_TARE_STORE_DEBT','RRL_TARE_POLICY_GUARD','RRL_TARE_DELIVERY_POLICY_GUARD') order by NAME,SEQUENCE")
 for row in q:print(row)
