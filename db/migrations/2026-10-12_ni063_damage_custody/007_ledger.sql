merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-552-tare-damage-custody' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Provenance of new damaged tare across existing dual-party transfers and owner-warehouse writeoff; physical balance stays original stock root',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
