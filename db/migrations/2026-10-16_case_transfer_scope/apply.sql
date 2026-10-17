@@before.sql
@@rrl_case_transfer_scope_package.sql
@@rrl_case_transfer_scope_package_body.sql
@@rrl_case_resource_policy_package_body.sql
@@compile_dependents.sql
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-16-case-transfer-scope','Guarded package-only increment; see frozen manifest and wiki',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
