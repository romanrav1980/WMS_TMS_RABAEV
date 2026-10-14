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
 q=c.cursor();q.execute("select r.OPERATION_ID from RRL_STORE_RETURN_RECEIPT r join RRL_STORE_RETURN_APPROVAL a on a.OPERATION_ID=r.APPROVAL_OPERATION_ID where a.RECEIPT_OPERATION_ID='STORE.RECEIPT:bea258a7dd'");receipt=q.fetchone()[0]
 body={"contract_version":2,"operation_id":"RETURN.PUT.DEBUG:"+uuid4().hex,"command_type":"STORE_RETURN_PUTAWAY_PLAN","actor":"admin","source":{"receipt_operation_id":receipt},"lines":[],"units":[],"metadata":{}}
 inp,out=q.var(oracledb.DB_TYPE_CLOB),q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,json.dumps(body))
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None])
  if out.getvalue() is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  print("Rollback-only plan succeeded")
 except oracledb.DatabaseError as exc:print(str(exc))
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
