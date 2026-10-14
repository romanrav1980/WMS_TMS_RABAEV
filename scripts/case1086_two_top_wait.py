exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
from app.modules.inventory.infrastructure.st_defer_waiting import StDeferWaiting
from app.modules.inventory.contracts_waiting_tasks import WaitingTaskRequest
from app.modules.inventory.infrastructure.task_completion import complete_existing_task
from app.schemas import WarehouseTaskStatusRequest
src=json.loads(Path("tmp/context987.json").read_text(encoding="utf-8"));old=json.loads(Path("tmp/context1080.json").read_text(encoding="utf-8"))
path=Path("tmp/context1086.json");r=json.loads(path.read_text(encoding="utf-8"))if path.exists()else{"stage":"NEW","roots":[old["root"],old["inner"]],"decision":src["decision"]}
def save():path.write_text(json.dumps(r,indent=2,default=str),encoding="utf-8")
save();g=OracleGateway();hu=WarehouseHu(g);waiting=StDeferWaiting(g);tag=src["tag"]
def command(kind,root,op,body):return hu.command(kind,root,op+":"+tag,body,"admin")
def rootver(root):return hu.preview(root,"admin")["nodes"][0]["version"]
def move(task,root,start,end,op):
 req=WarehouseTaskStatusRequest(operation_id=op+":"+tag,fact_qty="1",updated_by="admin",scanned_pallet=root,scanned_from_cell=start,scanned_to_cell=end)
 out=complete_existing_task(g,task,req,"admin")
 assert complete_existing_task(g,task,req,"admin")==out
 return out
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 def totals():
  q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS cl on cl.CELL=r.CELL where cl.WARE_ID=:w",w=src["ware"]);return list(q.fetchone())
 assert totals()==[20,20]
 if r["stage"]=="NEW":
  body={"child_uid":r["roots"][1],"expected_version":rootver(r["roots"][0]),"expected_child_version":rootver(r["roots"][1]),"scan_container":r["roots"][0],"scan_child":r["roots"][1],"reason":"Retained two existing containers become independent top places"}
  r["detach_body"]=body;save();r["detach"]=command("HU_DETACH",r["roots"][0],"HU1086.DETACH",body)
  r["stage"]="DETACHED";save()
 if r["stage"]=="DETACHED":
  case=hu.preview("CASE:1131","admin")["nodes"][0]
  body={"child_case_task_id":1131,"expected_version":rootver(r["roots"][0]),"expected_child_version":case["version"],"scan_container":r["roots"][0],"scan_child":case["sscc"],"retained_tare_booking_operation_id":"TARE987.BOOK:"+tag+":1131","reason":"Retained standalone CASE packed into existing empty outer"}
  r["attach_body"]=body;save();r["attach"]=command("HU_ATTACH",r["roots"][0],"HU1086.ATTACH.RETAINED",body)
  r["stage"]="TWO_TOP";save()
 if r["stage"]=="TWO_TOP":
  view=waiting.read(r["decision"],"admin",0,30);assert len(view["available_places"])==2 and all(p["place_kind"]=="HU"and p["available"]for p in view["available_places"]),view
  r["two_top_view"]=view;save()
  body={"expected_version":rootver(r["roots"][0]),"target_cell":"QH"+tag,"scan_container":r["roots"][0],"scanned_from_cell":src["wait"],"scanned_to_cell":"QH"+tag}
  r["control_a"]=command("HU_PLAN_MOVE",r["roots"][0],"HU1086.CONTROL.A.PLAN",body);r["stage"]="A_CONTROL_PLANNED";save()
 if r["stage"]=="A_CONTROL_PLANNED":
  r["control_a_move"]=move(r["control_a"]["task_id"],r["roots"][0],src["wait"],"QH"+tag,"HU1086.CONTROL.A.MOVE")
  r["stage"]="A_CONTROL";save()
 if r["stage"]=="A_CONTROL":
  # Arbitrary public HU_MOVE metadata may not grant shared WAIT target.
  wire={"contract_version":2,"operation_id":"HU1086.GENERIC.BYPASS:"+tag,"command_type":"HU_MOVE","actor":"admin","source":{"uid":r["roots"][0]},"lines":[],"units":[],"metadata":{"expected_version":rootver(r["roots"][0]),"target_cell":src["wait"],"defer_decision_operation_id":r["decision"],"defer_requested_root":r["roots"][0],"scan_container":r["roots"][0],"scanned_from_cell":"QH"+tag,"scanned_to_cell":src["wait"]}}
  try:
   result=q.var(oracledb.DB_TYPE_CLOB);resolution=q.var(oracledb.DB_TYPE_CLOB)
   q.execute("begin RRL_STOCK_POSTING_API.prepare_command(:payload,:actor,:result,:resolution);end;",payload=json.dumps(wire),actor="admin",result=result,resolution=resolution)
   raise AssertionError("Generic metadata bypass allowed")
  except oracledb.DatabaseError as exc:
   assert exc.args[0].code==20886 and "HU_MOVE_EMPTY_TARGET_REQUIRED"in exc.args[0].message,exc
   r["generic_metadata_refused"]=True
  finally:c.rollback()
  req=WaitingTaskRequest(operation_id="HU1086.WAIT.A.PLAN:"+tag,decision_operation_id=r["decision"],root_identifier=r["roots"][0])
  r["a_request"]=req.model_dump();r["a_plan"]=waiting.plan(req,"admin");r["stage"]="A_WAIT_PLANNED";save()
 if r["stage"]=="A_WAIT_PLANNED":
  body={"expected_version":rootver(r["roots"][1]),"target_cell":src["control"],"scan_container":r["roots"][1],"scanned_from_cell":src["wait"],"scanned_to_cell":src["control"]}
  r["control_b"]=command("HU_PLAN_MOVE",r["roots"][1],"HU1086.CONTROL.B.PLAN",body);r["stage"]="B_CONTROL_PLANNED";save()
 if r["stage"]=="B_CONTROL_PLANNED":
  r["control_b_move"]=move(r["control_b"]["task_id"],r["roots"][1],src["wait"],src["control"],"HU1086.CONTROL.B.MOVE");r["stage"]="B_CONTROL";save()
 if r["stage"]=="B_CONTROL":
  req=WaitingTaskRequest(operation_id="HU1086.WAIT.B.PLAN:"+tag,decision_operation_id=r["decision"],root_identifier=r["roots"][1])
  r["b_request"]=req.model_dump();r["b_plan"]=waiting.plan(req,"admin");r["stage"]="BOTH_WAIT_PLANNED";save()
 if r["stage"]=="BOTH_WAIT_PLANNED":
  view=waiting.read(r["decision"],"admin",0,40)
  assert all(not p["available"]and p.get("planned_task_id")for p in view["available_places"]),view
  r["both_planned_view"]=view;save()
  r["a_move"]=move(r["a_plan"]["tasks"][0]["task_id"],r["roots"][0],"QH"+tag,src["wait"],"HU1086.WAIT.A.MOVE");r["stage"]="A_DONE";save()
 if r["stage"]=="A_DONE":
  r["b_move"]=move(r["b_plan"]["tasks"][0]["task_id"],r["roots"][1],src["control"],src["wait"],"HU1086.WAIT.B.MOVE")
  assert totals()==[20,20]
  r.update(stage="DONE",physical_hard=totals(),sibling_after_first=True);save()
 print("PASS1086 two original TOP/12+8/shared wait/no generic metadata bypass/P20H20"if r["stage"]=="DONE"else r["stage"])
