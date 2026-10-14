merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-14-1316-stock-pallet-unload' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Store pallet unloading accepts original frozen ROOT_STOCK_TYPE loading proof',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
