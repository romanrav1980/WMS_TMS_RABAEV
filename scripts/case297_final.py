exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.domain.mark_identity import normalize_unit_scan_codes
from concurrent.futures import ThreadPoolExecutor
import uuid,httpx
base="http://127.0.0.1:8088/api/delivery/store-receipts/confirm"
for number in[291,292]:
 ctx=json.loads(Path("tmp/context"+str(number)+".json").read_text());onward=json.loads(Path("tmp/context296_"+str(number)+".json").read_text());preview=json.loads(Path("tmp/preview297_"+str(number)+".json").read_text());path=Path("tmp/context297_"+str(number)+".json")
 saved=json.loads(path.read_text())if path.exists()else None
 if saved is None:
  body=dict(load_operation_id=onward["load_operation_id"],store_address=onward["onward_result"]["final_address"],scan_place=preview["root_scan_identifier"],expected_composition_signature=preview["composition_signature"],before_cameras=True,observations=[],case_note="",scale_capture_key="",photo_ids=[],weight_act_confirmed=False)
  scans=[]
  if number==292:
   with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
    q=c.cursor();q.execute("select UNIT_ID from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id",lot_id=preview["root"]);ids={r[0]for r in q}
   scans=[dict(code,disposition="ACCEPTED")for u in ctx["units"]if u["unit_id"]in ids for code in u["codes"]];assert len(scans)==2
  body["scans"]=scans
  with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
   q=c.cursor();out=q.var(oracledb.DB_TYPE_CLOB);metadata={k:v for k,v in body.items()if k not in["load_operation_id","store_address","scans"]}
   if scans:
    normalized=normalize_unit_scan_codes([{k:v for k,v in x.items()if k!="disposition"}for x in scans])
    metadata["unit_scans"]=[dict(x,disposition="ACCEPTED")for x in normalized]
   req=dict(contract_version=2,operation_id="STORE297.ROLL:"+uuid.uuid4().hex,command_type="STORE_RECEIPT",actor="admin",source=dict(load_operation_id=body["load_operation_id"],store_address=body["store_address"]),lines=[],units=[],metadata=metadata)
   try:
    q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(req),"admin",out,None])
    if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
    result=read_oracle_json(out.getvalue());c.rollback();q.execute("select count(*)from RRL_STORE_RECEIPT_FACT where LOAD_OPERATION_ID=:op_id",op_id=body["load_operation_id"]);assert q.fetchone()==(0,)
   finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  bodies=[dict(body,operation_id="STORE297.RECEIVE:"+uuid.uuid4().hex)for _ in range(2)]
  def send(b):
   with httpx.Client(auth=("admin","admin123"),timeout=30)as h:
    r=h.post(base,json=b);return b,r.status_code,r.json()
  with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(send,bodies))
  assert sorted(x[1]for x in results)==[200,409],results
  win=next(x for x in results if x[1]==200);saved=dict(body=win[0],result=win[2]);path.write_text(json.dumps(saved,indent=2),encoding="utf-8")
 with httpx.Client(auth=("admin","admin123"),timeout=30)as h:
  r=h.post(base,json=saved["body"]);assert r.status_code==200 and r.json()==saved["result"],r.text
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();q.execute("select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=:source_st",source_st=onward["onward_result"]["source_st_id"]);order=q.fetchone()[0]
  with httpx.Client(auth=("admin","admin123"),timeout=30)as h:
   r=h.get("http://127.0.0.1:8088/api/customer-orders/"+str(order)+"/delivery");assert r.status_code==200,r.text
   x=r.json();assert x["quantities"][0]["shipped"]=="3"and x["quantities"][0]["accepted"]=="1"and x["quantities"][0]["unreceived"]=="2",x
   saved["order_id"]=order;saved["delivery_snapshot"]=x;path.write_text(json.dumps(saved,indent=2),encoding="utf-8")
print("PASS297 REUSED final STORE receipt exactactual1 ordinary+marked 2QR/rollback/race/replay/original shipped3 accepted1 unreceived2/no repeated FF")
