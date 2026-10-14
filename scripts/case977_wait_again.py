exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.st_deferral import StDeferral
from app.modules.inventory.infrastructure.task_completion import complete_existing_task
from app.modules.platform.public import read_oracle_json
from app.schemas import WarehouseTaskStatusRequest
ctx=json.loads(Path("tmp/context955.json").read_text(encoding="utf-8"));prior=json.loads(Path("tmp/context975.json").read_text(encoding="utf-8"));path=Path("tmp/context977.json")
assert not path.exists(),"977 continuation already registered; read retained source"
record={"case":ctx["case"],"st":ctx["st"],"stage":"NEW"}
def save():path.write_text(json.dumps(record,indent=2,default=str),encoding="utf-8")
save();g=OracleGateway()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select RRL_TRANSPORT_TASK_SQ.nextval from dual");trip=int(q.fetchone()[0])
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  q.execute("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED)select :id,TRANSPORT,TRANSTYPE,'Спланирован',trunc(SHIPMENT_DATE)+1,VODITEL_ID,DOCK,0 from RRL_TRANSPORT_TASK where ID=:source",id=trip,source=ctx["target_trip"]);c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 seen=StDeferral(g).context(ctx["st"],"admin");assert seen["physical_preparation"]["content_version"]==3
 body={"st_number":ctx["st"],"target_trip_id":trip,"expected_version":seen["version"],"source_hash":seen["source_hash"],"reason":"Existing controlled-zone CASE rescheduled to next planned day","reference":"WAIT977:"+ctx["tag"]}
 op="DEC977:"+ctx["tag"];result=StDeferral(g).defer(op,body,"admin");assert StDeferral(g).defer(op,body,"admin")==result
 record.update(trip=trip,decision=op,decision_result=result,stage="DEFERRED");save()
 out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_ST_DEFER_WAIT_API.plan_waiting",["PLAN977:"+ctx["tag"],op,"admin",out]);plan=read_oracle_json(out.getvalue());c.commit()
 task=int(plan["tasks"][0]["task_id"]);record.update(task=task,plan=plan,stage="PLANNED");save()
 request=WarehouseTaskStatusRequest(operation_id="MOVE977:"+ctx["tag"],fact_qty="1",updated_by="admin",scanned_pallet=ctx["carrier"],scanned_from_cell=prior["target"],scanned_to_cell=ctx["wait"])
 record["move_request"]=request.model_dump(mode="json");save()
 moved=complete_existing_task(g,task,request,"admin");assert complete_existing_task(g,task,request,"admin")==moved
 record.update(result=moved,stage="DONE");save()
 q.execute("select c.CONTENT_VERSION,f.PICKED_CONTENT_VERSION,c.CURRENT_CELL,f.STATUS from RRL_CASE_PICK_TASK c join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.PICKED_CASE_TASK_ID=c.CASE_PICK_TASK_ID where c.CASE_PICK_TASK_ID=:id",id=ctx["case"]);assert q.fetchone()==(4,4,ctx["wait"],"PICKED")
 q.execute("select BASE_QTY,BASE_UOM,OPERATION_ID from RRL_WAREHOUSE_TASK_STOCK_MOVE where TASK_ID=:id",id=task);assert q.fetchall()==[(12,"EA",request.operation_id)]
 q.execute("select SYNC_STATUS from RRL_WAREHOUSE_TASK_SYNC where TASK_ID=:id",id=task);assert q.fetchone()==("SYNCED",)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE),min(r.CELL),max(r.CELL)from RRL_REMAINS r join RRL_CASE_CARRIER_LOT l on l.LOT_UID=r.UID_POLETA where l.CASE_PICK_TASK_ID=:id and r.REMAIN>0",id=ctx["case"]);assert q.fetchone()==(12,12,ctx["wait"],ctx["wait"])
 q.execute("select FULFILLMENT_ID,PICKED_CONTENT_VERSION,PICKED_AT,PICKED_BY,FACT_QTY,FACT_UOM,FACT_COMPOSITION_JSON from RRL_CUSTOMER_ORDER_FULFILLMENT where PICKED_CASE_TASK_ID=:id",id=ctx["case"]);fact=list(q.fetchone());fact[-1]=fact[-1].read()if hasattr(fact[-1],"read")else fact[-1]
 before=prior["before_fulfillment"];assert str(fact[2])==before[2]and fact[3:]==before[3:]
 record["evidence"]={"case_version":4,"fulfillment_version":4,"place_quantity":"1","goods":"12","hard":"12","old_pick_facts_preserved":True,"sync":"SYNCED","journal":"12 EA","exact_replay":True};save()
 print("PASS977 same retainedCASE fromcontrol -> original ST future day -> current typed waiting DONE1CASE/journal12EA/P12H12/CT4=FF4/SYNCED/oldfacts/exact cache, one FF-version writer")
