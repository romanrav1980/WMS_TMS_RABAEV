create or replace package RRL_TARE_LOAD_RECOVERY_API authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TARE_BOOK_CMD,package RRL_STOCK_UNLOAD_CMD)as
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
