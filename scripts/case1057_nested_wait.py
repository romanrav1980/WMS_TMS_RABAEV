"""Retained 987/1002 source only: no new stock or receipt factory."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
from app.modules.inventory.infrastructure.st_defer_waiting import StDeferWaiting
from app.modules.inventory.contracts_waiting_tasks import WaitingTaskRequest
from app.modules.inventory.infrastructure.task_completion import complete_existing_task
from app.modules.transport.infrastructure.st_deferral import StDeferral
from app.modules.platform.public import read_oracle_json
from app.oracle_gateway import OracleGateway
from app.schemas import WarehouseTaskStatusRequest
src=json.loads(Path("tmp/context987.json").read_text(encoding="utf-8"));slot=json.loads(Path("tmp/context1002.json").read_text(encoding="utf-8"))
path=Path("tmp/context1057.json")
record=json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"stage":"NEW","source":987,"root":slot["root"],"decision":src["decision"],"st":src["st"]}
def save():path.write_text(json.dumps(record,indent=2,default=str),encoding="utf-8")
save();g=OracleGateway();hu=WarehouseHu(g);waiting=StDeferWaiting(g)
root=record["root"];tag=src["tag"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor()
 def totals():
  q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS cl on cl.CELL=r.CELL where cl.WARE_ID=:w",w=src["ware"])
  return list(q.fetchone())
 assert totals()==[20,20]
 if record["stage"]=="NEW":
  try:StDeferral(g).context(src["st"],"admin");raise AssertionError("Partial top/standalone source accepted")
  except Exception as e:
   assert "DEFER_HU_EXACT_ALL_ST_MEMBERS_IN_TOP_REQUIRED" in str(e),str(e)
   record["partial_tree_refused"]=True
  tree=hu.preview(root,"admin");child=hu.preview("CASE:1131","admin")
  body={"expected_version":tree["nodes"][0]["version"],"expected_child_version":child["nodes"][0]["version"],
   "child_case_task_id":1131,"scan_container":root,"scan_child":child["nodes"][0]["sscc"],
   "retained_tare_booking_operation_id":"TARE987.BOOK:"+tag+":1131",
   "reason":"Retained own twoCASE source assembled for whole waiting task",
   "scan_cell":tree["cell"],"scan_parent_slot":tree["placement"]["slot_code"],"scan_child_slot":child["placement"]["slot_code"],
   "measurements":{"origin":"MANUAL_CONFIRMED","content_version":tree["nodes"][0]["version"],"gross_weight_kg":"30","width_m":"1","depth_m":"0.75","height_m":"1"}}
  record["pack_body"]=body;save()
  record["pack"]=hu.command("HU_REPACK_SLOT",root,"HU1057.PACK.CANONICAL:"+tag,body,"admin")
  assert totals()==[20,20];record["stage"]="PACKED";save()
 if record["stage"]=="PACKED":
  context=StDeferral(g).context(src["st"],"admin");prep=context["physical_preparation"]
  assert prep["state"]=="PREPARED_HU"and prep["case_count"]==2 and prep["lot_count"]==2
  record["context"]=context;save()
  out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_ST_DEFER_WAIT_API.plan_waiting",["HU1057.TRIAL.PLAN:"+tag,src["decision"],"admin",out])
   trial=read_oracle_json(out.getvalue());task=int(trial["tasks"][0]["task_id"])
   q.execute("select STATUS,UNIT_CODE,QTY,HU_CONTENT_VERSION from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=task)
   assert q.fetchone()[0:3]==("PLANNED","HU",1)
   assert totals()==[20,20];record["plan_trial"]=trial
  finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select count(*)from RRL_ST_DEFER_WAIT_RUN where OPERATION_ID=:op",op="HU1057.TRIAL.PLAN:"+tag)
  assert q.fetchone()[0]==0
  record["plan_positive_rollback"]=True;save()
  req=WaitingTaskRequest(operation_id="HU1057.PLAN:"+tag,decision_operation_id=src["decision"])
  record["plan_request"]=req.model_dump();save()
  planned=waiting.plan(req,"admin");assert waiting.plan(req,"admin")==planned
  record.update(plan=planned,task=int(planned["tasks"][0]["task_id"]),stage="PLANNED",plan_replay=True);save()
 if record["stage"]=="PLANNED":
  task=record["task"];source=record["plan"]["from_cell"];target=record["plan"]["waiting_cell"]
  meta={"fact_qty":"1","scanned_pallet":root,"scanned_from_cell":source,"scanned_to_cell":target}
  native={"contract_version":2,"operation_id":"HU1057.TRIAL.MOVE:"+tag,"command_type":"HU_TASK_COMPLETE","actor":"admin","source":{"task_id":task},"lines":[],"units":[],"metadata":meta}
  out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   bad=json.loads(json.dumps(native));bad["operation_id"]="HU1057.PARTIAL:"+tag;bad["metadata"]["unit_keys"]=["UNSELECTED"]
   try:
    q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(bad),"admin",out,None])
    if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
    raise AssertionError("Partial physical selection accepted")
   except oracledb.DatabaseError as e:assert "DEFER_HU_NO_PARTIAL_UNIT_SELECTION" in str(e),str(e)
  finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  record["partial_selection_refused"]=True;save()
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(native),"admin",out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   trial=read_oracle_json(out.getvalue());assert trial["status"]=="DONE"
   q.execute("select STATUS,FACT_QTY from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=task);assert q.fetchone()==("DONE",1)
   assert totals()==[20,20];record["move_trial"]=trial
  finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=task);assert q.fetchone()[0]=="PLANNED"
  record["move_positive_rollback"]=True;save()
  req=WarehouseTaskStatusRequest(operation_id="HU1057.MOVE:"+tag,fact_qty="1",updated_by="admin",scanned_pallet=root,scanned_from_cell=source,scanned_to_cell=target)
  record["move_request"]=req.model_dump(mode="json");save()
  moved=complete_existing_task(g,task,req,"admin");assert complete_existing_task(g,task,req,"admin")==moved
  assert totals()==[20,20]
  tree=hu.preview(root,"admin");assert tree["cell"]==target and len([n for n in tree["nodes"]if n["kind"]=="CASE"])==2
  q.execute("select c.CASE_PICK_TASK_ID,c.CONTENT_VERSION,f.PICKED_CONTENT_VERSION,c.CURRENT_CELL from RRL_CASE_PICK_TASK c join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.PICKED_CASE_TASK_ID=c.CASE_PICK_TASK_ID where c.CASE_PICK_TASK_ID in(1131,1132)order by c.CASE_PICK_TASK_ID")
  versions=[list(x)for x in q];assert all(x[1]==x[2] and x[3]==target for x in versions)
  q.execute("select sum(BASE_QTY),count(*)from RRL_WAREHOUSE_TASK_STOCK_MOVE where TASK_ID=:id",id=task);assert q.fetchone()==(20,2)
  record.update(result=moved,current_tree=tree,current_versions=versions,physical_hard=totals(),stage="DONE",move_replay=True);save()
 print("DONE1057 whole retained twoCASE/1HU/20EA/plan+move rollback/exactreplay/P20H20/currentFFversions" if record["stage"]=="DONE" else "stage="+record["stage"])
