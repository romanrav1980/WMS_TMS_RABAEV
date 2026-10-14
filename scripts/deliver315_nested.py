exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.transport_composition import build_transport_loading
from app.delivery_composition import build_delivery_receipt
from app.modules.delivery.infrastructure.order_delivery import OrderDelivery
p=Path("tmp/context315.json");ctx=json.loads(p.read_text(encoding="utf-8"));source=ctx["source"]
gw=OracleGateway();loading=build_transport_loading();receiver=build_delivery_receipt();reader=OrderDelivery(gw)
def save():p.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
if "departure_result"not in ctx:ctx["departure_result"]=loading.depart("IW315.DEPART:"+source["tag"],source["target_trip"],"admin");save()
if "store_receipt_result"not in ctx:
 preview=receiver.preview(ctx["load_operation_id"],ctx["onward"]["final_address"],"admin")
 meta=dict(scan_place=preview["root_scan_identifier"],expected_composition_signature=preview["composition_signature"],before_cameras=True,observations=[],case_note="",scale_capture_key="",photo_ids=[],weight_act_confirmed=False,
  scans=[dict(code,disposition="ACCEPTED")for unit in source["units"]for code in unit["codes"]])
 op="STORE315.RECEIVE:"+source["tag"];result=receiver.confirm(op,ctx["load_operation_id"],ctx["onward"]["final_address"],meta,"admin")
 ctx.update(store_receipt_operation_id=op,store_receipt_metadata=meta,store_receipt_result=result);save()
assert receiver.confirm(ctx["store_receipt_operation_id"],ctx["load_operation_id"],ctx["onward"]["final_address"],ctx["store_receipt_metadata"],"admin")==ctx["store_receipt_result"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=:st_id",st_id=ctx["onward"]["source_st_id"]);order=q.fetchone()[0]
 q.execute("select sum(FACT_QTY),count(*)from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=:order_id and STATUS='SHIPPED'",order_id=order);assert q.fetchone()==(3,1)
 q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:lot_id",lot_id=source["lot"]);assert q.fetchone()[0]==6
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
snapshot=reader.get(order);ctx.update(order_id=order,delivery_snapshot=snapshot);save()
assert snapshot["quantities"][0]["shipped"]=="3"and snapshot["quantities"][0]["accepted"]=="3"and snapshot["quantities"][0]["unreceived"]=="0",snapshot
print("PASS315 actual nested onwardHU departure/storeaccepted3/exactrepeat/originalFFSHIPPED3once/old6codes/customer3/unreceived0/P20H20")
