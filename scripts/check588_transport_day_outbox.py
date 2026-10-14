exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from datetime import datetime,timezone
from app.modules.finance.infrastructure.reconciliation_sources import DAILY,BACKLOG
from app.modules.finance.infrastructure.reconciliation_erp import erp_snapshot
from app.modules.integrations.public import build_receipt_exporter
from hashlib import sha256
import xml.etree.ElementTree as ET
saved=json.loads(Path("tmp/context586.json").read_text(encoding="utf-8"));assert saved["done"];ware=saved["warehouse"]
op=saved["winner"]["body"]["operation_id"]
event="FIN:"+sha256(("TRANSPORT_COST_RECOGNIZED:"+op).encode()).hexdigest().upper()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name,query in DAILY:
  if name not in("warehouse_cost_runs","transport_cost_runs"):continue
  q.execute(query,ware=ware,day_from=datetime(2026,10,12,tzinfo=timezone.utc),day_to=datetime(2026,10,13,tzinfo=timezone.utc));assert q.fetchone()[0]==1,name
 for name,query in BACKLOG:
  if name=="transport_cost_unrecognized":q.execute(query,ware=ware);assert q.fetchone()[0]==0
 erp=erp_snapshot(q,ware);assert any(row["event_type"]=="TRANSPORT_COST_RECOGNIZED"for row in erp)
directory=Path("tmp/transport588_export")/op.replace(":","_")
exported=build_receipt_exporter().export(directory,1,(event,));assert len(exported)==1
assert build_receipt_exporter().export(directory,1,(event,))==[]
doc=ET.fromstring((directory/exported[0]["file"]).read_bytes())
assert doc.findtext("EventType")=="TRANSPORT_COST_RECOGNIZED"and doc.findtext("Total")=="107.25"
assert doc.findtext("PostingSemantics")=="MONETARY_RECOGNITION"and doc.findtext("ExternalSapAck")=="false"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select STATUS,ACKNOWLEDGED_AT from RRL_SAP_RECEIPT_OUTBOX where EVENT_ID=:id",id=event);assert q.fetchone()==("EXPORTED",None)
 assert any(row["event_type"]=="TRANSPORT_COST_RECOGNIZED"and row["status"]=="EXPORTED"for row in erp_snapshot(q,ware))
print("PASS588 warehouse1/transport1 separated; unrecognised original departure0; existing scoped XML export107.25 once/EXPORTED no external ACK; ERP pending remains visible, no physical writes.")
