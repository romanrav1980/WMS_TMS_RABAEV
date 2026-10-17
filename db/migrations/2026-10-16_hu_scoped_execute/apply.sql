@@before.sql
@@rrl_hu_exec_access_package.sql
@@rrl_hu_exec_access_package_body.sql
@@rrl_stock_hu_cmd_package_body.sql
@@rrl_stock_posting_api_package_body.sql
@@compile_dependents.sql
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-16-hu-scoped-execute','Guarded package-only increment; see frozen manifest and wiki',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
