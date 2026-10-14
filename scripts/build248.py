from pathlib import Path
import json
f="db/migrations/2026-10-11_ni081_trip_time/"
out={}
out[f+"001_schema.sql"]="""create table RRL_TT_TIME_APPROVAL(
 TT_ID number not null references RRL_TRANSPORT_TASK(ID),VERSION_NO number not null,
 OPERATION_ID varchar2(100)not null unique,ACTOR varchar2(50)not null,
 REQUEST_HASH varchar2(64)not null,SOURCE_HASH varchar2(64)not null,
 TIME_ZONE varchar2(50)not null,REASON nvarchar2(500)not null,
 RESULT_JSON clob not null check(RESULT_JSON is json),
 CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TT_TIME_APPROVAL_PK primary key(TT_ID,VERSION_NO),
 constraint RRL_TT_TIME_APPROVAL_VER_CK check(VERSION_NO>0),
 constraint RRL_TT_TIME_APPROVAL_TZ_CK check(TIME_ZONE in('UTC','Europe/Moscow','Asia/Tbilisi'))
);
/
"""
out[f+"002_api.sql"]="""create or replace package RRL_TT_TIME_API authid definer as
 function write_allowed(p_operation varchar2)return number;
 procedure context(p_trip number,p_actor varchar2,p_result out clob);
 procedure approve(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob);
end;
/
create or replace package body RRL_TT_TIME_API as
 g_operation varchar2(100);g_tx varchar2(100);
 function write_allowed(p_operation varchar2)return number is begin
  if g_operation=p_operation and g_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;
 end;
 procedure scope(p_trip number,p_actor varchar2)is w RRL_TRANSPORT_TASK%rowtype;n number:=0;allowed number;begin
  select count(*)into allowed from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'transport_dispatch_edit')=1;
  if allowed!=1 then raise_application_error(-20882,'TT_TIME_ACTIVE_DISPATCHER_REQUIRED');end if;
  select *into w from RRL_TRANSPORT_TASK where ID=p_trip;
  for member in(select ID,WARE_ID from RRL_SBORKA_PALLETS where TRANSTASK_ID=p_trip order by ID fetch first 201 rows only)loop
   n:=n+1;if n>200 then raise_application_error(-20886,'TT_TIME_MEMBER_BOUND_200');end if;
   RRL_TRANSPORT_PLAN_RULES.assert_actor(p_actor,member.WARE_ID);
  end loop;
  if n=0 and nvl(w.USER_ID,'~')!=p_actor then
   select count(*)into allowed from RUSERS where ID=p_actor and upper(trim(USER_GROUP))='GLOBAL_ADMIN';
   if allowed!=1 then raise_application_error(-20882,'TT_TIME_EMPTY_TRIP_OWNER_REQUIRED');end if;
  end if;
 end;
 procedure snapshot(p_trip number,p_source out clob,p_hash out varchar2)is
  w RRL_TRANSPORT_TASK%rowtype;b json_object_t:=json_object_t();a json_array_t:=json_array_t();o json_object_t;n number:=0;
 begin
  select *into w from RRL_TRANSPORT_TASK where ID=p_trip;
  b.put('trip_id',p_trip);b.put('vehicle_num',w.TRANSPORT);b.put('driver_id',w.VODITEL_ID);b.put('dock',w.DOCK);
  b.put('condition',w.CONDITION);b.put('deleted',w.DELETED);b.put('pay_order_id',w.PAY_ORDER_ID);
  b.put('shipment_date',to_char(w.SHIPMENT_DATE,'YYYY-MM-DD HH24:MI:SS'));b.put('shipment_time',to_char(w.SHIPMENT_TIME,'YYYY-MM-DD HH24:MI:SS'));
  for member in(select ID,ST_NUMBER,WARE_ID,CONDITION,PALLET_UID from RRL_SBORKA_PALLETS where TRANSTASK_ID=p_trip order by ID fetch first 201 rows only)loop
   n:=n+1;if n>200 then raise_application_error(-20886,'TT_TIME_MEMBER_BOUND_200');end if;
   o:=json_object_t();o.put('id',member.ID);o.put('st_number',member.ST_NUMBER);o.put('warehouse_id',member.WARE_ID);
   o.put('condition',member.CONDITION);o.put('pallet_identifier',member.PALLET_UID);a.append(o);
  end loop;
  b.put('members',a);a:=json_array_t();n:=0;
  for op in(select *from RRL_TT_OPERATIONS where TT_ID=p_trip order by ORD,ID fetch first 201 rows only)loop
   n:=n+1;if n>200 then raise_application_error(-20886,'TT_TIME_OPERATION_BOUND_200');end if;
   o:=json_object_t();o.put('operation_id',op.ID);o.put('code',op.OPERATION_CODE);o.put('ordinal',op.ORD);o.put('duration_min',op.DURATION_MIN);
   o.put('plan_start',to_char(op.PLAN_START,'YYYY-MM-DD HH24:MI:SS'));o.put('plan_end',to_char(op.PLAN_END,'YYYY-MM-DD HH24:MI:SS'));
   o.put('fact_start',to_char(op.FACT_START,'YYYY-MM-DD HH24:MI:SS'));o.put('fact_end',to_char(op.FACT_END,'YYYY-MM-DD HH24:MI:SS'));a.append(o);
  end loop;
  b.put('operations',a);p_source:=b.to_clob;
  p_hash:=lower(rawtohex(sys.dbms_crypto.hash(p_source,sys.dbms_crypto.hash_sh256)));
 end;
 procedure context(p_trip number,p_actor varchar2,p_result out clob)is
  src clob;hash varchar2(64);v_version number;saved RRL_TT_TIME_APPROVAL%rowtype;b json_object_t:=json_object_t();
 begin
  scope(p_trip,p_actor);snapshot(p_trip,src,hash);
  select nvl(max(VERSION_NO),0)into v_version from RRL_TT_TIME_APPROVAL where TT_ID=p_trip;
  b.put('trip_id',p_trip);b.put('source_hash',hash);b.put('version',v_version);b.put('source',json_object_t.parse(src));
  b.put('approval_status','NO_APPROVAL');b.put('operational_admission',false);
  if v_version>0 then
   select *into saved from RRL_TT_TIME_APPROVAL where TT_ID=p_trip and VERSION_NO=v_version;
   if saved.SOURCE_HASH=hash then b.put('approval_status','APPROVED');else b.put('approval_status','SOURCE_CHANGED');end if;
   b.put('last_approval',json_object_t.parse(saved.RESULT_JSON));
  end if;
  p_result:=b.to_clob;
 end;
 procedure approve(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob)is
  b json_object_t;w RRL_TRANSPORT_TASK%rowtype;saved RRL_TT_TIME_APPROVAL%rowtype;
  v_trip number;v_version number;v_req_hash varchar2(64);v_source clob;v_source_hash varchar2(64);v_zone varchar2(50);v_reason nvarchar2(500);
  v_metadata boolean:=false;n number;v_start date;v_finish date;v_aware clob;result json_object_t:=json_object_t();
 begin
  if p_operation is null or lengthb(p_operation)>100 or not regexp_like(p_operation,'^[A-Za-z0-9_.:-]+$')or p_body is null or dbms_lob.getlength(p_body)>2000 then raise_application_error(-20886,'TT_TIME_INPUT_BOUND');end if;
  b:=json_object_t.parse(p_body);v_trip:=b.get_number('trip_id');scope(v_trip,p_actor);
  v_req_hash:=lower(rawtohex(sys.dbms_crypto.hash(p_body,sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_METADATA_TX.begin_change(p_actor,'transport_dispatch_edit');v_metadata:=true;savepoint RRL_TT_TIME248;
  select *into w from RRL_TRANSPORT_TASK where ID=v_trip for update;scope(v_trip,p_actor);
  begin
   select *into saved from RRL_TT_TIME_APPROVAL where OPERATION_ID=p_operation;
   if saved.ACTOR!=p_actor or saved.TT_ID!=v_trip or saved.REQUEST_HASH!=v_req_hash then raise_application_error(-20886,'TT_TIME_OPERATION_PAYLOAD_CONFLICT');end if;
   p_result:=saved.RESULT_JSON;RRL_STOCK_METADATA_TX.end_change;return;
  exception when no_data_found then null;end;
  snapshot(v_trip,v_source,v_source_hash);
  select nvl(max(VERSION_NO),0)into v_version from RRL_TT_TIME_APPROVAL where TT_ID=v_trip;
  if b.get_number('expected_version')is null or b.get_number('expected_version')!=v_version or b.get_string('source_hash')is null or b.get_string('source_hash')!=v_source_hash then raise_application_error(-20886,'TT_TIME_SOURCE_CHANGED');end if;
  if nvl(w.DELETED,0)!=0 or w.CONDITION is null or w.CONDITION!='Спланирован'or nvl(w.PAY_ORDER_ID,0)>0 or w.TRANSPORT is null or w.VODITEL_ID is null or w.VODITEL_ID<=0 then raise_application_error(-20886,'TT_TIME_CURRENT_PLANNED_VEHICLE_DRIVER_REQUIRED');end if;
  select count(*)into n from RRL_TT_HU_LOAD_FACT where TT_ID=v_trip and STATUS in('LOADED','DEPARTED');
  if n>0 then raise_application_error(-20886,'TT_TIME_PHYSICAL_EXECUTION_FROZEN');end if;
  select count(*),min(PLAN_START),max(PLAN_END)into n,v_start,v_finish from RRL_TT_OPERATIONS where TT_ID=v_trip;
  if n<1 or n>200 or v_start is null or v_finish is null or v_finish<=v_start or v_finish-v_start>7 then raise_application_error(-20886,'TT_TIME_POSITIVE_BOUNDED_CHAIN_REQUIRED');end if;
  select count(*)into n from RRL_TT_OPERATIONS where TT_ID=v_trip and(PLAN_START is null or PLAN_END is null or PLAN_END<PLAN_START or FACT_START is not null or FACT_END is not null);
  if n>0 then raise_application_error(-20886,'TT_TIME_VALID_UNSTARTED_CHAIN_REQUIRED');end if;
  v_zone:=b.get_string('time_zone');v_reason:=b.get_string('reason');
  if v_zone is null or v_zone not in('UTC','Europe/Moscow','Asia/Tbilisi')then raise_application_error(-20886,'TT_TIME_EXPLICIT_REGION_REQUIRED');end if;
  if v_reason is null or length(trim(v_reason))<8 then raise_application_error(-20886,'TT_TIME_REASON_REQUIRED');end if;
  select json_arrayagg(json_object(
   'operation_id'value ID,'code'value OPERATION_CODE,'ordinal'value ORD,
   'start_at'value to_char(from_tz(cast(PLAN_START as timestamp),v_zone),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'),
   'finish_at'value to_char(from_tz(cast(PLAN_END as timestamp),v_zone),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')
   returning clob)order by ORD,ID returning clob)into v_aware from RRL_TT_OPERATIONS where TT_ID=v_trip;
  result.put('trip_id',v_trip);result.put('version',v_version+1);result.put('operation_id',p_operation);result.put('source_hash',v_source_hash);
  result.put('time_zone',v_zone);result.put('reason',v_reason);result.put('actor',p_actor);
  result.put('operations',json_array_t.parse(v_aware));result.put('approval_basis','EXPLICIT_ORIGINAL_PLANNED_WALL_TIMES');
  result.put('operational_admission',false);result.put('stock_changed',false);
  p_result:=result.to_clob;g_operation:=p_operation;g_tx:=dbms_transaction.local_transaction_id(false);
  insert into RRL_TT_TIME_APPROVAL(TT_ID,VERSION_NO,OPERATION_ID,ACTOR,REQUEST_HASH,SOURCE_HASH,TIME_ZONE,REASON,RESULT_JSON)
   values(v_trip,v_version+1,p_operation,p_actor,v_req_hash,v_source_hash,v_zone,v_reason,p_result);
  g_operation:=null;g_tx:=null;RRL_STOCK_METADATA_TX.end_change;
 exception when others then
  if v_metadata then rollback to RRL_TT_TIME248;end if;g_operation:=null;g_tx:=null;
  if v_metadata then RRL_STOCK_METADATA_TX.end_change;end if;raise;
 end;
end;
/
"""
out[f+"003_guard.sql"]="""create or replace trigger RRL_TT_TIME_APPROVAL_GUARD before insert or update or delete on RRL_TT_TIME_APPROVAL for each row
begin
 if not inserting or RRL_TT_TIME_API.write_allowed(:new.OPERATION_ID)!=1 then raise_application_error(-20863,'TT_TIME_APPROVAL_IMMUTABLE');end if;
end;
/
"""
out[f+"apply.sql"]="@001_schema.sql\n@002_api.sql\n@003_guard.sql\n"
out[f+"rollback.sql"]="""declare n number;begin
 select count(*)into n from RRL_TT_TIME_APPROVAL;
 if n>0 then raise_application_error(-20886,'TT_TIME_APPROVAL_FACTS_REMAIN_NO_DROP');end if;
end;
/
drop trigger RRL_TT_TIME_APPROVAL_GUARD;
/
drop package RRL_TT_TIME_API;
/
drop table RRL_TT_TIME_APPROVAL;
/
"""
for path,line in [("wiki/index.md","- [Утверждение времени ARM: проект решения248](database/nicora_ni081_trip_time_design_20261011.md): original source hash/immutable version/current scope/CFG-TT; implementation in progress."),("wiki/log.md","2026-10-11:248 design for explicit approval of original ARM wall-time interpretation: immutable metadata version/source hash/current scope/bounded original TT/OPS, no calendar replacement/quantity or legal admission. Implementation in progress; no APPLIED claim.")]:
 out[path]=Path(path).read_text(encoding="utf-8")+"\n"+line+"\n"
print(json.dumps(out,ensure_ascii=True))
