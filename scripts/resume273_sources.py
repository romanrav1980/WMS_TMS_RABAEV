exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.integrations.infrastructure.supply_orders import SupplyOrders
from app.modules.fulfillment.infrastructure.store_orders import StoreOrders
from uuid import uuid4
import xml.etree.ElementTree as ET
p=Path("tmp/context273.json");assert not p.exists(),"Resume already created sources"
source=json.loads(Path("tmp/context271.json").read_text(encoding="utf-8"));tag=uuid4().hex[:10];article=source["article"];ware=source["ware"];g=OracleGateway()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select NUMERATOR,DENOMINATOR from RRL_STOCK_UOM_CONVERSION where ARTICUL=:article and INPUT_UOM='CS'order by POLICY_VERSION desc fetch first 1 rows only",article=article);assert q.fetchone()==(1,3)
 q.execute("select DEFAULT_RECEIVE_CELL from RRL_WARES where ID=:ware",ware=ware);prior_default=q.fetchone()[0]
 assert prior_default is None,"Do not replace existing receiving configuration"
 q.execute("select BLOCKED_FOR_ACCEPT from RRL_CELLS where CELL='CPT_9807'and WARE_ID=:ware",ware=ware);assert q.fetchone()==(0,)
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:q.execute("update RRL_WARES set DEFAULT_RECEIVE_CELL='CPT_9807'where ID=:ware",ware=ware);c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
r=ET.Element("WarehouseSupplyOrder",version="1")
for k,v in {"Sender":"OWN.QA.SAP","MessageId":"SUP273.MSG:"+tag,"OrderNumber":"SUP273:"+tag,"Revision":"1","WarehouseId":str(ware),"ReceiveCell":"CPT_9807","Supplier":"Own273 rational source fixture"}.items():ET.SubElement(r,k).text=v
line=ET.SubElement(ET.SubElement(r,"Lines"),"Line");ET.SubElement(line,"LineNumber").text="1";ET.SubElement(line,"Material").text=article;ET.SubElement(line,"Quantity",unit="CS").text="3"
raw=ET.tostring(r,encoding="utf-8");supplies=SupplyOrders(g);result=supplies.receive(raw,"SAP_FILE_GATEWAY")
data={"tag":tag,"ware":ware,"article":article,"supply":result,"supply_raw":raw.decode(),"prior_default_receiving":prior_default,"configured_receiving":"CPT_9807"}
p.write_text(json.dumps(data,ensure_ascii=True),encoding="utf-8")
store=ET.fromstring(source["source_xml"])
for n in store:
 if n.tag=="MessageId":n.text="ST273.MSG:"+tag
 elif n.tag=="OrderNumber":n.text="ST273.ORDER:"+tag
line=store.find("./Lines/Line");line.find("Quantity").set("unit","CS");line.find("Quantity").text="144"
store_raw=ET.tostring(store,encoding="utf-8");store_result=StoreOrders(g).receive(store_raw,"SAP_FILE_GATEWAY");data.update(store=store_result,store_raw=store_raw.decode());p.write_text(json.dumps(data,ensure_ascii=True),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PLANNED_QTY,SOURCE_QTY,SOURCE_UOM,BASE_UOM from RRL_SAP_SUPPLY_LINE where ORDER_ID=:order_id",order_id=result["order_id"]);assert q.fetchone()==(1,3,"CS","EA")
 q.execute("select ORDER_QTY,UNIT_CODE from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=:order_id",order_id=store_result["customer_order_id"]);assert q.fetchone()==(48,"EA")
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
assert supplies.receive(raw,"SAP_FILE_GATEWAY")["order_id"]==result["order_id"]
print("PASS273 same published CS1/3/rational supply3->1/store144->48/original raw units preserved/current gateway sharedCFG/no stock born. Owned9807 receiving config CPT explicitly set, blocked allocation remains.")
