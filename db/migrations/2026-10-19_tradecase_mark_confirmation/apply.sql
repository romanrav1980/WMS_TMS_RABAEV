whenever sqlerror exit failure rollback
@@001_schema.sql
@@002_api.sql
@@003_guard.sql
declare n number;begin
 select count(*)into n from user_errors where name in('RRL_TRADE_STOCK_API','RRL_TRADE_MARK_WRITE_G');
 if n<>0 then raise_application_error(-20999,'TRADE_MARK_COMPILE_ERRORS');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-mark-confirmation' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Versioned per-unit marking confirmation inbox; current configured SKM; no ownership or quantity changes',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
