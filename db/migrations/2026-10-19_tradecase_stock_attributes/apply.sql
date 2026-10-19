whenever sqlerror exit failure rollback
@@001_schema.sql
@@002_guard.sql
@@003_api.sql
declare n number;begin
 select count(*)into n from user_errors where name in('RRL_TRADE_STOCK_API','RRL_TRADE_STOCK_GUARD');
 if n<>0 then raise_application_error(-20999,'TRADE_STOCK_NEW_API_COMPILE_ERRORS');end if;
end;
/
@@004_document_api.sql
@@005_posting_guard.sql
@@006_cell_invariant.sql
@@007_eligibility.sql
@@008_write_guards.sql
declare n number;begin
 select count(*)into n from user_errors where name like 'RRL_TRADE%' or name in('RRL_STOCK_POSTING_API','RRL_STOCK_INVARIANT_CORE','RRL_STOCK_ELIGIBILITY');
 if n<>0 then raise_application_error(-20999,'TRADE_STOCK_COMPILE_ERRORS');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-stock-attributes' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(x.MIGRATION_ID,'TRADECASE legal attributes on existing physical unit keys; scoped metadata and stock admission guards',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
