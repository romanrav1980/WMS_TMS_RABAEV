exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
import uuid
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,WARE_ID,DELETED,USER_GROUP from RUSERS where ID like 'CAL264%'and DELETED=1");rows=q.fetchall();assert len(rows)==1
 actor,oldware,deleted,group=rows[0];rights=["transport_dispatch_edit","store_return_approve"];old={}
 for right in rights:q.execute("select count(*)from RIGHTS where USER_GROUP=:grp and RIGHT1=:r",grp=group,r=right);old[right]=q.fetchone()[0]
 def config(fn):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:fn();c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 def native(kind,op,source,metadata,who):
  request=dict(contract_version=2,operation_id=op,command_type=kind,actor=who,source=source,lines=[],units=[],metadata=metadata)
  out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(request,ensure_ascii=False),who,out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   return read_oracle_json(out.getvalue())
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 try:
  for number in[291,292]:
   ctx=json.loads(Path("tmp/context"+str(number)+".json").read_text());lost=json.loads(Path("tmp/context295_"+str(number)+".json").read_text())
   def activate():
    q.execute("update RUSERS set DELETED=0,WARE_ID=:ware where ID=:actor",ware=ctx["target_warehouse"],actor=actor)
    for right in rights:
     if not old[right]:
      q.execute("select count(*)from RIGHTS where USER_GROUP=:grp and RIGHT1=:r",grp=group,r=right)
      if not q.fetchone()[0]:q.execute("insert into RIGHTS(USER_GROUP,RIGHT1)values(:grp,:r)",grp=group,r=right)
   config(activate)
   metadata=dict(quantity="2",reason="Найден ранее отсутствовавший товар: требуется корректирующая приёмка",evidence_reference="DEV299:found-exact-lost2")
   loss_id=lost["confirmation_operation_id"]
   q.execute("select OPERATION_ID from RRL_INTERWARE_RECOVERY_REQUEST where LOSS_OPERATION_ID=:loss_id",loss_id=loss_id);existing=q.fetchone();c.rollback()
   if not existing:
    op="IW299.ROLLREQ:"+uuid.uuid4().hex
    result=native("INTERWARE_RECOVERY_REPORT",op,dict(loss_operation_id=loss_id),metadata,"admin");assert len(result["source_units"])==(2 if number==292 else 0)
    try:native("INTERWARE_RECOVERY_APPROVE","IW299.SELF:"+uuid.uuid4().hex,dict(request_operation_id=op),metadata,"admin")
    except oracledb.DatabaseError as e:assert e.args[0].code==20882,e
    else:raise AssertionError("self approved recovery")
    c.rollback();op="IW299.REPORT:"+ctx["tag"];native("INTERWARE_RECOVERY_REPORT",op,dict(loss_operation_id=loss_id),metadata,actor);c.commit()
   else:op=existing[0]
   approval="IW299.ROLLAPP:"+uuid.uuid4().hex
   result=native("INTERWARE_RECOVERY_APPROVE",approval,dict(request_operation_id=op),metadata,"admin");assert result["status"]=="RECOVERY_APPROVED_PENDING_PHYSICAL_RECEIPT",result
   c.rollback();q.execute("select count(*)from RRL_INTERWARE_RECOVERY_APPROVAL where OPERATION_ID=:op_id",op_id=approval);assert q.fetchone()==(0,);c.rollback()
   Path("tmp/context299_"+str(number)+".json").write_text(json.dumps(dict(request_operation_id=op,loss_operation_id=loss_id,metadata=metadata,reporter=actor),ensure_ascii=False,indent=2),encoding="utf-8")
 finally:
  c.rollback()
  def restore():
   q.execute("update RUSERS set DELETED=:deleted,WARE_ID=:ware where ID=:actor",deleted=deleted,ware=oldware,actor=actor)
   for right in rights:
    if not old[right]:q.execute("delete from RIGHTS where USER_GROUP=:grp and RIGHT1=:r",grp=group,r=right)
  config(restore)
print("PASS299 original291/292 recovery report exact2 units/currentloss book, independent approval rollback/selfapproval20882/no qty; reporter restoredretired")
