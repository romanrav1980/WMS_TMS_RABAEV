exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.fulfillment.infrastructure.legacy_preparation import LegacyPreparation
from app.modules.fulfillment.api.store_order_routes import PreparationRequest
from app.modules.transport.infrastructure.trip_edit import create_existing_trip,update_existing_trip
from app.modules.transport.infrastructure.plan_application import assign_validated_sts
from datetime import date
import httpx
p=Path("tmp/context271.json");data=json.loads(p.read_text(encoding="utf-8"));g=OracleGateway();service=LegacyPreparation(g)
body=data.get("preparation_body")or {"operation_id":"SAP271.PREP:"+data["tag"],"pallets":[{"lines":[{"articul":data["article"],"quantity":"24"}]},{"lines":[{"articul":data["article"],"quantity":"24"}]}]}
data["preparation_body"]=body;p.write_text(json.dumps(data,ensure_ascii=True),encoding="utf-8")
canonical_body=PreparationRequest.model_validate(body).model_dump(mode="json")
# Existing preparation writers must roll back together, even before saved publication.
with g.transaction("Own271 outer rollback entire original SAP preparation")as q:
 from app.transaction_gateway import TransactionGateway
 # The existing adapter expects a source transaction; use a gateway facade bound to this exact cursor.
 class CursorGateway:
  def transaction(self,label):
   from contextlib import contextmanager
   @contextmanager
   def use():
    yield q
   return use()
 try:
  result=LegacyPreparation(CursorGateway()).prepare(data["order_id"],canonical_body,"admin")
  assert len(result["pallet_identifiers"])==2
 finally:
  q.connection.rollback()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from RRL_SBORKA_PALLETS where ST_NUMBER=:st_number",st_number="SAP_"+str(data["order_id"]));assert q.fetchone()==(0,)
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 r=client.post(f"http://127.0.0.1:8088/api/integrations/sap/store-orders/{data['order_id']}/prepare-st",json=body)
 assert r.status_code==200,r.text
 result=r.json();assert len(result["pallet_identifiers"])==2
 data["prepared"]=result;p.write_text(json.dumps(data,ensure_ascii=True),encoding="utf-8")
 again=client.post(f"http://127.0.0.1:8088/api/integrations/sap/store-orders/{data['order_id']}/prepare-st",json=body)
 assert again.status_code==200 and again.json()["pallet_identifiers"]==result["pallet_identifiers"]
trip=data.get("trip")
if not trip:
 trip=create_existing_trip(g,"15",date(2026,11,3),"admin");data["trip"]=trip;p.write_text(json.dumps(data,ensure_ascii=True),encoding="utf-8")
 update_existing_trip(g,trip,{"transport":"QC241ede877f6d1","primechanie":"Own271 assumed SAP source -> original two-pallet preparation. Planning only; not physical or legal dispatch."},"admin")
assigned=assign_validated_sts(g,trip,[result["st_number"]],"admin");assert assigned["written_sts"]==1
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from RRL_SBORKA_PALLETS where ST_NUMBER=:st_number and TRANSTASK_ID=:trip_id",st_number=result["st_number"],trip_id=trip);assert q.fetchone()==(2,)
 q.execute("select sum(QUANTITY),sum(ORDER_WEIGHT),sum(PACK_COUNT)from RRL_SBORKA_PALLET_ROWS where DOCID=:st_number",st_number=result["st_number"]);assert q.fetchone()==(48,20,2)
 q.execute("select count(*),sum(FACT_QTY),min(STATUS),max(STATUS)from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=:order_id",order_id=data["order_id"]);assert q.fetchone()==(2,0,"PLANNED","PLANNED")
 q.execute("select ORDER_QTY from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=:order_id",order_id=data["order_id"]);assert q.fetchone()==(48,)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS271 actual assumedARTMAS -> source48 -> originalORDERS/SBORKA2pallets -> existing native assignment/current2PLANNED zeroFact/source48 immutable/outer rollback/replay/P20H20/no stock birth; independent and realSAP contract not certified")
