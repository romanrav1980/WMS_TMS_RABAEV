exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.domain.mark_identity import normalize_unit_scan_codes
from app.modules.inventory.infrastructure.interwarehouse_shortage import read_shortage
from app.oracle_gateway import OracleGateway
import uuid
p=Path("tmp/context368_recovery.json");saved=json.loads(p.read_text(encoding="utf-8"))if p.exists()else {}
ctx=json.loads(Path("tmp/context368.json").read_text(encoding="utf-8"));gw=OracleGateway()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,WARE_ID,DELETED,USER_GROUP from RUSERS where ID like 'CAL264%'and DELETED=1");rows=q.fetchall();assert len(rows)==1
 actor,oldware,deleted,group=rows[0];q.execute("select count(*)from RIGHTS where USER_GROUP=:grp and RIGHT1='transport_dispatch_edit'",grp=group);old_right=q.fetchone()[0]
 def config(action):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:action();c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 def native(kind,op,source,metadata,who="admin",commit=True):
  req=dict(contract_version=2,operation_id=op,command_type=kind,actor=who,source=source,lines=[],units=[],metadata=metadata);out=q.var(oracledb.DB_TYPE_CLOB)
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
  evidence=dict(quantity="2",reason="Фактическая подтверждённая недостача двух единиц перевозчика",evidence_reference="DEV368:confirmedloss2")
  if "loss_operation_id"not in saved:
   req_op="IW368.LOSS.REPORT:"+ctx["tag"];report=native("INTERWARE_SHORTAGE_REPORT",req_op,dict(receipt_operation_id=ctx["receipt_operation"]),evidence,actor)
   loss_op="IW368.LOSS.CONFIRM:"+ctx["tag"];result=native("INTERWARE_SHORTAGE_CONFIRM",loss_op,dict(request_operation_id=req_op),evidence)
   saved.update(loss_operation_id=loss_op,loss_result=result);save()
  loss_op=saved["loss_operation_id"]
  q.execute("select PHYSICAL_UNIT_KEY,UNIT_ID from RRL_INTERWARE_SHORTAGE_UNIT b join RRL_WMS_RECEIPT_UNIT u using(PHYSICAL_UNIT_KEY)where b.FACT_OPERATION_ID=:loss_id order by u.UNIT_ID",loss_id=loss_op);lost=list(q);assert len(lost)==2;c.rollback()
  saved.setdefault("parts",[])
  for index,(physical_key,unit_id)in enumerate(lost):
   if len(saved["parts"])<=index:saved["parts"].append({});save()
   part=saved["parts"][index]
   metadata=dict(quantity="1",reason="Найдена одна конкретная маркированная единица из двух",evidence_reference="DEV368:found"+str(index+1),unit_keys=[physical_key])
   report_op="IW368.FOUND.REPORT:"+str(index)+":"+ctx["tag"]
   if "report"not in part:
    result=native("INTERWARE_RECOVERY_REPORT",report_op,dict(loss_operation_id=loss_op),metadata,actor)
    assert len(result["source_units"])==1 and result["quantity"]=="1",result
    part.update(report=result,report_operation_id=report_op);save()
    try:native("INTERWARE_RECOVERY_REPORT","IW368.OVERLAP:"+uuid.uuid4().hex,dict(loss_operation_id=loss_op),metadata,actor)
    except oracledb.DatabaseError as exc:assert exc.args[0].code==20886,exc
    else:raise AssertionError("overlap reported twice")
   approval_meta={k:v for k,v in metadata.items()if k!="unit_keys"};approval_op="IW368.FOUND.APPROVE:"+str(index)+":"+ctx["tag"]
   if "approval"not in part:
    part["approval"]=native("INTERWARE_RECOVERY_APPROVE",approval_op,dict(request_operation_id=report_op),approval_meta);part["approval_operation_id"]=approval_op;save()
   if "receipt"not in part:
    unit=next(u for u in ctx["units"]if u["unit_id"]==unit_id);lot="REC368:"+str(index)+":"+ctx["tag"]
    receipt_meta=dict(quantity="1",gross_weight_kg="2",receipt_pallet_identifier=lot,scan_source_pallet=ctx["lot"],scan_pallet=lot,scan_cell=ctx["receive_cell"],scan_article=ctx["barcode"],article=ctx["article"],base_uom="EA",
       discrepancy_reason="Фактически принята одна найденная маркированная единица",discrepancy_reference="DEV368:partial-found",unit_scans=normalize_unit_scan_codes(unit["codes"]))
    try:native("INTERWARE_SHORTAGE_RECOVER","IW368.BADQR:"+uuid.uuid4().hex,dict(approval_operation_id=approval_op),dict(receipt_meta,unit_scans=receipt_meta["unit_scans"][:-1]),commit=False)
    except oracledb.DatabaseError as exc:assert exc.args[0].code==20886,exc
    else:raise AssertionError("one profile missing accepted")
    rolled=native("INTERWARE_SHORTAGE_RECOVER","IW368.REC.ROLL:"+uuid.uuid4().hex,dict(approval_operation_id=approval_op),receipt_meta,commit=False)
    assert rolled["quantity"]=="1"and rolled["physical_unit_count"]==1; c.rollback()
    q.execute("select count(*)from RRL_PALLETS where UID_PALLET=:lot_id",lot_id=lot);assert q.fetchone()==(0,)
    op="IW368.REC:"+str(index)+":"+ctx["tag"];result=native("INTERWARE_SHORTAGE_RECOVER",op,dict(approval_operation_id=approval_op),receipt_meta)
    part.update(receipt=result,receipt_operation_id=op,receipt_metadata=receipt_meta,unit_id=unit_id,physical_unit_key=physical_key);save()
   assert native("INTERWARE_SHORTAGE_RECOVER",part["receipt_operation_id"],dict(approval_operation_id=approval_op),part["receipt_metadata"])==part["receipt"]
   view=read_shortage(gw,ctx["receipt_operation"],"admin",report_op)
   assert view["recovered_quantity"]==str(index+1)and view["net_unrecovered_short_quantity"]==str(1-index),view
   assert len(view["currently_missing_units"])==1-index and not view["current_unit_state_conflicts"]
   q.execute("select count(*)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id and STOCK_STATUS='ISSUED'",lot_id=ctx["lot"]);assert q.fetchone()==(1-index,);c.rollback()
  q.execute("select count(*),sum(BASE_QTY)from RRL_INTERWARE_RECOVERY_RECEIPT where LOSS_OPERATION_ID=:loss_id",loss_id=loss_op);assert q.fetchone()==(2,2)
  q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:lot_id",lot_id=ctx["lot"]);assert q.fetchone()==(6,)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
 finally:
  c.rollback()
  def restore():
   q.execute("update RUSERS set DELETED=:deleted,WARE_ID=:ware where ID=:actor",deleted=deleted,ware=oldware,actor=actor)
   if not old_right:q.execute("delete from RIGHTS where USER_GROUP=:grp and RIGHT1='transport_dispatch_edit'",grp=group)
  config(restore)
print("PASS368 actual lost2 -> two found1 independentapprovals/same old2keys4QR/overlapdenied/missingQRdenied/rollback/replay/firstnet1-nextnet0/6codes/protected20-20; CAL264 restoredretired")
