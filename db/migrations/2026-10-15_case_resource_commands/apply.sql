-- MIGRATION_ID: 2026-10-15-case-resource-commands
-- PREPARED only. Root independent review/apply required; no quantity fixture writes.
@@before.sql
@@schema.sql
@@spec.sql
@@case_access_spec.sql
@@case_access_body.sql
@@resource_policy_body.sql
@@body.sql
@@version_guard.sql
@@start_guard.sql
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-15-case-resource-commands','Scoped CASE CLAIM/START metadata with derived assignment versions and immutable APPLIED/REJECTED receipts',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
