"""155 private simulated provider once, Oracle-finalization failure, process reconstruction."""
import sys,json
from pathlib import Path
from uuid import uuid4
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.services.outbox_service import OutboxService
from app.modules.integrations.public import RegulatoryResponse,OutboxResponseJournal
s=get_settings();tag=uuid4().hex[:10];target="Q155_"+tag
root=Path("tmp/outbox_response155_"+tag)
calls=[]
class Simulated:
 mode="MOCK";configured=True;simulated=True;signature_status="MOCK_NOT_SIGNED";cert_alias=None;cert_thumbprint=None
 def send(self,event):
  calls.append(event["event_outbox_id"])
  return RegulatoryResponse("DONE","SIMULATED_DELIVERED","SIMULATED155:"+tag,None,200,'{"simulation":true}',False)
class Disabled:
 configured=False
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from RRL_EVENTS");stock=q.fetchone()
 payload=q.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,'{"fixture":"'+tag+'"}')
 event=int(q.callfunc("RRL_TRACEABILITY_API.enqueue_event",oracledb.DB_TYPE_NUMBER,
  ["QA_RECOVERY","OUTBOX_TEST",tag,"Q155:"+tag,payload,target,tag,3]));c.commit()
 journal=OutboxResponseJournal(root);service=OutboxService(adapter=Simulated(),journal=journal)
 original=service.delivery.finish
 def fail_finish(*args,**kwargs):raise ConnectionError("Own synthetic Oracle finalization unavailable")
 service.delivery.finish=fail_finish
 try:service.process_next("QA155:"+tag,target)
 except ConnectionError:pass
 else:raise AssertionError("Expected unconfirmed database finish")
 assert calls==[event] and len(list(journal.pending.glob("*.json")))==1
 q.execute("select STATUS,CLAIM_VERSION from RRL_EVENT_OUTBOX where EVENT_OUTBOX_ID=:id",id=event);assert q.fetchone()==("LOCKED",1)
 q.execute("select STATUS,FINISH_HASH from RRL_ADAPTER_REQUEST_LOG where EVENT_OUTBOX_ID=:id",id=event);assert q.fetchone()==("STARTED",None)
 # Reconstructed worker, even disabled adapter: persisted outcome finishes without provider.
 recovered=OutboxService(adapter=Disabled(),journal=OutboxResponseJournal(root)).process_next("QA155:NEW:"+tag,target)
 assert recovered["status"]=="DONE" and recovered["response_recovered"] is True and recovered["real_external_ack"] is False,recovered
 assert calls==[event] and not list(journal.pending.glob("*.json"))
 q.execute("select STATUS from RRL_EVENT_OUTBOX where EVENT_OUTBOX_ID=:id",id=event);assert q.fetchone()==("DONE",)
 q.execute("select STATUS,FINISH_HASH from RRL_ADAPTER_REQUEST_LOG where EVENT_OUTBOX_ID=:id",id=event)
 row=q.fetchone();assert row[0]=="DONE" and len(row[1])==64
 q.execute("select count(*)from RRL_EVENTS");assert q.fetchone()==stock
 print("PASS155 response persisted before failed Oracle finish/reconstructed disabled worker finishes/no provider resend/mock not legalACK/no stock",event,tag,flush=True)
