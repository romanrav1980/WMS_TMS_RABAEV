merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-539-store-unloading-start-finish-facts' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'System-captured unloading start; actual method/difficulty/loader finished atomically with original STORE_RECEIPT owner',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
