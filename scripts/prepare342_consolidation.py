exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.public import build_stock_posting_service,StockCommand
from app.modules.inventory.infrastructure.interwarehouse import Interwarehouse
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
from app.modules.transport.public import assign_sts
from app.oracle_gateway import OracleGateway
import httpx
sources=[json.loads(Path("tmp/context"+n+".json").read_text(encoding="utf-8"))for n in["340","341"]]
p=Path("tmp/context342.json");saved=json.loads(p.read_text(encoding="utf-8"))if p.exists()else{"sources":sources,"parts":{}}
gw=OracleGateway();posting=build_stock_posting_service();service=Interwarehouse(gw,posting);hu=WarehouseHu(gw)
def save():p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  q.execute("update RRL_TR_VEHICLE set PALLETS=2 where NUM=:plate",plate="QL"+sources[0]["tag"])
  for source in sources:
   for cell,blocked in[(source["outbound"],0),("IR342"+source["tag"],1)]:
    q.execute("select count(*)from RRL_CELLS where CELL=:cell",cell=cell)
    if not q.fetchone()[0]:
     q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE)values(:cell,:ware,0,0,0,0,0,0,0,:blocked,:blocked)",cell=cell,ware=source["target_warehouse"],blocked=blocked)
     q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
  c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
for source in sources:
 tag=source["tag"];part=saved["parts"].setdefault(tag,{});cell="IR342"+tag;receipt="IW342.RECEIVE:"+tag
 if "unload"not in part:part["unload"]=service.receive_action("INTERWARE_UNLOAD","IW342.UNLOAD:"+tag,source["plan_operation_id"],dict(scan_pallet=source["lot"],scan_vehicle="QL"+tag,scan_dock=source["inbound"]),"admin");save()
 if "receipt"not in part:part["receipt"]=service.receive_action("INTERWARE_RECEIVE",receipt,source["plan_operation_id"],dict(scan_pallet=source["lot"],scan_cell=cell,scan_article=source["barcode"],article=source["article"],quantity="3",base_uom="EA",aggregation_scans=source["aggregations"]),"admin");save()
 if "placement"not in part:part["placement"]=service.plan_placement("IW342.PUT:"+tag,receipt,"admin");save()
 if "placed"not in part:part["placed"]=posting.post(StockCommand(operation_id="IW342.PLACED:"+tag,command_type="TASK_COMPLETE",actor="admin",source=dict(task_id=part["placement"]["task_id"]),lines=(),metadata=dict(fact_qty="3",scanned_pallet=source["lot"],scanned_from_cell=cell,scanned_to_cell=source["outbound"])));save()
 if "custody"not in part:part["custody"]=service.release_custody("IW342.CUSTODY:"+tag,receipt,"admin");save()
 if "onward"not in part:part["onward"]=service.prepare_onward("IW342.ST:"+tag,receipt,"Две исходные поставки в одном верхнем месте","DEV342:original two ST preserved","admin",True);save()
 if "assigned"not in part:assign_sts(gw,source["target_trip"],[part["onward"]["st_number"]],"admin");part["assigned"]=True;save()
common=sources[0];top="IH342:"+common["tag"]
if "create"not in saved:saved["create"]=hu.command("HU_CREATE",top,"IW342.CREATE:"+common["tag"],dict(cell=common["outbound"],warehouse=common["target_warehouse"],container_type="PALLET",tare_weight_kg="1",scan_container=top,scan_cell=common["outbound"]),"admin");save()
for source in sources:
 key="attach:"+source["tag"]
 if key not in saved:
  parent=hu.preview(top,"admin");child=hu.preview(source["lot"],"admin")
  saved[key]=hu.command("HU_ATTACH",top,"IW342.ATTACH:"+source["tag"],dict(child_uid=source["lot"],expected_version=parent["nodes"][0]["version"],expected_child_version=child["nodes"][0]["version"],scan_container=top,scan_child=source["lot"],reason="Консолидация двух принятых немаркированных паллет в одно физическое место"),"admin");save()
with httpx.Client(auth=("admin","admin123"),timeout=35)as client:
 for source in sources:
  key="qc:"+source["tag"]
  if key in saved:continue
  st=saved["parts"][source["tag"]]["onward"]["shipment_identifier"];r=client.get("http://127.0.0.1:8088/api/outgoing-quality/"+st);assert r.status_code==200,r.text
  r=client.post("http://127.0.0.1:8088/api/outgoing-quality/"+st+"/scan",json=dict(operation_id="IW342.QC:"+source["tag"],expected_composition_signature=r.json()["composition_signature"],error_count=0,scans=[code for unit in source["units"]for code in unit["codes"]]));assert r.status_code==200,r.text;saved[key]=r.json();save()
saved.update(root=top,tree=hu.preview(top,"admin"));save()
assert saved["tree"]["leaf_count"]==2
print("PREP342 two original ordinary3EA receipts/oldtasks/custody/ST/same TT/QC/one physical top with two STOCK leaves")
