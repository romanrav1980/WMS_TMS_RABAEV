exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
import uuid,httpx
from concurrent.futures import ThreadPoolExecutor
base="http://127.0.0.1:8088/api/inventory/interwarehouse"
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 for number in[291,292]:
  p=Path("tmp/context295_"+str(number)+".json");ctx=json.loads(p.read_text(encoding="utf-8"))
  body=dict(ctx["metadata"],request_operation_id=ctx["request_operation_id"])
  if "confirmation_operation_id"not in ctx:
   def send(b):
    with httpx.Client(auth=("admin","admin123"),timeout=30)as session:
     r=session.post(base+"/shortage-confirmations",json=b);return b,r.status_code,r.json()
   bodies=[dict(body,operation_id="IW295.CONFIRM:"+uuid.uuid4().hex)for _ in range(2)]
   with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(send,bodies))
   assert sorted(x[1]for x in results)==[200,409],results
   win=next(x for x in results if x[1]==200);ctx["confirmation_operation_id"]=win[0]["operation_id"];ctx["confirmation_result"]=win[2]
   p.write_text(json.dumps(ctx,ensure_ascii=False,indent=2),encoding="utf-8")
  body["operation_id"]=ctx["confirmation_operation_id"]
  r=client.post(base+"/shortage-confirmations",json=body);assert r.status_code==200 and r.json()==ctx["confirmation_result"],r.text
  r=client.post(base+"/shortage-confirmations",json=dict(body,quantity="1"));assert r.status_code==409,r.text
  r=client.get(base+"/receipts/"+ctx["receipt_operation_id"]+"/shortage");assert r.status_code==200,r.text
  result=r.json();assert result["loss_confirmed"]and result["short_quantity"]=="2"and not result["carrier_custody_released"],result
  assert len(result["missing_units"])==(2 if number==292 else 0)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select count(*)from RRL_INTERWARE_SHORTAGE_FACT");assert q.fetchone()==(2,)
 q.execute("select count(*)from RRL_INTERWARE_SHORTAGE_UNIT");assert q.fetchone()==(2,)
 for number in[291,292]:
  ctx=json.loads(Path("tmp/context"+str(number)+".json").read_text(encoding="utf-8"))
  q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=ctx["receipt_result"]["pallet_identifier"]);assert q.fetchone()==(1,0)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS295 actual ordinary+marked independent confirm/native core/concurrent200-409/exactreplay/collision/confirmed2/P1/no duplicate deduction/custody stillopen/protected20-20")
