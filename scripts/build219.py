raise SystemExit("Retired authoring generator: use final219 SQL and fresh capture; never overwrite checkpoint/live owners")
from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni063_offer_cancel");out={}
out["wiki/database/nicora_ni063_offer_cancel_design_20261011.md"]="""# NI06.3: отмена непринятой передачи
219 original TARE_OFFER remains immutable; append-only cancellation unique by source offer and operation, original booked-place links retained. Only original sender with current holder/right or current GLOBAL_ADMIN may cancel; exact vehicle scan/reason, no acceptance/departed booked load. Root checks current scope before replay and after locks. Same ROW offer mutex as ACCEPT, plus original trip/vehicle/books/load rows; native fresh source recheck after locks. No balance or goods journal effect. Cancelled offer cannot accept or obstruct unload/new pending offer; accepted offer must follow actual reverse transfer/recovery. Readers exclude cancelled offers from pending forecasts/reconciliation but retain visible history. No new ledger/physical writer. Fresh capture219 and refusal rollback after history.
"""
out[str(f/"001_schema.sql")]="""create table RRL_TARE_OFFER_CANCEL(
 OPERATION_ID varchar2(100)primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 OFFER_OPERATION_ID varchar2(100)not null unique references RRL_TARE_OFFER(OPERATION_ID),
 REASON nvarchar2(500)not null,CANCELLED_BY nvarchar2(50)not null,
 CANCELLED_AT timestamp with time zone default systimestamp not null
);
"""
out[str(f/"002_cancel.sql")]="""create or replace package RRL_STOCK_TARE_CANCEL_CMD authid definer accessible by(package RRL_STOCK_POSTING_API)as
 procedure assert_scope(p_request clob,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_TARE_CANCEL_CMD as
 procedure assert_scope(p_request clob,p_actor varchar2)is
  d json_object_t:=json_object_t.parse(p_request);o RRL_TARE_OFFER%rowtype;t RRL_TRANSPORT_TASK%rowtype;n number;
 begin
  select *into o from RRL_TARE_OFFER where OPERATION_ID=d.get_object('source').get_string('offer_operation_id');
  select *into t from RRL_TRANSPORT_TASK where ID=o.TT_ID;
  if RRL_HAS_WRIGHT(p_actor,'tare_offer')!=1 then raise_application_error(-20882,'TARE_CANCEL_CURRENT_PERMISSION_REQUIRED');end if;
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and upper(trim(USER_GROUP))='GLOBAL_ADMIN';
  if n=0 then
   if p_actor!=o.OFFERED_BY then raise_application_error(-20882,'TARE_CANCEL_ORIGINAL_SENDER_REQUIRED');end if;
   RRL_TARE_PARTICIPANT.holder_actor(p_actor,o.FROM_KIND,o.FROM_ID,o.OWNER_WARE_ID,t,'tare_offer');
  end if;
 exception when no_data_found then raise_application_error(-20886,'TARE_CANCEL_ORIGINAL_OFFER_REQUIRED');end;
 function describe_command(p_request clob,p_actor varchar2)return json_object_t is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');j json_object_t:=json_object_t();a json_array_t:=json_array_t();x json_object_t;
  id varchar2(100):=d.get_object('source').get_string('offer_operation_id');o RRL_TARE_OFFER%rowtype;t RRL_TRANSPORT_TASK%rowtype;veh RRL_TR_VEHICLE%rowtype;n number;
 begin
  assert_scope(p_request,p_actor);select *into o from RRL_TARE_OFFER where OPERATION_ID=id;
  select count(*)into n from RRL_TARE_ACCEPT where OFFER_OPERATION_ID=id;
  if n!=0 then raise_application_error(-20886,'TARE_CANCEL_ACCEPTED_RETURN_REQUIRED');end if;
  select count(*)into n from RRL_TARE_OFFER_CANCEL where OFFER_OPERATION_ID=id;
  if n!=0 then raise_application_error(-20886,'TARE_OFFER_ALREADY_CANCELLED');end if;
  if trim(m.get_string('reason'))is null or length(m.get_string('reason'))>500 or m.get_string('scan_vehicle')is null or m.get_string('scan_vehicle')!=o.VEHICLE_NUMBER then raise_application_error(-20886,'TARE_CANCEL_REASON_ORIGINAL_VEHICLE_SCAN_REQUIRED');end if;
  select *into t from RRL_TRANSPORT_TASK where ID=o.TT_ID;
  select *into veh from RRL_TR_VEHICLE where ID=o.VEHICLE_ID;
  if nvl(t.DELETED,0)!=0 or t.TRANSPORT!=o.VEHICLE_NUMBER or nvl(veh.DELETED,0)!=0 or veh.NUM!=o.VEHICLE_NUMBER then raise_application_error(-20886,'TARE_CANCEL_CURRENT_ORIGINAL_TRIP_REQUIRED');end if;
  for b in(select ob.BOOK_OPERATION_ID,ob.LOAD_OPERATION_ID,tb.STATUS,lf.STATUS LOAD_STATUS,lf.DEPARTURE_OPERATION_ID from RRL_TARE_OFFER_BOOK ob join RRL_TARE_BOOK tb on tb.OPERATION_ID=ob.BOOK_OPERATION_ID join RRL_TT_HU_LOAD_FACT lf on lf.LOAD_OPERATION_ID=ob.LOAD_OPERATION_ID where ob.OFFER_OPERATION_ID=id order by ob.BOOK_OPERATION_ID)loop
   if b.STATUS!='HELD'or b.LOAD_STATUS!='LOADED'or b.DEPARTURE_OPERATION_ID is not null then raise_application_error(-20886,'TARE_CANCEL_HELD_UNDEPARTED_BOOK_REQUIRED');end if;
   x:=json_object_t();x.put('book',b.BOOK_OPERATION_ID);x.put('load',b.LOAD_OPERATION_ID);a.append(x);
   if a.get_size>100 then raise_application_error(-20881,'TARE_CANCEL_BOOK_BOUND_100');end if;
  end loop;
  j.put('offer_operation_id',id);j.put('task_id',o.TT_ID);j.put('vehicle_id',o.VEHICLE_ID);j.put('warehouse_id',o.OWNER_WARE_ID);j.put('books',a);j.put('reason',m.get_string('reason'));j.put('vehicle',o.VEHICLE_NUMBER);return j;
 exception when no_data_found then raise_application_error(-20886,'TARE_CANCEL_ORIGINAL_CONTEXT_REQUIRED');end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob)is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t;x json_object_t;
 begin
  v:=describe_command(p_request,d.get_string('actor'));RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_OFFER',v.get_string('offer_operation_id'));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_OFFER_CANCEL',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TRANSPORT_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('task_id')));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TR_VEHICLE',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('vehicle_id')));
  a:=v.get_array('books');
  for i in 0..a.get_size-1 loop x:=treat(a.get(i)as json_object_t);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_BOOK',x.get_string('book'));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_HU_LOAD_FACT',x.get_string('load'));
  end loop;
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');wire clob;v json_object_t;fresh json_object_t;j json_object_t:=json_object_t();offer_id varchar2(100);reason_value nvarchar2(500);
 begin
  select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(wire).get_object('domain');
  fresh:=describe_command(p_request,p_actor);
  if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: tare cancellation');end if;
  offer_id:=v.get_string('offer_operation_id');reason_value:=v.get_string('reason');
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TARE_OFFER',offer_id));
  insert into RRL_TARE_OFFER_CANCEL(OPERATION_ID,OFFER_OPERATION_ID,REASON,CANCELLED_BY)values(op,offer_id,reason_value,p_actor);
  j.put('operation_id',op);j.put('offer_operation_id',offer_id);j.put('status','CANCELLED');j.put('tare_balance_changed',false);j.put('original_offer_preserved',true);p_result:=j.to_clob;
 end;
end;
/
"""
s=(f/"000_before_rrl_stock_posting_api.sql").read_text(encoding="utf-8")
anchor="  assert_actor_active(p_actor);";assert s.count(anchor)==2;s=s.replace(anchor,anchor+"\n  if g_kind='TARE_OFFER_CANCEL'then RRL_STOCK_TARE_CANCEL_CMD.assert_scope(p_request,p_actor);end if;")
anchor="  elsif g_kind in('TARE_COUNT','TARE_OFFER','TARE_ACCEPT') then"
assert s.count(anchor)==2
s=s.replace(anchor+" RRL_STOCK_TARE_CMD.compile_command", "  elsif g_kind='TARE_OFFER_CANCEL'then RRL_STOCK_TARE_CANCEL_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n"+anchor+" RRL_STOCK_TARE_CMD.compile_command",1)
s=s.replace(anchor+" RRL_STOCK_TARE_CMD.execute_command", "  elsif g_kind='TARE_OFFER_CANCEL'then RRL_STOCK_TARE_CANCEL_CMD.execute_command(g_request,g_actor,p_result);\n"+anchor+" RRL_STOCK_TARE_CMD.execute_command",1)
out[str(f/"003_root.sql")]=s
s=(f/"000_before_rrl_stock_tare_cmd.sql").read_text(encoding="utf-8")
anchor="   select count(*) into n from RRL_TARE_ACCEPT where OFFER_OPERATION_ID=offer.OPERATION_ID;"
assert anchor in s;s=s.replace(anchor,"   select count(*)into n from RRL_TARE_OFFER_CANCEL where OFFER_OPERATION_ID=offer.OPERATION_ID;\n   if n!=0 then raise_application_error(-20886,'TARE_CANCELLED_OFFER_CANNOT_ACCEPT');end if;\n"+anchor,1);out[str(f/"004_tare.sql")]=s
s=(f/"000_before_rrl_stock_tare_handover.sql").read_text(encoding="utf-8");anchor="  if book.OWNER_WARE_ID!=p_owner";idx=s.index(anchor)
s=s[:idx]+"""  if p_kind='TARE_OFFER'then
   select count(*)into n from RRL_TARE_OFFER_BOOK ob where ob.BOOK_OPERATION_ID=v_id and not exists(select 1 from RRL_TARE_OFFER_CANCEL c where c.OFFER_OPERATION_ID=ob.OFFER_OPERATION_ID);
   if n>0 then raise_application_error(-20886,'TARE_BOOK_HAS_ACTIVE_HANDOVER_OFFER');end if;
  end if;
"""+s[idx:];out[str(f/"005_handover.sql")]=s
s=(f/"000_before_rrl_stock_unload_cmd.sql").read_text(encoding="utf-8");old="where LOAD_OPERATION_ID=p_load and not exists(";assert old in s;s=s.replace(old,"where LOAD_OPERATION_ID=p_load and not exists(select 1 from RRL_TARE_OFFER_CANCEL cancelled where cancelled.OFFER_OPERATION_ID=old_offer.OFFER_OPERATION_ID)and not exists(",1)
anchor="  for proof in(select OPERATION_ID,ORIGINAL_BOOK_OPERATION_ID"
idx=s.index(anchor);s=s[:idx]+"""  for association in(select ob.OFFER_OPERATION_ID,c.OPERATION_ID CANCEL_ID from RRL_TARE_OFFER_BOOK ob left join RRL_TARE_OFFER_CANCEL c on c.OFFER_OPERATION_ID=ob.OFFER_OPERATION_ID where ob.LOAD_OPERATION_ID=load_id order by ob.OFFER_OPERATION_ID)loop
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_OFFER',association.OFFER_OPERATION_ID);
   if association.CANCEL_ID is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_OFFER_CANCEL',association.CANCEL_ID);end if;
  end loop;
"""+s[idx:];out[str(f/"006_unload.sql")]=s
out[str(f/"007_guard.sql")]="""create or replace trigger RRL_TARE_OFFER_CANCEL_GUARD before insert or update or delete on RRL_TARE_OFFER_CANCEL for each row
declare wire clob;v json_object_t;
begin
 if not inserting then raise_application_error(-20863,'TARE_OFFER_CANCEL_IMMUTABLE');end if;
 if :new.OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')then raise_application_error(-20863,'TARE_OFFER_CANCEL_ROOT_REQUIRED');end if;
 RRL_TARE_ASSERT_WRITE('RRL_TARE_OFFER_CANCEL',:new.OPERATION_ID,'TARE_OFFER_CANCEL');
 select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=:new.OPERATION_ID;v:=json_object_t.parse(wire).get_object('domain');
 if v.get_string('offer_operation_id')!=:new.OFFER_OPERATION_ID or v.get_string('reason')!=:new.REASON or :new.CANCELLED_BY!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'TARE_OFFER_CANCEL_EXACT_PLAN_REQUIRED');end if;
end;
/
"""
out[str(f/"rollback.sql")]="""declare n number;begin select count(*)into n from RRL_TARE_OFFER_CANCEL;if n>0 then raise_application_error(-20863,'TARE_CANCEL_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_rrl_stock_posting_api.sql
@@000_before_rrl_stock_tare_cmd.sql
@@000_before_rrl_stock_tare_handover.sql
@@000_before_rrl_stock_unload_cmd.sql
drop package RRL_STOCK_TARE_CANCEL_CMD;
drop table RRL_TARE_OFFER_CANCEL;
"""
out[str(f/"verify.sql")]="select name,type,line,position,text from user_errors where name not like 'BIN$%';\nselect object_name,object_type from user_objects where status='INVALID';\n"
out[str(f/"apply.sql")]="".join("@@"+name+"\n"for name in["001_schema.sql","002_cancel.sql","003_root.sql","004_tare.sql","005_handover.sql","006_unload.sql","007_guard.sql"])
print(json.dumps(out,ensure_ascii=True))
