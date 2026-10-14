from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni061_dispatch_decision")
out[str(f/"001_schema.sql")]="""create table RRL_INTERWARE_DECISION(
 OPERATION_ID varchar2(100)constraint RRL_IW_DECISION_PK primary key,
 PLAN_OPERATION_ID varchar2(100)not null references RRL_INTERWARE_PLAN(OPERATION_ID),
 REVISION_NO number(10)not null,DECISION_KIND varchar2(10)not null check(DECISION_KIND in('WAIT','DEFER')),
 PREVIOUS_TT_ID number not null references RRL_TRANSPORT_TASK(ID),
 TARGET_TT_ID number not null references RRL_TRANSPORT_TASK(ID),OUTBOUND_DOCK varchar2(15)not null,
 EXPECTED_ARRIVAL timestamp with time zone not null,READY_DUE timestamp with time zone not null,
 REASON_TEXT nvarchar2(500)not null,DECISION_REFERENCE varchar2(60)not null,ACTOR nvarchar2(50)not null,
 PAYLOAD_HASH raw(32)not null,CANONICAL_REQUEST clob not null check(CANONICAL_REQUEST is json),
 RESULT_JSON clob not null check(RESULT_JSON is json),CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_IW_DECISION_REV_UK unique(PLAN_OPERATION_ID,REVISION_NO)
);
"""
routing="""create or replace package RRL_INTERWARE_ROUTING authid definer as
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
  op varchar2(100):=d.get_string('operation_id');plan_id varchar2(100):=d.get_string('plan_operation_id');kind varchar2(10):=d.get_string('decision_kind');requested number:=d.get_number('target_trip_id');rev number;n number;old_hash raw(32);hash_value raw(32):=sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256);arrival timestamp with time zone;ready timestamp with time zone;reason nvarchar2(500):=d.get_string('reason');ref varchar2(60):=d.get_string('decision_reference');
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
  arrival:=to_timestamp_tz(d.get_string('expected_arrival'),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');ready:=current_plan.READY_DUE;
  if arrival<systimestamp then raise_application_error(-20886,'INTERWARE_PROSPECTIVE_ARRIVAL_REQUIRED');end if;
  if kind='WAIT'then
   if requested is not null or d.has('ready_due')then raise_application_error(-20871,'INTERWARE_WAIT_RETURNS_SAME_ROUTE');end if;requested:=current_plan.TARGET_TT_ID;
  else
   if requested is null or requested=current_plan.TARGET_TT_ID then raise_application_error(-20886,'INTERWARE_DIFFERENT_EXISTING_TARGET_TRIP_REQUIRED');end if;
   select count(*)into n from RRL_INTERWARE_RECEIPT where PLAN_OPERATION_ID=plan_id;if n>0 then raise_application_error(-20886,'INTERWARE_RECEIVED_CARGO_REASSIGNMENT_TASK_REQUIRED');end if;
   ready:=to_timestamp_tz(d.get_string('ready_due'),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');if ready is null or ready<arrival then raise_application_error(-20886,'INTERWARE_NEW_READY_AFTER_EXPECTED_ARRIVAL_REQUIRED');end if;
  end if;
  for x in(select ID from RRL_TRANSPORT_TASK where ID in(current_plan.TARGET_TT_ID,requested)order by ID)loop select *into tt from RRL_TRANSPORT_TASK where ID=x.ID for update;end loop;
  select *into tt from RRL_TRANSPORT_TASK where ID=current_plan.TARGET_TT_ID;
  if nvl(tt.DELETED,0)!=0 or tt.CONDITION!='Спланирован'then raise_application_error(-20886,'INTERWARE_CURRENT_TARGET_TRIP_NOT_PLANNED');end if;
  select *into tt from RRL_TRANSPORT_TASK where ID=requested;
  select count(*)into n from RRL_TT_DOCK where DOCK=tt.DOCK and WARE_ID=original.TARGET_WARE_ID and nvl(DOCK_IS_BLOCKED,0)=0;
  if n!=1 or nvl(tt.DELETED,0)!=0 or tt.CONDITION!='Спланирован'then raise_application_error(-20886,'INTERWARE_NEW_PLANNED_TRIP_TARGET_WARE_REQUIRED');end if;
  scope_check;
  j.put('operation_id',op);j.put('plan_operation_id',plan_id);j.put('revision',rev+1);j.put('decision_kind',kind);j.put('original_target_trip_id',original.TARGET_TT_ID);j.put('previous_trip_id',current_plan.TARGET_TT_ID);j.put('target_trip_id',requested);j.put('outbound_dock',tt.DOCK);j.put('expected_arrival',d.get_string('expected_arrival'));j.put('ready_due',to_char(ready,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));j.put('stock_changed',false);p_result:=j.to_clob;
  insert into RRL_INTERWARE_DECISION(OPERATION_ID,PLAN_OPERATION_ID,REVISION_NO,DECISION_KIND,PREVIOUS_TT_ID,TARGET_TT_ID,OUTBOUND_DOCK,EXPECTED_ARRIVAL,READY_DUE,REASON_TEXT,DECISION_REFERENCE,ACTOR,PAYLOAD_HASH,CANONICAL_REQUEST,RESULT_JSON)
   values(op,plan_id,rev+1,kind,current_plan.TARGET_TT_ID,requested,tt.DOCK,arrival,ready,reason,ref,p_actor,hash_value,p_request,p_result);
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_CURRENT_PLAN_TRIP_REQUIRED');
 end;
end;
/
"""
out[str(f/"002_routing.sql")]=routing
out[str(f/"003_guard.sql")]="""create or replace trigger RRL_INTERWARE_DECISION_GUARD before insert or update or delete on RRL_INTERWARE_DECISION for each row
declare n number;begin
 if not inserting then raise_application_error(-20863,'INTERWARE_DISPATCH_DECISION_IMMUTABLE');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 select count(*)into n from RRL_INTERWARE_PLAN p join RUSERS u on u.ID=:new.ACTOR where p.OPERATION_ID=:new.PLAN_OPERATION_ID and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_edit')=1 and(u.WARE_ID=p.TARGET_WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
 if n!=1 then raise_application_error(-20882,'INTERWARE_CURRENT_TARGET_DISPATCHER_REQUIRED');end if;
 select nvl(max(REVISION_NO),0)+1 into n from RRL_INTERWARE_DECISION where PLAN_OPERATION_ID=:new.PLAN_OPERATION_ID;
 if :new.REVISION_NO!=n then raise_application_error(-20890,'CLOSURE_CHANGED: interwarehouse decision revision');end if;
end;
/
"""
# Row trigger cannot select its own mutating table; unique revision and recorder enforce sequence.
out[str(f/"003_guard.sql")]=out[str(f/"003_guard.sql")].replace(" select nvl(max(REVISION_NO),0)+1 into n from RRL_INTERWARE_DECISION where PLAN_OPERATION_ID=:new.PLAN_OPERATION_ID;\n if :new.REVISION_NO!=n then raise_application_error(-20890,'CLOSURE_CHANGED: interwarehouse decision revision');end if;\n","")
gate="""create or replace package RRL_INTERWARE_DEPART_GATE authid definer as
 function promises(p_trip number)return clob;
 procedure assert_ready(p_promises clob);
end;
/
create or replace package body RRL_INTERWARE_DEPART_GATE as
 function promises(p_trip number)return clob is a json_array_t:=json_array_t();j json_object_t;n number;count_value number:=0;
 begin
  for p in(select OPERATION_ID from RRL_INTERWARE_PLAN where RRL_INTERWARE_ROUTING.target_trip(OPERATION_ID)=p_trip order by OPERATION_ID fetch first 201 rows only)loop
   count_value:=count_value+1;if count_value>200 then raise_application_error(-20881,'INTERWARE_DEPART_PROMISE_BOUND_200');end if;
   select count(*)into n from RRL_INTERWARE_RECEIPT r join RRL_INTERWARE_ONWARD_BIND b on b.RECEIPT_OPERATION_ID=r.OPERATION_ID join RRL_TT_HU_LOAD_ST m on m.SBORKA_PALLET_ID=b.ST_ID and m.ACTIVE_FLAG=1 join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=m.LOAD_OPERATION_ID where r.PLAN_OPERATION_ID=p.OPERATION_ID and l.TT_ID=p_trip and l.STATUS='LOADED';
   j:=json_object_t();j.put('plan_operation_id',p.OPERATION_ID);j.put('physically_loaded',n=1);a.append(j);
  end loop;
  return a.to_clob;
 end;
 procedure assert_ready(p_promises clob)is a json_array_t:=json_array_t.parse(p_promises);j json_object_t;
 begin
  for i in 0..a.get_size-1 loop j:=treat(a.get(i)as json_object_t);if not j.get_boolean('physically_loaded')then raise_application_error(-20886,'DEPART_EXPECTED_INTERWARE_CARGO_NOT_READY: '||j.get_string('plan_operation_id'));end if;end loop;
 end;
end;
/
"""
out[str(f/"004_depart_gate.sql")]=gate
s=(f/"000_before_rrl_stock_trip_depart_cmd.sql").read_text(encoding="utf-8").replace("n number:=0;","n number:=0;promise_wire clob;",1)
s=s.replace("  select * into tt from RRL_TRANSPORT_TASK where ID=trip_no;","  promise_wire:=RRL_INTERWARE_DEPART_GATE.promises(trip_no);RRL_INTERWARE_DEPART_GATE.assert_ready(promise_wire);\n  select * into tt from RRL_TRANSPORT_TASK where ID=trip_no;",1)
s=s.replace("  v.put('trip',trip_no);","  v.put('incoming_promises',json_array_t.parse(promise_wire));\n  v.put('trip',trip_no);",1)
s=s.replace("dock_name varchar2(50);","dock_name varchar2(50);promise_wire clob;",1)
s=s.replace("  for sp in(select ID from RRL_SBORKA_PALLETS", "  for sp in(select ID from RRL_SBORKA_PALLETS",1)
idx=s.index("  for sp in(select ID from RRL_SBORKA_PALLETS",s.index(" procedure execute_command",s.index("package body")))
s=s[:idx]+"""  promise_wire:=RRL_INTERWARE_DEPART_GATE.promises(trip_no);RRL_INTERWARE_DEPART_GATE.assert_ready(promise_wire);
  if dbms_lob.compare(promise_wire,v.get_array('incoming_promises').to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: expected incoming cargo');end if;
"""+s[idx:];out[str(f/"005_depart.sql")]=s
for name,file in[("RRL_STOCK_INTERWARE_REC","006_receiving.sql"),("RRL_STOCK_INTERWARE_PUT","007_placement.sql")]:
 s=(f/("000_before_"+name.lower()+".sql")).read_text(encoding="utf-8")
 needle=" select *into plan from RRL_INTERWARE_PLAN where OPERATION_ID=receipt.PLAN_OPERATION_ID;"
 if name.endswith("_REC"):needle=" select * into plan from RRL_INTERWARE_PLAN where OPERATION_ID=v_plan;"
 assert needle in s,name;s=s.replace(needle,needle+"\n plan:=RRL_INTERWARE_ROUTING.resolved(plan);",1);out[str(f/file)]=s
s=(f/"000_before_rrl_interware_onward_bind_guard.sql").read_text(encoding="utf-8").replace("p.TARGET_TT_ID=:new.TARGET_TT_ID","RRL_INTERWARE_ROUTING.target_trip(p.OPERATION_ID)=:new.TARGET_TT_ID",1);out[str(f/"008_onward_guard.sql")]=s
out["wiki/database/retailcase_ni061_dispatch_decision_design_20261011.md"]="# NI06.1: решение диспетчера по задержанному подвозу\n239 adds append-only WAIT/DEFER history/current target dispatcher/WARE/revision/expected arrival. Original plan/departure identity retained. DEFER only before physical receipt, to another existing planned trip/same warehouse/dock/new ready deadline; no changing moving warehouse task. Pure routing resolver feeds original receive/putaway/onward ST/queue. Existing departure refuses unfulfilled incoming promise before departure and rechecks frozen promises under current TT/CONFIG locks. Original loaded ST/capacity/driver checks remain. No stock/assignment clone or legal ACK.\n"
print(json.dumps(out,ensure_ascii=True))
