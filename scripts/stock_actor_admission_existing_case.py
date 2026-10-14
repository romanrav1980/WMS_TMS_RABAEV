"""152 current native actor admission, rollback-only admin deactivation/original receipt replay."""
import sys,json
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.platform.public import read_oracle_json
s=get_settings();operation="REUSE.SAP.RECEIVE:cdbf4c0962"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select to_clob(CANONICAL_REQUEST),RESULT_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=operation)
 raw,expected=q.fetchone();raw=raw.read()if hasattr(raw,"read")else raw
 assert isinstance(raw,str),type(raw);expected=read_oracle_json(expected)
 q.execute("select count(*)from RRL_EVENTS");before=q.fetchone()
 def prepare(body,actor):
  bind=q.var(oracledb.DB_TYPE_CLOB);bind.setvalue(0,body);result=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[bind,actor,result,None])
   return result.getvalue()
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 try:
  q.execute("update RUSERS set DELETED=1 where ID='admin'")
  try:prepare(raw,"admin")
  except oracledb.DatabaseError as exc:assert exc.args[0].code==20882 and "STOCK_CURRENT_ACTOR_REQUIRED"in exc.args[0].message,exc
  else:raise AssertionError("Deactivated actor replay admitted")
 finally:c.rollback()
 ghost=json.loads(raw);ghost["actor"]="NO_SUCH_STOCK_ACTOR_152"
 try:prepare(json.dumps(ghost,separators=(",",":")),"NO_SUCH_STOCK_ACTOR_152")
 except oracledb.DatabaseError as exc:assert exc.args[0].code==20882,exc
 else:raise AssertionError("Unknown actor admitted")
 c.rollback()
 saved=read_oracle_json(prepare(raw,"admin"));assert saved==expected
 c.rollback()
 q.execute("select count(*)from RRL_EVENTS");assert q.fetchone()==before
 q.execute("select DELETED from RUSERS where ID='admin'");assert q.fetchone()==(0,)
 print("PASS152 native exact original SAP replay denied for rollback-only deactivated admin; unknown actor denied; restored current admin same saved result/events unchanged/no persistent user edit",flush=True)
