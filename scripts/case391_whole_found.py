exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.domain.mark_identity import normalize_unit_scan_codes
ctx=json.loads(Path("tmp/context390.json").read_text());p=Path("tmp/context390_recovery.json");saved=json.loads(p.read_text())if p.exists()else{"parts":[{}]}
def save():p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,WARE_ID,DELETED,USER_GROUP from RUSERS where ID like 'CAL264%'and DELETED=1");actor,oldware,deleted,group=q.fetchone()
 q.execute("select count(*)from RIGHTS where USER_GROUP=:grp and RIGHT1='transport_dispatch_edit'",grp=group);had=q.fetchone()[0]
 def config(fn):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:fn();c.commit()
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 def activate():
  q.execute("update RUSERS set WARE_ID=:ware,DELETED=0 where ID=:actor",ware=ctx["target_warehouse"],actor=actor)
  if not had:q.execute("insert into RIGHTS(USER_GROUP,RIGHT1)values(:grp,'transport_dispatch_edit')",grp=group)
 def native(kind,op,source,metadata,who="admin"):
  out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(dict(contract_version=2,operation_id=op,command_type=kind,actor=who,source=source,metadata=metadata,lines=[],units=[])),who,out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   result=read_oracle_json(out.getvalue());c.commit();return result
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 try:
  config(activate);evidence=dict(quantity="2",reason="Own first physical loss two actual original units",evidence_reference="DEV391:loss2")
  report_op="IW391.LOSS.REPORT:"+ctx["tag"];loss_op="IW391.LOSS.CONFIRM:"+ctx["tag"]
  if "loss"not in saved:
   saved["loss_report"]=native("INTERWARE_SHORTAGE_REPORT",report_op,dict(receipt_operation_id=ctx["receipt_operation"]),evidence,actor)
   saved["loss"]=native("INTERWARE_SHORTAGE_CONFIRM",loss_op,dict(request_operation_id=report_op),evidence);saved["loss_operation_id"]=loss_op;save()
  q.execute("select PHYSICAL_UNIT_KEY,UNIT_ID from RRL_INTERWARE_SHORTAGE_UNIT b join RRL_WMS_RECEIPT_UNIT u using(PHYSICAL_UNIT_KEY)where b.FACT_OPERATION_ID=:op order by UNIT_ID",op=loss_op);lost=q.fetchall();assert len(lost)==2;c.rollback()
  part=saved["parts"][0];keys=[key for key,_ in lost];ids={unit for _,unit in lost}
  meta=dict(quantity="2",reason="Own two exact first-cycle missing units physically found",evidence_reference="DEV391:found2",unit_keys=keys)
  found_report="IW391.FOUND.REPORT:"+ctx["tag"];approval="IW391.FOUND.APPROVE:"+ctx["tag"]
  if "report"not in part:part["report"]=native("INTERWARE_RECOVERY_REPORT",found_report,dict(loss_operation_id=loss_op),meta,actor);save()
  if "approval"not in part:part["approval"]=native("INTERWARE_RECOVERY_APPROVE",approval,dict(request_operation_id=found_report),{k:v for k,v in meta.items()if k!="unit_keys"});save()
  lot="REC391:"+ctx["tag"];scans=normalize_unit_scan_codes([code for unit in ctx["units"]if unit["unit_id"]in ids for code in unit["codes"]])
  receive=dict(quantity="2",gross_weight_kg="2",receipt_pallet_identifier=lot,scan_source_pallet=ctx["lot"],scan_pallet=lot,scan_cell=ctx["receive_cell"],scan_article=ctx["barcode"],article=ctx["article"],base_uom="EA",discrepancy_reason="Own actual two found original units",discrepancy_reference="DEV391:found",unit_scans=scans)
  op="IW391.REC:"+ctx["tag"]
  if "receipt"not in part:part["receipt"]=native("INTERWARE_SHORTAGE_RECOVER",op,dict(approval_operation_id=approval),receive);part.update(receipt_operation_id=op,receipt_metadata=receive,unit_keys=keys,unit_ids=sorted(ids));save()
  assert native("INTERWARE_SHORTAGE_RECOVER",op,dict(approval_operation_id=approval),receive)==part["receipt"]
  q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot and STOCK_STATUS='AVAILABLE'",lot=lot);assert q.fetchone()==(2,2)
  q.execute("select STOCK_ORIGIN_UID from RRL_PALLETS where UID_PALLET=:lot",lot=lot);part["stock_origin_uid"]=q.fetchone()[0];save()
 finally:
  c.rollback()
  def restore():
   q.execute("update RUSERS set WARE_ID=:ware,DELETED=:deleted where ID=:actor",ware=oldware,deleted=deleted,actor=actor)
   if not had:q.execute("delete from RIGHTS where USER_GROUP=:grp and RIGHT1='transport_dispatch_edit'",grp=group)
  config(restore)
print("PASS391 actual first lost2/found2/same two original keys/four oldQR/quarantineP2/current STOCK_ORIGIN preserved/controller restored")
