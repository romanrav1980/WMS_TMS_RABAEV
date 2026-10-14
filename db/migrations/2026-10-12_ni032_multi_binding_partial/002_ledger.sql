merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-631-multi-binding-partial-target'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing partial target replacement across multiple own bindings with exactly one reduced physical continuation',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
