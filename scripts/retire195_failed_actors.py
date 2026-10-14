import sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID in('QA19565f9646801','QA1958f669a9bb4','QA195e0038f3fc5')and nvl(DELETED,0)=0");print("Retired own195 failed fixture actors:",q.rowcount);c.commit()
