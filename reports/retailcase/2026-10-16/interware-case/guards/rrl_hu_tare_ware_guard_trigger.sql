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
