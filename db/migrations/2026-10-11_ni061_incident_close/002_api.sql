create or replace package RRL_INTERWARE_INCIDENT_API authid definer as
 function write_allowed return number;
 procedure close_case(p_operation varchar2,p_actor varchar2,p_request clob,p_result out clob);
end;
/
create or replace package body RRL_INTERWARE_INCIDENT_API as
 g_tx varchar2(100);
 function write_allowed return number is begin
  if g_tx is not null and g_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;
 end;
 procedure scope(p_plan varchar2,p_actor varchar2)is n number;begin
  select count(*)into n from RRL_INTERWARE_PLAN p join RUSERS u on u.ID=p_actor
   where p.OPERATION_ID=p_plan and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_edit')=1
   and(u.WARE_ID=p.TARGET_WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
  if n!=1 then raise_application_error(-20882,'INTERWARE_INCIDENT_CURRENT_TARGET_DISPATCHER_REQUIRED');end if;
 end;
 procedure close_case(p_operation varchar2,p_actor varchar2,p_request clob,p_result out clob)is
  b json_object_t;incident RRL_INTERWARE_DECISION%rowtype;receipt RRL_INTERWARE_RECEIPT%rowtype;plan RRL_INTERWARE_PLAN%rowtype;
  saved RRL_INTERWARE_INCIDENT_CLOSE%rowtype;entered boolean:=false;sp boolean:=false;n number;declared_qty number;hash varchar2(64);j json_object_t;
  incident_id varchar2(100);receipt_id varchar2(100);rev number;reason varchar2(2000);ref varchar2(2000);
 begin
  if p_operation is null or lengthb(p_operation)>100 or not regexp_like(p_operation,'^[A-Za-z0-9_.:-]+$')or p_request is null or dbms_lob.getlength(p_request)>6000 then raise_application_error(-20886,'INTERWARE_INCIDENT_CLOSE_REQUEST_BOUND');end if;
  b:=json_object_t.parse(p_request);incident_id:=b.get_string('incident_operation_id');receipt_id:=b.get_string('followup_receipt_operation_id');rev:=b.get_number('incident_revision');
  reason:=b.get_string('reason');ref:=b.get_string('evidence_reference');
  if b.get_size!=5 or incident_id is null or receipt_id is null or lengthb(incident_id)>100 or lengthb(receipt_id)>100 or rev is null or rev<1 or trunc(rev)!=rev
   or trim(reason)is null or length(trim(reason))<8 or length(reason)>500 or trim(ref)is null or length(ref)>255 then raise_application_error(-20886,'INTERWARE_INCIDENT_CLOSE_EXPLICIT_EVIDENCE_REQUIRED');end if;
  select *into incident from RRL_INTERWARE_DECISION where OPERATION_ID=incident_id;scope(incident.PLAN_OPERATION_ID,p_actor);
  hash:=lower(rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_METADATA_TX.begin_change(p_actor,'transport_dispatch_edit');entered:=true;savepoint INCIDENT293;sp:=true;scope(incident.PLAN_OPERATION_ID,p_actor);
  begin select *into saved from RRL_INTERWARE_INCIDENT_CLOSE where OPERATION_ID=p_operation;
   if saved.ACTOR!=p_actor or saved.REQUEST_HASH!=hash or dbms_lob.compare(saved.REQUEST_JSON,p_request)!=0 then raise_application_error(-20886,'INTERWARE_INCIDENT_CLOSE_PAYLOAD_CONFLICT');end if;
   p_result:=saved.RESULT_JSON;RRL_STOCK_METADATA_TX.end_change;return;
  exception when no_data_found then null;end;
  select *into incident from RRL_INTERWARE_DECISION where OPERATION_ID=incident_id;
  if incident.INCIDENT_KIND is null or incident.REVISION_NO!=rev then raise_application_error(-20886,'INTERWARE_INCIDENT_REPORTED_REVISION_REQUIRED');end if;
  select count(*)into n from RRL_INTERWARE_INCIDENT_CLOSE where INCIDENT_OPERATION_ID=incident_id;
  if n!=0 then raise_application_error(-20886,'INTERWARE_INCIDENT_ALREADY_CLOSED');end if;
  select *into receipt from RRL_INTERWARE_RECEIPT where OPERATION_ID=receipt_id;
  select *into plan from RRL_INTERWARE_PLAN where OPERATION_ID=incident.PLAN_OPERATION_ID;
  select RRL_STOCK_MATH.quantity(json_value(plan.SOURCE_COMPOSITION_JSON,'$.nodes[0].quantity'))into declared_qty from dual;
  if receipt.PLAN_OPERATION_ID!=plan.OPERATION_ID or receipt.ROOT_UID!=plan.ROOT_UID or receipt.ORIGINAL_ROOT_UID is not null or receipt.BASE_QTY!=declared_qty or receipt.CREATED_AT<=incident.CREATED_AT then raise_application_error(-20886,'INTERWARE_INCIDENT_ACTUAL_FULL_FOLLOWUP_REQUIRED');end if;
  select count(*)into n from RRL_STOCK_OPERATION o join RRL_EVENTS e on e.OPERATION_ID=o.OPERATION_ID
   where o.OPERATION_ID=receipt_id and o.STATE='APPLIED'and o.COMMAND_TYPE='INTERWARE_RECEIVE'
    and e.ID_EVENT=receipt.STOCK_EVENT_ID and e.UID_POLETA=receipt.ROOT_UID and e.BASE_QTY=receipt.BASE_QTY and e.CELL_TO=receipt.RECEIVE_CELL;
  if n!=1 then raise_application_error(-20886,'INTERWARE_INCIDENT_APPLIED_RECEIPT_EVENT_REQUIRED');end if;
  j:=json_object_t();j.put('operation_id',p_operation);j.put('incident_operation_id',incident_id);j.put('incident_revision',rev);
  j.put('plan_operation_id',plan.OPERATION_ID);j.put('followup_receipt_operation_id',receipt_id);j.put('status','CLOSED_AFTER_FULL_RECEIPT');
  j.put('reason',reason);j.put('evidence_reference',ref);j.put('actor',p_actor);j.put('stock_changed',false);j.put('regulatory_ack_verified',false);p_result:=j.to_clob;
  g_tx:=dbms_transaction.local_transaction_id(false);
  insert into RRL_INTERWARE_INCIDENT_CLOSE(OPERATION_ID,PLAN_OPERATION_ID,INCIDENT_OPERATION_ID,FOLLOWUP_RECEIPT_OPERATION_ID,ACTOR,REASON_TEXT,EVIDENCE_REFERENCE,REQUEST_HASH,REQUEST_JSON,RESULT_JSON)
   values(p_operation,plan.OPERATION_ID,incident_id,receipt_id,p_actor,reason,ref,hash,p_request,p_result);
  g_tx:=null;RRL_STOCK_METADATA_TX.end_change;
 exception when no_data_found then
  g_tx:=null;if sp then rollback to INCIDENT293;end if;if entered then RRL_STOCK_METADATA_TX.end_change;end if;
  raise_application_error(-20886,'INTERWARE_INCIDENT_OR_FOLLOWUP_NOT_FOUND');
 when others then g_tx:=null;if sp then rollback to INCIDENT293;end if;if entered then RRL_STOCK_METADATA_TX.end_change;end if;raise;
 end;
end;
/
create or replace trigger RRL_INTERWARE_INCIDENT_CLOSE_G before insert or update or delete on RRL_INTERWARE_INCIDENT_CLOSE for each row
begin
 if updating or deleting or RRL_INTERWARE_INCIDENT_API.write_allowed!=1 then raise_application_error(-20863,'INTERWARE_INCIDENT_CLOSE_IMMUTABLE_NATIVE_ONLY');end if;
end;
/
