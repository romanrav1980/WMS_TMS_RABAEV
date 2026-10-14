exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
from app.modules.inventory.infrastructure.task_completion import complete_existing_task
from app.schemas import WarehouseTaskStatusRequest
from app.modules.platform.public import read_oracle_json
src=json.loads(Path("tmp/context987.json").read_text(encoding="utf-8"));prior=json.loads(Path("tmp/context994.json").read_text(encoding="utf-8"))
path=Path("tmp/context1002.json");assert not path.exists(),"retained phase only"
record={"root":prior["root"],"stage":"NEW","source":987};hu=WarehouseHu(OracleGateway())
def save():path.write_text(json.dumps(record,indent=2,default=str),encoding="utf-8")
save()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 caseid,line,carrier,qty,cell=src["cases"][0];root=record["root"];ware=src["ware"];target="QI"+src["tag"]
 tree=hu.preview(root,"admin");child=hu.preview(carrier,"admin")
 attach={"child_case_task_id":caseid,"expected_version":tree["nodes"][0]["version"],"expected_child_version":child["nodes"][0]["version"],"scan_container":root,"scan_child":carrier,"retained_tare_booking_operation_id":"TARE987.BOOK:"+src["tag"]+":"+str(caseid)}
 record["attach_body"]=attach;save()
 record["attach"]=hu.command("HU_ATTACH",root,"HU1002.ATTACH:"+src["tag"],attach,"admin");record["stage"]="ATTACHED";save()
 def seq(name):q.execute("select "+name+".nextval from dual");return int(q.fetchone()[0])
 topo=seq("RRL_WH_TOPOLOGY_SQ");tc=seq("RRL_TOPOLOGY_CELL_SQ");slots=[(seq("RRL_TOPO_CELL_SLOT_SQ"),"CASE1002:"+src["tag"]+":"+str(i))for i in range(3)]
 record.update(target=target,topology=topo,topology_cell=tc,slots=slots);save()
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_HEIGHT,LIMIT_WEIGHT)values(:cell,:ware,0,0,0,0,0,0,0)",cell=target,ware=ware)
  q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=target)
  q.execute("insert into RRL_WAREHOUSE_TOPOLOGY(TOPOLOGY_ID,WARE_ID,TOPOLOGY_CODE,STATUS)values(:id,:ware,:code,'PUBLISHED')",id=topo,ware=ware,code="HU1002:"+src["tag"])
  q.execute("insert into RRL_TOPOLOGY_CELL(TOPOLOGY_CELL_ID,TOPOLOGY_ID,WARE_ID,CELL_CODE,LEGACY_CELL_CODE,SLOT_LAYER_KIND,MAX_WEIGHT_KG,MAX_VOLUME_M3)values(:id,:topo,:ware,:cell,:cell,'STORAGE_SLOT',100,4)",id=tc,topo=topo,ware=ware,cell=target)
  for i,(sid,code)in enumerate(slots):
   q.execute("insert into RRL_TOPOLOGY_CELL_SLOT(CELL_SLOT_ID,TOPOLOGY_ID,TOPOLOGY_CELL_ID,PARENT_SLOT_LAYER_KIND,SLOT_KIND,SLOT_CODE,CAPACITY_QTY,CAPACITY_WEIGHT_KG,CAPACITY_VOLUME_M3,WIDTH_M,DEPTH_M,HEIGHT_M,SUB_COLUMN_NO)values(:id,:topo,:tc,'STORAGE_SLOT','STORAGE_SLOT',:code,1,100,3,1.2,1.2,2,:i)",id=sid,topo=topo,tc=tc,code=code,i=i)
  c.commit()
 except BaseException:c.rollback();raise
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 record["stage"]="CONFIGURED";save()
 def measures(v,mass):return {"origin":"MANUAL_CONFIRMED","content_version":v,"gross_weight_kg":str(mass),"width_m":"0.5","depth_m":"1","height_m":"1.5"}
 tree=hu.preview(root,"admin");version=tree["nodes"][0]["version"]
 body={"expected_version":version,"target_cell":target,"target_slot_id":slots[0][0],"measurements":measures(version,30),"scan_container":root,"scanned_from_cell":prior["target"],"scanned_to_cell":target}
 record["plan_body"]=body;save()
 record["plan"]=hu.command("HU_PLAN_MOVE",root,"HU1002.PLAN:"+src["tag"],body,"admin");record["task"]=int(record["plan"]["task_id"]);record["stage"]="PLANNED";save()
 request=WarehouseTaskStatusRequest(operation_id="HU1002.MOVE:"+src["tag"],fact_qty="1",updated_by="admin",scanned_pallet=root,scanned_from_cell=prior["target"],scanned_to_cell=target,scanned_to_slot_code=slots[0][1])
 record["request"]=request.model_dump(mode="json");save()
 record["move"]=complete_existing_task(OracleGateway(),record["task"],request,"admin");record["stage"]="PLACED";save()
 tree=hu.preview(root,"admin");child=hu.preview(carrier,"admin")
 body={"child_case_task_id":caseid,"expected_version":tree["nodes"][0]["version"],"expected_child_version":child["nodes"][0]["version"],"scan_container":root,"scan_child":carrier,"scan_cell":target,"scan_parent_slot":slots[0][1],"scan_child_slot":slots[1][1],"child_slot_id":slots[1][0],"reason":"Own retained CASE separate physical placement","parent_measurements":measures(tree["nodes"][0]["version"],15),"child_measurements":measures(child["nodes"][0]["version"],15)}
 record["unpack_body"]=body;save()
 record["unpack"]=hu.command("HU_UNPACK",root,"HU1002.UNPACK:"+src["tag"],body,"admin");record["stage"]="UNPACKED";save()
 child=hu.preview(carrier,"admin");version=int(child["nodes"][0]["version"])
 body={"case_task_id":caseid,"expected_version":version,"target_slot_id":slots[2][0],"scan_container":carrier,"scan_cell":target,"scan_from_slot":slots[1][1],"scan_to_slot":slots[2][1],"measurements":measures(version,15),"reason":"Current bound CASE relocated between slots"}
 record["relocate_body"]=body;record["old_version"]=version;save()
 command={"contract_version":2,"operation_id":"HU1002.RELOCATE.TRIAL:"+src["tag"],"command_type":"HU_RELOCATE_SLOT","actor":"admin","source":{"uid":"CASE:"+str(caseid)},"lines":[],"units":[],"metadata":body}
 out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),"admin",out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  record["trial"]=read_oracle_json(out.getvalue())
  q.execute("select c.CONTENT_VERSION,f.PICKED_CONTENT_VERSION from RRL_CASE_PICK_TASK c join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.PICKED_CASE_TASK_ID=c.CASE_PICK_TASK_ID where c.CASE_PICK_TASK_ID=:id",id=caseid);assert q.fetchone()==(version+1,version+1)
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select c.CONTENT_VERSION,f.PICKED_CONTENT_VERSION from RRL_CASE_PICK_TASK c join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.PICKED_CASE_TASK_ID=c.CASE_PICK_TASK_ID where c.CASE_PICK_TASK_ID=:id",id=caseid);assert q.fetchone()==(version,version)
 record["positive_rollback"]=True;save()
 op="HU1002.RELOCATE:"+src["tag"];uid="CASE:"+str(caseid)
 record["relocate"]=hu.command("HU_RELOCATE_SLOT",uid,op,body,"admin");assert hu.command("HU_RELOCATE_SLOT",uid,op,body,"admin")==record["relocate"]
 record["stage"]="RELOCATED";record["exact_replay"]=True;save()
 q.execute("select c.CONTENT_VERSION,f.PICKED_CONTENT_VERSION,c.CURRENT_CELL from RRL_CASE_PICK_TASK c join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.PICKED_CASE_TASK_ID=c.CASE_PICK_TASK_ID where c.CASE_PICK_TASK_ID=:id",id=caseid);assert q.fetchone()==(version+1,version+1,target)
 q.execute("select CELL_SLOT_ID,HU_COMPOSITION_VERSION from RRL_RECEIPT_SLOT_CLAIM where HU_CASE_TASK_ID=:id and STATUS='OCCUPIED'",id=caseid);assert q.fetchone()==(slots[2][0],version+1)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CASE_CARRIER_LOT l on l.LOT_UID=r.UID_POLETA join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID where ct.PICK_WAVE_ID=:w",w=src["wave"]);assert q.fetchone()==(20,20)
 record.update(current_case=hu.preview(carrier,"admin"),current_hu=hu.preview(root,"admin"),physical="20",hard="20");save()
 print("PASS1002 retained987 attach/slottedtask/unpack/CASErelocate/currentCTFF/claim/positiveRollback/replay/P20H20")
