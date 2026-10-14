merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-708-group-task-origin'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing HU task reconstructs grouped receipt origin from its immutable plan, not operator input',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
