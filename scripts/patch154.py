import json
from pathlib import Path
p=Path("db/migrations/2026-10-10_outbox_lease/002_api.sql");s=p.read_text(encoding="utf-8")
s=s.replace("if e.CLAIM_VERSION!=p_version", "if p_version is null or p_version<1 or trim(p_worker)is null or e.CLAIM_VERSION!=p_version",1)
s=s.replace("fetch candidates into e;exit when candidates%notfound;\n   v_seen:=v_seen+1;if v_seen>100 then exit;end if;", "exit when v_seen>=100;fetch candidates into e;exit when candidates%notfound;\n   v_seen:=v_seen+1;")
s=s.replace("e RRL_EVENT_OUTBOX%rowtype;v_saved boolean:=false;\n begin\n  select *into e", "e RRL_EVENT_OUTBOX%rowtype;v_saved boolean:=false;n number;\n begin\n  select *into e",1)
s=s.replace("savepoint RRL_OUTBOX154;v_saved:=true;open_write(p_event);\n  p_request_id:=", """if e.LEASE_UNTIL<=systimestamp then raise_application_error(-20886,'OUTBOX_LEASE_EXPIRED');end if;
  select count(*),max(ADAPTER_REQUEST_ID)into n,p_request_id from RRL_ADAPTER_REQUEST_LOG
   where EVENT_OUTBOX_ID=p_event and CLAIM_VERSION=p_version and CLAIM_WORKER=p_worker;
  if n>0 then raise_application_error(-20886,'OUTBOX_ATTEMPT_ALREADY_STARTED_RECONCILE');end if;
  savepoint RRL_OUTBOX154;v_saved:=true;open_write(p_event);
  p_request_id:=""",1)
s=s.replace("digest:=lower(rawtohex", """if p_event is null or p_request_id is null or p_version is null or p_version<1 or trim(p_worker)is null then
   raise_application_error(-20881,'OUTBOX_RESPONSE_CLAIM_REQUIRED');end if;
  digest:=lower(rawtohex""")
s=s.replace("or e.LOCKED_BY!=p_worker;\n  savepoint", "or e.LOCKED_BY!=p_worker or e.LEASE_UNTIL is null or e.LEASE_UNTIL<=systimestamp;\n  savepoint")
s=s.replace("e RRL_EVENT_OUTBOX%rowtype;n number;v_saved boolean:=false;", "e RRL_EVENT_OUTBOX%rowtype;n number;v_saved boolean:=false;j json_object_t:=json_object_t();v_payload clob;v_request number;")
s=s.replace("if e.STATUS in('DONE','EXPORTED','ACKNOWLEDGED')", """select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'external_outbox_retry')=1;
  if n!=1 then raise_application_error(-20882,'OUTBOX_RETRY_CURRENT_ACTOR_REQUIRED');end if;
  if e.STATUS in('DONE','EXPORTED','ACKNOWLEDGED')""")
s=s.replace("set STATUS='PENDING',CLAIM_VERSION=CLAIM_VERSION+1,LEASE_UNTIL=null,", "set STATUS='PENDING',CLAIM_VERSION=CLAIM_VERSION+1,LEASE_UNTIL=null,MAX_TRY_COUNT=greatest(MAX_TRY_COUNT,TRY_COUNT+1),")
s=s.replace("  clear_write;\n exception when others then if v_saved then rollback to RRL_OUTBOX154;end if;clear_write;raise;\n end;\nend;", """  j.put('actor',p_actor);j.put('reason',p_reason);j.put('old_try_count',e.TRY_COUNT);j.put('old_max_try_count',e.MAX_TRY_COUNT);
  j.put('new_max_try_count',greatest(e.MAX_TRY_COUNT,e.TRY_COUNT+1));v_payload:=j.to_clob;
  v_request:=RRL_TRACEABILITY_API.add_adapter_request(e.TARGET_SYSTEM,'MANUAL_RETRY',p_event,e.IDEMPOTENCY_KEY,
    null,null,'NOT_APPLICABLE',v_payload,'MANUAL_RETRY',e.TRY_COUNT+1);
  update RRL_ADAPTER_REQUEST_LOG set CLAIM_VERSION=e.CLAIM_VERSION+1,CLAIM_WORKER=p_actor,RESPONSE_AT_TZ=systimestamp
    where ADAPTER_REQUEST_ID=v_request;
  clear_write;
 exception when others then if v_saved then rollback to RRL_OUTBOX154;end if;clear_write;raise;
 end;
end;""")
g=Path("db/migrations/2026-10-10_outbox_lease/003_guards.sql").read_text(encoding="utf-8").replace("if :old.CLAIM_VERSION>0 then","if :old.CLAIM_VERSION>0 or (updating and :new.CLAIM_VERSION>0)then")
print(json.dumps({str(p):s,"db/migrations/2026-10-10_outbox_lease/003_guards.sql":g}))
