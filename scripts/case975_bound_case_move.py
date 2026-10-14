exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.inventory.application.case_carrier_move import CaseCarrierMove
from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
from app.modules.platform.public import read_oracle_json
ctx=json.loads(Path("tmp/context955.json").read_text(encoding="utf-8"));path=Path("tmp/context975.json")
assert not path.exists(),"975 source already progressed; retained phase continuation only"
record={"case":ctx["case"],"st":ctx["st"],"tag":ctx["tag"],"stage":"NEW"}
def save():path.write_text(json.dumps(record,indent=2,default=str),encoding="utf-8")
save();g=OracleGateway();mover=CaseCarrierMove(StockPosting())
before_qc=OutgoingQuality(g).status(ctx["st"],"admin");record["before_qc"]=before_qc;save()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();target="QX"+ctx["tag"]
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM)values(:c,:w,0,0,0,0,1)",c=target,w=ctx["ware"])
  q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=target);c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 q.execute("select CONTENT_VERSION,CURRENT_CELL from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=ctx["case"]);version,origin=q.fetchone()
 q.execute("select FULFILLMENT_ID,PICKED_CONTENT_VERSION,PICKED_AT,PICKED_BY,FACT_QTY,FACT_UOM,FACT_COMPOSITION_JSON from RRL_CUSTOMER_ORDER_FULFILLMENT where PICKED_CASE_TASK_ID=:id",id=ctx["case"])
 before=list(q.fetchone());before[-1]=before[-1].read()if hasattr(before[-1],"read")else before[-1]
 assert before[1]==version==2
 record.update(target=target,origin=origin,before_version=version,before_fulfillment=before,stage="PREPARED");save()
 metadata={"scan_container":ctx["carrier"],"target_cell":target,"scanned_to_cell":target,"expected_content_version":int(version)}
 request={"contract_version":2,"operation_id":"TRIAL975:"+ctx["tag"],"command_type":"CASE_CARRIER_MOVE","actor":"admin","source":{"case_task_id":ctx["case"]},"lines":[],"units":[],"metadata":metadata}
 out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(request),"admin",out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  assert read_oracle_json(out.getvalue())["status"]=="MOVED"
  q.execute("select PICKED_CONTENT_VERSION from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=:id",id=before[0]);assert q.fetchone()==(3,)
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select CONTENT_VERSION,CURRENT_CELL from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=ctx["case"]);assert q.fetchone()==(2,origin)
 q.execute("select PICKED_CONTENT_VERSION from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=:id",id=before[0]);assert q.fetchone()==(2,)
 result=mover.execute("MOVE975:"+ctx["tag"],"admin",ctx["case"],ctx["carrier"],target,2)
 assert mover.execute("MOVE975:"+ctx["tag"],"admin",ctx["case"],ctx["carrier"],target,2)==result
 record.update(result=result,stage="MOVED");save()
 q.execute("select FULFILLMENT_ID,PICKED_CONTENT_VERSION,PICKED_AT,PICKED_BY,FACT_QTY,FACT_UOM,FACT_COMPOSITION_JSON from RRL_CUSTOMER_ORDER_FULFILLMENT where PICKED_CASE_TASK_ID=:id",id=ctx["case"])
 after=list(q.fetchone());after[-1]=after[-1].read()if hasattr(after[-1],"read")else after[-1]
 assert after[0]==before[0]and after[1]==3 and after[2:]==before[2:],(before,after)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE),min(r.CELL),max(r.CELL)from RRL_REMAINS r join RRL_CASE_CARRIER_LOT l on l.LOT_UID=r.UID_POLETA where l.CASE_PICK_TASK_ID=:id and r.REMAIN>0",id=ctx["case"]);assert q.fetchone()==(12,12,target,target)
 record.update(after_fulfillment=after,positive_rollback=True,exact_replay=True,pick_facts_preserved=True,goods="12",hard="12");save()
after_qc=OutgoingQuality(g).status(ctx["st"],"admin");assert after_qc["composition_signature"]!=before_qc["composition_signature"],(before_qc,after_qc)
record["after_qc"]=after_qc;save()
print("PASS975 retainedCASE12/H12 waiting -> existing generic control move; CT3=FF3/sameTX rollback/cache/original pick facts/current QC signature changed")
