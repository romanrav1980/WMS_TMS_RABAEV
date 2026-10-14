create or replace trigger RRL_TARE_BOOK_GUARD before insert or update or delete on RRL_TARE_BOOK for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
begin
 if deleting then raise_application_error(-20863,'TARE_BOOK_HISTORY_IMMUTABLE');end if;
 if inserting then
  if :new.OPERATION_ID!=op or :new.STATUS!='HELD' or :new.CREATED_BY!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR') then raise_application_error(-20863,'TARE_BOOK_ROOT_REQUIRED');end if;
  RRL_TARE_ASSERT_WRITE('RRL_TARE_BOOK',:new.OPERATION_ID,'TARE_BOOK');
 else
  if :old.STATUS!='HELD' or :new.STATUS not in('CANCELLED','TRANSFERRED') or :new.CLOSED_OPERATION_ID is null or :new.CLOSED_OPERATION_ID!=op or :new.CLOSED_BY!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')
   or :new.OPERATION_ID!=:old.OPERATION_ID or :new.BALANCE_KEY!=:old.BALANCE_KEY or :new.OWNER_WARE_ID!=:old.OWNER_WARE_ID or :new.PALLET_TYPE_ID!=:old.PALLET_TYPE_ID or :new.PLACE_KIND!=:old.PLACE_KIND or :new.PLACE_ID!=:old.PLACE_ID or :new.QUANTITY!=:old.QUANTITY or :new.CREATED_BY!=:old.CREATED_BY or :new.CREATED_AT!=:old.CREATED_AT then raise_application_error(-20863,'TARE_BOOK_HISTORY_IMMUTABLE');end if;
  RRL_TARE_ASSERT_WRITE('RRL_TARE_BOOK',:new.OPERATION_ID,case when :new.STATUS='TRANSFERRED' then 'TARE_ACCEPT' else 'TARE_BOOK_CANCEL' end);
 end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TARE_BALANCE',rawtohex(:new.BALANCE_KEY)));
end;
/
create or replace trigger RRL_CASE_TARE_START_GUARD before update of STARTED_AT,WARE_ID,PALLET_TYPE_ID on RRL_CASE_PICK_TASK for each row
declare n number;
begin
 if :old.STARTED_AT is null and :new.STARTED_AT is not null then RRL_TARE_PLANNING.require_case(:new.CASE_PICK_TASK_ID,:new.WARE_ID,:new.PALLET_TYPE_ID);end if;
 if nvl(:old.WARE_ID,-1)!=nvl(:new.WARE_ID,-1)or nvl(:old.PALLET_TYPE_ID,-1)!=nvl(:new.PALLET_TYPE_ID,-1)then
 select count(*) into n from RRL_TARE_BOOK where PLACE_KIND='CASE' and PLACE_ID=to_char(:old.CASE_PICK_TASK_ID,'TM9') and STATUS='HELD';
 if n!=0 then raise_application_error(-20863,'TARE_BOOK_CASE_WARE_TYPE_IMMUTABLE');end if;
 end if;
end;
/
create or replace trigger RRL_HU_TARE_LINK_GUARD before insert or update on RRL_WMS_HU_LINK for each row
declare n number;
begin
 if :new.ACTIVE_FLAG!=1 then return;end if;
 if updating and :old.ACTIVE_FLAG=1 and :old.PARENT_UID=:new.PARENT_UID and nvl(:old.CHILD_PALLET_UID,'~')=nvl(:new.CHILD_PALLET_UID,'~') and nvl(:old.CHILD_CASE_TASK_ID,-1)=nvl(:new.CHILD_CASE_TASK_ID,-1)then return;end if;
 select count(*) into n from RRL_TARE_BOOK where STATUS='HELD' and((PLACE_KIND='HU' and PLACE_ID=:new.CHILD_PALLET_UID)or(PLACE_KIND='CASE' and PLACE_ID=to_char(:new.CHILD_CASE_TASK_ID,'TM9')));
 if n!=0 then raise_application_error(-20886,'TARE_BOOKED_CHILD_REPACK_PROOF_REQUIRED');end if;
end;
/
create or replace trigger RRL_HU_TARE_WARE_GUARD before update of HU_CURRENT_CELL,UID_PALLET on RRL_PALLETS for each row
declare n number;v_ware number;v_book_ware number;
begin
 select count(*),min(OWNER_WARE_ID) into n,v_book_ware from RRL_TARE_BOOK where PLACE_KIND='HU' and PLACE_ID=:old.UID_PALLET and STATUS='HELD';
 if n=0 then return;end if;
 if :new.UID_PALLET!=:old.UID_PALLET then raise_application_error(-20863,'TARE_BOOK_HU_IDENTITY_IMMUTABLE');end if;
 if :new.HU_CURRENT_CELL is not null then
 select WARE_ID into v_ware from RRL_CELLS where CELL=:new.HU_CURRENT_CELL;
 if v_ware!=v_book_ware then raise_application_error(-20886,'TARE_BOOK_INTERWAREHOUSE_CUSTODY_REQUIRED');end if;
 end if;
end;
/

create or replace trigger RRL_TARE_OFFER_BOOK_GUARD before insert or update or delete on RRL_TARE_OFFER_BOOK for each row
begin
 if not inserting then raise_application_error(-20863,'TARE_OFFER_BOOK_HISTORY_IMMUTABLE');end if;
 if :new.OFFER_OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')then raise_application_error(-20863,'TARE_ROOT_OPERATION_REQUIRED');end if;
 RRL_TARE_ASSERT_WRITE('RRL_TARE_OFFER_BOOK',:new.OFFER_OPERATION_ID||':'||:new.BOOK_OPERATION_ID,'TARE_OFFER');
end;
/
