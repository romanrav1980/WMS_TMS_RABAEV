merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-13-006-ni072-case-wait-identity'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Waiting physical task owns its self source task ID; original CASE ID remains in immutable plan; permits repeated rescheduling without changing old records',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
