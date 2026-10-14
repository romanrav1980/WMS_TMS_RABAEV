from pathlib import Path
import json
source=Path("scripts/ni052_single_case_case.py").read_text(encoding="utf-8")
prefix=source[:source.index('  meta("insert into RRL_RECEIPT_SKU_RULE')]
prefix=prefix.replace('qc_actor="admin";cfg=get_settings();tag=uuid4().hex[:10];','qc_actor="admin";cfg=get_settings();tag=uuid4().hex[:10];',1)
needle='with oracledb.connect(user=cfg.oracle_user'
prefix=prefix.replace(needle,'path=Path("tmp/context987.json");assert not path.exists(),"987 already exists; retained phase only"\nrecord={"tag":tag,"stage":"NEW"}\ndef save():path.write_text(json.dumps(record,indent=2,default=str),encoding="utf-8")\nsave()\n'+needle,1)
prefix=prefix.replace('  released=post("WAVE_PICK_RELEASE",{},{"wave_id":wave})',"""  from app.services.case_pick_service import CasePickService
  from app.modules.inventory.infrastructure.replenishment_continuation import ReplenishmentContinuation
  from app.modules.resources.public import sync_existing_wave_tasks
  ReplenishmentContinuation(OracleGateway(),sync_existing_wave_tasks).reconcile(ware,"admin")
  CasePickService(OracleGateway()).ensure_wave_case_pick_tasks(wave,"admin")
  record.update(ware=ware,article=article,wave=wave,revision=revision,orders=orders,lot=lot,dst=dst);save()
  released=post("WAVE_PICK_RELEASE",{},{"wave_id":wave})""")
needle='  cases=CasePickService()\n';assert prefix.count(needle)==1
prefix=prefix.replace(needle,needle+"""  q.execute("select PALLET_TYPE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=lines[0][0]);tare_type=int(q.fetchone()[0])
  post("TARE_COUNT",{"owner_ware_id":ware,"pallet_type_id":tare_type,"condition":"GOOD","observed_quantity":"2","expected_version":0,"reason":"Own software multiCASE opening tare observation","decision_reference":"MULTI987:"+tag},{},"TARE987.COUNT:"+tag)
  for caseid,*unused in lines:
   post("TARE_BOOK",{"pallet_type_id":None},{"place_kind":"CASE","place_id":str(caseid)},"TARE987.BOOK:"+tag+":"+str(caseid))
""")
prefix=prefix.replace("WARE_ID,CONDITION,ADDR) values(:sid,:u,:u,:ware,0,'Own existing CASE QC ST')","WARE_ID,CONDITION,ADDR) values(:sid,:u,:st,:ware,0,'Own existing CASE QC ST')")
prefix=prefix.replace("sid=sid,u=identifier)\n","sid=sid,u=identifier,st='MULTI987:'+tag)\n",1)
prefix=prefix.replace('shipments[int(ct)]=identifier','shipments[int(ct)]=identifier\n   record.update(cases=[list(x)for x in lines],shipments=shipments,stage="BOUND");save()')
addition="""  from app.modules.transport.infrastructure.st_deferral import StDeferral
  from app.modules.inventory.application.case_carrier_move import CaseCarrierMove
  from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
  from app.modules.inventory.infrastructure.task_completion import complete_existing_task
  from app.modules.platform.public import read_oracle_json
  from app.schemas import WarehouseTaskStatusRequest
  wait="QW"+tag;control="QX"+tag;st="MULTI987:"+tag
  for cell,system in((wait,0),(control,1)):
   meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_HEIGHT,LIMIT_WEIGHT)values(:c,:ware,0,0,0,0,:sys,0,0)",c=cell,sys=system)
   meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell)
  meta("update RRL_RECEIPT_WARE_SETTINGS set DEFER_WAIT_CELL=:c where WARE_ID=:ware",c=wait)
  mover=CaseCarrierMove(StockPosting())
  for ct,cl,carrier,qty,cell in lines:
   moved=mover.execute("PRE987:"+tag+":"+str(ct),"admin",int(ct),carrier,control,1);assert moved["content_version"]==2
  q.execute("select TRANSPORTTYPE from RRL_TRANSPORT_TYPE where TRANSPORTTYPE='15'");trtype=q.fetchone()[0]
  q.execute("select min(ID)from RRL_TR_VODITEL where ID>0");driver=q.fetchone()[0]
  vehicle=int(q.callfunc("RRL_TR_VEHICLE_ADD",oracledb.DB_TYPE_NUMBER,["QM"+tag,trtype,40,2,0,None]));conn.commit()
  source_trip=seq("RRL_TRANSPORT_TASK_SQ");target_trip=seq("RRL_TRANSPORT_TASK_SQ");dock="QD"+tag
  meta("insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED)values(:dock,:ware,0)",dock=dock)
  for trip,offset in((source_trip,1),(target_trip,2)):
   meta("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED)values(:id,:plate,:typ,'Спланирован',trunc(sysdate)+:d,:driver,:dock,0)",id=trip,plate="QM"+tag,typ=trtype,d=offset,driver=driver,dock=dock)
  meta("update RRL_SBORKA_PALLETS set TRANSTASK_ID=:trip where ST_NUMBER=:st",trip=source_trip,st=st)
  record.update(st=st,wait=wait,control=control,source_trip=source_trip,target_trip=target_trip,stage="PREPARED");save()
  defer=StDeferral(OracleGateway());seen=defer.context(st,"admin");prep=seen["physical_preparation"]
  assert prep["state"]=="PREPARED_CASES"and prep["case_count"]==2 and prep["lot_count"]==2,prep
  decision="DEC987:"+tag;body={"st_number":st,"target_trip_id":target_trip,"expected_version":seen["version"],"source_hash":seen["source_hash"],"reason":"Two fully prepared CASE places on one existing ST","reference":"MULTI987:"+tag}
  result=defer.defer(decision,body,"admin");assert defer.defer(decision,body,"admin")==result
  record.update(decision=decision,decision_body=body,decision_result=result,stage="DEFERRED");save()
  def plan():
   out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_ST_DEFER_WAIT_API.plan_waiting",["PLAN987:"+tag,decision,"admin",out]);return read_oracle_json(out.getvalue())
  trial=plan();assert len(trial["tasks"])==2;conn.rollback()
  q.execute("select count(*)from RRL_ST_DEFER_WAIT_RUN where OPERATION_ID=:op",op="PLAN987:"+tag);assert q.fetchone()==(0,)
  planned=plan();conn.commit();assert plan()==planned;conn.rollback()
  record.update(plan=planned,stage="PLANNED");save()
  results=[]
  for i,item in enumerate(planned["tasks"]):
   task=int(item["task_id"]);caseid=int(item["case_pick_task_id"]);carrier=item["pallet_identifier"]
   request=WarehouseTaskStatusRequest(operation_id="MOVE987:"+tag+":"+str(caseid),fact_qty="1",updated_by="admin",scanned_pallet=carrier,scanned_from_cell=control,scanned_to_cell=wait)
   moved=complete_existing_task(OracleGateway(),task,request,"admin");assert complete_existing_task(OracleGateway(),task,request,"admin")==moved
   results.append({"task":task,"case":caseid,"request":request.model_dump(mode="json"),"result":moved});record.update(moves=results,stage="PARTIAL"if i==0 else"DONE");save()
   # The first completion must not invalidate the other frozen member.
   q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=task);assert q.fetchone()==("DONE",)
  for caseid,*unused in lines:
   q.execute("select c.CONTENT_VERSION,f.PICKED_CONTENT_VERSION,c.CURRENT_CELL from RRL_CASE_PICK_TASK c join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.PICKED_CASE_TASK_ID=c.CASE_PICK_TASK_ID where c.CASE_PICK_TASK_ID=:id",id=caseid);assert q.fetchone()==(3,3,wait)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE),min(r.CELL),max(r.CELL)from RRL_REMAINS r join RRL_CASE_CARRIER_LOT l on l.LOT_UID=r.UID_POLETA join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID where ct.PICK_WAVE_ID=:w and r.REMAIN>0",w=wave);assert q.fetchone()==(20,20,wait,wait)
  q.execute("select sum(BASE_QTY),count(*)from RRL_WAREHOUSE_TASK_STOCK_MOVE where OPERATION_ID in(:a,:b)",a=results[0]["request"]["operation_id"],b=results[1]["request"]["operation_id"]);assert q.fetchone()==(20,2)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
  record["evidence"]={"single_st":True,"cases":2,"task_places":"1+1","goods_by_case":["12","8"],"physical_total":"20","hard_total":"20","case_ff_versions":"3/3 each","sibling_after_first_completion":True,"plan_rollback":True,"exact_replays":True,"protected_ware_unchanged":True};save()
  print("PASS987 one original ST/two actual preparedCASE12+8 -> plan rollback/replay -> firstDONE does not invalidate sibling -> bothDONE1CASE/currentFF3/CT3/P20H20/journals12+8/protectedWARE",flush=True)
 except BaseException as exc:
  record["error"]=str(exc);save();raise
"""
print(json.dumps({"scripts/case987_multi_case_wait.py":prefix+addition},ensure_ascii=True))
