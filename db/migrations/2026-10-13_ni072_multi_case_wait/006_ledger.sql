merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-13-007-ni072-multi-case-wait'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Prepared ST supports multiple standalone CASE places with bounded exact per-place frozen plans; sibling completion does not invalidate another case source',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
