merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-285-warehouse-depot-source-v4'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Configured existing warehouse origin and sourceV4',sysdate,user,'db/migrations/2026-10-11_ni081_warehouse_depot/002_api.sql','db/migrations/2026-10-11_ni081_warehouse_depot/rollback.sql','APPLIED','CurrentWARE CONFIG6 version history exactreplay; sourceV4 origins; actualpositive outerrollback +nullsetting concurrent200/409/replay/resolve. No guessedrealbase or qty.');
commit;
