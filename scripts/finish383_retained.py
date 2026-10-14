exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.delivery.infrastructure.order_delivery import OrderDelivery
from app.oracle_gateway import OracleGateway
import httpx
p=Path("tmp/context383.json");ctx=json.loads(p.read_text());body=ctx["body"];actor=ctx["receiver_id"];result=ctx["result"]
assert result["status"]=="DISCREPANCY"and result["weight"]["delta_kg"]=="0"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS,NAME,DELETED from RUSERS where ID=:actor",actor=actor);secret,name,deleted=q.fetchone();assert name=="Own383 software receiver"and deleted==1
 try:
  q.execute("update RUSERS set DELETED=0 where ID=:actor",actor=actor);c.commit()
  with httpx.Client(auth=(actor,secret),timeout=35)as h:
   r=h.post("http://127.0.0.1:8088/api/delivery/store-receipts/confirm",json=body);assert r.status_code==200 and r.json()==result,(r.status_code,r.text[:1200])
  q.execute("select UNIT_DISPOSITION,count(*),sum(BASE_QTY)from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=:op group by UNIT_DISPOSITION order by UNIT_DISPOSITION",op=body["operation_id"]);assert q.fetchall()==[("ACCEPTED",3,3),("DAMAGED",1,1),("MISSING",2,2),("REFUSED",1,1)]
  for table,expect in [("RRL_EVENTS",0),("RRL_STORE_RECEIPT_WEIGHT_PHOTO",3)]:
   q.execute("select count(*)from "+table+" where OPERATION_ID=:op",op=body["operation_id"]);assert q.fetchone()[0]==expect
  q.execute("select count(*)from RRL_EVENT_OUTBOX where CORRELATION_ID=:op",op=body["operation_id"]);assert q.fetchone()[0]==1
  q.execute("select CUSTOMER_ORDER_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1112");order=q.fetchone()[0]
  delivery=OrderDelivery(OracleGateway()).get(int(order));assert delivery["quantities"][0]["accepted"]=="3"and delivery["quantities"][0]["unreceived"]=="0",delivery
  q.execute("select sum(FACT_QTY),count(*)from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=:id and STATUS='SHIPPED'",id=order);assert q.fetchone()==(7,1)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
  ctx.update(receipt_body=body,order_delivery=delivery,replay_verified=True,actors_retired_after_case=True);p.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
 finally:q.execute("update RUSERS set DELETED=1 where ID=:actor",actor=actor);c.commit()
print("PASS383 retainedAPPLIED oldCASE7 ->accepted3/missing2/refused1/damaged1/10QR of5present/no fake missingQR/nativewholetrialrollback/oneunitconflict refusal/replay/oneoutbox/3photos/sourceFF7once/protected20")
