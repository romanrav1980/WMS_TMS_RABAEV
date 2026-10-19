whenever sqlerror exit failure rollback
@@001_qc_access.sql
@@002_stock_guard.sql
@@003_posting.sql
declare n number;begin select count(*)into n from user_errors where NAME in('RRL_OUTGOING_QC_ACCESS','RRL_TRADE_STOCK_GUARD','RRL_STOCK_POSTING_API');if n<>0 then raise_application_error(-20999,'TRADE_QC_ADMISSION_COMPILE_ERRORS');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-quality-admission'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Resolve physical QC identifiers and enforce scoped current legal-owner quality admission',sysdate,user,'apply.sql','rollback.sql','APPLIED');commit;
