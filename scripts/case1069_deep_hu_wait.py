"""Retain the 20 already picked goods; add only an empty outer container."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import time
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
from app.modules.inventory.infrastructure.task_completion import complete_existing_task
from app.modules.inventory.infrastructure.st_defer_waiting import StDeferWaiting
from app.modules.inventory.contracts_waiting_tasks import WaitingTaskRequest
from app.modules.transport.infrastructure.st_deferral import StDeferral
from app.modules.platform.public import read_oracle_json
from app.schemas import WarehouseTaskStatusRequest
src=json.loads(Path("tmp/context987.json").read_text(encoding="utf-8"));prior=json.loads(Path("tmp/context1057.json").read_text(encoding="utf-8"))
assert prior["stage"]=="DONE"
path=Path("tmp/context1069.json")
record=json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"stage":"NEW","root":"HU1069:"+src["tag"],"inner":prior["root"],"source":987,"decision":src["decision"]}
def save():path.write_text(json.dumps(record,indent=2,default=str),encoding="utf-8")
save();g=OracleGateway();hu=WarehouseHu(g);waiting=StDeferWaiting(g);tag=src["tag"];root=record["root"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=12000;q=c.cursor()
 def totals():
  q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS cl on cl.CELL=r.CELL where cl.WARE_ID=:w",w=src["ware"])
  return list(q.fetchone())
 assert totals()==[20,20]
 if record["stage"]=="NEW":
  create={"cell":src["wait"],"warehouse":src["ware"],"container_type":"PALLET","tare_weight_kg":"1","scan_container":root,"scan_cell":src["wait"]}
  record["create_body"]=create;save()
  record["created"]=hu.command("HU_CREATE",root,"HU1069.CREATE:"+tag,create,"admin")
  record["stage"]="CREATED";save()
 if record["stage"]=="CREATED":
  outer=hu.preview(root,"admin");inner=hu.preview(record["inner"],"admin")
  attach={"child_uid":record["inner"],"expected_version":outer["nodes"][0]["version"],"expected_child_version":inner["nodes"][0]["version"],"scan_container":root,"scan_child":record["inner"]}
  record["attach_body"]=attach;save()
  record["attached"]=hu.command("HU_ATTACH",root,"HU1069.ATTACH:"+tag,attach,"admin")
  assert totals()==[20,20];record["stage"]="ATTACHED";save()
 if record["stage"]=="ATTACHED":
  tree=hu.preview(root,"admin");assert len([n for n in tree["nodes"]if n["kind"]=="CONTAINER"])==2
  context=StDeferral(g).context(src["st"],"admin")
  assert context["physical_preparation"]["state"]=="PREPARED_HU"and context["physical_preparation"]["root"]==root
  record["initial_deep_context"]=context
  body={"expected_version":tree["nodes"][0]["version"],"target_cell":"QH"+tag,"scan_container":root,"scanned_from_cell":tree["cell"],"scanned_to_cell":"QH"+tag}
  record["control_plan_body"]=body;save()
  record["control_plan"]=hu.command("HU_PLAN_MOVE",root,"HU1069.CONTROL.PLAN:"+tag,body,"admin")
  record["control_task"]=int(record["control_plan"]["task_id"]);record["stage"]="CONTROL_PLANNED";save()
 if record["stage"]=="CONTROL_PLANNED":
  req=WarehouseTaskStatusRequest(operation_id="HU1069.CONTROL.MOVE:"+tag,fact_qty="1",updated_by="admin",scanned_pallet=root,scanned_from_cell=src["wait"],scanned_to_cell="QH"+tag)
  record["control_move"]=complete_existing_task(g,record["control_task"],req,"admin")
  assert totals()==[20,20];record["stage"]="CONTROL_DONE";save()
 if record["stage"]=="CONTROL_DONE":
  context=StDeferral(g).context(src["st"],"admin")
  assert context["physical_preparation"]["root"]==root and context["physical_preparation"]["physical_move_required"]is True
  record["current_deep_context"]=context;save()
  operation="HU1069.WAIT.PLAN:"+tag
  # A separate holder keeps only our own TT row; no business data is written.
  with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as holder:
   holder.call_timeout=5000;hold=holder.cursor()
   hold.execute("select ID from RRL_TRANSPORT_TASK where ID=:id for update",id=src["target_trip"]);assert hold.fetchone()[0]==src["target_trip"]
   out=q.var(oracledb.DB_TYPE_CLOB);started=time.monotonic()
   try:
    try:q.callproc("RRL_ST_DEFER_WAIT_API.plan_waiting",[operation,src["decision"],"admin",out]);raise AssertionError("Busy target trip accepted")
    except oracledb.DatabaseError as exc:
     assert getattr(exc.args[0],"code",0)==20840,str(exc)
     record["row_contention_error"]=str(exc).split("\n",1)[0];record["row_contention_seconds"]=time.monotonic()-started
     assert record["row_contention_seconds"]<5
   finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection");holder.rollback()
  q.execute("select count(*)from RRL_ST_DEFER_WAIT_RUN where OPERATION_ID=:op",op=operation);assert q.fetchone()[0]==0
  assert totals()==[20,20];record["bounded_contention_no_plan"]=True;save()
  req=WaitingTaskRequest(operation_id=operation,decision_operation_id=src["decision"])
  record["plan_request"]=req.model_dump();save()
  record["plan"]=waiting.plan(req,"admin");assert waiting.plan(req,"admin")==record["plan"]
  record.update(task=int(record["plan"]["tasks"][0]["task_id"]),stage="WAIT_PLANNED",plan_replay=True);save()
 if record["stage"]=="WAIT_PLANNED":
  req=WarehouseTaskStatusRequest(operation_id="HU1069.WAIT.MOVE:"+tag,fact_qty="1",updated_by="admin",scanned_pallet=root,scanned_from_cell="QH"+tag,scanned_to_cell=src["wait"])
  record["move_request"]=req.model_dump(mode="json");save()
  result=complete_existing_task(g,record["task"],req,"admin");assert complete_existing_task(g,record["task"],req,"admin")==result
  tree=hu.preview(root,"admin");assert tree["cell"]==src["wait"]and tree["top_place_count"]==1 and tree["leaf_count"]==2
  assert len([n for n in tree["nodes"]if n["kind"]=="CONTAINER"])==2 and len([n for n in tree["nodes"]if n["kind"]=="CASE"])==2
  assert totals()==[20,20]
  q.execute("select c.CASE_PICK_TASK_ID,c.CONTENT_VERSION,f.PICKED_CONTENT_VERSION,c.CURRENT_CELL from RRL_CASE_PICK_TASK c join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.PICKED_CASE_TASK_ID=c.CASE_PICK_TASK_ID where c.CASE_PICK_TASK_ID in(1131,1132)order by c.CASE_PICK_TASK_ID")
  versions=[list(x)for x in q];assert all(x[1]==x[2] and x[3]==src["wait"]for x in versions)
  q.execute("select sum(BASE_QTY),count(*)from RRL_WAREHOUSE_TASK_STOCK_MOVE where TASK_ID=:id",id=record["task"]);assert q.fetchone()==(20,2)
  record.update(result=result,current_tree=tree,current_versions=versions,physical_hard=totals(),stage="DONE",move_replay=True);save()
 print("DONE1069 two container levels/twoCASE/1top/twoleaves20/P20H20/TT NOWAIT20840 no plan/exact replay" if record["stage"]=="DONE" else "stage="+record["stage"])
