create or replace trigger RRL_SAP_PALLET_WRITE_GUARD
before insert or delete or update of UID_PALLET,UNIT_COUNT,PRIHOD_NAKLAD_ID on RRL_PALLETS
for each row
declare n number;
begin
 select count(*) into n from RRL_SAP_SUPPLY_ORDER
 where NAKLAD_ID=:new.PRIHOD_NAKLAD_ID or NAKLAD_ID=:old.PRIHOD_NAKLAD_ID;
 if n>0 and not RRL_SAP_RECEIPT_API.pallet_write_allowed then
 raise_application_error(-20804,'SAP incoming pallets require the physical receiving API'); end if;
end;
/
