merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-529-versioned-existing-transport-norms' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Immutable period/currency/type/size and unload norms published from exact existing legacy transport-price row',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
