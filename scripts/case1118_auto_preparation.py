"""One resumable isolated automatic ST case, no physical stock or original fixture changes."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.oracle_gateway import OracleGateway
from app.transaction_gateway import TransactionGateway
from app.modules.integrations.infrastructure.artmas_inbox import ArtmasInbox
from app.modules.integrations.infrastructure.article_master import ArticleMasterApply
from app.modules.integrations.domain.artmas import read_artmas10
from app.modules.fulfillment.infrastructure.store_orders import StoreOrders
from app.modules.fulfillment.infrastructure.legacy_preparation import LegacyPreparation
from app.modules.fulfillment.api.preparation_read_routes import AutoPreparationRequest
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as ET
import time,copy
g=OracleGateway();service=LegacyPreparation(g);p=Path("tmp/context1118.json")
data=json.loads(p.read_text(encoding="utf-8"))if p.exists()else {"tag":uuid4().hex[:10],"phase":"INIT","doc":str(int(time.time()*1000000))}
def save():p.write_text(json.dumps(data,ensure_ascii=True,default=str),encoding="utf-8")
save()
old=json.loads(Path("tmp/context271.json").read_text(encoding="utf-8"))
if data["phase"]=="INIT":
 articles=["QAUTO"+data["tag"]+x for x in("A","B")];data["articles"]=articles;save()
 for index,article in enumerate(articles):
  root=ET.fromstring(old["artmas_xml"]);idoc=root.find("IDOC")
  idoc.find("./EDI_DC40/DOCNUM").text=str(int(data["doc"])+index)
  for field in idoc.iter("MATERIAL"):field.text=article
  idoc.find("./E1BPE1MAKTRT/MATL_DESC").text="Own1118 auto preparation "+article
  ea=next(n for n in idoc.findall("E1BPE1MARMRT")if n.findtext("ALT_UNIT")=="EA")
  ea.find("EAN_UPC").text="QA1118"+data["tag"]+str(index)
  box=next(n for n in idoc.findall("E1BPE1MARMRT")if n.findtext("ALT_UNIT")=="BOX")
  box.find("NUMERATOR").text="6";box.find("GROSS_WT").text="4000"
  pal=ET.SubElement(idoc,"E1BPE1MARMRT")
  for k,v in {"MATERIAL":article,"ALT_UNIT":"PAL","NUMERATOR":"24","DENOMINATR":"1"}.items():ET.SubElement(pal,k).text=v
  inbox=ArtmasInbox(g).receive(read_artmas10(ET.tostring(root,encoding="utf-8")),"SAP_FILE_GATEWAY")
  ArticleMasterApply(g).apply(inbox["inbox_id"],"SAP_FILE_GATEWAY")
 with g.transaction("Own1118 isolated picking metadata only")as q:
  for index,article in enumerate(articles):
   q.execute("update RRL_ARTICULS set CELL=:cell where ACTICUL=:a",cell="DS-BASE-P1",a=article)
   q.execute("select count(*)from RRL_COMPL_SEQ where WARE_ID=9807 and ARTICUL=:a",a=article)
   if q.fetchone()[0]==0:q.execute("insert into RRL_COMPL_SEQ(ARTICUL,WARE_ID,SEQ,SEQ_GROUP)values(:a,9807,:s,1118)",a=article,s=index+1)
 root=ET.fromstring(old["source_xml"])
 root.find("MessageId").text="AUTO1118.MSG:"+data["tag"];root.find("OrderNumber").text="AUTO1118.ORDER:"+data["tag"]
 line=root.find("./Lines/Line");line.find("Material").text=articles[0];line.find("Quantity").text="18"
 second=copy.deepcopy(line);second.find("LineNumber").text="2";second.find("Material").text=articles[1];root.find("Lines").append(second)
 data["source_xml"]=ET.tostring(root,encoding="unicode")
 data["source"]=StoreOrders(g).receive(data["source_xml"].encode(),"SAP_FILE_GATEWAY")
 data["phase"]="SOURCE";save()
order=data["source"]["customer_order_id"]
limits={"max_goods_weight_kg":"16","max_goods_volume_m3":"0.096","max_pallets":100}
if data["phase"]=="SOURCE":
 preview=service.auto_preview(order,limits,"admin");assert len(preview["pallets"])==2,preview
 assert len(preview["pallets"][0]["lines"])==2
 data["preview"]=preview
 data["body"]=AutoPreparationRequest.model_validate({"operation_id":"AUTO1118.PREP:"+data["tag"],"source_signature":preview["source_signature"],"limits":limits}).model_dump(mode="json")
 save()
 # Real existing writers, then caller rollback: no partial ST/FF or receipt survives.
 with g.transaction("Own1118 shared writer outer rollback")as q:
  try:
   r=LegacyPreparation(TransactionGateway(q)).auto_prepare(order,data["body"],"admin")
   assert len(r["pallet_identifiers"])==2
   assert r["status"]=="ST_PREPARED"
  finally:q.connection.rollback()
 absent=service.auto_resolve(order,data["body"],"admin");assert absent["state"]=="NOT_PREPARED",absent
 # Commit a change only to our new synthetic SKU, verify stale rejection, restore it.
 with g.transaction("Own1118 change own norm")as q:
  q.execute("update RRL_ARTICULS set NORMA_UKLADKI=12 where ACTICUL=:a",a=data["articles"][0])
 try:
  try:service.auto_prepare(order,data["body"],"admin")
  except ValueError as exc:assert "SOURCE_CHANGED" in str(exc),str(exc)
  else:raise AssertionError("Stale preview accepted")
 finally:
  with g.transaction("Own1118 restore own norm")as q:
   q.execute("update RRL_ARTICULS set NORMA_UKLADKI=24 where ACTICUL=:a",a=data["articles"][0])
 data["phase"]="VERIFIED_ROLLBACK";save()
if data["phase"]=="VERIFIED_ROLLBACK":
 def run(body):
  try:return {"result":service.auto_prepare(order,body,"admin")}
  except ValueError as exc:return {"conflict":str(exc)}
 with ThreadPoolExecutor(max_workers=2)as pool:
  replies=list(pool.map(run,[data["body"],dict(data["body"],operation_id=data["body"]["operation_id"]+".race")]))
 assert sum("result"in r for r in replies)==1 and sum("conflict"in r for r in replies)==1,replies
 data["race"]=replies;data["result"]=next(r["result"]for r in replies if"result"in r)
 data["body"]["operation_id"]=data["result"]["operation_id"];data["phase"]="PREPARED";save()
r=service.auto_prepare(order,data["body"],"admin");assert r["idempotent"]
resolved=service.auto_resolve(order,data["body"],"admin");assert resolved["state"]=="ST_PREPARED"
try:service.auto_prepare(order,{**data["body"],"limits":dict(limits,max_pallets=99)},"admin")
except ValueError:pass
else:raise AssertionError("Changed body reused operation")
# Replay must not recompute after master changes, on our own synthetic card only.
with g.transaction("Own1118 change saved-result norm")as q:
 q.execute("update RRL_ARTICULS set NORMA_UKLADKI=0 where ACTICUL=:a",a=data["articles"][0])
try:assert service.auto_prepare(order,data["body"],"admin")["idempotent"]
finally:
 with g.transaction("Own1118 restore saved-result norm")as q:
  q.execute("update RRL_ARTICULS set NORMA_UKLADKI=24 where ACTICUL=:a",a=data["articles"][0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("set transaction read only")
 q.execute("select ARTICUL,sum(QUANTITY),sum(PACK_COUNT),sum(ORDER_WEIGHT)from RRL_SBORKA_PALLET_ROWS where DOCID=:n group by ARTICUL order by ARTICUL",n=r["st_number"])
 data["actual_rows"]=[list(x)for x in q];assert data["actual_rows"]==[[a,18,3,12]for a in data["articles"]],data["actual_rows"]
 q.execute("select count(*),sum(FACT_QTY),min(STATUS),max(STATUS)from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=:o",o=order);assert q.fetchone()==(2,0,"PLANNED","PLANNED")
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=5062399");assert q.fetchone()==(20,20)
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2),substr(SQL_TEXT,1,160)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and executions>0 and SQL_TEXT not like '%V$SQL%'
 and(SQL_TEXT like '%SOURCE_PICKING_READINESS268%'or SQL_TEXT like '%select ARTICUL,SEQ_GROUP,SEQ from RRL_COMPL_SEQ%')
 order by last_active_time desc fetch first 4 rows only""");data["slow_sql"]=[list(x)for x in q]
data["phase"]="DONE";save()
print(json.dumps({"case":"PASS1118","order":order,"ST":r["st_number"],"pallets":r["pallet_identifiers"],"exact_rows":data["actual_rows"],"slow_sql":data["slow_sql"],"stock_changed":False},ensure_ascii=True))
