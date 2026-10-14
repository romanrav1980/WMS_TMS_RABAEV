declare n number;begin select count(*)into n from(select RATE_KEY,EFFECTIVE_FROM from RRL_LOGISTICS_RATE_HISTORY group by RATE_KEY,EFFECTIVE_FROM having count(*)>1);if n>0 then raise_application_error(-20899,'SAME_PERIOD_REVISION_HISTORY_REQUIRES_FORWARD_REPAIR');end if;end;
/
@@000_before_guard.sql
-- Restore previous Python selector/operator and date uniqueness together only before any revised period is committed.
