create or replace package body RRL_OUTBOX_DELIVERY_API as
 g_event number;g_tx varchar2(100);
 function write_allowed(p_event number)return number is begin
  if p_event=g_event and g_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;
 end;
 procedure open_write(p_event number)is begin g_event:=p_event;g_tx:=dbms_transaction.local_transaction_id(true);end;
 procedure clear_write is begin g_event:=null;g_tx:=null;end;
 procedure owned(e RRL_EVENT_OUTBOX%rowtype,p_version number,p_worker varchar2)is begin
  if p_version is null or p_version<1 or trim(p_worker)is null or e.CLAIM_VERSION!=p_version or e.STATUS!='LOCKED' or e.LOCKED_BY is null or e.LOCKED_BY!=p_worker then
   raise_application_error(-20886,'OUTBOX_CLAIM_FENCED');end if;
 end;
 procedure claim_next(p_worker varchar2,p_target varchar2,p_seconds number,p_result out clob)is
  cursor candidates is select *from RRL_EVENT_OUTBOX where
   ((STATUS in('PENDING','RETRY')and(NEXT_RETRY_AT is null or NEXT_RETRY_AT<=sysdate))
     or(STATUS='LOCKED'and LEASE_UNTIL is not null and LEASE_UNTIL<=systimestamp))
   and(p_target is null or TARGET_SYSTEM=upper(p_target))
   order by CREATED_AT,EVENT_OUTBOX_ID for update skip locked;
  e RRL_EVENT_OUTBOX%rowtype;j json_object_t:=json_object_t();v_seen number:=0;v_until timestamp with time zone;
  v_saved boolean:=false;
 begin
  p_result:=null;
  if trim(p_worker)is null or lengthb(p_worker)>100 or p_seconds is null or p_seconds not between 1 and 900 then
   raise_application_error(-20881,'OUTBOX_CLAIM_INPUT_REQUIRED');end if;
  open candidates;
  loop
   exit when v_seen>=100;fetch candidates into e;exit when candidates%notfound;
   v_seen:=v_seen+1;
   savepoint RRL_OUTBOX154;v_saved:=true;open_write(e.EVENT_OUTBOX_ID);
   if e.STATUS='LOCKED' then
    update RRL_EVENT_OUTBOX set TRY_COUNT=TRY_COUNT+1,LAST_ERROR='LEASE_EXPIRED_OUTCOME_UNCONFIRMED'where EVENT_OUTBOX_ID=e.EVENT_OUTBOX_ID;
    e.TRY_COUNT:=e.TRY_COUNT+1;
    update RRL_ADAPTER_REQUEST_LOG set STATUS='UNCONFIRMED',ERROR_CODE='LEASE_EXPIRED',
     ERROR_TEXT='Worker lease expired before final response',RESPONSE_AT_TZ=systimestamp
     where EVENT_OUTBOX_ID=e.EVENT_OUTBOX_ID and CLAIM_VERSION=e.CLAIM_VERSION and FINISH_HASH is null and STATUS='STARTED';
   end if;
   if e.TRY_COUNT>=e.MAX_TRY_COUNT then
    update RRL_EVENT_OUTBOX set STATUS='DEAD_LETTER',FINISHED_AT=sysdate,LOCKED_BY=null,LOCKED_AT=null,LEASE_UNTIL=null
     where EVENT_OUTBOX_ID=e.EVENT_OUTBOX_ID;
    clear_write;v_saved:=false;
   else
    v_until:=systimestamp+numtodsinterval(p_seconds,'SECOND');
    update RRL_EVENT_OUTBOX set STATUS='LOCKED',LOCKED_BY=p_worker,LOCKED_AT=sysdate,
     CLAIM_VERSION=CLAIM_VERSION+1,LEASE_UNTIL=v_until where EVENT_OUTBOX_ID=e.EVENT_OUTBOX_ID;
    j.put('event_outbox_id',e.EVENT_OUTBOX_ID);j.put('claim_version',e.CLAIM_VERSION+1);j.put('worker_id',p_worker);
    j.put('lease_until',to_char(v_until at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));
    p_result:=j.to_clob;clear_write;v_saved:=false;exit;
   end if;
  end loop;
  close candidates;
 exception when others then
  if candidates%isopen then close candidates;end if;
  if v_saved then rollback to RRL_OUTBOX154;end if;clear_write;raise;
 end;
 procedure begin_attempt(p_event number,p_version number,p_worker varchar2,p_system varchar2,p_kind varchar2,
  p_business varchar2,p_cert varchar2,p_thumb varchar2,p_signature varchar2,p_request clob,p_request_id out number)is
  e RRL_EVENT_OUTBOX%rowtype;v_saved boolean:=false;n number;
 begin
  select *into e from RRL_EVENT_OUTBOX where EVENT_OUTBOX_ID=p_event for update;owned(e,p_version,p_worker);
  if e.LEASE_UNTIL<=systimestamp then raise_application_error(-20886,'OUTBOX_LEASE_EXPIRED');end if;
  select count(*),max(ADAPTER_REQUEST_ID)into n,p_request_id from RRL_ADAPTER_REQUEST_LOG
   where EVENT_OUTBOX_ID=p_event and CLAIM_VERSION=p_version and CLAIM_WORKER=p_worker;
  if n>0 then raise_application_error(-20886,'OUTBOX_ATTEMPT_ALREADY_STARTED_RECONCILE');end if;
  savepoint RRL_OUTBOX154;v_saved:=true;open_write(p_event);
  p_request_id:=RRL_TRACEABILITY_API.add_adapter_request(p_system,p_kind,p_event,p_business,p_cert,p_thumb,p_signature,p_request,'STARTED',e.TRY_COUNT+1);
  update RRL_ADAPTER_REQUEST_LOG set CLAIM_VERSION=p_version,CLAIM_WORKER=p_worker where ADAPTER_REQUEST_ID=p_request_id;
  clear_write;
 exception when others then if v_saved then rollback to RRL_OUTBOX154;end if;clear_write;raise;
 end;
 procedure finish_attempt(p_event number,p_version number,p_worker varchar2,p_request_id number,p_body clob,p_result out clob)is
  e RRL_EVENT_OUTBOX%rowtype;r RRL_ADAPTER_REQUEST_LOG%rowtype;b json_object_t:=json_object_t.parse(p_body);
  digest varchar2(64);v_status varchar2(30);v_error varchar2(4000);j json_object_t:=json_object_t();v_stale boolean;v_saved boolean:=false;
 begin
  if p_event is null or p_request_id is null or p_version is null or p_version<1 or trim(p_worker)is null then
   raise_application_error(-20881,'OUTBOX_RESPONSE_CLAIM_REQUIRED');end if;
  digest:=lower(rawtohex(sys.dbms_crypto.hash(p_body,sys.dbms_crypto.hash_sh256)));
  select *into e from RRL_EVENT_OUTBOX where EVENT_OUTBOX_ID=p_event for update;
  select *into r from RRL_ADAPTER_REQUEST_LOG where ADAPTER_REQUEST_ID=p_request_id for update;
  if r.EVENT_OUTBOX_ID!=p_event or r.CLAIM_VERSION!=p_version or r.CLAIM_WORKER is null or r.CLAIM_WORKER!=p_worker then
   raise_application_error(-20882,'OUTBOX_REQUEST_CLAIM_IDENTITY_CONFLICT');end if;
  if r.FINISH_HASH is not null then
   if r.FINISH_HASH!=digest then raise_application_error(-20886,'OUTBOX_RESPONSE_PAYLOAD_CONFLICT');end if;
   j.put('event_outbox_id',p_event);j.put('adapter_request_id',p_request_id);j.put('status',r.STATUS);j.put('idempotent',true);
   p_result:=j.to_clob;return;
  end if;
  v_status:=b.get_string('status');v_error:=b.get_string('error_text');
  if v_status not in('DONE','ERROR')or v_status is null then raise_application_error(-20881,'OUTBOX_FINAL_OUTCOME_REQUIRED');end if;
  v_stale:=e.CLAIM_VERSION!=p_version or e.STATUS!='LOCKED' or e.LOCKED_BY is null or e.LOCKED_BY!=p_worker or e.LEASE_UNTIL is null or e.LEASE_UNTIL<=systimestamp;
  savepoint RRL_OUTBOX154;v_saved:=true;open_write(p_event);
  RRL_TRACEABILITY_API.update_adapter_request(p_request_id,b.get_clob('response_json'),b.get_string('external_request_id'),
   b.get_string('external_document_id'),b.get_string('external_status'),b.get_number('http_status'),
   case when v_stale then 'STALE_RESPONSE'else v_status end,
   case when v_stale then 'OUTBOX_CLAIM_FENCED'else b.get_string('error_code')end,
   case when v_stale then 'Response retained; current event generation unchanged'else v_error end);
  update RRL_ADAPTER_REQUEST_LOG set FINISH_HASH=digest,RESPONSE_AT_TZ=systimestamp where ADAPTER_REQUEST_ID=p_request_id;
  if not v_stale then
   if v_status='DONE'then RRL_TRACEABILITY_API.mark_outbox_done(p_event,'DONE');
   else RRL_TRACEABILITY_API.mark_outbox_error(p_event,v_error,5,0);end if;
   update RRL_EVENT_OUTBOX set LEASE_UNTIL=null where EVENT_OUTBOX_ID=p_event;
  end if;
  j.put('event_outbox_id',p_event);j.put('adapter_request_id',p_request_id);
  j.put('status',case when v_stale then 'STALE_RESPONSE'else v_status end);j.put('idempotent',false);
  p_result:=j.to_clob;clear_write;
 exception when others then if v_saved then rollback to RRL_OUTBOX154;end if;clear_write;raise;
 end;
 procedure manual_retry(p_event number,p_actor varchar2,p_reason varchar2)is
  e RRL_EVENT_OUTBOX%rowtype;n number;v_saved boolean:=false;j json_object_t:=json_object_t();v_payload clob;v_request number;
 begin
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'external_outbox_retry')=1;
  if n!=1 then raise_application_error(-20882,'OUTBOX_RETRY_CURRENT_ACTOR_REQUIRED');end if;
  if p_reason is null or length(p_reason)<8 then raise_application_error(-20881,'OUTBOX_RETRY_REASON_REQUIRED');end if;
  select *into e from RRL_EVENT_OUTBOX where EVENT_OUTBOX_ID=p_event for update;
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'external_outbox_retry')=1;
  if n!=1 then raise_application_error(-20882,'OUTBOX_RETRY_CURRENT_ACTOR_REQUIRED');end if;
  if e.STATUS in('DONE','EXPORTED','ACKNOWLEDGED')then raise_application_error(-20886,'OUTBOX_COMPLETED_CANNOT_RETRY');end if;
  if e.STATUS='LOCKED'and(e.LEASE_UNTIL is null or e.LEASE_UNTIL>systimestamp)then
   raise_application_error(-20886,'OUTBOX_ACTIVE_OR_LEGACY_LOCK_REQUIRES_RECONCILIATION');end if;
  savepoint RRL_OUTBOX154;v_saved:=true;open_write(p_event);
  update RRL_EVENT_OUTBOX set STATUS='PENDING',CLAIM_VERSION=CLAIM_VERSION+1,LEASE_UNTIL=null,MAX_TRY_COUNT=greatest(MAX_TRY_COUNT,TRY_COUNT+1),
   LOCKED_BY=null,LOCKED_AT=null,NEXT_RETRY_AT=null,LAST_ERROR=substr('Manual retry: '||p_reason,1,4000)
   where EVENT_OUTBOX_ID=p_event;
  j.put('actor',p_actor);j.put('reason',p_reason);j.put('old_try_count',e.TRY_COUNT);j.put('old_max_try_count',e.MAX_TRY_COUNT);
  j.put('new_max_try_count',greatest(e.MAX_TRY_COUNT,e.TRY_COUNT+1));v_payload:=j.to_clob;
  v_request:=RRL_TRACEABILITY_API.add_adapter_request(e.TARGET_SYSTEM,'MANUAL_RETRY',p_event,e.IDEMPOTENCY_KEY,
    null,null,'NOT_APPLICABLE',v_payload,'MANUAL_RETRY',e.TRY_COUNT+1);
  update RRL_ADAPTER_REQUEST_LOG set CLAIM_VERSION=e.CLAIM_VERSION+1,CLAIM_WORKER=p_actor,RESPONSE_AT_TZ=systimestamp
    where ADAPTER_REQUEST_ID=v_request;
  clear_write;
 exception when others then if v_saved then rollback to RRL_OUTBOX154;end if;clear_write;raise;
 end;
end;
/
