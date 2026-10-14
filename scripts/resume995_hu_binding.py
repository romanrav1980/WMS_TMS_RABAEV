exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
from app.modules.inventory.infrastructure.task_completion import complete_existing_task
from app.modules.platform.public import read_oracle_json
from app.schemas import WarehouseTaskStatusRequest
ctx=json.loads(Path("tmp/context987.json").read_text(encoding="utf-8"));path=Path("tmp/context994.json")
record=json.loads(path.read_text(encoding="utf-8"));assert record["stage"]=="CREATED","Retained phase required"
root=record["root"]
def save():path.write_text(json.dumps(record,indent=2,default=str),encoding="utf-8")
g=OracleGateway();hu=WarehouseHu(g)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for caseid,line,carrier,qty,cell in ctx["cases"]:
  tree=hu.preview(root,"admin");parent_version=int(tree["nodes"][0]["version"])
  body={"child_case_task_id":int(caseid),"expected_version":parent_version,"expected_child_version":3,"scan_container":root,"scan_child":carrier,"retained_tare_booking_operation_id":"TARE987.BOOK:"+ctx["tag"]+":"+str(caseid)}
  packed=hu.command("HU_ATTACH",root,"HU995.ATTACH:"+ctx["tag"]+":"+str(caseid),body,"admin")
  assert hu.command("HU_ATTACH",root,"HU995.ATTACH:"+ctx["tag"]+":"+str(caseid),body,"admin")==packed
  q.execute("select c.CONTENT_VERSION,f.PICKED_CONTENT_VERSION from RRL_CASE_PICK_TASK c join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.PICKED_CASE_TASK_ID=c.CASE_PICK_TASK_ID where c.CASE_PICK_TASK_ID=:id",id=caseid);assert q.fetchone()==(4,4)
  record.setdefault("attachments",[]).append({"case":caseid,"body":body,"result":packed});save()
 tree=hu.preview(root,"admin");assert len([n for n in tree["nodes"]if n["kind"]=="CASE"])==2
 target="QH"+ctx["tag"]
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_HEIGHT,LIMIT_WEIGHT)values(:c,:w,0,0,0,0,0,0,0)",c=target,w=ctx["ware"])
  q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=target);c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 plan_body={"expected_version":int(tree["nodes"][0]["version"]),"target_cell":target,"scan_container":root,"scanned_from_cell":ctx["wait"],"scanned_to_cell":target}
 planned=hu.command("HU_PLAN_MOVE",root,"HU994.PLAN:"+ctx["tag"],plan_body,"admin")
 task=int(planned["task_id"]);record.update(plan=planned,plan_body=plan_body,task=task,target=target,stage="PLANNED");save()
 request=WarehouseTaskStatusRequest(operation_id="HU994.MOVE:"+ctx["tag"],fact_qty="1",updated_by="admin",scanned_pallet=root,scanned_from_cell=ctx["wait"],scanned_to_cell=target)
 record["request"]=request.model_dump(mode="json");save()
 native={"contract_version":2,"operation_id":"HU994.TRIAL:"+ctx["tag"],"command_type":"HU_TASK_COMPLETE","actor":"admin","source":{"task_id":task},"lines":[],"units":[],"metadata":{"fact_qty":"1","scanned_pallet":root,"scanned_from_cell":ctx["wait"],"scanned_to_cell":target}}
 out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(native),"admin",out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  assert read_oracle_json(out.getvalue())["status"]=="DONE"
  for caseid,*unused in ctx["cases"]:
   q.execute("select c.CONTENT_VERSION,f.PICKED_CONTENT_VERSION from RRL_CASE_PICK_TASK c join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.PICKED_CASE_TASK_ID=c.CASE_PICK_TASK_ID where c.CASE_PICK_TASK_ID=:id",id=caseid);assert q.fetchone()==(5,5)
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 for caseid,*unused in ctx["cases"]:
  q.execute("select c.CONTENT_VERSION,f.PICKED_CONTENT_VERSION,c.CURRENT_CELL from RRL_CASE_PICK_TASK c join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.PICKED_CASE_TASK_ID=c.CASE_PICK_TASK_ID where c.CASE_PICK_TASK_ID=:id",id=caseid);assert q.fetchone()==(4,4,ctx["wait"])
 moved=complete_existing_task(g,task,request,"admin");assert complete_existing_task(g,task,request,"admin")==moved
 record.update(result=moved,stage="DONE",positive_rollback=True,exact_replay=True);save()
 tree=hu.preview(root,"admin");assert tree["cell"]==target
 for caseid,*unused in ctx["cases"]:
  q.execute("select c.CONTENT_VERSION,f.PICKED_CONTENT_VERSION,c.CURRENT_CELL from RRL_CASE_PICK_TASK c join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.PICKED_CASE_TASK_ID=c.CASE_PICK_TASK_ID where c.CASE_PICK_TASK_ID=:id",id=caseid);assert q.fetchone()==(5,5,target)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CASE_CARRIER_LOT l on l.LOT_UID=r.UID_POLETA join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID where ct.PICK_WAVE_ID=:w",w=ctx["wave"]);assert q.fetchone()==(20,20)
 q.execute("select sum(BASE_QTY),count(*)from RRL_WAREHOUSE_TASK_STOCK_MOVE where TASK_ID=:id",id=task);assert q.fetchone()==(20,2)
 record["tree"]=tree;record["evidence"]={"cases":2,"case_ff_versions":"5/5 each","physical":"20","hard":"20","task_place_quantity":"1 HU","lot_journal":"12+8 EA","attach_case_ff_versions":"4/4","positive_rollback":True,"bridge_replay":True};save()
 print("PASS994 retained twoCASE packed into existingHU/CTFF4 -> oldHU_PLAN_MOVE/warehouse task/positive rollback/current CTFF5/currentcell/P20H20/journal20 in2lots/exact bridgecache")
