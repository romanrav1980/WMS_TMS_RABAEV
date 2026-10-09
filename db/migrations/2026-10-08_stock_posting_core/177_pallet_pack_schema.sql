-- Freeze the actual packaging policy at first stock admission, including unknown factor.
declare n number;v varchar2(20);begin
 select STATE into v from RRL_STOCK_RELEASE where RELEASE_ID=1;
 select count(*) into n from RRL_REMAINS where REMAIN>0 or HARD_RESERVED_BASE>0;
 if v!='PREPARED' or n>0 then raise_application_error(-20808,'PACK_SCHEMA_REQUIRES_EMPTY_PREPARED_STOCK');end if;
end;
/
alter table RRL_PALLETS add(STOCK_BOX_FACTOR number,STOCK_PACK_BASE_UOM varchar2(20),STOCK_PACK_FROZEN number default 0 not null);
alter table RRL_PALLETS add constraint RRL_PALLET_PACK_CHK check(STOCK_PACK_FROZEN in(0,1) and
 (STOCK_BOX_FACTOR is null or (STOCK_BOX_FACTOR>=1 and STOCK_BOX_FACTOR=trunc(STOCK_BOX_FACTOR) and STOCK_BOX_FACTOR<=1000000000)) and
 (STOCK_PACK_FROZEN=0 or STOCK_PACK_BASE_UOM is not null));
create or replace trigger RRL_PALLET_PACK_GUARD
 before insert or update of STOCK_BOX_FACTOR,STOCK_PACK_BASE_UOM,STOCK_PACK_FROZEN on RRL_PALLETS for each row
begin
 if updating and :old.STOCK_PACK_FROZEN=1 then
  if :new.STOCK_PACK_FROZEN!=1 or :new.STOCK_PACK_BASE_UOM is null or :new.STOCK_PACK_BASE_UOM!=:old.STOCK_PACK_BASE_UOM
   or (:old.STOCK_BOX_FACTOR is null and :new.STOCK_BOX_FACTOR is not null)
   or (:old.STOCK_BOX_FACTOR is not null and :new.STOCK_BOX_FACTOR is null)
   or :old.STOCK_BOX_FACTOR!=:new.STOCK_BOX_FACTOR then raise_application_error(-20887,'PALLET_PACK_SNAPSHOT_IMMUTABLE');end if;
 elsif :new.STOCK_PACK_FROZEN=1 then
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','MODE') not in('EXPLICIT','COMPAT')
   or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null
   or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'PALLET_PACK_WRITE_FORBIDDEN');end if;
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',:new.UID_PALLET));
 end if;
end;
/
