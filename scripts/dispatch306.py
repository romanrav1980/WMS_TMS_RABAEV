exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.interwarehouse import Interwarehouse
from app.modules.inventory.public import build_stock_posting_service
from app.modules.inventory.infrastructure.interwarehouse_recovery_st import prepare_recovery_st
from app.modules.transport.public import create_existing_trip,update_existing_trip,assign_sts
from app.transport_composition import build_transport_loading
from app.delivery_composition import build_delivery_receipt
from app.modules.delivery.infrastructure.order_delivery import OrderDelivery
from datetime import date
import httpx
gw=OracleGateway();service=Interwarehouse(gw,build_stock_posting_service());loading=build_transport_loading();receiver=build_delivery_receipt();reader=OrderDelivery(gw)
ctx_path=Path("tmp/context305.json");ctx=json.loads(ctx_path.read_text(encoding="utf-8"));found_path=Path("tmp/context305_recovery.json");found=json.loads(found_path.read_text(encoding="utf-8"));p=Path("tmp/context306.json");saved=json.loads(p.read_text(encoding="utf-8"))if p.exists()else {}
def save():p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
if "custody"not in saved:saved["custody"]=service.release_custody("IW306.CUSTODY:"+ctx["tag"],ctx["receipt_operation"],"admin");save()
if "original_onward"not in saved:
 saved["original_onward"]=service.prepare_onward("IW306.ORIGINAL.ST:"+ctx["tag"],ctx["receipt_operation"],"Повторное плечо принятой части исходного груза","DEV306:original1","admin",True);save()
 assign_sts(gw,ctx["target_trip"],[saved["original_onward"]["st_number"]],"admin")
 saved["original_assigned"]=True;save()
saved.setdefault("deliveries",[{}for _ in range(3)]);save()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select VODITEL_ID from RRL_TRANSPORT_TASK where ID=:trip_id",trip_id=ctx["target_trip"]);driver=q.fetchone()[0]
 q.execute("select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=:st_id",st_id=saved["original_onward"]["source_st_id"]);order=q.fetchone()[0];saved["order_id"]=order;save()
with httpx.Client(auth=("admin","admin123"),timeout=35)as h:
 for index,item in enumerate(saved["deliveries"]):
  if "onward"not in item:
   if index==0:item.update(onward=saved["original_onward"],trip_id=ctx["target_trip"])
   else:
    if "trip_id"not in item:item["trip_id"]=create_existing_trip(gw,"15",date(2026,10,12),"admin");save()
    update_existing_trip(gw,item["trip_id"],dict(transport="QL"+ctx["tag"],transtype="15",dock=ctx["outbound"],voditel_id=driver),"admin")
    part=found["parts"][index-1];item["onward"]=prepare_recovery_st(gw,"IW306.FOUND.ST:"+str(index)+":"+ctx["tag"],part["receipt_operation_id"],item["trip_id"],"Повторная доставка найденной конкретной единицы","DEV306:found"+str(index),"admin")
    save();assign_sts(gw,item["trip_id"],[item["onward"]["st_number"]],"admin")
   save()
  onward=item["onward"];st=onward["shipment_identifier"];lot=onward["pallet_identifier"]
  if "load_result"not in item:
   r=h.get("http://127.0.0.1:8088/api/outgoing-quality/"+st);assert r.status_code==200,r.text;quality=r.json()
   with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
    q=c.cursor();q.execute("select UNIT_ID from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id",lot_id=lot);ids={row[0]for row in q};assert len(ids)==1
   scans=[code for unit in ctx["units"]if unit["unit_id"]in ids for code in unit["codes"]];assert len(scans)==2
   r=h.post("http://127.0.0.1:8088/api/outgoing-quality/"+st+"/scan",json=dict(operation_id="IW306.QC:"+str(index)+":"+ctx["tag"],expected_composition_signature=quality["composition_signature"],error_count=0,scans=scans));assert r.status_code==200,r.text
   preview=loading.preview_single(st)
   meta=dict(expected_version=preview["expected_version"],expected_composition_signature=preview["composition_signature"],scan_container=lot,scan_cell=ctx["outbound"],
     loading_context=dict(transport_task_id=item["trip_id"],scan_vehicle="QL"+ctx["tag"],scan_dock=ctx["outbound"],measurements=dict(origin="MANUAL_CONFIRMED",content_version=preview["expected_version"],gross_weight_kg="2",width_m="1",depth_m="1",height_m="1.5")))
   op="IW306.LOAD:"+str(index)+":"+ctx["tag"];item["load_result"]=loading.load_single(op,st,meta,"admin");item.update(load_operation_id=op,load_metadata=meta,scans=scans);save()
  assert loading.load_single(item["load_operation_id"],st,item["load_metadata"],"admin")==item["load_result"]
  if "departure_result"not in item:
   op="IW306.DEPART:"+str(index)+":"+ctx["tag"];item["departure_result"]=loading.depart(op,item["trip_id"],"admin");item["departure_operation_id"]=op;save()
  if "receipt_result"not in item:
   preview=receiver.preview(item["load_operation_id"],onward["final_address"],"admin")
   meta=dict(scan_place=preview["root_scan_identifier"],expected_composition_signature=preview["composition_signature"],before_cameras=True,observations=[],case_note="",scale_capture_key="",photo_ids=[],weight_act_confirmed=False,scans=[dict(scan,disposition="ACCEPTED")for scan in item["scans"]])
   op="STORE306.RECEIVE:"+str(index)+":"+ctx["tag"];item["receipt_result"]=receiver.confirm(op,item["load_operation_id"],onward["final_address"],meta,"admin");item.update(receipt_operation_id=op,receipt_metadata=meta);save()
  assert receiver.confirm(item["receipt_operation_id"],item["load_operation_id"],onward["final_address"],item["receipt_metadata"],"admin")==item["receipt_result"]
  result=reader.get(order);quantity=result["quantities"][0]
  assert quantity["shipped"]=="3"and quantity["accepted"]==str(index+1)and quantity["unreceived"]==str(2-index)and quantity["historical_transport_shortage"]=="2"and quantity["recovered_transport_quantity"]=="2"and quantity["confirmed_transport_shortage"]=="0",result
  item["delivery_snapshot"]=result;save()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sum(FACT_QTY),count(*)from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=:order_id and STATUS='SHIPPED'",order_id=order);assert q.fetchone()==(3,1)
 q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:lot_id",lot_id=ctx["lot"]);assert q.fetchone()==(6,)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS306 actual initial1 +found1+found1 three existingST/QC/LOAD/DEPART/STORE; buyeraccepted1->2->3/unreceived2->1->0/sourceFF3once/history2-found2-net0/old3keys6QR/P20H20")
