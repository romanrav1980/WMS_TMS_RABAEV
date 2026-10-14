"""169 saved decision replay checks current warehouse before immutable receipt."""
import sys,json
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select to_clob(CANONICAL_REQUEST) from RRL_STOCK_OPERATION where OPERATION_ID='WAVE.DEFER169:402.ROLLBACK'");raw=q.fetchone()[0];saved=raw.read()if hasattr(raw,"read")else raw
 payload=q.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,saved);result=q.var(oracledb.DB_TYPE_CLOB)
 q.callproc("RRL_STOCK_POSTING_API.prepare_command",[payload,"admin",result,None]);original=result.getvalue();original=original.read()if hasattr(original,"read")else original;q.callproc("RRL_STOCK_POSTING_API.reset_connection");c.rollback()
 q.execute("select USER_GROUP from RUSERS where ID='Q1341a19738325'");group=q.fetchone()[0]
 try:
  for right in('pick_wave_launch','pick_wave_cancel'):
   q.execute("insert into RIGHTS(USER_GROUP,RIGHT1)select :p_grp,:p_right from dual where not exists(select 1 from RIGHTS where USER_GROUP=:p_grp and RIGHT1=:p_right)",p_grp=group,p_right=right)
  q.execute("update RUSERS set USER_GROUP=:p_grp,WARE_ID=6667491 where ID='admin'",p_grp=group)
  try:q.callproc("RRL_STOCK_POSTING_API.prepare_command",[payload,"admin",result,None]);raise AssertionError("Foreign replay admitted")
  except oracledb.DatabaseError as exc:assert exc.args[0].code==20882 and "WAVE_CURRENT_WARE_FORBIDDEN"in str(exc.args[0])
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.callproc("RRL_STOCK_POSTING_API.prepare_command",[payload,"admin",result,None]);restored=result.getvalue();restored=restored.read()if hasattr(restored,"read")else restored;assert restored==original;c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
print("PASS169 current foreignWARE20882 before immutable replay, rollback restores exact saved admin receipt; no new wave/order/stock facts")
