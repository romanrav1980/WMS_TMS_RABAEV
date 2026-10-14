create or replace package RRL_TARE_PLANNING authid definer as
 function held_quantity(p_key raw) return number;
 procedure assert_available(p_key raw,p_physical number,p_required number);
 function case_booking(p_task number,p_ware number,p_type number) return varchar2;
 procedure require_case(p_task number,p_ware number,p_type number);
end;
/

create or replace package body RRL_TARE_PLANNING as
 function held_quantity(p_key raw) return number is q number;
 begin select nvl(sum(QUANTITY),0) into q from RRL_TARE_BOOK where BALANCE_KEY=p_key and STATUS='HELD';return q;end;
 procedure assert_available(p_key raw,p_physical number,p_required number) is
 begin if p_physical-held_quantity(p_key)<p_required then raise_application_error(-20886,'TARE_SOURCE_HELD_FOR_ASSEMBLY');end if;end;
 function case_booking(p_task number,p_ware number,p_type number) return varchar2 is
 n number;parent_uid varchar2(200);next_uid varchar2(200);depth number:=0;v_book varchar2(100);
 begin
 select count(*) into n from RRL_TARE_BOOK where PLACE_KIND='CASE' and PLACE_ID=to_char(p_task,'TM9') and OWNER_WARE_ID=p_ware and PALLET_TYPE_ID=p_type and STATUS='HELD';
 if n=1 then select OPERATION_ID into v_book from RRL_TARE_BOOK where PLACE_KIND='CASE' and PLACE_ID=to_char(p_task,'TM9') and OWNER_WARE_ID=p_ware and PALLET_TYPE_ID=p_type and STATUS='HELD';return v_book;end if;
 begin select PARENT_UID into parent_uid from RRL_WMS_HU_LINK where CHILD_CASE_TASK_ID=p_task and ACTIVE_FLAG=1;
 exception when no_data_found then return null;end;
 loop
 depth:=depth+1;if depth>100 then raise_application_error(-20881,'TARE_CONTAINER_PARENT_BOUND_100');end if;
 begin select PARENT_UID into next_uid from RRL_WMS_HU_LINK where CHILD_PALLET_UID=parent_uid and ACTIVE_FLAG=1;parent_uid:=next_uid;
 exception when no_data_found then exit;end;
 end loop;
 select count(*) into n from RRL_TARE_BOOK where PLACE_KIND='HU' and PLACE_ID=parent_uid and OWNER_WARE_ID=p_ware and PALLET_TYPE_ID=p_type and STATUS='HELD';
 if n!=1 then return null;end if;
 select OPERATION_ID into v_book from RRL_TARE_BOOK where PLACE_KIND='HU' and PLACE_ID=parent_uid and OWNER_WARE_ID=p_ware and PALLET_TYPE_ID=p_type and STATUS='HELD';return v_book;
 end;
 procedure require_case(p_task number,p_ware number,p_type number) is
 begin if case_booking(p_task,p_ware,p_type) is null then raise_application_error(-20886,'CASE_ASSEMBLY_GOOD_TARE_BOOK_REQUIRED');end if;end;
end;
/
