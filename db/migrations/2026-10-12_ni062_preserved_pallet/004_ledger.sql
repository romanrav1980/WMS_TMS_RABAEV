merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-639-preserved-return-pallet'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Preserve unchanged whole original pallet on registered PALLET return using existing stock transaction',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
