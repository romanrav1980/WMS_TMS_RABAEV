"""165 native current CASE actor before replay; rollback-only identity/right changes."""
import sys,json
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();actor="Q1341a19738325";operation="NATIVE.CASE:a6bcf2cbe3:1030"
read=lambda value:value.read()if hasattr(value,"read")else value
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select to_clob(CANONICAL_REQUEST),to_clob(RESULT_JSON)from RRL_STOCK_OPERATION where OPERATION_ID=:id",id=operation)
 request,saved=map(read,q.fetchone());body=json.loads(request);task=body["source"]["case_task_id"]
 q.execute("select WARE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=task);foreignware=q.fetchone()[0]
 q.execute("select USER_GROUP,WARE_ID,DELETED from RUSERS where ID=:id",id=actor);group,ware,deleted=q.fetchone()
 assert foreignware!=ware
 q.execute("select count(*),sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:id",id=operation);events=q.fetchone()
 q.callproc("RRL_CASE_TASK_ACCESS.assert_scope",[1031,actor,"case_pick_execute",None])
 def forbidden(call):
  try:call();raise AssertionError("Foreign/inactive/revoked CASE actor admitted")
  except oracledb.DatabaseError as exc:assert exc.args[0].code==20882,exc
 forbidden(lambda:q.callproc("RRL_CASE_TASK_ACCESS.assert_scope",[task,actor,"case_pick_execute",None]))
 try:
  q.execute("insert into RIGHTS(USER_GROUP,RIGHT1)values(:grp,'case_pick_manage')",grp=group)
  forbidden(lambda:q.callfunc("RRL_CASE_RESOURCE_POLICY.context_json",oracledb.DB_TYPE_CLOB,[task,"REPORT",actor,None,None,None]))
  ctx=read(q.callfunc("RRL_CASE_RESOURCE_POLICY.context_json",oracledb.DB_TYPE_CLOB,[1031,"REPORT",actor,None,None,None]))
  assert json.loads(ctx)["assigned_to"]==actor
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor)
  forbidden(lambda:q.callproc("RRL_CASE_TASK_ACCESS.assert_scope",[1031,actor,"case_pick_execute",None]))
 finally:c.rollback()
 wire=q.var(oracledb.DB_TYPE_CLOB);wire.setvalue(0,request);result=q.var(oracledb.DB_TYPE_CLOB)
 def prepare():
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[wire,"admin",result,None])
  return read(result.getvalue())
 assert prepare()==saved
 q.callproc("RRL_STOCK_POSTING_API.reset_connection");c.rollback()
 try:
  # Other sessions still see original admin; no committed account change.
  q.execute("update RUSERS set USER_GROUP=:grp,WARE_ID=:ware where ID='admin'",grp=group,ware=ware)
  forbidden(prepare)
 finally:
  q.callproc("RRL_STOCK_POSTING_API.reset_connection");c.rollback()
 assert prepare()==saved
 q.callproc("RRL_STOCK_POSTING_API.reset_connection");c.rollback()
 q.execute("select count(*),sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:id",id=operation);assert q.fetchone()==events
 q.execute("select WARE_ID,DELETED from RUSERS where ID=:id",id=actor);assert q.fetchone()==(ware,deleted)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS165 original1031 own/foreignCASE denied; managerwithoutsession ownREPORT works/foreign denied; inactive denied; original1030 exact native replay blocked by currentforeignWARE then restored exact/events unchanged/P20H20; all metadata rollback")
