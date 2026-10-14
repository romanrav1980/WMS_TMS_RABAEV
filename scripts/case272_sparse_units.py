exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.integrations.infrastructure.artmas_inbox import ArtmasInbox
from app.modules.integrations.infrastructure.article_master import ArticleMasterApply
from app.modules.integrations.domain.artmas import read_artmas10
from app.modules.integrations.domain.article_units import map_units,merge_units
from app.modules.platform.public import read_oracle_json
import xml.etree.ElementTree as ET,time,httpx
data=json.loads(Path("tmp/context271.json").read_text(encoding="utf-8"));article=data["article"];g=OracleGateway()
old=[{"uom":"EA","numerator":1,"denominator":1,"ratio":"1","ean":"item"},{"uom":"BOX","numerator":24,"denominator":1,"ratio":"24","ean":"box"}]
patch=map_units([{"segment":"E1BPE1MARMRT","fields":{"ALT_UNIT":"BOX","LENGTH":"40","UNIT_DIM":"CM"}},{"segment":"E1BPE1MARMRTX","fields":{"ALT_UNIT":"BOX","LENGTH":"X"}}])
merged=merge_units(old,patch,"EA");assert next(r for r in merged if r["uom"]=="BOX")["numerator"]==24 and len(merged)==2
for records in [
 [{"segment":"E1BPE1MARMRT","fields":{"ALT_UNIT":"BOX","NUMERATOR":"24"}}],
 [{"segment":"E1BPE1MARMRT","fields":{"ALT_UNIT":"CS","LENGTH":"40"}},{"segment":"E1BPE1MARMRTX","fields":{"ALT_UNIT":"CS","LENGTH":"X"}}]]:
 try:merge_units(old,map_units(records),"EA")
 except ValueError:pass
 else:raise AssertionError("Unproven unit conversion")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COUNT_SHT_IN_KOR,BRUTTO_WEIGHT_OF_KOR,DIMKOR_X,DIMKOR_Y,DIMKOR_Z from RRL_ARTICULS where ACTICUL=:article",article=article);baseline=q.fetchone()
 q.execute("select UNITS_JSON from RRL_SAP_ARTICLE_META where ARTICUL=:article",article=article);previous_units=read_oracle_json(q.fetchone()[0])
def make(uom,flag,doc):
 root=ET.Element("ARTMAS10");idoc=ET.SubElement(root,"IDOC");control=ET.SubElement(idoc,"EDI_DC40")
 for k,v in {"DOCNUM":doc,"MESTYP":"ARTMAS","IDOCTYP":"ARTMAS10","SNDPRN":"OWN.QA.SAP","CREDAT":"20261011","CRETIM":"145500"}.items():ET.SubElement(control,k).text=v
 for name,fields in [("E1BPE1MATHEAD",{"BASIC_VIEW":"X"}),("E1BPE1MARMRT",{"ALT_UNIT":uom,"LENGTH":"40","UNIT_DIM":"CM"}),("E1BPE1MARMRTX",{"ALT_UNIT":uom,flag:"X"})]:
  node=ET.SubElement(idoc,name)
  for k,v in {"MATERIAL":article,**fields}.items():ET.SubElement(node,k).text=v
 return ET.tostring(root,encoding="utf-8")
doc=str(int(time.time()*1000000));raw=make("BOX","LENGTH",doc)
received=ArtmasInbox(g).receive(read_artmas10(raw),"SAP_FILE_GATEWAY")
result=ArticleMasterApply(g).apply(received["inbox_id"],"SAP_FILE_GATEWAY");assert result["articles_applied"]
bad_doc=str(int(time.time()*1000000));bad=ArtmasInbox(g).receive(read_artmas10(make("CS","LENGTH",bad_doc)),"SAP_FILE_GATEWAY")
try:ArticleMasterApply(g).apply(bad["inbox_id"],"SAP_FILE_GATEWAY")
except ValueError:pass
else:raise AssertionError("New unit without ratio")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COUNT_SHT_IN_KOR,BRUTTO_WEIGHT_OF_KOR,DIMKOR_X,DIMKOR_Y,DIMKOR_Z from RRL_ARTICULS where ACTICUL=:article",article=article);assert q.fetchone()==baseline
 q.execute("select UNITS_JSON,SOURCE_DOCNUM from RRL_SAP_ARTICLE_META where ARTICUL=:article",article=article);stored,source_doc=q.fetchone();stored=read_oracle_json(stored)
 assert {r["uom"]for r in stored}=={r["uom"]for r in previous_units} and next(r for r in stored if r["uom"]=="BOX")["numerator"]==24 and source_doc==doc
 q.execute("select STATUS from RRL_SAP_IDOC_INBOX where INBOX_ID=:inbox_id",inbox_id=bad["inbox_id"]);assert q.fetchone()==("ERROR",)
 q.execute("select ORDER_QTY from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=:order_id",order_id=data["order_id"]);assert q.fetchone()==(48,)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3),substr(SQL_TEXT,1,110)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and SQL_TEXT not like '%V$SQL%'and executions>0 and last_active_time>sysdate-15/1440
 and(SQL_TEXT like '%RRL_SAP_ARTICLE_META%'or SQL_TEXT like '%RRL_ORDER_ROWS%'or SQL_TEXT like '%RRL_SBORKA_PALLET_ROWS%')
 order by elapsed_time/nullif(executions,0)desc fetch first 6 rows only""");print("SQL_MS",json.dumps(q.fetchall(),ensure_ascii=True))
Path("tmp/context272.json").write_text(json.dumps({"inbox_id":received["inbox_id"],"failed_inbox_id":bad["inbox_id"],"raw":raw.decode(),"source_doc":doc},ensure_ascii=True),encoding="utf-8")
print("PASS272 actual sparse MARM length X/no ratio ->preservedBOX24 and omittedEA/unknownnewCS conversion rejected atomiccardmetadata/errorinbox/source48 immutable/P20H20/no stock event")
