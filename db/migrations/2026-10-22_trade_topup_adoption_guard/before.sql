create or replace trigger RRL_STOCK_RESERVATION_GUARD
 before insert or update or delete on RRL_STOCK_RESERVATION for each row
begin
 if not RRL_STOCK_WRITE_GUARD.enforcement_required then return;end if;
 if deleting then raise_application_error(-20863,'RESERVATION_DELETE_FORBIDDEN');end if;
 RRL_STOCK_WRITE_GUARD.require_effect('RESERVATION',:new.UID_PALLET,:new.CELL,:new.RESERVATION_ID);
 if updating then
  if :old.UID_PALLET is not null then RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',:old.UID_PALLET));end if;
  if :new.RESERVATION_ID!=:old.RESERVATION_ID or :new.RESERVATION_VERSION!=:old.RESERVATION_VERSION+1
   or (:new.SOURCE_DOC_TYPE!=:old.SOURCE_DOC_TYPE or (:new.SOURCE_DOC_TYPE is null and :old.SOURCE_DOC_TYPE is not null) or (:new.SOURCE_DOC_TYPE is not null and :old.SOURCE_DOC_TYPE is null)) or (:new.SOURCE_DOC_ID!=:old.SOURCE_DOC_ID or (:new.SOURCE_DOC_ID is null and :old.SOURCE_DOC_ID is not null) or (:new.SOURCE_DOC_ID is not null and :old.SOURCE_DOC_ID is null)) then
   raise_application_error(-20869,'RESERVATION_IDENTITY_OR_VERSION_CONFLICT');end if;
 end if;
end;
/
