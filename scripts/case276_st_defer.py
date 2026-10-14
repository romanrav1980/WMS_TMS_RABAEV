exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.trip_edit import create_existing_trip,update_existing_trip
from app.modules.transport.infrastructure.st_deferral import StDeferral
from datetime import date
from concurrent.futures import ThreadPoolExecutor
import httpx,uuid
g=OracleGateway(); service=StDeferral(g); p=Path("tmp/context276.json")
data=json.loads(p.read_text(encoding="utf-8"))if p.exists()else {"tag":uuid.uuid4().hex[:10],"st":"SAP_2046","source_trip":33571}
if "target_trip"not in data:
 data["target_trip"]=create_existing_trip(g,"15",date(2026,11,4),"admin");p.write_text(json.dumps(data),encoding="utf-8")
 update_existing_trip(g,data["target_trip"],{"transport":"QC241ede877f6d1","primechanie":"Own276 reasoned unpicked ST deferral. Planning only."},"admin")
if "body"not in data:
 ctx=service.context(data["st"],"admin")
 assert ctx["source_trip_id"]==33571 and len(ctx["members"])==2 and len(ctx["cargo"])==2,ctx
 data["context"]=ctx
 data["body"]={"st_number":data["st"],"target_trip_id":data["target_trip"],"expected_version":ctx["version"],"source_hash":ctx["source_hash"],"reason":"Own276 transport rescheduling","reference":"OWN276:"+data["tag"]}
 data["operation"]="ST276:"+data["tag"];p.write_text(json.dumps(data),encoding="utf-8")
# Original reassignment and journal share this cursor and outer rollback.
if "result"not in data:
 with g.transaction("Own276 complete metadata outer rollback")as q:
  class Bound:
   def transaction(self,label):
    from contextlib import contextmanager
    @contextmanager
    def use():yield q
    return use()
  try:
   result=StDeferral(Bound()).defer(data["operation"],data["body"],"admin")
   assert result["version"]==1 and not result["stock_changed"]
  finally:q.connection.rollback()
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();q.execute("select count(*)from RRL_ST_DEFER_DECISION where OPERATION_ID=:operation_id",operation_id=data["operation"]);assert q.fetchone()==(0,)
  q.execute("select count(*)from RRL_SBORKA_PALLETS where ST_NUMBER=:st_number and TRANSTASK_ID=33571",st_number=data["st"]);assert q.fetchone()==(2,)
 body=dict(data["body"],operation_id=data["operation"])
 def send(op):
  with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
   return client.post("http://127.0.0.1:8088/api/transport/st-deferrals",json=dict(body,operation_id=op))
 with ThreadPoolExecutor(max_workers=2)as pool:
  replies=list(pool.map(send,[data["operation"],data["operation"]+".race"]))
 assert sorted(r.status_code for r in replies)==[200,409],[(r.status_code,r.text)for r in replies]
 winner=next(r.json()for r in replies if r.status_code==200)
 data["operation"]=winner["operation_id"];data["result"]=winner;p.write_text(json.dumps(data),encoding="utf-8")
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 body=dict(data["body"],operation_id=data["operation"])
 replay=client.post("http://127.0.0.1:8088/api/transport/st-deferrals",json=body);assert replay.status_code==200 and replay.json()==data["result"],replay.text
 collision=client.post("http://127.0.0.1:8088/api/transport/st-deferrals",json=dict(body,reason="Changed original reason"));assert collision.status_code==409,collision.text
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from RRL_SBORKA_PALLETS where ST_NUMBER=:st_number and TRANSTASK_ID=:trip_id",st_number=data["st"],trip_id=data["target_trip"]);assert q.fetchone()==(2,)
 q.execute("select sum(QUANTITY),sum(ORDER_WEIGHT),sum(PACK_COUNT)from RRL_SBORKA_PALLET_ROWS where DOCID=:st_number",st_number=data["st"]);assert q.fetchone()==(48,20,2)
 q.execute("select ORDER_QTY from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=2046");assert q.fetchone()==(48,)
 q.execute("select count(*),sum(FACT_QTY),min(STATUS),max(STATUS)from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=2046");assert q.fetchone()==(2,0,"PLANNED","PLANNED")
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
assert data["result"]["original_shipping_date"]=="2026-11-03"and data["result"]["target_shipping_date"]=="2026-11-04"
print("PASS276 original unassign/reassign atomic rollback; concurrent one winner; exact replay/collision; source48 immutable; planned2 zeroFact; protected P20H20; promise Nov3 retained vs target Nov4")
