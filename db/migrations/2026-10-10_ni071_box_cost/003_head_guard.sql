create or replace trigger RRL_LOG_RATE_HEAD_GUARD before insert or update or delete on RRL_LOGISTICS_RATE_HEAD for each row
declare n number;
begin
 if deleting then raise_application_error(-20863,'LOGISTICS_RATE_HEAD_RETAIN_HISTORY');end if;
 if updating and(:new.RATE_KEY!=:old.RATE_KEY or :new.WARE_ID!=:old.WARE_ID or :new.COST_CODE!=:old.COST_CODE or :new.CURRENCY!=:old.CURRENCY or :new.VERSION_NO!=:old.VERSION_NO+1)then raise_application_error(-20863,'LOGISTICS_RATE_IDENTITY_IMMUTABLE');end if;
 if inserting then
  select count(*)into n from RRL_WARES where ID=:new.WARE_ID;if n!=1 then raise_application_error(-20886,'LOGISTICS_RATE_UNIQUE_WAREHOUSE_REQUIRED');end if;
  if :new.VERSION_NO!=1 then raise_application_error(-20886,'LOGISTICS_RATE_INITIAL_VERSION_REQUIRED');end if;
 end if;
end;
/
