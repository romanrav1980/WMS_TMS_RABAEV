exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from concurrent.futures import ThreadPoolExecutor
import uuid,httpx
base="http://127.0.0.1:8088/api/inventory/interwarehouse"
with httpx.Client(auth=("admin","admin123"),timeout=30)as h:
 for number in[291,292]:
  p=Path("tmp/context300_"+str(number)+".json");ctx=json.loads(p.read_text(encoding="utf-8"))
  body={k:v for k,v in ctx["body"].items()if k!="unit_scans"};body["approval_operation_id"]=ctx["approval_operation_id"];body["scans"]=ctx["scans"]
  if "actual_body"not in ctx:
   if number==292:
    incomplete=dict(body,operation_id="IW300.INCOMPLETE:"+uuid.uuid4().hex,scans=ctx["scans"][:-1])
    r=h.post(base+"/recovery-receipts",json=incomplete);assert r.status_code==409,r.text
   bodies=[dict(body,operation_id="IW300.RECEIVE:"+uuid.uuid4().hex),dict(body,operation_id="IW300.RECEIVE:"+uuid.uuid4().hex,receipt_pallet_identifier=body["receipt_pallet_identifier"]+"L",scan_pallet=body["scan_pallet"]+"L")]
   def send(b):
    with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
     r=client.post(base+"/recovery-receipts",json=b);return b,r.status_code,r.json()
   with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(send,bodies))
   assert sorted(x[1]for x in results)==[200,409],results
   win=next(x for x in results if x[1]==200);ctx["actual_body"]=win[0];ctx["receipt_result"]=win[2];p.write_text(json.dumps(ctx,ensure_ascii=False,indent=2),encoding="utf-8")
  r=h.post(base+"/recovery-receipts",json=ctx["actual_body"]);assert r.status_code==200 and r.json()==ctx["receipt_result"],r.text
  r=h.post(base+"/recovery-receipts",json=dict(ctx["actual_body"],quantity="1"));assert r.status_code==409,r.text
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for number in[291,292]:
  ctx=json.loads(Path("tmp/context300_"+str(number)+".json").read_text(encoding="utf-8"));lot=ctx["receipt_result"]["pallet_identifier"]
  q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=lot);assert q.fetchone()==(2,0)
  q.execute("select count(*)from RRL_INTERWARE_RECOVERY_UNIT where RECOVERY_OPERATION_ID=:op_id",op_id=ctx["actual_body"]["operation_id"]);assert q.fetchone()==(2 if number==292 else 0,)
  if number==292:
   q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id and STOCK_STATUS='AVAILABLE'",lot_id=lot);assert q.fetchone()==(2,2)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS300 actual ordinary+marked recovered2/newUID/receivingcell/P2H0/same2units-codes/no birth/QRmissingdenied/race200-409/replay/collision/protected20-20")
