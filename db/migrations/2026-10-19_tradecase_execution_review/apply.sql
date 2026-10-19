whenever sqlerror exit failure rollback
@@001_sort_guard.sql
@@002_posting.sql
@@003_buyout.sql
@@004_stock_view.sql
declare n number;begin
 select count(*)into n from user_errors where name in('RRL_TRADE_SORT_GUARD','RRL_STOCK_POSTING_API','RRL_TRADE_BUYOUT_CORE','RRL_TRADE_STOCK_API');
 if n<>0 then raise_application_error(-20999,'TRADE_EXECUTION_REVIEW_COMPILE_ERRORS');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-execution-review'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Review: narrow sorting fence, empty target, lifecycle-compatible financial admission and visible holds',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
