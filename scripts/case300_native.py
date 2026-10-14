exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.domain.mark_identity import normalize_unit_scan_codes
import uuid
for number in[291,292]:
 ctx=json.loads(Path("tmp/context"+str(number)+".json").read_text(encoding="utf-8"));approval=json.loads(Path("tmp/context299_"+str(number)+".json").read_text(encoding="utf-8"))
 cell="IR"+str(number)+ctx["tag"];uid="REC300:"+ctx["tag"];source=ctx["lot"]
 scans=[]
 if number==292:
  with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
   q=c.cursor();q.execute("select UNIT_ID from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id",lot_id=source);ids={r[0]for r in q}
  scans=[code for unit in ctx["units"]if unit["unit_id"]in ids for code in unit["codes"]];assert len(scans)==4
 body=dict(quantity="2",gross_weight_kg="10",receipt_pallet_identifier=uid,scan_source_pallet=source,scan_pallet=uid,scan_cell=cell,
           scan_article=ctx["barcode"],article=ctx["article"],base_uom="EA",discrepancy_reason="Фактически найден весь ранее отсутствовавший остаток",discrepancy_reference="DEV300:found-lost2")
 if scans:body["unit_scans"]=normalize_unit_scan_codes(scans)
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();out=q.var(oracledb.DB_TYPE_CLOB)
  req=dict(contract_version=2,operation_id="IW300.ROLL:"+uuid.uuid4().hex,command_type="INTERWARE_SHORTAGE_RECOVER",actor="admin",source=dict(approval_operation_id=approval["approval_operation_id"]),lines=[],units=[],metadata=body)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(req,ensure_ascii=False),"admin",out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   x=read_oracle_json(out.getvalue());assert x["quantity"]=="2"and x["physical_unit_count"]==(2 if number==292 else 0),x
   q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=uid);assert q.fetchone()==(2,0)
   c.rollback();q.execute("select count(*)from RRL_PALLETS where UID_PALLET=:lot_id",lot_id=uid);assert q.fetchone()==(0,)
   q.execute("select count(*)from RRL_INTERWARE_RECOVERY_RECEIPT where APPROVAL_OPERATION_ID=:approval_id",approval_id=approval["approval_operation_id"]);assert q.fetchone()==(0,)
   if number==292:
    q.execute("select count(*)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id and STOCK_STATUS='ISSUED'",lot_id=source);assert q.fetchone()==(2,)
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 Path("tmp/context300_"+str(number)+".json").write_text(json.dumps(dict(body=body,approval_operation_id=approval["approval_operation_id"],scans=scans),ensure_ascii=False,indent=2),encoding="utf-8")
print("PASS300 native ordinary+marked actualrestore2 under outerrollback removes newP2/pallet/recoveryfacts/units/outbox; originallostkeys stillISSUED afterrollback")
