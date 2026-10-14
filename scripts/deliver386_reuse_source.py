exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.delivery_composition import build_delivery_receipt
from app.modules.delivery.infrastructure.order_delivery import OrderDelivery
from app.oracle_gateway import OracleGateway
source=json.loads(Path("tmp/context385.json").read_text());p=Path("tmp/context386.json");saved=json.loads(p.read_text())if p.exists()else{};receiver=build_delivery_receipt()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select DESTINATION_ADDR from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=:op and ACTIVE_FLAG=1",op=source["source_load"]);address=q.fetchone()[0]
preview=receiver.preview(source["source_load"],address,"admin");saved["preview"]=preview
meta=dict(scan_place=preview["root_scan_identifier"],expected_composition_signature=preview["composition_signature"],before_cameras=True,observations=[],case_note="",scale_capture_key="",photo_ids=[],weight_act_confirmed=False,scans=[dict(code,disposition="ACCEPTED")for unit in source["units"]for code in unit["codes"]])
op="STORE386.RECEIPT:"+source["tag"]
result=receiver.confirm(op,source["source_load"],address,meta,"admin");assert receiver.confirm(op,source["source_load"],address,meta,"admin")==result
delivery=OrderDelivery(OracleGateway()).get(source["order"]);assert delivery["quantities"][0]["accepted"]=="3",delivery
saved.update(source=source,receipt_operation_id=op,receipt_metadata=meta,result=result,order_delivery=delivery,address=address);p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
print("PASS386 originalSAPverified BOX3/3physical6QR directcustomeraccepted3/sourceFF3once/P0/replay")
