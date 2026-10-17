@@before.sql
@@rrl_stock_case_return_cmd_package_body.sql
@@compile_dependents.sql
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-16-empty-short-disposition','Guarded package-only increment; see frozen manifest and wiki',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
