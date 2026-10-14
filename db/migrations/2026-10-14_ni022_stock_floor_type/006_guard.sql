create or replace trigger RRL_PALLET_FLOOR_GUARD
 before insert or update or delete on RRL_PALLET_FLOOR_TYPE for each row
begin
 if deleting then raise_application_error(-20863,'PALLET_FLOOR_HISTORY_REQUIRED');end if;
 if updating and(:new.UID_PALLET!=:old.UID_PALLET or :new.TYPE_VERSION!=:old.TYPE_VERSION+1)then
  raise_application_error(-20863,'PALLET_FLOOR_NEXT_VERSION_REQUIRED');end if;
 if inserting and :new.TYPE_VERSION!=1 then raise_application_error(-20863,'PALLET_FLOOR_INITIAL_VERSION_REQUIRED');end if;
 RRL_STOCK_PALLET_TYPE_CMD.assert_writing(:new.UID_PALLET,:new.LAST_OPERATION_ID);
end;
/
