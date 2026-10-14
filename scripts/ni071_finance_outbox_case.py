import sys,xml.etree.ElementTree as ET
from pathlib import Path
from uuid import uuid4
from hashlib import sha256
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.integrations.public import build_receipt_exporter
s=get_settings();tag=uuid4().hex[:10];actor="QFO"+tag;group=actor.upper();secret=uuid4().hex
admin=httpx.Client(auth=("admin","admin123"),timeout=35);user=httpx.Client(auth=(actor,secret),timeout=35);base="http://127.0.0.1:8088"
def api(client,path,body):
 r=client.post(base+path,json=body);assert r.status_code==200,(r.status_code,r.text[:1700]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();ware=2378876;p="/api/finance/logistics-expenses"
 q.execute("select VEHICLE_ID from RRL_TT_HU_LOAD_FACT where TT_ID=33514");vehicle=int(q.fetchone()[0])
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own finance outbox observer',:grp,:ware,0,0)",id=actor,secret=secret,grp=group,ware=ware);c.commit()
 api(admin,"/api/admin/rights/groups",{"id":group,"name":"Own finance outbox"})
 for right in ["transport_dispatch_view","edit_bill_tt","calc_tt_price"]:
  api(admin,f"/api/admin/rights/groups/{group}/rights",{"right_name":right,"description":"Own finance outbox"})
 try:
  report={"operation_id":"EX.OUTBOX:"+tag,"warehouse_id":ware,"article_code":"EX.QA:80B1FC8567","object_kind":"VEHICLE","object_id":vehicle,"amount":"2.01","currency":"GEL","expense_date":"2026-10-10","document_reference":"DEV.OUTBOX:"+tag,"reason":"Own synthetic documentary expense"}
  api(user,p+"/report",report)
  decision={"operation_id":"EX.OUTBOX.LOGIST:"+tag,"expense_operation_id":report["operation_id"],"phase":"LOGIST","outcome":"APPROVE","distribution_basis":"NONE","decision_reference":"LOGIST:"+tag,"reason":"Own vehicle-only expense"}
  api(user,p+"/decide",decision)
  finance={**decision,"operation_id":"EX.OUTBOX.FIN:"+tag,"phase":"FINANCE"}
  result=api(admin,p+"/decide",finance);assert api(admin,p+"/decide",finance)==result
  event="FIN:"+sha256(("EXTRA_EXPENSE_RECOGNIZED:"+finance["operation_id"]).encode()).hexdigest()
  q.execute("select STATUS,json_value(PAYLOAD_JSON,'$.posting_semantics'),json_value(PAYLOAD_JSON,'$.amount'),json_value(PAYLOAD_JSON,'$.decision_actor')from RRL_SAP_RECEIPT_OUTBOX where EVENT_ID=:id",id=event);assert q.fetchone()==("PENDING","MONETARY_RECOGNITION","2.01","admin")
  directory=Path("tmp/nicora_finance115")/tag
  exported=build_receipt_exporter().export(directory,1,(event,));assert len(exported)==1 and exported[0]["event_id"]==event
  assert build_receipt_exporter().export(directory,1,(event,))==[]
  document=ET.fromstring((directory/exported[0]["file"]).read_bytes())
  assert document.findtext("EventType")=="EXTRA_EXPENSE_RECOGNIZED" and document.findtext("PostingSemantics")=="MONETARY_RECOGNITION" and document.findtext("Amount")=="2.01"
  q.execute("select STATUS,ACKNOWLEDGED_AT from RRL_SAP_RECEIPT_OUTBOX where EVENT_ID=:id",id=event);assert q.fetchone()==("EXPORTED",None)
  print("PASS115 own finance approval+same-transaction outbox/replay/event1, original generic XML file export scoped event/atomic publication/retry no duplicate, EXPORTED not SAP ACK; tag="+tag,flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor);c.commit()
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%FIN:%' and upper(SQL_TEXT) like '%RRL_SAP_RECEIPT_OUTBOX%' and upper(SQL_TEXT) not like '%V$SQL%' and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""")
 print("SQL milliseconds/executions",q.fetchall())
