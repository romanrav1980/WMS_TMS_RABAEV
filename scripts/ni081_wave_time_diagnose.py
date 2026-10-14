import sys,json
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.platform.public import read_oracle_json
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();out=q.var(oracledb.DB_TYPE_CLOB)
 q.callproc("RRL_WAVE_TIME_API.context",[395,"admin",out]);ctx=read_oracle_json(out.getvalue())
 body={"wave_id":395,"expected_version":ctx["version"],"source_token":ctx["source_token"],"start_at":"2026-10-10T14:52:16.000000+00:00","finish_at":"2026-10-10T16:52:16.000000+00:00","time_zone":"Asia/Tbilisi","reason":"Own140 explicit shift approval with current staffing"}
 try:
  q.callproc("RRL_WAVE_TIME_API.approve",["WAVE140.APPROVE:d9a5c53b54","admin",json.dumps(body,sort_keys=True,separators=(",",":")),out])
  print("Native approval succeeds; diagnostic transaction rolled back",flush=True)
 except oracledb.DatabaseError as exc:print(str(exc.args[0])[:1800],flush=True)
 finally:c.rollback()
