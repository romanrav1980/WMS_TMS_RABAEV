merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-232-final-store-custody-release'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Full final receipt releases physical load custody without repeated stock',sysdate,user,'db/migrations/2026-10-11_ni053_final_custody/apply.sql','db/migrations/2026-10-11_ni053_final_custody/rollback.sql','APPLIED','Actual manual old229 and automatic marked3/6QR order2032, rollback/concurrent/replay/partial retains custody/no quantity/history rewrite/native VALID. Capacity downstream excludes only released loads.');
commit;
