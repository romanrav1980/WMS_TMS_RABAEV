exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.infrastructure.interwarehouse_shortage import read_shortage
from app.oracle_gateway import OracleGateway
import uuid
ctx=json.loads(Path("tmp/context307.json").read_text(encoding="utf-8"));p=Path("tmp/context307_cancel.json");saved=json.loads(p.read_text(encoding="utf-8"))if p.exists()else {}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,WARE_ID,DELETED,USER_GROUP from RUSERS where ID like 'CAL264%'and DELETED=1");rows=q.fetchall();assert len(rows)==1
 actor,oldware,deleted,group=rows[0];q.execute("select count(*)from RIGHTS where USER_GROUP=:grp and RIGHT1='transport_dispatch_edit'",grp=group);old_right=q.fetchone()[0]
 def config(action):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:action();c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 def native(kind,op,source,meta,who="admin",commit=True):
  req=dict(contract_version=2,operation_id=op,command_type=kind,actor=who,source=source,lines=[],units=[],metadata=meta);out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(req),who,out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   result=read_oracle_json(out.getvalue())
   if commit:c.commit()
   return result
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 def save():p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
 def activate():
  q.execute("update RUSERS set DELETED=0,WARE_ID=:ware where ID=:actor",ware=ctx["target_warehouse"],actor=actor)
  if not old_right:q.execute("insert into RIGHTS(USER_GROUP,RIGHT1)values(:grp,'transport_dispatch_edit')",grp=group)
 try:
  config(activate)
  if "loss_operation_id"not in saved:
   meta=dict(quantity="2",reason="Подтверждена фактическая недостача двух маркированных единиц",evidence_reference="DEV307:loss2")
   report="IW307.LOSS.REPORT:"+ctx["tag"];native("INTERWARE_SHORTAGE_REPORT",report,dict(receipt_operation_id=ctx["receipt_operation"]),meta,actor)
   loss="IW307.LOSS.CONFIRM:"+ctx["tag"];saved["loss_result"]=native("INTERWARE_SHORTAGE_CONFIRM",loss,dict(request_operation_id=report),meta);saved["loss_operation_id"]=loss;save()
  q.execute("select PHYSICAL_UNIT_KEY from RRL_INTERWARE_SHORTAGE_UNIT where FACT_OPERATION_ID=:loss_id order by PHYSICAL_UNIT_KEY",loss_id=saved["loss_operation_id"]);keys=[r[0]for r in q];assert len(keys)==2;c.rollback()
  report_meta=dict(quantity="1",reason="Заявлена найденная единица, затем обнаружена ошибка наблюдения",evidence_reference="DEV307:incorrectfinding",unit_keys=[keys[0]])
  report_op="IW307.FOUND.REPORT:"+ctx["tag"]
  if "report"not in saved:saved["report"]=native("INTERWARE_RECOVERY_REPORT",report_op,dict(loss_operation_id=saved["loss_operation_id"]),report_meta,actor);saved["report_operation_id"]=report_op;save()
  approval_meta={k:v for k,v in report_meta.items()if k!="unit_keys"};approval_op="IW307.FOUND.APPROVE:"+ctx["tag"]
  if "approval"not in saved:saved["approval"]=native("INTERWARE_RECOVERY_APPROVE",approval_op,dict(request_operation_id=report_op),approval_meta);saved["approval_operation_id"]=approval_op;save()
  cancel_meta=dict(quantity="1",reason="Согласованная находка ошибочна: товар физически не поступил",evidence_reference="DEV307:cancelbeforephysical")
  if "cancel"not in saved:
   rolled=native("INTERWARE_RECOVERY_CANCEL","IW307.CANCEL.ROLL:"+uuid.uuid4().hex,dict(request_operation_id=report_op),cancel_meta,commit=False);assert rolled["stock_changed"]is False;c.rollback()
   q.execute("select count(*)from RRL_IW_RECOVERY_CANCEL where REQUEST_OPERATION_ID=:request_id",request_id=report_op);assert q.fetchone()==(0,)
   op="IW307.CANCEL:"+ctx["tag"];saved["cancel"]=native("INTERWARE_RECOVERY_CANCEL",op,dict(request_operation_id=report_op),cancel_meta);saved["cancel_operation_id"]=op;saved["cancel_metadata"]=cancel_meta;save()
  assert native("INTERWARE_RECOVERY_CANCEL",saved["cancel_operation_id"],dict(request_operation_id=report_op),saved["cancel_metadata"])==saved["cancel"]
  try:native("INTERWARE_RECOVERY_CANCEL",saved["cancel_operation_id"],dict(request_operation_id=report_op),dict(saved["cancel_metadata"],quantity="2"))
  except oracledb.DatabaseError as exc:assert 20800<=exc.args[0].code<=20999,exc
  else:raise AssertionError("changedcancelpayloadaccepted")
  view=read_shortage(OracleGateway(),ctx["receipt_operation"],"admin",report_op);assert view["status"]=="RECOVERY_REQUEST_CANCELLED"and view["unreported_recovery_quantity"]=="2"and view["net_unrecovered_short_quantity"]=="2",view
  try:native("INTERWARE_RECOVERY_APPROVE","IW307.APP.AFTERCANCEL:"+uuid.uuid4().hex,dict(request_operation_id=report_op),approval_meta)
  except oracledb.DatabaseError as exc:assert exc.args[0].code==20886 and "CANCELLED"in str(exc),exc
  else:raise AssertionError("cancelledapprovalaccepted")
  if "replacement"not in saved:
   op="IW307.FOUND.REPLACEMENT:"+ctx["tag"];saved["replacement"]=native("INTERWARE_RECOVERY_REPORT",op,dict(loss_operation_id=saved["loss_operation_id"]),report_meta,actor);saved["replacement_operation_id"]=op;save()
  view=read_shortage(OracleGateway(),ctx["receipt_operation"],"admin",saved["replacement_operation_id"])
  assert len(view["recovery_cases"])==2 and view["unreported_recovery_quantity"]=="1"and view["recovered_quantity"]=="0",view
  q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id and STOCK_STATUS='ISSUED'",lot_id=ctx["lot"]);assert q.fetchone()==(2,2)
  q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:lot_id",lot_id=ctx["lot"]);assert q.fetchone()==(6,)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
 finally:
  c.rollback()
  def restore():
   q.execute("update RUSERS set DELETED=:deleted,WARE_ID=:ware where ID=:actor",deleted=deleted,ware=oldware,actor=actor)
   if not old_right:q.execute("delete from RIGHTS where USER_GROUP=:grp and RIGHT1='transport_dispatch_edit'",grp=group)
  config(restore)
print("PASS307 actual approved prephysicalcancel/rollback/replay/collision/historyretained/quota2 restored/samekey replacement/currentcancelread/newapprovaldenied/no P-or-unit changes/CAL restored")
