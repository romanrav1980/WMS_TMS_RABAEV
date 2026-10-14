merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-403-grouped-interware-plan' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Immutable whole multi-ST source plan, no quantity effect',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
