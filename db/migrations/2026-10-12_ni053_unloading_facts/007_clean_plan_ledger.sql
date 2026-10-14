merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-544-unload-clean-plan-before-savepoint' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Unloading metadata obeys clean-transaction stock lock acquisition before local savepoint; safe plan cleanup',sysdate,user,'006_clean_plan.sql','rollback.sql','APPLIED');
/
