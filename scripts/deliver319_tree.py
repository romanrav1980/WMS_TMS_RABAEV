exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.interwarehouse import Interwarehouse
from app.modules.inventory.public import build_stock_posting_service
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
from app.modules.transport.public import assign_sts
from app.transport_composition import build_transport_loading
from app.delivery_composition import build_delivery_receipt
from app.modules.delivery.infrastructure.order_delivery import OrderDelivery
from app.oracle_gateway import OracleGateway
import httpx
received=json.loads(Path("tmp/context314_received.json").read_text(encoding="utf-8"));source=received["source"];p=Path("tmp/context319.json");saved=json.loads(p.read_text(encoding="utf-8"))if p.exists()else{}
gw=OracleGateway();service=Interwarehouse(gw,build_stock_posting_service());hu=WarehouseHu(gw);loading=build_transport_loading();receiver=build_delivery_receipt()
def save():p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
if "onward"not in saved:saved["onward"]=service.prepare_onward("IW319.ST:"+source["tag"],received["operation_id"],"Доставка исходного принятого вложенного места без изменения его состава","DEV319:original same physical tree","admin",True);save()
if "assigned"not in saved:assign_sts(gw,source["target_trip"],[saved["onward"]["st_number"]],"admin");saved["assigned"]=True;save()
if "load"not in saved:
 st=saved["onward"]["shipment_identifier"]
 with httpx.Client(auth=("admin","admin123"),timeout=35)as client:
  r=client.get("http://127.0.0.1:8088/api/outgoing-quality/"+st);assert r.status_code==200,r.text;quality=r.json()
  r=client.post("http://127.0.0.1:8088/api/outgoing-quality/"+st+"/scan",json=dict(operation_id="IW319.QC:"+source["tag"],expected_composition_signature=quality["composition_signature"],error_count=0,scans=[code for unit in source["units"]for code in unit["codes"]]));assert r.status_code==200,r.text
 tree=hu.preview(source["physical_root"],"admin");ver=tree["nodes"][0]["version"]
 meta=dict(expected_version=ver,scan_container=source["physical_root"],scan_cell=source["outbound"],loading_context=dict(transport_task_id=source["target_trip"],scan_vehicle="QL"+source["tag"],scan_dock=source["outbound"],measurements=dict(origin="MANUAL_CONFIRMED",content_version=ver,gross_weight_kg="12",width_m="1",depth_m="1",height_m="1.5")))
 op="IW319.LOAD:"+source["tag"];saved["load"]=loading.load(op,source["physical_root"],meta,"admin");saved.update(load_operation_id=op,load_metadata=meta);save()
assert loading.load(saved["load_operation_id"],source["physical_root"],saved["load_metadata"],"admin")==saved["load"]
if "depart"not in saved:saved["depart"]=loading.depart("IW319.DEPART:"+source["tag"],source["target_trip"],"admin");save()
if "receipt"not in saved:
 preview=receiver.preview(saved["load_operation_id"],saved["onward"]["final_address"],"admin")
 meta=dict(scan_place=preview["root_scan_identifier"],expected_composition_signature=preview["composition_signature"],before_cameras=True,observations=[],case_note="",scale_capture_key="",photo_ids=[],weight_act_confirmed=False,
  scans=[dict(code,disposition="ACCEPTED")for unit in source["units"]for code in unit["codes"]])
 op="STORE319.RECEIVE:"+source["tag"];saved["receipt"]=receiver.confirm(op,saved["load_operation_id"],saved["onward"]["final_address"],meta,"admin");saved.update(receipt_operation_id=op,receipt_metadata=meta);save()
assert receiver.confirm(saved["receipt_operation_id"],saved["load_operation_id"],saved["onward"]["final_address"],saved["receipt_metadata"],"admin")==saved["receipt"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=:st_id",st_id=saved["onward"]["source_st_id"]);order=q.fetchone()[0]
 q.execute("select sum(FACT_QTY),count(*)from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=:order_id and STATUS='SHIPPED'",order_id=order);assert q.fetchone()==(3,1)
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=source["lot"]);assert q.fetchone()==(0,0)
 q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:lot_id",lot_id=source["lot"]);assert q.fetchone()[0]==6
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
 snapshot=OrderDelivery(gw).get(order);saved.update(order_id=order,delivery_snapshot=snapshot);save()
 assert snapshot["quantities"][0]["accepted"]=="3"and snapshot["quantities"][0]["unreceived"]=="0",snapshot
print("PASS319 SAPbirth -> first nestedHU leg -> actualwarehouse same-tree receive/wholeHU task/custody -> secondleg sameTOP-BOX/STOCK -> storeaccepted3; originalFF3once/old6codes/lineage/protected20-20")
