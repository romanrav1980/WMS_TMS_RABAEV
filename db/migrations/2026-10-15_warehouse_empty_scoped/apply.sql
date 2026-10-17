@@before.sql
@@resource_policy_body.sql
@@queue_body.sql
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-15-warehouse-empty-scoped','Own ordinary scoped EMPTY_TARE admission only; no quantity effects',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
