from pathlib import Path
import json
source=Path("scripts/ni052_single_case_case.py").read_text(encoding="utf-8")
cut=source.index('  meta("insert into RRL_RECEIPT_SKU_RULE')
prefix=source[:cut]
prefix=prefix.replace('with oracledb.connect(user=cfg.oracle_user',"""context_path=Path("tmp/context955.json")
assert not context_path.exists(),"955 source already exists; use retained context for continuation, no source rebirth"
context={"tag":tag,"lot":lot,"article":"pending","stage":"NEW"}
def save_context():context_path.write_text(json.dumps(context,indent=2),encoding="utf-8")
save_context()
with oracledb.connect(user=cfg.oracle_user""",1)
needle=' revision=int(q.callfunc('
pos=prefix.index(needle)
prefix=prefix[:pos]+' context.update(ware=ware,article=article,src=src,dst=dst);save_context()\n'+prefix[pos:]
prefix=prefix.replace('   bind_case_shipment(OracleGateway(),int(ct),identifier,carrier,int(version),"admin");shipments[int(ct)]=identifier',
'   bind_case_shipment(OracleGateway(),int(ct),identifier,carrier,int(version),"admin");shipments[int(ct)]=identifier\n   context.update(cases=[list(x)for x in lines],shipments=shipments,wave=wave,orders=orders);save_context()')
addition="""  from app.modules.transport.infrastructure.st_deferral import StDeferral
  from app.modules.inventory.infrastructure.task_completion import complete_existing_task
  from app.schemas import WarehouseTaskStatusRequest
  from app.modules.platform.public import read_oracle_json
  wait="QW"+tag
  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_HEIGHT,LIMIT_WEIGHT)values(:c,:ware,0,0,0,0,0,0,0)",c=wait)
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=wait)
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.callproc("RRL_RECEIPT_SETTINGS_API.set_waiting_cell",[ware,wait,"admin"]);conn.commit()
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
  q.execute("select TRANSPORTTYPE from RRL_TRANSPORT_TYPE where TRANSPORTTYPE='15'");trtype=q.fetchone()[0]
  q.execute("select min(ID)from RRL_TR_VODITEL where ID>0");driver=q.fetchone()[0]
  vehicle=int(q.callfunc("RRL_TR_VEHICLE_ADD",oracledb.DB_TYPE_NUMBER,["QW"+tag,trtype,40,2,0,None]));conn.commit()
  source_trip=seq("RRL_TRANSPORT_TASK_SQ");target_trip=seq("RRL_TRANSPORT_TASK_SQ");dock="QD"+tag
  meta("insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED)values(:dock,:ware,0)",dock=dock)
  for trip,offset in((source_trip,1),(target_trip,2)):
   meta("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED)values(:id,:plate,:typ,'Спланирован',trunc(sysdate)+:d,:driver,:dock,0)",id=trip,plate="QW"+tag,typ=trtype,d=offset,driver=driver,dock=dock)
  ct,cl,carrier,qty,cell=lines[0];st=shipments[int(ct)]
  meta("update RRL_SBORKA_PALLETS set TRANSTASK_ID=:trip where PALLET_UID=:u",trip=source_trip,u=st)
  context.update(wait=wait,case=int(ct),carrier=carrier,st=st,source_trip=source_trip,target_trip=target_trip,stage="PREPARED");save_context()
  defer=StDeferral(OracleGateway());seen=defer.context(st,"admin");assert seen["physical_preparation"]["state"]=="PREPARED_CASE",seen
  body={"st_number":st,"target_trip_id":target_trip,"expected_version":seen["version"],"source_hash":seen["source_hash"],"reason":"Own prepared CASE waiting source","reference":"WAIT955:"+tag}
  decision="DEC955:"+tag;result=defer.defer(decision,body,"admin");assert defer.defer(decision,body,"admin")==result
  context.update(decision=decision,decision_body=body,decision_result=result,stage="DEFERRED");save_context()
  def planning():
   out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_ST_DEFER_WAIT_API.plan_waiting",["PLAN955:"+tag,decision,"admin",out]);return read_oracle_json(out.getvalue())
  trial=planning();assert len(trial["tasks"])==1;conn.rollback()
  q.execute("select count(*)from RRL_ST_DEFER_WAIT_RUN where OPERATION_ID=:op",op="PLAN955:"+tag);assert q.fetchone()==(0,)
  planned=planning();conn.commit();assert planning()==planned;conn.rollback()
  task=int(planned["tasks"][0]["task_id"]);context.update(task=task,plan_result=planned,stage="PLANNED");save_context()
  q.execute("select PICKED_AT,PICKED_BY,FACT_QTY,FACT_UOM,FACT_COMPOSITION_JSON,PICKED_CONTENT_VERSION from RRL_CUSTOMER_ORDER_FULFILLMENT where PICKED_CASE_TASK_ID=:id",id=int(ct))
  before=q.fetchone();before=list(before);before[4]=before[4].read()if hasattr(before[4],"read")else before[4]
  q.execute("select CURRENT_CELL,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=int(ct));origin,version=q.fetchone()
  command={"fact_qty":"1","scanned_pallet":carrier,"scanned_from_cell":origin,"scanned_to_cell":wait,"physical_task_id":task,"scan_container":carrier,"target_cell":wait,"expected_content_version":int(version)}
  context.update(move_body=command,move_operation="MOVE955:"+tag);save_context()
  # A wrong physical scan fails with no movement; execute through the public existing-task bridge.
  bad=dict(command,scanned_to_cell=src)
  try:post("CASE_CARRIER_MOVE",bad,{"case_task_id":int(ct)},"BAD955:"+tag);raise AssertionError("Wrong destination accepted")
  except oracledb.DatabaseError as exc:assert "CASE_CARRIER_DESTINATION_SCAN_REQUIRED"in str(exc),str(exc)
  req=WarehouseTaskStatusRequest(operation_id=context["move_operation"],updated_by="admin",fact_qty="1",scanned_pallet=carrier,scanned_from_cell=origin,scanned_to_cell=wait)
  moved=complete_existing_task(OracleGateway(),task,req,"admin");assert complete_existing_task(OracleGateway(),task,req,"admin")==moved
  context.update(move_result=moved,stage="DONE");save_context()
  q.execute("select STATUS,FACT_QTY,TO_CELL from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=task);assert q.fetchone()==("DONE",1,wait)
  q.execute("select SYNC_STATUS from RRL_WAREHOUSE_TASK_SYNC where TASK_ID=:id",id=task);assert q.fetchone()==("SYNCED",)
  q.execute("select CURRENT_CELL,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=int(ct));assert q.fetchone()==(wait,int(version)+1)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE),min(r.CELL),max(r.CELL)from RRL_REMAINS r join RRL_CASE_CARRIER_LOT l on l.LOT_UID=r.UID_POLETA where l.CASE_PICK_TASK_ID=:id and r.REMAIN>0",id=int(ct));assert q.fetchone()==(12,12,wait,wait)
  q.execute("select PICKED_AT,PICKED_BY,FACT_QTY,FACT_UOM,FACT_COMPOSITION_JSON,PICKED_CONTENT_VERSION from RRL_CUSTOMER_ORDER_FULFILLMENT where PICKED_CASE_TASK_ID=:id",id=int(ct));after=list(q.fetchone());after[4]=after[4].read()if hasattr(after[4],"read")else after[4]
  assert after[:5]==before[:5]and after[5]==int(version)+1
  q.execute("select count(*)from RRL_EVENT_OUTBOX where IDEMPOTENCY_KEY='STOCK:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(:op,'AL32UTF8'),sys.dbms_crypto.hash_sh256))",op=context["move_operation"]);assert q.fetchone()[0]>=1
  context["evidence"]={"case_quantity":"12","case_hard":"12","task_place_quantity":"1","task_status":"DONE","sync":"SYNCED","pick_facts_preserved":True,"bridge_exact_replay":True};save_context()
  print("PASS955 preparedCASE physical12/H12 -> existing ST deferral -> plan rollback/replay -> native wrong scan rollback -> existing bridge DONE1CASE/SYNCED/reserve12/exact replay/originalfacts",flush=True)
"""
cleanup=source[source.index("\n finally:\n")+1:]
# Cancel only this fixture's waiting task before own carrier cleanup if a later assertion fails.
cleanup=cleanup.replace(' finally:\n',' finally:\n  if "task"in context:\n   meta("update RRL_WAREHOUSE_TASK set STATUS=\'CANCELLED\'where TASK_ID=:id and STATUS not in(\'DONE\',\'CANCELLED\')",id=context["task"])\n',1)
cleanup+="\n  context['cleanup']='OWN_P_H_ZERO';save_context()\n"
files={"scripts/case955_case_wait.py":prefix+addition+cleanup}
print(json.dumps(files,ensure_ascii=True))
