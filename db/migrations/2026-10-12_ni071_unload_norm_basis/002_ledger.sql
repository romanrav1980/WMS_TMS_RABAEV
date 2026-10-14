merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-572-explicit-unload-cost-basis' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Explicit POINT or PLACE unloading charge and pallet rate; preserve historical exact retries',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
