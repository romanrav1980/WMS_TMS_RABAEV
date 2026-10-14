merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-13-872-ni032-shared-binding-closure'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Explicit consumer post-arrival closure accounts for all same-owner bindings on whole source; continuation uses total own incoming',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
