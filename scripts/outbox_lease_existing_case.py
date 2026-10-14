"""154 isolated metadata delivery; no provider or stock changes."""
import sys,json,time
from pathlib import Path
from uuid import uuid4
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.integrations.public import OutboxDelivery
s=get_settings();tag=uuid4().hex[:10];target="Q154_"+tag
class Adapter:
 cert_alias=None;cert_thumbprint=None;signature_status="MOCK_NOT_SIGNED"
delivery=OutboxDelivery(OracleGateway())
def connection():return oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)
def rejected(fn,code):
 try:fn()
 except oracledb.DatabaseError as exc:
  assert exc.args[0].code==code,str(exc)
 else:raise AssertionError("Expected refusal")
with connection()as c:
 q=c.cursor();q.execute("select count(*)from RRL_EVENTS");stock=q.fetchone()
 events=[]
 for n in range(2):
  payload=q.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,'{"fixture":"'+tag+'","n":'+str(n)+'}')
  events.append(int(q.callfunc("RRL_TRACEABILITY_API.enqueue_event",oracledb.DB_TYPE_NUMBER,
   ["QA_LEASE","OUTBOX_TEST",tag+":"+str(n),"Q154:"+tag+":"+str(n),payload,target,tag,3])))
 c.commit()
 # Locked oldest row must not hide the next available row.
 q.execute("select EVENT_OUTBOX_ID from RRL_EVENT_OUTBOX where EVENT_OUTBOX_ID=:id for update",id=events[0]);q.fetchone()
 second=delivery.claim("QA154:B:"+tag,target,300);assert second["event_outbox_id"]==events[1],second
 c.rollback()
 second_request=delivery.begin(second,delivery.event(events[1]),Adapter())
 second_finish=delivery.finish(second,second_request,{"status":"DONE","response_json":"{\"simulation\":true}"})
 assert second_finish["status"]=="DONE"
 first=delivery.claim("QA154:A:"+tag,target,1);assert first["event_outbox_id"]==events[0]
 old_request=delivery.begin(first,delivery.event(events[0]),Adapter())
 rejected(lambda:delivery.begin(first,delivery.event(events[0]),Adapter()),20886)
 time.sleep(1.2)
 newer=delivery.claim("QA154:C:"+tag,target,300);assert newer["claim_version"]==first["claim_version"]+1
 new_request=delivery.begin(newer,delivery.event(events[0]),Adapter())
 body={"status":"DONE","response_json":"{\"simulation\":true}","external_request_id":"SIMULATED154:"+tag}
 old=delivery.finish(first,old_request,body);assert old["status"]=="STALE_RESPONSE",old
 q.execute("select STATUS,CLAIM_VERSION,TRY_COUNT from RRL_EVENT_OUTBOX where EVENT_OUTBOX_ID=:id",id=events[0])
 assert q.fetchone()==("LOCKED",newer["claim_version"],1)
 # Native finalization can be rolled back as one unit by its owner.
 blob=q.var(oracledb.DB_TYPE_CLOB);blob.setvalue(0,json.dumps(body,sort_keys=True,separators=(",",":")))
 result=q.var(oracledb.DB_TYPE_CLOB)
 q.callproc("RRL_OUTBOX_DELIVERY_API.finish_attempt",[events[0],newer["claim_version"],newer["worker_id"],new_request,blob,result])
 c.rollback()
 q.execute("select STATUS,FINISH_HASH from RRL_ADAPTER_REQUEST_LOG where ADAPTER_REQUEST_ID=:id",id=new_request)
 assert q.fetchone()==("STARTED",None)
 q.execute("select STATUS from RRL_EVENT_OUTBOX where EVENT_OUTBOX_ID=:id",id=events[0]);assert q.fetchone()==("LOCKED",)
 done=delivery.finish(newer,new_request,body);assert done["status"]=="DONE"
 replay=delivery.finish(newer,new_request,body);assert replay["idempotent"] is True
 rejected(lambda:delivery.finish(newer,new_request,{**body,"external_status":"changed"}),20886)
 rejected(lambda:delivery.retry(events[0],"admin","Do not resend completed event"),20886)
 rejected(lambda:q.callproc("RRL_TRACEABILITY_API.mark_outbox_done",[events[0],"DONE"]),20863);c.rollback()
 # Manual retry retains failure history and grants one explicitly audited attempt.
 payload=q.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,'{"fixture":"'+tag+'"}')
 third=int(q.callfunc("RRL_TRACEABILITY_API.enqueue_event",oracledb.DB_TYPE_NUMBER,
  ["QA_LEASE","OUTBOX_TEST",tag+":2","Q154:"+tag+":2",payload,target,tag,1]));c.commit()
 from concurrent.futures import ThreadPoolExecutor
 with ThreadPoolExecutor(max_workers=2)as pool:
  claims=list(pool.map(lambda worker:delivery.claim(worker,target,300),["QA154:D:"+tag,"QA154:E:"+tag]))
 winners=[v for v in claims if v is not None];assert len(winners)==1,claims
 claim=winners[0];request=delivery.begin(claim,delivery.event(third),Adapter())
 rejected(lambda:delivery.retry(third,"admin","Do not steal current active lease"),20886)
 delivery.finish(claim,request,{"status":"ERROR","error_text":"Own synthetic failure"})
 q.execute("select STATUS,TRY_COUNT,MAX_TRY_COUNT from RRL_EVENT_OUTBOX where EVENT_OUTBOX_ID=:id",id=third)
 assert q.fetchone()==("DEAD_LETTER",1,1)
 rejected(lambda:delivery.retry(third,"UNKNOWN154","Current actor required"),20882)
 delivery.retry(third,"admin","One explicitly authorized synthetic retry")
 q.execute("select STATUS,TRY_COUNT,MAX_TRY_COUNT from RRL_EVENT_OUTBOX where EVENT_OUTBOX_ID=:id",id=third)
 assert q.fetchone()==("PENDING",1,2)
 q.execute("select STATUS,to_clob(REQUEST_JSON)from RRL_ADAPTER_REQUEST_LOG where EVENT_OUTBOX_ID=:id and REQUEST_KIND='MANUAL_RETRY'",id=third)
 audit=q.fetchone();assert audit[0]=="MANUAL_RETRY";raw=audit[1].read()
 assert json.loads(raw)["old_max_try_count"]==1 and json.loads(raw)["actor"]=="admin"
 claim=delivery.claim("QA154:F:"+tag,target,300);request=delivery.begin(claim,delivery.event(third),Adapter())
 delivery.finish(claim,request,{"status":"ERROR","error_text":"Close own synthetic retry"})
 q.execute("select STATUS,TRY_COUNT from RRL_EVENT_OUTBOX where EVENT_OUTBOX_ID=:id",id=third);assert q.fetchone()==("DEAD_LETTER",2)
 q.execute("select count(*)from RRL_EVENTS");assert q.fetchone()==stock
 print("PASS154 locked-head skipped/expired lease generation+1/stale response fenced/finish atomic rollback/exact replay/conflict/legacy write denied/no stock",events,tag,flush=True)
