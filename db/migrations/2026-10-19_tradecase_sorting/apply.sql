whenever sqlerror exit failure rollback
@@001_sort_guard.sql
@@002_internal.sql
@@003_posting.sql
declare n number;begin
 select count(*)into n from user_errors where name in('RRL_TRADE_SORT_GUARD','RRL_STOCK_INTERNAL_CMD','RRL_STOCK_POSTING_API');
 if n<>0 then raise_application_error(-20999,'TRADE_SORT_COMPILE_ERRORS');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-sorting'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Exact scanned homogeneous sorting through existing internal transfer',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
