exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.delivery.infrastructure.order_delivery import OrderDelivery
from app.delivery_composition import build_delivery_receipt
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.domain.mark_identity import normalize_unit_scan_codes
from app.modules.delivery.domain.receipt_totals import combine_receipts
from decimal import Decimal
import uuid
gw=OracleGateway();service=build_delivery_receipt();reader=OrderDelivery(gw)
for number in [291,292]:
 ctx=json.loads(Path("tmp/context"+str(number)+".json").read_text(encoding="utf-8"));onward=json.loads(Path("tmp/context302_"+str(number)+".json").read_text(encoding="utf-8"));original=json.loads(Path("tmp/context297_"+str(number)+".json").read_text(encoding="utf-8"));p=Path("tmp/context303_"+str(number)+".json");saved=json.loads(p.read_text(encoding="utf-8"))if p.exists()else {}
 if "result"not in saved:
  before=reader.get(original["order_id"]);quantity=before["quantities"][0]
  assert quantity["shipped"]=="3"and quantity["accepted"]=="1"and quantity["unreceived"]=="2"and quantity["historical_transport_shortage"]=="2"and quantity["recovered_transport_quantity"]=="2"and quantity["confirmed_transport_shortage"]=="0",before
  address=onward["prepared"]["final_address"];preview=service.preview(onward["load_operation_id"],address,"admin")
  meta=dict(scan_place=preview["root_scan_identifier"],expected_composition_signature=preview["composition_signature"],before_cameras=True,observations=[],case_note="",scale_capture_key="",photo_ids=[],weight_act_confirmed=False)
  scans=[]
  if number==292:
   with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
    q=c.cursor();q.execute("select UNIT_ID from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id",lot_id=preview["root"]);ids={r[0]for r in q}
   scans=[dict(code,disposition="ACCEPTED")for u in ctx["units"]if u["unit_id"]in ids for code in u["codes"]];assert len(scans)==4
   meta["scans"]=scans
  native=dict(meta);native.pop("scans",None)
  if scans:native["unit_scans"]=normalize_unit_scan_codes(scans)
  with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
   q=c.cursor();out=q.var(oracledb.DB_TYPE_CLOB)
   req=dict(contract_version=2,operation_id="STORE303.ROLL:"+uuid.uuid4().hex,command_type="STORE_RECEIPT",actor="admin",source=dict(load_operation_id=onward["load_operation_id"],store_address=address),lines=[],units=[],metadata=native)
   try:
    q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(req),"admin",out,None])
    if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
    result=read_oracle_json(out.getvalue());c.rollback();q.execute("select count(*)from RRL_STORE_RECEIPT_FACT where LOAD_OPERATION_ID=:load_id",load_id=onward["load_operation_id"]);assert q.fetchone()==(0,)
   finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  op="STORE303.RECEIVE:"+str(number)+":"+ctx["tag"];result=service.confirm(op,onward["load_operation_id"],address,meta,"admin")
  saved=dict(operation_id=op,load_operation_id=onward["load_operation_id"],store_address=address,metadata=meta,result=result,order_id=original["order_id"]);p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
 assert service.confirm(saved["operation_id"],saved["load_operation_id"],saved["store_address"],saved["metadata"],"admin")==saved["result"]
 result=reader.get(saved["order_id"]);quantity=result["quantities"][0]
 assert quantity["shipped"]=="3"and quantity["accepted"]=="3"and quantity["unreceived"]=="0"and quantity["confirmed_transport_shortage"]=="0"and quantity["historical_transport_shortage"]=="2"and quantity["recovered_transport_quantity"]=="2",result
 assert result["delivery_status"]=="RECEIVED_SHIPPED_VOLUME"and len(result["receipt_lineage"])==2,result
 saved["delivery_snapshot"]=result;p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();q.execute("select sum(FACT_QTY),count(*)from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=:order_id and STATUS='SHIPPED'",order_id=saved["order_id"]);assert q.fetchone()==(3,1)
  q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:op_id",op_id=saved["operation_id"]);assert q.fetchone()==(0,)
original=reader.get(2030);assert original["quantities"][0]["accepted"]=="3"and original["quantities"][0]["historical_transport_shortage"]=="0"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS303 actual finaloriginalSTORE_RECEIPT found2/ordinary+marked4QR/rollback/replay/original FF shipped3 once/buyer1+2=3/unreceived0/history2+found2 preserved/no stockevent/protected20-20")
