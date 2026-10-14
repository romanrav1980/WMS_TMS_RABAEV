"""153 one private outbox event/simulated error in real Oracle, no external provider/stock."""
import sys,json
from pathlib import Path
from uuid import uuid4
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.services.outbox_service import OutboxService
from app.modules.integrations.public import RegulatoryResponse
s=get_settings();tag=uuid4().hex[:10];target="Q153_"+tag
payload='{ "original_exact_number": 12345678901234567890123456789.123456789, "fixture": true }'
class SimulatedError:
 mode="MOCK";configured=True;simulated=True;signature_status="MOCK_NOT_SIGNED";cert_alias=None;cert_thumbprint=None
 def send(self,event):
  assert event["payload_json"]==payload,(type(event["payload_json"]),event["payload_json"])
  return RegulatoryResponse("ERROR","SIMULATED_RETRYABLE_ERROR","SIMULATED-153-"+tag,None,503,
   json.dumps({"simulation":True,"error":"Private synthetic provider unavailable"}),False)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from RRL_EVENTS");stock_events=q.fetchone()
 q.execute("select count(*)from RRL_ADAPTER_REQUEST_LOG");before_requests=q.fetchone()[0]
 bind=q.var(oracledb.DB_TYPE_CLOB);bind.setvalue(0,payload)
 event=int(q.callfunc("RRL_TRACEABILITY_API.enqueue_event",oracledb.DB_TYPE_NUMBER,
  ["QA_RESPONSE_TEST","OUTBOX_TEST","153:"+tag,"Q153:"+tag,bind,target,"Q153:"+tag,2]))
 c.commit()
 try:
  service=OutboxService(adapter=SimulatedError());result=service.process_next("QA153:"+tag,target)
  assert result["event_outbox_id"]==event and result["status"]=="ERROR",result
  assert result["simulation"]and result["real_external_ack"]is False,result
  q.execute("select STATUS,TRY_COUNT from RRL_EVENT_OUTBOX where EVENT_OUTBOX_ID=:id",id=event);assert q.fetchone()==("RETRY",1)
  q.execute("select STATUS,HTTP_STATUS,EXTERNAL_STATUS,ERROR_CODE,to_clob(REQUEST_JSON),to_clob(RESPONSE_JSON),SIGNATURE_STATUS from RRL_ADAPTER_REQUEST_LOG where ADAPTER_REQUEST_ID=:id",id=result["adapter_request_id"])
  row=q.fetchone();texts=[v.read()if hasattr(v,"read")else v for v in row]
  assert texts[0:4]==["ERROR",503,"SIMULATED_RETRYABLE_ERROR","ADAPTER_RESPONSE_NOT_DELIVERED"],texts[:4]
  assert texts[4]==payload and json.loads(texts[5])["simulation"]and texts[6]=="MOCK_NOT_SIGNED"
  q.execute("select count(*)from RRL_ADAPTER_REQUEST_LOG");assert q.fetchone()[0]==before_requests+1
  q.execute("select count(*)from RRL_EVENTS");assert q.fetchone()==stock_events
  print("PASS153 private simulated responseERROR/http503 -> requestERROR/response+IDs retained/eventRETRY1, not DONE/legalACK; exact38digit original CLOB retained/no stock/event="+str(event)+"/tag="+tag,flush=True)
 finally:
  service.delivery.retry(event,"admin","Close own simulated response scenario")
  claim=service.delivery.claim("QA153:CLEAN:"+tag,target)
  request=service.delivery.begin(claim,service.delivery.event(event),service.adapter)
  service.delivery.finish(claim,request,{"status":"ERROR","error_text":"Own synthetic cleanup failure"})
