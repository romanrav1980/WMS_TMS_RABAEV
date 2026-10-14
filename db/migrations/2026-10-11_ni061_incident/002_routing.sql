create or replace package RRL_INTERWARE_ROUTING authid definer as
 function target_trip(p_plan varchar2)return number;
 function outbound_dock(p_plan varchar2)return varchar2;
 function ready_due(p_plan varchar2)return timestamp with time zone;
 function resolved(p_plan RRL_INTERWARE_PLAN%rowtype)return RRL_INTERWARE_PLAN%rowtype;
 procedure record_decision(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_INTERWARE_ROUTING as
 function resolved(p_plan RRL_INTERWARE_PLAN%rowtype)return RRL_INTERWARE_PLAN%rowtype is r RRL_INTERWARE_PLAN%rowtype:=p_plan;
 begin
  begin select TARGET_TT_ID,OUTBOUND_DOCK,READY_DUE into r.TARGET_TT_ID,r.OUTBOUND_DOCK,r.READY_DUE from RRL_INTERWARE_DECISION where PLAN_OPERATION_ID=p_plan.OPERATION_ID order by REVISION_NO desc fetch first 1 row only;exception when no_data_found then null;end;
  return r;
 end;
 function target_trip(p_plan varchar2)return number is r RRL_INTERWARE_PLAN%rowtype;
 begin select *into r from RRL_INTERWARE_PLAN where OPERATION_ID=p_plan;r:=resolved(r);return r.TARGET_TT_ID;end;
 function outbound_dock(p_plan varchar2)return varchar2 is r RRL_INTERWARE_PLAN%rowtype;
 begin select *into r from RRL_INTERWARE_PLAN where OPERATION_ID=p_plan;r:=resolved(r);return r.OUTBOUND_DOCK;end;
 function ready_due(p_plan varchar2)return timestamp with time zone is r RRL_INTERWARE_PLAN%rowtype;
 begin select *into r from RRL_INTERWARE_PLAN where OPERATION_ID=p_plan;r:=resolved(r);return r.READY_DUE;end;
 procedure record_decision(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);original RRL_INTERWARE_PLAN%rowtype;current_plan RRL_INTERWARE_PLAN%rowtype;tt RRL_TRANSPORT_TASK%rowtype;j json_object_t:=json_object_t();
  op varchar2(100):=d.get_string('operation_id');plan_id varchar2(100):=d.get_string('plan_operation_id');kind varchar2(10):=d.get_string('decision_kind');requested number:=d.get_number('target_trip_id');rev number;n number;old_hash raw(32);hash_value raw(32):=sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256);arrival timestamp with time zone;ready timestamp with time zone;reason nvarchar2(500):=d.get_string('reason');ref varchar2(60):=d.get_string('decision_reference');incident_kind varchar2(30):=d.get_string('incident_kind');incident_detail nvarchar2(1000):=d.get_string('incident_detail');evidence_reference nvarchar2(200):=d.get_string('evidence_reference');
  procedure scope_check is
  begin select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'transport_dispatch_edit')=1 and(WARE_ID=original.TARGET_WARE_ID or upper(trim(USER_GROUP))='GLOBAL_ADMIN');if n!=1 then raise_application_error(-20882,'INTERWARE_CURRENT_TARGET_DISPATCHER_REQUIRED');end if;end;
 begin
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
  select *into original from RRL_INTERWARE_PLAN where OPERATION_ID=plan_id;
  scope_check;
  begin select PAYLOAD_HASH,RESULT_JSON into old_hash,p_result from RRL_INTERWARE_DECISION where OPERATION_ID=op;if old_hash!=hash_value then raise_application_error(-20871,'INTERWARE_DECISION_PAYLOAD_CONFLICT');end if;return;exception when no_data_found then null;end;
  select *into original from RRL_INTERWARE_PLAN where OPERATION_ID=plan_id for update;current_plan:=resolved(original);
  select nvl(max(REVISION_NO),0)into rev from RRL_INTERWARE_DECISION where PLAN_OPERATION_ID=plan_id;
  if d.get_number('expected_revision')is null or d.get_number('expected_revision')!=rev then raise_application_error(-20890,'CLOSURE_CHANGED: interwarehouse decision revision');end if;
  if kind is null or kind not in('WAIT','DEFER')or trim(reason)is null or trim(ref)is null then raise_application_error(-20871,'INTERWARE_DISPATCHER_DECISION_REQUIRED');end if;
  if incident_kind is null then
   if d.has('incident_detail')or d.has('evidence_reference')then raise_application_error(-20871,'INTERWARE_INCIDENT_KIND_REQUIRED');end if;
  elsif incident_kind not in('TRANSPORT_DELAY','MISSING_PALLET','IDENTIFIER_MISMATCH')or trim(incident_detail)is null or trim(evidence_reference)is null then raise_application_error(-20871,'INTERWARE_INCIDENT_DETAIL_EVIDENCE_REQUIRED');end if;
  arrival:=to_timestamp_tz(d.get_string('expected_arrival'),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');ready:=current_plan.READY_DUE;
  if arrival is null or arrival<systimestamp then raise_application_error(-20886,'INTERWARE_PROSPECTIVE_ARRIVAL_REQUIRED');end if;
  if kind='WAIT'then
   if requested is not null or d.has('ready_due')then raise_application_error(-20871,'INTERWARE_WAIT_RETURNS_SAME_ROUTE');end if;requested:=current_plan.TARGET_TT_ID;
  else
   if requested is null or requested=current_plan.TARGET_TT_ID then raise_application_error(-20886,'INTERWARE_DIFFERENT_EXISTING_TARGET_TRIP_REQUIRED');end if;
   select count(*)into n from RRL_INTERWARE_RECEIPT where PLAN_OPERATION_ID=plan_id;if n>0 then raise_application_error(-20886,'INTERWARE_RECEIVED_CARGO_REASSIGNMENT_TASK_REQUIRED');end if;
   ready:=to_timestamp_tz(d.get_string('ready_due'),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');if ready is null or ready<arrival then raise_application_error(-20886,'INTERWARE_NEW_READY_AFTER_EXPECTED_ARRIVAL_REQUIRED');end if;
  end if;
  for x in(select ID from RRL_TRANSPORT_TASK where ID in(current_plan.TARGET_TT_ID,requested)order by ID)loop select *into tt from RRL_TRANSPORT_TASK where ID=x.ID for update;end loop;
  select *into tt from RRL_TRANSPORT_TASK where ID=current_plan.TARGET_TT_ID;
  if nvl(tt.DELETED,0)!=0 or tt.CONDITION is null or tt.CONDITION!='Спланирован'then raise_application_error(-20886,'INTERWARE_CURRENT_TARGET_TRIP_NOT_PLANNED');end if;
  select *into tt from RRL_TRANSPORT_TASK where ID=requested;
  select count(*)into n from RRL_TT_DOCK where DOCK=tt.DOCK and WARE_ID=original.TARGET_WARE_ID and nvl(DOCK_IS_BLOCKED,0)=0;
  if n!=1 or nvl(tt.DELETED,0)!=0 or tt.CONDITION is null or tt.CONDITION!='Спланирован'then raise_application_error(-20886,'INTERWARE_NEW_PLANNED_TRIP_TARGET_WARE_REQUIRED');end if;
  scope_check;
  j.put('operation_id',op);j.put('plan_operation_id',plan_id);j.put('revision',rev+1);j.put('decision_kind',kind);j.put('original_target_trip_id',original.TARGET_TT_ID);j.put('previous_trip_id',current_plan.TARGET_TT_ID);j.put('target_trip_id',requested);j.put('outbound_dock',tt.DOCK);j.put('expected_arrival',d.get_string('expected_arrival'));j.put('ready_due',to_char(ready,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));j.put('stock_changed',false);
  if incident_kind is not null then j.put('incident_kind',incident_kind);j.put('incident_detail',incident_detail);j.put('evidence_reference',evidence_reference);j.put('incident_basis','OPERATOR_REPORT');j.put('quantity_adjusted',false);end if;
  p_result:=j.to_clob;
  insert into RRL_INTERWARE_DECISION(OPERATION_ID,PLAN_OPERATION_ID,REVISION_NO,DECISION_KIND,PREVIOUS_TT_ID,TARGET_TT_ID,OUTBOUND_DOCK,EXPECTED_ARRIVAL,READY_DUE,REASON_TEXT,DECISION_REFERENCE,ACTOR,PAYLOAD_HASH,CANONICAL_REQUEST,RESULT_JSON,INCIDENT_KIND,INCIDENT_DETAIL,EVIDENCE_REFERENCE)
   values(op,plan_id,rev+1,kind,current_plan.TARGET_TT_ID,requested,tt.DOCK,arrival,ready,reason,ref,p_actor,hash_value,p_request,p_result,incident_kind,incident_detail,evidence_reference);
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_CURRENT_PLAN_TRIP_REQUIRED');
 end;
end;
/
