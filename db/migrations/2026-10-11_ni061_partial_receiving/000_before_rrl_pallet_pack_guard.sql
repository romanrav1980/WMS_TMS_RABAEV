
  CREATE OR REPLACE EDITIONABLE TRIGGER "RABAEV"."RRL_PALLET_PACK_GUARD" 
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

ALTER TRIGGER "RABAEV"."RRL_PALLET_PACK_GUARD" ENABLE
