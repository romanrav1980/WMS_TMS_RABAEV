exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.fulfillment.infrastructure.store_orders import StoreOrders
from app.modules.fulfillment.infrastructure.legacy_preparation import LegacyPreparation
from app.modules.fulfillment.domain.preparation_quantities import pallet_share
from app.modules.fulfillment.api.store_order_routes import PreparationRequest
from decimal import Decimal as D
import xml.etree.ElementTree as ET
from uuid import uuid4
g=OracleGateway();p=Path("tmp/context277.json")
assert pallet_share(D(24),D(72),D(3),D(30))==(1,D(10))
try:pallet_share(D(12),D(72),D(3),D(30))
except ValueError:pass
else:raise AssertionError("Half a package accepted")
data=json.loads(p.read_text(encoding="utf-8"))if p.exists()else {"tag":uuid4().hex[:10]}
if "source"not in data:
 old=json.loads(Path("tmp/context271.json").read_text(encoding="utf-8"));root=ET.fromstring(old["source_xml"])
 root.find("MessageId").text="ST277.MSG:"+data["tag"];root.find("OrderNumber").text="ST277.ORDER:"+data["tag"]
 root.find("./Lines/Line/Quantity").text="72"
 data["raw"]=ET.tostring(root,encoding="unicode");data["source"]=StoreOrders(g).receive(data["raw"].encode(),"SAP_FILE_GATEWAY")
 data["article"]=old["article"];data["body"]={"operation_id":"PREP277:"+data["tag"],"pallets":[{"lines":[{"articul":old["article"],"quantity":"24"}]}for _ in range(3)]}
 p.write_text(json.dumps(data),encoding="utf-8")
order=data["source"]["customer_order_id"];body=PreparationRequest.model_validate(data["body"]).model_dump(mode="json")
if "result"not in data:
 with g.transaction("Own277 exact thirds outer rollback")as q:
  class Bound:
   def transaction(self,label):
    from contextlib import contextmanager
    @contextmanager
    def use():yield q
    return use()
  try:
   r=LegacyPreparation(Bound()).prepare(order,body,"admin");assert len(r["pallet_identifiers"])==3
  finally:q.connection.rollback()
 data["result"]=LegacyPreparation(g).prepare(order,body,"admin");p.write_text(json.dumps(data),encoding="utf-8")
r=LegacyPreparation(g).prepare(order,body,"admin");assert r["idempotent"]and len(r["pallet_identifiers"])==3
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select QUANTITY,PACK_COUNT,ORDER_WEIGHT from RRL_SBORKA_PALLET_ROWS where DOCID=:st_number order by PALLET_UID",st_number=r["st_number"]);assert q.fetchall()==[(24,1,10)]*3
 q.execute("select ORDER_QTY from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=:order_id",order_id=order);assert q.fetchone()==(72,)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3),substr(SQL_TEXT,1,100)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and executions>0 and SQL_TEXT not like '%V$SQL%'
 and(SQL_TEXT like '%RRL_SBORKA_PALLET_ROWS_ADD4%'or SQL_TEXT like '%ORDERS.ADD_ORDER_ROW%')
 order by last_active_time desc fetch first 4 rows only""");print("SQL277_MS",json.dumps(q.fetchall()))
print("PASS277 actual source72EA -> original3planned pallets each24EA/1box/10kg; exact one-third; original outer rollback/replay/source72/P20H20; no stock birth")
