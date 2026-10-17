@@before.sql
@@history_trigger.sql
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-16-finance-rate-scope','Scoped rate history; shared access REV',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
