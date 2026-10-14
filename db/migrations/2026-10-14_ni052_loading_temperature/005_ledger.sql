merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-14-1160-loading-temperature' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Current declared SKU thermal limits and manual-at-loading confirmation in existing root load transaction; no sensor inference',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
