-- Forward repair is required after multiple-period costs. Never delete recognised history.
declare n number;begin
 select count(*)into n from(select LOAD_OPERATION_ID,COST_CODE,CURRENCY from RRL_LOGISTICS_COST_LINE group by LOAD_OPERATION_ID,COST_CODE,CURRENCY having count(*)>1);
 if n!=0 then raise_application_error(-20886,'COST_MULTIPERIOD_FORWARD_REPAIR_REQUIRED');end if;
end;
/
alter table RRL_LOGISTICS_COST_LINE drop constraint RRL_LOG_COST_SOURCE_FK;
alter table RRL_LOGISTICS_COST_LINE drop constraint RRL_LOG_COST_PERIOD_PK;
alter table RRL_LOGISTICS_COST_LINE drop constraint RRL_LOG_COST_PERIOD_UQ;
alter table RRL_LOGISTICS_COST_LINE add primary key(OPERATION_ID,LOAD_OPERATION_ID,COST_CODE);
alter table RRL_LOGISTICS_COST_LINE add unique(LOAD_OPERATION_ID,COST_CODE,CURRENCY);
drop trigger RRL_LOG_COST_CLAIM_GUARD;
drop table RRL_LOG_COST_SOURCE_CLAIM;
alter table RRL_LOGISTICS_COST_LINE drop column PERIOD_KEY;
@@000_before_guard.sql
-- Restore Python/UI/summary together; no monetary or quantity facts are removed.
