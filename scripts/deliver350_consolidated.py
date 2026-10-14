exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.transport_composition import build_transport_loading
from app.delivery_composition import build_delivery_receipt
from app.modules.delivery.infrastructure.order_delivery import OrderDelivery
from app.oracle_gateway import OracleGateway
p=Path("tmp/context348.json");saved=json.loads(p.read_text(encoding="utf-8"));source=saved["sources"][0];loading=build_transport_loading();receiver=build_delivery_receipt()
def save():p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
if "depart"not in saved:saved["depart"]=loading.depart("IW350.DEPART:"+source["tag"],source["target_trip"],"admin");save()
address=saved["parts"][source["tag"]]["onward"]["final_address"]
if "store_receipt"not in saved:
 preview=receiver.preview(saved["load_operation_id"],address,"admin");saved["store_preview"]=preview;save()
 meta=dict(scan_place=preview["root_scan_identifier"],expected_composition_signature=preview["composition_signature"],before_cameras=True,observations=[],case_note="",scale_capture_key="",photo_ids=[],weight_act_confirmed=False,scans=[dict(code,disposition="ACCEPTED")for item in saved["sources"]for unit in item.get("units",[])for code in unit["codes"]])
 op="STORE350.RECEIVE:"+source["tag"];result=receiver.confirm(op,saved["load_operation_id"],address,meta,"admin");saved.update(store_receipt=result,store_operation_id=op,store_metadata=meta);save()
assert receiver.confirm(saved["store_operation_id"],saved["load_operation_id"],address,saved["store_metadata"],"admin")==saved["store_receipt"]
saved["orders"]=[]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for item in saved["sources"]:
  st=saved["parts"][item["tag"]]["onward"]["source_st_id"]
  q.execute("select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=:st",st=st);order=q.fetchone()[0]
  q.execute("select sum(FACT_QTY),count(*)from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=:id and STATUS='SHIPPED'",id=order);assert q.fetchone()==(3,1)
  snapshot=OrderDelivery(OracleGateway()).get(order);saved["orders"].append(snapshot);assert snapshot["quantities"][0]["accepted"]=="3"and snapshot["quantities"][0]["unreceived"]=="0",snapshot
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
save()
print("PASS350 consolidated ordinaryTOP/2ST/6EA departure+store receipt, both original ordersaccepted3once/protected20-20")
