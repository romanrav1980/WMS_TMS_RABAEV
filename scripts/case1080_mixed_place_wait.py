"""Use original 987 goods: split only packaging, then plan HU and standalone CASE independently."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
from app.modules.inventory.application.case_carrier_move import CaseCarrierMove
from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
from app.modules.inventory.infrastructure.st_defer_waiting import StDeferWaiting
from app.modules.inventory.contracts_waiting_tasks import WaitingTaskRequest,WaitingTaskError
from app.modules.inventory.infrastructure.task_completion import complete_existing_task
from app.modules.transport.infrastructure.st_deferral import StDeferral
from app.schemas import WarehouseTaskStatusRequest
src=json.loads(Path("tmp/context987.json").read_text(encoding="utf-8"));deep=json.loads(Path("tmp/context1069.json").read_text(encoding="utf-8"))
path=Path("tmp/context1080.json")
record=json.loads(path.read_text(encoding="utf-8")) if path.exists()else{"stage":"NEW","source":987,"root":deep["root"],"inner":deep["inner"],"decision":src["decision"]}
def save():path.write_text(json.dumps(record,indent=2,default=str),encoding="utf-8")
save();g=OracleGateway();hu=WarehouseHu(g);waiting=StDeferWaiting(g);mover=CaseCarrierMove(StockPosting());tag=src["tag"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 def totals():
  q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS cl on cl.CELL=r.CELL where cl.WARE_ID=:w",w=src["ware"])
  return list(q.fetchone())
 assert totals()==[20,20]
 if record["stage"]=="NEW":
  parent=hu.preview(record["inner"],"admin");child=hu.preview("CASE:1131","admin")
  body={"child_case_task_id":1131,"expected_version":parent["nodes"][0]["version"],"expected_child_version":child["nodes"][0]["version"],
    "scan_container":record["inner"],"scan_child":child["nodes"][0]["sscc"],"reason":"Retained own CASE becomes separate top place for mixed ST waiting"}
  record["detach_body"]=body;save()
  record["detach"]=hu.command("HU_DETACH",record["inner"],"HU1080.DETACH:"+tag,body,"admin")
  assert totals()==[20,20];record["stage"]="DETACHED";save()
 if record["stage"]=="DETACHED":
  context=StDeferral(g).context(src["st"],"admin")
  assert context["physical_preparation"]["state"]=="PREPARED_PLACES"and len(context["physical_preparation"]["places"])==2,context
  view=waiting.read(src["decision"],"admin",0,20)
  assert view["selection_required"]is True and {p["place_kind"]for p in view["available_places"]}=={"HU","CASE"}
  record.update(context=context,view=view);save()
  try:waiting.plan(WaitingTaskRequest(operation_id="HU1080.NOSELECTION:"+tag,decision_operation_id=src["decision"]),"admin");raise AssertionError("Default selected arbitrary top")
  except WaitingTaskError as exc:assert exc.code=="ST_WAITING_ROOT_SELECTION_REQUIRED",str(exc)
  q.execute("select count(*)from RRL_ST_DEFER_WAIT_RUN where OPERATION_ID=:op",op="HU1080.NOSELECTION:"+tag);assert q.fetchone()[0]==0
  tree=hu.preview(record["root"],"admin")
  body={"expected_version":tree["nodes"][0]["version"],"target_cell":"QH"+tag,"scan_container":record["root"],"scanned_from_cell":src["wait"],"scanned_to_cell":"QH"+tag}
  record["control_plan_body"]=body;save()
  record["control_plan"]=hu.command("HU_PLAN_MOVE",record["root"],"HU1080.CONTROL.PLAN:"+tag,body,"admin")
  record["control_task"]=int(record["control_plan"]["task_id"]);record["stage"]="CONTROL_PLANNED";save()
 if record["stage"]=="CONTROL_PLANNED":
  req=WarehouseTaskStatusRequest(operation_id="HU1080.CONTROL.MOVE:"+tag,fact_qty="1",updated_by="admin",scanned_pallet=record["root"],scanned_from_cell=src["wait"],scanned_to_cell="QH"+tag)
  record["control_move"]=complete_existing_task(g,record["control_task"],req,"admin")
  record["stage"]="HU_CONTROL";save()
 if record["stage"]=="HU_CONTROL":
  case=hu.preview("CASE:1131","admin");version=case["nodes"][0]["version"];carrier=case["nodes"][0]["sscc"]
  record["case_control_args"]={"version":version,"carrier":carrier,"target":src["control"]};save()
  record["case_control"]=mover.execute("CASE1080.CONTROL:"+tag,"admin",1131,carrier,src["control"],version)
  assert totals()==[20,20];record["stage"]="CONTROL_DONE";save()
 if record["stage"]=="CONTROL_DONE":
  req=WaitingTaskRequest(operation_id="HU1080.WAIT.PLAN:"+tag,decision_operation_id=src["decision"],root_identifier=record["root"])
  record["hu_plan_request"]=req.model_dump();save()
  record["hu_plan"]=waiting.plan(req,"admin");assert waiting.plan(req,"admin")==record["hu_plan"]
  record["hu_task"]=int(record["hu_plan"]["tasks"][0]["task_id"]);record["stage"]="HU_PLANNED";save()
 if record["stage"]=="HU_PLANNED":
  view=waiting.read(src["decision"],"admin",0,30)
  planned=next(x for x in view["available_places"]if x["root_identifier"]==record["root"])
  independent=next(x for x in view["available_places"]if x["root_identifier"]=="CASE:1131")
  assert planned["available"]is False and planned["planned_task_id"]==record["hu_task"] and independent["available"]is True,view
  record["view_after_first_plan"]=view;save()
  req=WaitingTaskRequest(operation_id="CASE1080.WAIT.PLAN:"+tag,decision_operation_id=src["decision"],root_identifier="CASE:1131")
  record["case_plan_request"]=req.model_dump();save()
  record["case_plan"]=waiting.plan(req,"admin");assert waiting.plan(req,"admin")==record["case_plan"]
  record["case_task"]=int(record["case_plan"]["tasks"][0]["task_id"]);record["stage"]="BOTH_PLANNED";save()
 if record["stage"]=="BOTH_PLANNED":
  req=WarehouseTaskStatusRequest(operation_id="HU1080.WAIT.MOVE:"+tag,fact_qty="1",updated_by="admin",scanned_pallet=record["root"],scanned_from_cell="QH"+tag,scanned_to_cell=src["wait"])
  record["hu_move_request"]=req.model_dump(mode="json");save()
  record["hu_move"]=complete_existing_task(g,record["hu_task"],req,"admin");assert complete_existing_task(g,record["hu_task"],req,"admin")==record["hu_move"]
  assert totals()==[20,20];record["stage"]="HU_DONE";save()
 if record["stage"]=="HU_DONE":
  carrier=record["case_control_args"]["carrier"]
  req=WarehouseTaskStatusRequest(operation_id="CASE1080.WAIT.MOVE:"+tag,fact_qty="1",updated_by="admin",scanned_pallet=carrier,scanned_from_cell=src["control"],scanned_to_cell=src["wait"])
  record["case_move_request"]=req.model_dump(mode="json");save()
  record["case_move"]=complete_existing_task(g,record["case_task"],req,"admin");assert complete_existing_task(g,record["case_task"],req,"admin")==record["case_move"]
  assert totals()==[20,20]
  q.execute("select c.CASE_PICK_TASK_ID,c.CONTENT_VERSION,f.PICKED_CONTENT_VERSION,c.CURRENT_CELL from RRL_CASE_PICK_TASK c join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.PICKED_CASE_TASK_ID=c.CASE_PICK_TASK_ID where c.CASE_PICK_TASK_ID in(1131,1132)order by c.CASE_PICK_TASK_ID")
  versions=[list(x)for x in q];assert all(x[1]==x[2]and x[3]==src["wait"]for x in versions)
  q.execute("select TASK_ID,STATUS,UNIT_CODE,FACT_QTY from RRL_WAREHOUSE_TASK where TASK_ID in(:hu,:ca)order by TASK_ID",hu=record["hu_task"],ca=record["case_task"]);facts=[list(x)for x in q];assert all(x[1]=="DONE"and x[3]==1 for x in facts)
  record.update(stage="DONE",versions=versions,task_facts=facts,physical_hard=totals(),independent_sibling_after_first=True);save()
 print("DONE1080 mixedHU8+CASE12/sameST/twoindependenttypedtasks/currentmanifest/no-arbitrarychoice/CTFF/P20H20"if record["stage"]=="DONE"else record["stage"])
