merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-518-shared-box-assembly-date-source' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'One readonly native clock resolver for actual CASE/BOX start used by finance preview and posting guards',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
