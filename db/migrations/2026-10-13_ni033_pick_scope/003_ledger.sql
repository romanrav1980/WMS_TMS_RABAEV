merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-13-877-ni033-pick-current-scope'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing pick release checks active actor/current warehouse before replay and after root resource locks',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
