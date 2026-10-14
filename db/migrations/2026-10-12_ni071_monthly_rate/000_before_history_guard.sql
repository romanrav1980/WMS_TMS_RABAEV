create or replace trigger RRL_LOG_RATE_HISTORY_GUARD before insert or update or delete on RRL_LOGISTICS_RATE_HISTORY for each row
declare n number;
begin
 if not inserting then raise_application_error(-20863,'LOGISTICS_RATE_HISTORY_IMMUTABLE');end if;
 select count(*)into n from RRL_LOGISTICS_RATE_HEAD h join RUSERS u on u.ID=:new.ACTOR and nvl(u.DELETED,0)=0
 where h.RATE_KEY=:new.RATE_KEY and h.VERSION_NO=:new.VERSION_NO and(u.WARE_ID=h.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,'create_tt_price')=1;
 if n!=1 then raise_application_error(-20882,'LOGISTICS_RATE_CURRENT_BOUND_FINANCE_REQUIRED');end if;
end;
/
