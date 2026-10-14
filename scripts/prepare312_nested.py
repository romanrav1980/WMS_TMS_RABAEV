exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.public import build_stock_posting_service,StockCommand
from app.modules.inventory.infrastructure.interwarehouse import Interwarehouse
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import assign_sts
import httpx
source=json.loads(Path("tmp/context310.json").read_text(encoding="utf-8"));p=Path("tmp/context312.json");saved=json.loads(p.read_text(encoding="utf-8"))if p.exists()else{}
gw=OracleGateway();posting=build_stock_posting_service();service=Interwarehouse(gw,posting);hu=WarehouseHu(gw)
def save():p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  q.execute("select count(*)from RRL_CELLS where CELL=:cell_code",cell_code=source["outbound"])
  if not q.fetchone()[0]:
   q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell_code,:ware,0,0,0,0,0,0,0)",cell_code=source["outbound"],ware=source["target_warehouse"])
   q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell_code),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell_code=source["outbound"])
  c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
if "placement"in saved:pass
else:saved["placement"]=service.plan_placement("IW312.PUT.PLAN:"+source["tag"],source["receipt_operation"],"admin");save()
task=saved["placement"]["task_id"]
if "placed"not in saved:
 saved["placed"]=posting.post(StockCommand(operation_id="IW312.PUT.DONE:"+source["tag"],command_type="TASK_COMPLETE",actor="admin",source=dict(task_id=task),lines=(),metadata=dict(fact_qty="3",scanned_pallet=source["lot"],scanned_from_cell=source["receive_cell"],scanned_to_cell=source["outbound"])));save()
if "custody"not in saved:saved["custody"]=service.release_custody("IW312.CUSTODY:"+source["tag"],source["receipt_operation"],"admin");save()
if "onward"not in saved:saved["onward"]=service.prepare_onward("IW312.ONWARD:"+source["tag"],source["receipt_operation"],"Консолидация целого принятого груза в физический верхний HU","DEV312:retained original fulfillment","admin",True);save()
if "assigned"not in saved:assign_sts(gw,source["target_trip"],[saved["onward"]["st_number"]],"admin");saved["assigned"]=True;save()
top="IH312:"+source["tag"];inner="IB312:"+source["tag"]
for identifier,kind,tare in[(top,"PALLET","1"),(inner,"BOX","0.2")]:
 label="create:"+identifier
 if label not in saved:
  saved[label]=hu.command("HU_CREATE",identifier,"IW312.CREATE:"+identifier,dict(cell=source["outbound"],warehouse=source["target_warehouse"],container_type=kind,tare_weight_kg=tare,scan_container=identifier,scan_cell=source["outbound"]),"admin");save()
for parent,child in[(inner,source["lot"]),(top,inner)]:
 label="attach:"+child
 if label not in saved:
  parent_tree=hu.preview(parent,"admin");child_tree=hu.preview(child,"admin")
  meta=dict(child_uid=child,expected_version=parent_tree["nodes"][0]["version"],expected_child_version=child_tree["nodes"][0]["version"],scan_container=parent,scan_child=child,reason="Физическая упаковка принятого целого груза в верхнее место")
  saved[label]=hu.command("HU_ATTACH",parent,"IW312.ATTACH:"+child,meta,"admin");save()
saved.update(source=source,root=top,inner=inner,tree=hu.preview(top,"admin"));save()
assert len(saved["tree"]["nodes"])==3 and saved["tree"]["leaf_count"]==1
with httpx.Client(auth=("admin","admin123"),timeout=35)as client:
 st=saved["onward"]["shipment_identifier"];r=client.get("http://127.0.0.1:8088/api/outgoing-quality/"+st);assert r.status_code==200,r.text
 control=r.json()
 r=client.post("http://127.0.0.1:8088/api/outgoing-quality/"+st+"/scan",json=dict(operation_id="IW312.QC:"+source["tag"],expected_composition_signature=control["composition_signature"],error_count=0,scans=[code for unit in source["units"]for code in unit["codes"]]));assert r.status_code==200,r.text
 saved["quality"]=r.json();save()
print("PREP312 existing placement/custody/ST/assignment/physical HU TOP->BOX->one acceptedSTOCK3/QC6; no duplicate fulfillment/stock")
