create or replace trigger RRL_LOG_COST_PERIOD_HEAD_G before update or delete on RRL_LOG_COST_PERIOD_HEAD for each row
begin
 if deleting or :new.WARE_ID!=:old.WARE_ID or :new.VERSION_NO!=:old.VERSION_NO+1 then raise_application_error(-20863,'COST_PERIOD_HEAD_VERSION_REQUIRED');end if;
end;
/
create or replace trigger RRL_LOG_COST_PERIOD_HISTORY_G before insert or update or delete on RRL_LOG_COST_PERIOD_HISTORY for each row
declare n number;z varchar2(64);begin
 if not inserting then raise_application_error(-20863,'COST_PERIOD_HISTORY_IMMUTABLE');end if;
 select count(*)into n from RRL_LOG_COST_PERIOD_HEAD h join RUSERS u on u.ID=:new.ACTOR and nvl(u.DELETED,0)=0
 where h.WARE_ID=:new.WARE_ID and h.VERSION_NO=:new.VERSION_NO and RRL_HAS_WRIGHT(u.ID,'create_tt_price')=1
 and(u.WARE_ID=h.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')and 1=(select count(*)from RRL_WARES where ID=h.WARE_ID);
 if n!=1 then raise_application_error(-20882,'COST_PERIOD_CURRENT_BOUND_FINANCE_REQUIRED');end if;
 if :new.PERIOD_MODE='CASE_ASSEMBLY'then select to_char(systimestamp at time zone(:new.TIME_ZONE),'TZR')into z from dual;end if;
end;
/
