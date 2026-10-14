exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.integrations.domain.artmas import read_artmas10
from app.modules.integrations.infrastructure.artmas_inbox import ArtmasInbox
from app.modules.integrations.infrastructure.article_master import ArticleMasterApply
from app.modules.integrations.infrastructure.supply_orders import SupplyOrders
from app.modules.fulfillment.infrastructure.store_orders import StoreOrders
from app.modules.inventory.public import convert_sap_source_quantity
from app.modules.platform.public import read_oracle_json
from datetime import datetime
from uuid import uuid4
import xml.etree.ElementTree as ET,time
p=Path("tmp/context273.json");assert not p.exists(),"Resume own source273, no new quantities"
source=json.loads(Path("tmp/context271.json").read_text(encoding="utf-8"));old=json.loads(Path("tmp/context264.json").read_text(encoding="utf-8"));tag=uuid4().hex[:10];article=source["article"];ware=source["ware"];g=OracleGateway()
root=ET.Element("ARTMAS10");idoc=ET.SubElement(root,"IDOC");ctrl=ET.SubElement(idoc,"EDI_DC40");doc=str(int(time.time()*1000000))
for k,v in {"DOCNUM":doc,"MESTYP":"ARTMAS","IDOCTYP":"ARTMAS10","SNDPRN":"OWN.QA.SAP","CREDAT":"20261011","CRETIM":"151000"}.items():ET.SubElement(ctrl,k).text=v
for name,fields in [("E1BPE1MATHEAD",{"BASIC_VIEW":"X"}),("E1BPE1MARMRT",{"ALT_UNIT":"CS","NUMERATOR":"1","DENOMINATR":"3"})]:
 node=ET.SubElement(idoc,name)
 for k,v in {"MATERIAL":article,**fields}.items():ET.SubElement(node,k).text=v
inbox=ArtmasInbox(g).receive(read_artmas10(ET.tostring(root,encoding="utf-8")),"SAP_FILE_GATEWAY")
ArticleMasterApply(g).apply(inbox["inbox_id"],"SAP_FILE_GATEWAY")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select UNITS_JSON from RRL_SAP_ARTICLE_META where ARTICUL=:article",article=article);units=read_oracle_json(q.fetchone()[0])
 q.callproc("RRL_STORE_ORDER_SCOPE.begin_source",["admin","sap_supply_import",ware,None])
 try:
  assert convert_sap_source_quantity(q,article,"CS","3","EA",units)==1
  assert convert_sap_source_quantity(q,article,"CS","144","EA",units)==48
  try:convert_sap_source_quantity(q,article,"CS","1","EA",units)
  except ValueError:pass
  else:raise AssertionError("Fractional piece source")
 finally:q.callproc("RRL_STORE_ORDER_SCOPE.end_source");c.rollback()
 q.execute("select CELL from RRL_CELLS where WARE_ID=:ware and nvl(BLOCKED_FOR_ACCEPT,0)=0 order by CELL fetch first 1 rows only",ware=ware);cell=q.fetchone()[0]
r=ET.Element("WarehouseSupplyOrder",version="1")
for k,v in {"Sender":"OWN.QA.SAP","MessageId":"SUP273.MSG:"+tag,"OrderNumber":"SUP273:"+tag,"Revision":"1","WarehouseId":str(ware),"ReceiveCell":cell,"Supplier":"Own273 rational source fixture"}.items():ET.SubElement(r,k).text=v
line=ET.SubElement(ET.SubElement(r,"Lines"),"Line");ET.SubElement(line,"LineNumber").text="1";ET.SubElement(line,"Material").text=article;ET.SubElement(line,"Quantity",unit="CS").text="3"
raw=ET.tostring(r,encoding="utf-8");supplies=SupplyOrders(g);result=supplies.receive(raw,"SAP_FILE_GATEWAY")
store=ET.fromstring(source["source_xml"])
for n in store:
 if n.tag=="MessageId":n.text="ST273.MSG:"+tag
 elif n.tag=="OrderNumber":n.text="ST273.ORDER:"+tag
line=store.find("./Lines/Line");line.find("Quantity").set("unit","CS");line.find("Quantity").text="144"
store_result=StoreOrders(g).receive(ET.tostring(store,encoding="utf-8"),"SAP_FILE_GATEWAY")
data={"tag":tag,"ware":ware,"article":article,"supply":result,"supply_raw":raw.decode(),"store":store_result,"inbox_id":inbox["inbox_id"]}
p.write_text(json.dumps(data,ensure_ascii=True),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PLANNED_QTY,SOURCE_QTY,SOURCE_UOM,BASE_UOM from RRL_SAP_SUPPLY_LINE where ORDER_ID=:order_id",order_id=result["order_id"]);assert q.fetchone()==(1,3,"CS","EA")
 q.execute("select ORDER_QTY,UNIT_CODE from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=:order_id",order_id=store_result["customer_order_id"]);assert q.fetchone()==(48,"EA")
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
assert supplies.receive(raw,"SAP_FILE_GATEWAY")["order_id"]==result["order_id"]
print("PASS273 native rational1/3 policy source3CS->1EA/store144CS->48EA/fractional1CS denied/sharedCFG/sourcewide leastprivileged service/original quantities kept/no stock born; currenthuman cached warehouse rights next")
