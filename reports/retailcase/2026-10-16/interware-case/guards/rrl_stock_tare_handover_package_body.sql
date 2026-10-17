create or replace package body RRL_STOCK_TARE_HANDOVER as
 procedure describe_books(p_request clob,p_kind varchar2,p_offer varchar2,p_owner number,p_type number,p_condition varchar2,p_from_kind varchar2,p_trip number,p_vehicle number,p_qty number,p_books out json_array_t) is
 d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');ids json_array_t:=json_array_t();item json_object_t;book RRL_TARE_BOOK%rowtype;
 v_id varchar2(100);v_load varchar2(100);v_saved_load varchar2(100);n number;case_no number;seen clob;
 begin
 if p_kind='TARE_ACCEPT' then
  for row_record in(select BOOK_OPERATION_ID from RRL_TARE_OFFER_BOOK where OFFER_OPERATION_ID=p_offer order by BOOK_OPERATION_ID)loop ids.append(row_record.BOOK_OPERATION_ID);end loop;
 elsif m.has('booking_operation_ids') then ids:=m.get_array('booking_operation_ids');end if;
 if ids is null or ids.get_size>100 then raise_application_error(-20881,'TARE_HANDOVER_BOOK_BOUND_100');end if;
 if ids.get_size>0 and(p_from_kind!='WAREHOUSE' or p_condition!='GOOD')then raise_application_error(-20886,'TARE_HANDOVER_GOOD_WAREHOUSE_BOOKS_REQUIRED');end if;
 if p_qty<ids.get_size then raise_application_error(-20886,'TARE_HANDOVER_WHOLE_SELECTED_BOOKS_REQUIRED');end if;
 p_books:=json_array_t();seen:=ids.to_clob;
 select count(*)-count(distinct ID) into n from json_table(seen,'$[*]' columns(ID varchar2(100) path '$' error on error));
 if n!=0 then raise_application_error(-20886,'TARE_HANDOVER_DUPLICATE_BOOK');end if;
 for row_record in(select ID from json_table(seen,'$[*]' columns(ID varchar2(100) path '$' error on error))order by ID)loop
  v_id:=row_record.ID;select * into book from RRL_TARE_BOOK where OPERATION_ID=v_id and STATUS='HELD';
  if p_kind='TARE_OFFER'then
   select count(*)into n from RRL_TARE_OFFER_BOOK ob where ob.BOOK_OPERATION_ID=v_id and not exists(select 1 from RRL_TARE_OFFER_CANCEL c where c.OFFER_OPERATION_ID=ob.OFFER_OPERATION_ID);
   if n>0 then raise_application_error(-20886,'TARE_BOOK_HAS_ACTIVE_HANDOVER_OFFER');end if;
  end if;
  if book.OWNER_WARE_ID!=p_owner or book.PALLET_TYPE_ID!=p_type then raise_application_error(-20886,'TARE_HANDOVER_BOOK_WARE_TYPE_CONFLICT');end if;
  case_no:=case when book.PLACE_KIND='CASE' then to_number(book.PLACE_ID) else null end;
  select count(*),min(lf.LOAD_OPERATION_ID)into n,v_load from RRL_TT_HU_LOAD_FACT lf
   where lf.TT_ID=p_trip and lf.VEHICLE_ID=p_vehicle and lf.WARE_ID=p_owner and lf.STATUS in('LOADED','DEPARTED')
   and((book.PLACE_KIND='HU'and lf.ROOT_UID=book.PLACE_ID)or(book.PLACE_KIND='CASE'and lf.ROOT_CASE_TASK_ID=case_no)
    or(book.PLACE_KIND='CASE'and exists(select 1 from json_table(lf.COMPOSITION_JSON,'$.nodes[*]'
     columns(K varchar2(20)path '$.kind',CASE_ID number path '$.case_task_id'))node where node.K='CASE'and node.CASE_ID=case_no)));
  if n!=1 then raise_application_error(-20886,'TARE_HANDOVER_ONE_ARCHIVED_PHYSICAL_LOAD_REQUIRED');end if;
  if p_kind='TARE_ACCEPT' then
   select LOAD_OPERATION_ID into v_saved_load from RRL_TARE_OFFER_BOOK where OFFER_OPERATION_ID=p_offer and BOOK_OPERATION_ID=v_id;
   if v_saved_load!=v_load then raise_application_error(-20886,'TARE_HANDOVER_ORIGINAL_LOAD_CHANGED');end if;
  end if;
  item:=json_object_t();item.put('booking_operation_id',v_id);item.put('load_operation_id',v_load);item.put('place_kind',book.PLACE_KIND);item.put('place_id',book.PLACE_ID);p_books.append(item);
 end loop;
 exception when no_data_found then raise_application_error(-20886,'TARE_HANDOVER_CURRENT_BOOK_AND_ACTUAL_LOAD_REQUIRED');end;
 procedure declare_books(p_books json_array_t,p_offer varchar2,p_resources in out nocopy json_array_t) is
 item json_object_t;v_id varchar2(100);
 begin
 if p_books.get_size>0 then
 for idx in 0..p_books.get_size-1 loop
  item:=treat(p_books.get(idx) as json_object_t);v_id:=item.get_string('booking_operation_id');
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_TARE_BOOK',v_id);
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_TARE_OFFER_BOOK',p_offer||':'||v_id);
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_TT_HU_LOAD_FACT',item.get_string('load_operation_id'));
 end loop;end if;
 end;
 procedure persist_offer(p_offer varchar2,p_books json_array_t) is
 item json_object_t;v_id varchar2(100);v_load varchar2(100);
 begin
 if p_books.get_size>0 then for idx in 0..p_books.get_size-1 loop
 item:=treat(p_books.get(idx) as json_object_t);v_id:=item.get_string('booking_operation_id');v_load:=item.get_string('load_operation_id');
 insert into RRL_TARE_OFFER_BOOK(OFFER_OPERATION_ID,BOOK_OPERATION_ID,LOAD_OPERATION_ID)values(p_offer,v_id,v_load);
 end loop;end if;
 end;
 procedure transfer_books(p_books json_array_t,p_operation varchar2,p_actor varchar2) is
 item json_object_t;v_id varchar2(100);
 begin
 if p_books.get_size>0 then for idx in 0..p_books.get_size-1 loop
 item:=treat(p_books.get(idx) as json_object_t);v_id:=item.get_string('booking_operation_id');
 update RRL_TARE_BOOK set STATUS='TRANSFERRED',CLOSED_OPERATION_ID=p_operation,CLOSED_BY=p_actor,CLOSED_AT=systimestamp where OPERATION_ID=v_id and STATUS='HELD';
 if sql%rowcount!=1 then raise_application_error(-20886,'TARE_HANDOVER_BOOK_ALREADY_TRANSFERRED');end if;
 end loop;end if;
 end;
end;
/
