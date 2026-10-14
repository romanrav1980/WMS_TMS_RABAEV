from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni063_load_recovery");out={}
out["wiki/database/retailcase_ni063_load_recovery_design_20261011.md"]="""# NI06.3/NI05.2: возвращённая тара исходной погрузки
216 reuses existing vehicle→warehouse TARE_OFFER/TARE_ACCEPT two-participant quantitative return, then existing TARE_BOOK with an optional strict load_recovery proof. CASE-only original transferred book, same original LOADED predeparture load/vehicle/trip/warehouse/type/GOOD/one accepted returned quantity, original CASE epoch/SSCC. Exact return offer can fund one new book, original transferred book recovered once. Immutable recovery proof connects all original facts and new HELD book; no original terminal book/transfer reactivation. Current tare_plan/warehouse before replay/after wait via private helper. Native booking owns current balance mutex/available hold/version; declared original load/book/offer/accept/proof/source uniqueness prevents race with unload/departure/another recovery. Unload permits transferred tare only while corresponding new original-place recovery book still HELD and declared. Pending/unaccepted return/wrong type/store/departed/incomplete coverage refused. No goods quantity during tare return/booking; original stock unload changes P/H once later. Fresh source/paired forward repair.
"""
out[str(f/"001_schema.sql")]="""create table RRL_TARE_LOAD_RECOVERY(
 OPERATION_ID varchar2(100)primary key references RRL_TARE_BOOK(OPERATION_ID),
 LOAD_OPERATION_ID varchar2(100)not null references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 ORIGINAL_BOOK_OPERATION_ID varchar2(100)not null unique references RRL_TARE_BOOK(OPERATION_ID),
 RETURN_OFFER_OPERATION_ID varchar2(100)not null unique references RRL_TARE_OFFER(OPERATION_ID),
 RETURN_ACCEPT_OPERATION_ID varchar2(100)not null unique references RRL_TARE_ACCEPT(OPERATION_ID),
 WARE_ID number not null,PALLET_TYPE_ID number not null references RRL_PALLET_TYPE(PALLET_TYPE_ID),
 CASE_PICK_TASK_ID number not null references RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID),
 CREATED_BY varchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null);
"""
helper="""create or replace package RRL_TARE_LOAD_RECOVERY_API authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TARE_BOOK_CMD,package RRL_STOCK_UNLOAD_CMD)as
 procedure assert_scope(p_request clob,p_actor varchar2);
 function describe_recovery(p_request clob,p_actor varchar2)return clob;
 procedure declare_recovery(p_domain clob,p_operation varchar2,r in out nocopy json_array_t);
 procedure record_recovery(p_domain clob,p_operation varchar2,p_actor varchar2);
end;
/
create or replace package body RRL_TARE_LOAD_RECOVERY_API as
 procedure assert_scope(p_request clob,p_actor varchar2)is d json_object_t:=json_object_t.parse(p_request);m json_object_t;v json_object_t;book_id varchar2(100);ware number;
 begin
  if d.get_string('command_type')!='TARE_BOOK'then return;end if;m:=d.get_object('metadata');
  if not m.has('load_recovery')or m.get('load_recovery').is_null then return;end if;
  if RRL_HAS_WRIGHT(p_actor,'tare_plan')!=1 then raise_application_error(-20882,'TARE_RECOVERY_PLANNING_PERMISSION_REQUIRED');end if;
  v:=m.get_object('load_recovery');book_id:=v.get_string('original_booking_operation_id');
  select OWNER_WARE_ID into ware from RRL_TARE_BOOK where OPERATION_ID=book_id;
  RRL_TARE_PARTICIPANT.warehouse_actor(p_actor,ware);
 end;
 function describe_recovery(p_request clob,p_actor varchar2)return clob is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');s json_object_t:=d.get_object('source');v json_object_t;j json_object_t:=json_object_t();
  old_book RRL_TARE_BOOK%rowtype;load_fact RRL_TT_HU_LOAD_FACT%rowtype;old_offer RRL_TARE_OFFER%rowtype;back_offer RRL_TARE_OFFER%rowtype;back_accept RRL_TARE_ACCEPT%rowtype;old_accept RRL_TARE_ACCEPT%rowtype;ct RRL_CASE_PICK_TASK%rowtype;
  load_id varchar2(100);book_id varchar2(100);return_id varchar2(100);old_offer_id varchar2(100);case_id number;n number;wire clob;scan_value varchar2(200);original_version number;
 begin
  assert_scope(p_request,p_actor);v:=m.get_object('load_recovery');load_id:=v.get_string('load_operation_id');book_id:=v.get_string('original_booking_operation_id');return_id:=v.get_string('return_offer_operation_id');
  select *into old_book from RRL_TARE_BOOK where OPERATION_ID=book_id;
  if old_book.STATUS!='TRANSFERRED'or old_book.PLACE_KIND!='CASE'or old_book.QUANTITY!=1 or s.get_string('place_kind')!='CASE'or s.get_string('place_id')!=old_book.PLACE_ID then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_TRANSFERRED_CASE_REQUIRED');end if;
  select *into load_fact from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=load_id;
  if load_fact.STATUS!='LOADED'or load_fact.DEPARTURE_OPERATION_ID is not null or load_fact.CUSTODY_RELEASE_OPERATION_ID is not null or old_book.OWNER_WARE_ID!=load_fact.WARE_ID or v.get_number('expected_load_version')is null or v.get_number('expected_load_version')!=load_fact.CONTENT_VERSION then raise_application_error(-20886,'TARE_RECOVERY_PREDEPARTURE_ORIGINAL_LOAD_REQUIRED');end if;
  select o.OPERATION_ID into old_offer_id from RRL_TARE_OFFER o join RRL_TARE_OFFER_BOOK b on b.OFFER_OPERATION_ID=o.OPERATION_ID join RRL_TARE_ACCEPT a on a.OFFER_OPERATION_ID=o.OPERATION_ID
   where b.LOAD_OPERATION_ID=load_id and b.BOOK_OPERATION_ID=book_id and a.OPERATION_ID=old_book.CLOSED_OPERATION_ID and a.ACCEPTED_QTY=o.QUANTITY;
  select *into old_offer from RRL_TARE_OFFER where OPERATION_ID=old_offer_id;
  select *into old_accept from RRL_TARE_ACCEPT where OPERATION_ID=old_book.CLOSED_OPERATION_ID;
  select *into back_offer from RRL_TARE_OFFER where OPERATION_ID=return_id;
  select *into back_accept from RRL_TARE_ACCEPT where OFFER_OPERATION_ID=return_id;
  if old_offer.FROM_KIND!='WAREHOUSE'or old_offer.TO_KIND!='VEHICLE'or old_offer.OWNER_WARE_ID!=load_fact.WARE_ID or old_offer.VEHICLE_ID!=load_fact.VEHICLE_ID or old_offer.TT_ID!=load_fact.TT_ID
   or back_offer.FROM_KIND!='VEHICLE'or back_offer.TO_KIND!='WAREHOUSE'or back_offer.FROM_BALANCE_KEY!=old_offer.TO_BALANCE_KEY or back_offer.TO_BALANCE_KEY!=old_book.BALANCE_KEY
   or back_offer.OWNER_WARE_ID!=old_book.OWNER_WARE_ID or back_offer.PALLET_TYPE_ID!=old_book.PALLET_TYPE_ID or back_offer.CONDITION_CODE!='GOOD'
   or back_offer.VEHICLE_ID!=load_fact.VEHICLE_ID or back_offer.TT_ID!=load_fact.TT_ID or back_offer.QUANTITY!=old_book.QUANTITY or back_accept.ACCEPTED_QTY!=old_book.QUANTITY or back_accept.SHORT_QTY!=0
   or back_offer.OFFERED_AT<old_accept.ACCEPTED_AT or back_accept.ACCEPTED_AT<back_offer.OFFERED_AT
   or back_accept.ACCEPTED_BY=back_offer.OFFERED_BY then raise_application_error(-20886,'TARE_RECOVERY_EXACT_ACCEPTED_VEHICLE_RETURN_REQUIRED');end if;
  case_id:=to_number(old_book.PLACE_ID);select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=case_id;
  if ct.STATUS!='SHIPPED'or ct.SHIPPED_OPERATION!=load_id or ct.WARE_ID!=old_book.OWNER_WARE_ID or ct.PALLET_TYPE_ID!=old_book.PALLET_TYPE_ID then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_CASE_OWNER_REQUIRED');end if;
  wire:=load_fact.COMPOSITION_JSON;
  select count(*),max(S),max(V)into n,scan_value,original_version from json_table(wire,'$.nodes[*]'columns(K varchar2(20)path '$.kind',C number path '$.case_task_id',S varchar2(200)path '$.sscc',V number path '$.version'))where K='CASE'and C=case_id;
  if n!=1 or ct.CONTENT_VERSION!=original_version+1 or v.get_string('scan_place')is null or v.get_string('scan_place')!=scan_value then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_CASE_SCAN_EPOCH_REQUIRED');end if;
  select count(*)into n from RRL_TARE_LOAD_RECOVERY where ORIGINAL_BOOK_OPERATION_ID=book_id or RETURN_OFFER_OPERATION_ID=return_id or RETURN_ACCEPT_OPERATION_ID=back_accept.OPERATION_ID;
  if n!=0 then raise_application_error(-20886,'TARE_RECOVERY_SOURCE_ALREADY_USED');end if;
  j.put('load_operation_id',load_id);j.put('original_booking_operation_id',book_id);j.put('return_offer_operation_id',return_id);j.put('return_accept_operation_id',back_accept.OPERATION_ID);j.put('original_offer_operation_id',old_offer_id);
  j.put('warehouse_id',old_book.OWNER_WARE_ID);j.put('pallet_type_id',old_book.PALLET_TYPE_ID);j.put('case_id',case_id);j.put('case_version',ct.CONTENT_VERSION);j.put('balance_key',rawtohex(old_book.BALANCE_KEY));j.put('load_version',load_fact.CONTENT_VERSION);
  return j.to_clob;
 exception when no_data_found then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_ACCEPTED_RETURN_REQUIRED');end;
 procedure declare_recovery(p_domain clob,p_operation varchar2,r in out nocopy json_array_t)is v json_object_t:=json_object_t.parse(p_domain);
 begin
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_LOAD_RECOVERY',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_BOOK',v.get_string('original_booking_operation_id'));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_HU_LOAD_FACT',v.get_string('load_operation_id'));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_OFFER',v.get_string('original_offer_operation_id'));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_OFFER',v.get_string('return_offer_operation_id'));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_ACCEPT',v.get_string('return_accept_operation_id'));
  RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU','CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('case_id')));
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','TARE.RECOVER.BOOK:'||v.get_string('original_booking_operation_id'));
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','TARE.RECOVER.RETURN:'||v.get_string('return_offer_operation_id'));
 end;
 procedure record_recovery(p_domain clob,p_operation varchar2,p_actor varchar2)is
  v json_object_t:=json_object_t.parse(p_domain);load_id varchar2(100):=v.get_string('load_operation_id');book_id varchar2(100):=v.get_string('original_booking_operation_id');return_id varchar2(100):=v.get_string('return_offer_operation_id');accept_id varchar2(100):=v.get_string('return_accept_operation_id');ware number:=v.get_number('warehouse_id');typ number:=v.get_number('pallet_type_id');ct number:=v.get_number('case_id');
 begin
  insert into RRL_TARE_LOAD_RECOVERY(OPERATION_ID,LOAD_OPERATION_ID,ORIGINAL_BOOK_OPERATION_ID,RETURN_OFFER_OPERATION_ID,RETURN_ACCEPT_OPERATION_ID,WARE_ID,PALLET_TYPE_ID,CASE_PICK_TASK_ID,CREATED_BY)values(p_operation,load_id,book_id,return_id,accept_id,ware,typ,ct,p_actor);
 end;
end;
/
"""
out[str(f/"002_recovery.sql")]=helper
s=(f/"000_before_book.sql").read_text(encoding="utf-8")
s=s.replace("booked RRL_TARE_BOOK%rowtype;","recovery_json json_object_t;recovery_wire clob;\n booked RRL_TARE_BOOK%rowtype;",1)
anchor=" if kind='TARE_BOOK_CANCEL' then"
idx=s.index(anchor)
s=s[:idx]+""" if m.has('load_recovery')and not m.get('load_recovery').is_null then
  if kind!='TARE_BOOK'then raise_application_error(-20886,'TARE_RECOVERY_BOOK_ONLY');end if;
  recovery_wire:=RRL_TARE_LOAD_RECOVERY_API.describe_recovery(p_request,p_actor);recovery_json:=json_object_t.parse(recovery_wire);
 end if;
"""+s[idx:]
s=s.replace("elsif task.STATUS in('SHIPPED','CANCELLED')then","elsif task.STATUS in('SHIPPED','CANCELLED')and recovery_json is null then",1)
anchor=" p_domain.put('balance_key'"
idx=s.index(anchor)
s=s[:idx]+" if recovery_json is not null then p_domain.put('load_recovery',recovery_json);end if;\n"+s[idx:]
anchor=" p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;"
idx=s.index(anchor)
s=s[:idx]+" if v.has('load_recovery')then RRL_TARE_LOAD_RECOVERY_API.declare_recovery(v.get_object('load_recovery').to_clob,p_operation,r);end if;\n"+s[idx:]
anchor=" v_available:=v_available-1;"
idx=s.index(anchor)
s=s[:idx]+" if v.has('load_recovery')then RRL_TARE_LOAD_RECOVERY_API.record_recovery(v.get_object('load_recovery').to_clob,op,p_actor);j.put('load_recovery',v.get_object('load_recovery'));end if;\n"+s[idx:]
out[str(f/"003_book.sql")]=s
s=(f/"000_before_root.sql").read_text(encoding="utf-8")
needle="  assert_actor_active(p_actor);"
assert s.count(needle)==2
s=s.replace(needle,needle+"\n  if g_kind='TARE_BOOK'then RRL_TARE_LOAD_RECOVERY_API.assert_scope(p_request,p_actor);end if;")
out[str(f/"004_root.sql")]=s
s=(f/"000_before_unload.sql").read_text(encoding="utf-8")
s=s.replace("select count(*)into n from RRL_TARE_OFFER_BOOK where LOAD_OPERATION_ID=p_load;","""select count(*)into n from RRL_TARE_OFFER_BOOK old_offer where LOAD_OPERATION_ID=p_load and not exists(
   select 1 from RRL_TARE_LOAD_RECOVERY recovery join RRL_TARE_BOOK replacement on replacement.OPERATION_ID=recovery.OPERATION_ID
    where recovery.LOAD_OPERATION_ID=p_load and recovery.ORIGINAL_BOOK_OPERATION_ID=old_offer.BOOK_OPERATION_ID and replacement.STATUS='HELD');""",1)
# Every recovery proof and its original associations declared; load row serializes departure/recovery/unload.
anchor="  nodes:=tree.get_array('nodes');"
idx=s.index(anchor)
s=s[:idx]+"""  for proof in(select OPERATION_ID,ORIGINAL_BOOK_OPERATION_ID,RETURN_OFFER_OPERATION_ID,RETURN_ACCEPT_OPERATION_ID from RRL_TARE_LOAD_RECOVERY where LOAD_OPERATION_ID=load_id order by OPERATION_ID)loop
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_LOAD_RECOVERY',proof.OPERATION_ID);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_BOOK',proof.ORIGINAL_BOOK_OPERATION_ID);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_OFFER',proof.RETURN_OFFER_OPERATION_ID);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_ACCEPT',proof.RETURN_ACCEPT_OPERATION_ID);
  end loop;
"""+s[idx:]
out[str(f/"005_unload.sql")]=s
out[str(f/"006_guard.sql")]="""create or replace trigger RRL_TARE_LOAD_RECOVERY_GUARD before insert or update or delete on RRL_TARE_LOAD_RECOVERY for each row
declare wire clob;v json_object_t;n number;
begin
 if not inserting then raise_application_error(-20863,'TARE_LOAD_RECOVERY_IMMUTABLE');end if;
 if :new.OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')then raise_application_error(-20863,'TARE_LOAD_RECOVERY_ROOT_REQUIRED');end if;
 RRL_TARE_ASSERT_WRITE('RRL_TARE_LOAD_RECOVERY',:new.OPERATION_ID,'TARE_BOOK');
 select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=:new.OPERATION_ID;
 v:=json_object_t.parse(wire).get_object('domain').get_object('load_recovery');
 if v.get_string('load_operation_id')!=:new.LOAD_OPERATION_ID or v.get_string('original_booking_operation_id')!=:new.ORIGINAL_BOOK_OPERATION_ID or v.get_string('return_offer_operation_id')!=:new.RETURN_OFFER_OPERATION_ID or v.get_string('return_accept_operation_id')!=:new.RETURN_ACCEPT_OPERATION_ID or v.get_number('warehouse_id')!=:new.WARE_ID or v.get_number('pallet_type_id')!=:new.PALLET_TYPE_ID or v.get_number('case_id')!=:new.CASE_PICK_TASK_ID or :new.CREATED_BY!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'TARE_LOAD_RECOVERY_EXACT_PLAN_REQUIRED');end if;
 select count(*)into n from RRL_TARE_BOOK where OPERATION_ID=:new.OPERATION_ID and STATUS='HELD'and PLACE_KIND='CASE'and PLACE_ID=RRL_STOCK_PLAN_HELPER.decimal_text(:new.CASE_PICK_TASK_ID)and OWNER_WARE_ID=:new.WARE_ID and PALLET_TYPE_ID=:new.PALLET_TYPE_ID;
 if n!=1 then raise_application_error(-20863,'TARE_LOAD_RECOVERY_NEW_BOOK_REQUIRED');end if;
end;
/
"""
out[str(f/"apply.sql")]="".join("@@"+name+"\n"for name in ["001_schema.sql","002_recovery.sql","003_book.sql","004_root.sql","005_unload.sql","006_guard.sql"])
out[str(f/"rollback.sql")]="""declare n number;begin select count(*)into n from RRL_TARE_LOAD_RECOVERY;if n>0 then raise_application_error(-20863,'TARE_LOAD_RECOVERY_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_root.sql
@@000_before_book.sql
@@000_before_unload.sql
drop package RRL_TARE_LOAD_RECOVERY_API;
drop table RRL_TARE_LOAD_RECOVERY;
"""
print(json.dumps(out,ensure_ascii=True))


