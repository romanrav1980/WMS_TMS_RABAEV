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
