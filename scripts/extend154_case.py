import json
from pathlib import Path
p=Path("scripts/outbox_lease_existing_case.py");s=p.read_text(encoding="utf-8")
pos=s.index(' q.execute("select count(*)from RRL_EVENTS");assert')
s=s[:pos]+''' # Manual retry retains failure history and grants one explicitly audited attempt.
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
''' +s[pos:]
p2=Path("scripts/regulatory_outbox_error_existing_case.py");r=p2.read_text(encoding="utf-8")
r=r.replace('  q.callproc("RRL_TRACEABILITY_API.mark_outbox_error",[event,"Close own simulated error scenario",5,1]);c.commit()', '''  service.delivery.retry(event,"admin","Close own simulated response scenario")
  claim=service.delivery.claim("QA153:CLEAN:"+tag,target)
  request=service.delivery.begin(claim,service.delivery.event(event),service.adapter)
  service.delivery.finish(claim,request,{"status":"ERROR","error_text":"Own synthetic cleanup failure"})''')
print(json.dumps({str(p):s,str(p2):r}))
