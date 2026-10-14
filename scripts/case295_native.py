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
  request={"contract_version":2,"operation_id":op,"command_type":kind,"actor":who,"source":source,"lines":[],"units":[],"metadata":metadata}
  out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(request,ensure_ascii=False),who,out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   return read_oracle_json(out.getvalue())
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 try:
  for number in[291,292]:
   ctx=json.loads(Path("tmp/context"+str(number)+".json").read_text(encoding="utf-8"))
   def activate():
    q.execute("update RUSERS set DELETED=0,WARE_ID=:ware where ID=:actor",ware=ctx["target_warehouse"],actor=actor)
    for right in rights:
     if not old[right]:
      q.execute("select count(*)from RIGHTS where USER_GROUP=:grp and RIGHT1=:r",grp=group,r=right)
      if not q.fetchone()[0]:q.execute("insert into RIGHTS(USER_GROUP,RIGHT1)values(:grp,:r)",grp=group,r=right)
   config(activate)
   metadata=dict(quantity="2",reason="Подтверждение фактической недостачи перевозчиком",evidence_reference="DEV295:carrier-shortage")
   q.execute("select OPERATION_ID from RRL_INTERWARE_SHORTAGE_REQUEST where RECEIPT_OPERATION_ID=:rec",rec=ctx["receipt_operation"]);existing=q.fetchone();c.rollback()
   if not existing:
    op="IW295.ROLLREQ:"+uuid.uuid4().hex
    result=native("INTERWARE_SHORTAGE_REPORT",op,{"receipt_operation_id":ctx["receipt_operation"]},metadata,"admin");assert result["status"]=="PENDING_INDEPENDENT_CONFIRMATION"
    try:native("INTERWARE_SHORTAGE_CONFIRM","IW295.SELF:"+uuid.uuid4().hex,{"request_operation_id":op},metadata,"admin")
    except oracledb.DatabaseError as e:assert e.args[0].code==20882,e
    else:raise AssertionError("self-approved shortage")
    c.rollback();q.execute("select count(*)from RRL_INTERWARE_SHORTAGE_REQUEST where OPERATION_ID=:op_id",op_id=op);assert q.fetchone()==(0,);c.rollback()
    op="IW295.REPORT:"+ctx["tag"]
    result=native("INTERWARE_SHORTAGE_REPORT",op,{"receipt_operation_id":ctx["receipt_operation"]},metadata,actor);c.commit()
   else:op=existing[0]
   fact="IW295.ROLLFACT:"+uuid.uuid4().hex
   result=native("INTERWARE_SHORTAGE_CONFIRM",fact,{"request_operation_id":op},metadata,"admin")
   assert result["status"]=="CONFIRMED_CARRIER_SHORTAGE"and len(result["missing_units"])==(2 if number==292 else 0),result
   q.execute("select count(*)from RRL_INTERWARE_SHORTAGE_UNIT where FACT_OPERATION_ID=:op_id",op_id=fact);assert q.fetchone()==(2 if number==292 else 0,)
   c.rollback();q.execute("select count(*)from RRL_INTERWARE_SHORTAGE_FACT where OPERATION_ID=:op_id",op_id=fact);assert q.fetchone()==(0,);c.rollback()
   Path("tmp/context295_"+str(number)+".json").write_text(json.dumps(dict(request_operation_id=op,receipt_operation_id=ctx["receipt_operation"],metadata=metadata,reporter=actor),ensure_ascii=False,indent=2),encoding="utf-8")
 finally:
  c.rollback()
  def restore():
   q.execute("update RUSERS set DELETED=:deleted,WARE_ID=:ware where ID=:actor",deleted=deleted,ware=oldware,actor=actor)
   for right in rights:
    if not old[right]:q.execute("delete from RIGHTS where USER_GROUP=:grp and RIGHT1=:r",grp=group,r=right)
  config(restore)
print("PASS295 native ordinary+marked report rollback, actual distinct reporter, confirm outerrollback/selfapproval20882/no qty writes; reporter restoredretired")
