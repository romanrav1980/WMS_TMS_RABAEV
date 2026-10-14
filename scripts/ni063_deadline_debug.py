import sys,json
from pathlib import Path
from uuid import uuid4
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=10000;q=c.cursor()
 q.execute("select o.OPERATION_ID,o.VEHICLE_NUMBER from RRL_TARE_OFFER o where o.OPERATION_ID like 'TARE.DEAD.OFFER:%:STORE' and not exists(select 1 from RRL_TARE_ACCEPT a where a.OFFER_OPERATION_ID=o.OPERATION_ID) order by OFFERED_AT desc fetch first 1 row only")
 offer,plate=q.fetchone()
 # GLOBAL_ADMIN is an allowed store receiver, never a substitute driver.
 body={"contract_version":2,"operation_id":"TARE.DEAD.DEBUG:"+uuid4().hex[:10],"command_type":"TARE_ACCEPT","actor":"admin","source":{"offer_operation_id":offer},"lines":[],"units":[],"metadata":{"accepted_quantity":"2","scan_vehicle":plate}}
 inp,out=q.var(oracledb.DB_TYPE_CLOB),q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,json.dumps(body))
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None])
  if out.getvalue() is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  print("Rollback-only accepted")
 except oracledb.DatabaseError as exc:print(str(exc))
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
