exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.integrations.infrastructure.artmas_inbox import ArtmasInbox
from app.modules.integrations.infrastructure.article_master import ArticleMasterApply
from app.modules.integrations.domain.artmas import read_artmas10
from app.modules.fulfillment.infrastructure.store_orders import StoreOrders
from app.modules.fulfillment.infrastructure.legacy_preparation import LegacyPreparation
from app.modules.platform.public import read_oracle_json
from uuid import uuid4
from datetime import datetime,timezone
import xml.etree.ElementTree as ET
import time
p=Path("tmp/context271.json");assert not p.exists(),"Resume owned context271"
g=OracleGateway();tag=uuid4().hex[:10];article="QPOOL2e9b6614d9";ware=9807;old=json.loads(Path("tmp/context264.json").read_text(encoding="utf-8"))
doc=str(int(time.time()*1000000)).zfill(16)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select NAME,BARCODE_SHT,CELL,COUNT_SHT_IN_KOR,BRUTTO_WEIGHT_OF_KOR,DIMKOR_X,DIMKOR_Y,DIMKOR_Z from RRL_ARTICULS where ACTICUL=:article",article=article);original=q.fetchone()
 q.execute("select DATA_PRECISION,DATA_SCALE,COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME='RRL_ARTICULS'and COLUMN_NAME in('BRUTTO_WEIGHT_OF_KOR','DIMKOR_X','DIMKOR_Y','DIMKOR_Z')");print("MEASURE_COLUMNS",q.fetchall())
r=ET.Element("ARTMAS10");idoc=ET.SubElement(r,"IDOC");ctrl=ET.SubElement(idoc,"EDI_DC40")
for k,v in {"DOCNUM":doc,"MESTYP":"ARTMAS","IDOCTYP":"ARTMAS10","SNDPRN":"OWN.QA.SAP","CREDAT":"20261011","CRETIM":"143000"}.items():ET.SubElement(ctrl,k).text=v
def segment(name,fields):
 node=ET.SubElement(idoc,name)
 for k,v in {"MATERIAL":article,**fields}.items():ET.SubElement(node,k).text=str(v)
segment("E1BPE1MATHEAD",{"FUNCTION":"005","BASIC_VIEW":"X"})
segment("E1BPE1MARART",{"BASE_UOM":"EA"})
segment("E1BPE1MAKTRT",{"LANGU_ISO":"EN","MATL_DESC":original[0]})
segment("E1BPE1MARMRT",{"ALT_UNIT":"EA","NUMERATOR":"1","DENOMINATR":"1","EAN_UPC":original[1]})
segment("E1BPE1MARMRT",{"ALT_UNIT":"BOX","NUMERATOR":"24","DENOMINATR":"1","GROSS_WT":"10000","UNIT_OF_WT":"G","UNIT_OF_WT_ISO":"GRM","LENGTH":"40","WIDTH":"30","HEIGHT":"20","UNIT_DIM":"CM","UNIT_DIM_ISO":"CMT"})
raw=ET.tostring(r,encoding="utf-8")
received=ArtmasInbox(g).receive(read_artmas10(raw),"SAP_FILE_GATEWAY")
data={"tag":tag,"article":article,"ware":ware,"docnum":doc,"inbox_id":received["inbox_id"],"artmas_xml":raw.decode(),"original":list(original),"store":old["store"],"map_id":old["map_id"]}
p.write_text(json.dumps(data,ensure_ascii=True,default=str),encoding="utf-8")
applied=ArticleMasterApply(g).apply(received["inbox_id"],"SAP_FILE_GATEWAY");assert applied["articles_applied"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select NAME,BARCODE_SHT,CELL,COUNT_SHT_IN_KOR,BRUTTO_WEIGHT_OF_KOR,DIMKOR_X,DIMKOR_Y,DIMKOR_Z from RRL_ARTICULS where ACTICUL=:article",article=article);assert q.fetchone()==original
 q.execute("select ARTICUL,BASE_UOM,SENDER from RRL_SAP_ARTICLE_META where ARTICUL=:article",article=article);assert q.fetchone()==(article,"EA","OWN.QA.SAP")
assert ArticleMasterApply(g).apply(received["inbox_id"],"SAP_FILE_GATEWAY")==applied
svc=StoreOrders(g);svc.configure(ware,old["store"],{"utc_offset_minutes":240,"delivery_weekdays":[1,2,3,4,5,6,7],"allow_same_day":False},"admin")
order=ET.fromstring(old["raw_open"])
fields={"MessageId":"SAP271.MSG:"+tag,"OrderNumber":"SAP271.ORDER:"+tag,"WarehouseId":str(ware)}
for n in order:
 if n.tag in fields:n.text=fields[n.tag]
line=order.find("./Lines/Line");line.find("Material").text=article;line.find("Quantity").text="48"
source_raw=ET.tostring(order,encoding="utf-8")
source=svc.receive(source_raw,"SAP_FILE_GATEWAY");assert source["admission_status"]=="ACCEPTED"
data.update(order_id=source["customer_order_id"],source_xml=source_raw.decode(),source=source)
p.write_text(json.dumps(data,ensure_ascii=True,default=str),encoding="utf-8")
ready=LegacyPreparation(g).readiness(source["customer_order_id"],"admin");assert ready["ready_for_operator_layout"],ready
print("PASS271 actual assumedARTMAS10 existing syntheticSKU/native metadata+exact conversion/mmkg/legacy existing measurements unchanged/newaccepted48EA source/readonlyready/no stock or physical cargo born; continue existing preparation")
