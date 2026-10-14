create or replace trigger RRL_LOG_RATE_HISTORY_GUARD before insert or update or delete on RRL_LOGISTICS_RATE_HISTORY for each row
declare n number;
begin
 if not inserting then raise_application_error(-20863,'LOGISTICS_RATE_HISTORY_IMMUTABLE');end if;
 select count(*)into n from RRL_LOGISTICS_RATE_HEAD h join RUSERS u on u.ID=:new.ACTOR and nvl(u.DELETED,0)=0
 where h.RATE_KEY=:new.RATE_KEY and h.VERSION_NO=:new.VERSION_NO and(u.WARE_ID=h.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,'create_tt_price')=1;
 if n!=1 then raise_application_error(-20882,'LOGISTICS_RATE_CURRENT_BOUND_FINANCE_REQUIRED');end if;
end;
/
create or replace trigger RRL_LOG_COST_RUN_GUARD before insert or update or delete on RRL_LOGISTICS_COST_RUN for each row
declare n number;
begin
 if not inserting then raise_application_error(-20863,'LOGISTICS_COST_HISTORY_IMMUTABLE');end if;
 select count(*)into n from RUSERS u where u.ID=:new.ACTOR and nvl(u.DELETED,0)=0 and(u.WARE_ID=:new.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,'calc_tt_price')=1;
 if n!=1 then raise_application_error(-20882,'LOGISTICS_COST_CURRENT_BOUND_FINANCE_REQUIRED');end if;
end;
/
create or replace trigger RRL_LOG_COST_LINE_GUARD before insert or update or delete on RRL_LOGISTICS_COST_LINE for each row
declare n number;
begin
 if not inserting then raise_application_error(-20863,'LOGISTICS_COST_LINE_IMMUTABLE');end if;
 select count(*)into n from RRL_LOGISTICS_COST_RUN r join RRL_TT_HU_LOAD_FACT l on l.TT_ID=r.TT_ID and l.WARE_ID=r.WARE_ID
 join RRL_LOGISTICS_RATE_HISTORY h on h.RATE_KEY=:new.RATE_KEY and h.VERSION_NO=:new.VERSION_NO
 join RRL_LOGISTICS_RATE_HEAD rh on rh.RATE_KEY=h.RATE_KEY and rh.WARE_ID=r.WARE_ID and rh.CURRENCY=r.CURRENCY
 where r.OPERATION_ID=:new.OPERATION_ID and l.LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID and l.STATUS='DEPARTED'
 and r.CURRENCY=:new.CURRENCY and rh.COST_CODE=:new.COST_CODE and h.RATE_VALUE=:new.RATE_VALUE and h.BASIS=:new.BASIS
 and h.EFFECTIVE_FROM<=cast(sys_extract_utc(l.LOADED_AT) as date)
 and :new.QUANTITY=(select count(*)from RRL_TT_LOAD_BOX_WEIGHT b where b.LOAD_OPERATION_ID=l.LOAD_OPERATION_ID);
 if n!=1 then raise_application_error(-20886,'LOGISTICS_COST_ACTUAL_SOURCE_RATE_REQUIRED');end if;
end;
/
