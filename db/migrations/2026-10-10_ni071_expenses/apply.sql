@@001_schema.sql
@@002_guards.sql
@@003_document_key.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-112-extra-expense-dual-approval' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Explicit extra expense articles existing trip or vehicle, immutable report and logistic/independent finance decisions; vehicle never allocated to goods',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
